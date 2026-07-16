"""Game session orchestration.

Based on:
- DOC-DSN-032 State Machine Design
- DOC-SPC-020 Game Rules Specification
- DOC-SPC-023 Scoring and Level Specification
"""
from typing import Optional

from .models import GameSession
from .pieces import spawn_piece
from .randomizer import PieceRandomizer
from .board_rules import can_move, detect_full_lines, clear_lines, is_valid_position, occupied_cells
from .active_piece_service import move, rotate
from .tspin_detector import is_tspin
from .scoring_service import line_clear_points, apply_score
from .level_progression_service import calc_level
from .constants import ARE_FRAMES, FRAMES_PER_ROW, SOFT_DROP_INTERVAL, BOARD_HEIGHT, BOARD_WIDTH
from .constants import LINE_CLEAR_DELAY, TSPIN_FLASH_FRAMES


class SessionService:
    def __init__(self, seed: Optional[int] = None):
        self.rand = PieceRandomizer(seed)

    def _normalize_start_level(self, start_level: int) -> int:
        # A-TYPE 開始レベルは仕様上 0..9。API直呼びでも落ちないよう境界内へ丸める。
        return max(0, min(9, int(start_level)))

    def _safe_fall_interval(self, level: int) -> int:
        if level in FRAMES_PER_ROW:
            return FRAMES_PER_ROW[level]
        return FRAMES_PER_ROW[0] if level < 0 else FRAMES_PER_ROW[max(FRAMES_PER_ROW)]

    def _validate_board_shape(self, board: list[list[int]]) -> None:
        if len(board) != BOARD_HEIGHT or any(len(row) != BOARD_WIDTH for row in board):
            raise ValueError("board shape must be 10x18")

    def new_play_session(self, start_level: int = 0) -> GameSession:
        normalized_start = self._normalize_start_level(start_level)
        s = GameSession(start_level=normalized_start, level=normalized_start)
        s.next_kind = self.rand.next_piece()
        self.spawn_from_next(s)
        return s

    def spawn_from_next(self, s: GameSession) -> None:
        self._validate_board_shape(s.board)
        try:
            s.current = spawn_piece(s.next_kind)
        except KeyError as exc:
            raise ValueError(f"invalid next piece kind: {s.next_kind}") from exc

        s.next_kind = self.rand.next_piece()
        s.soft_drop_cells = 0
        s.soft_drop_counter = 0
        s.fall_counter = 0
        s.are_timer = 0

        # 出現直後に衝突する場合はゲームオーバー理由を保持する。
        if not is_valid_position(s.board, s.current):
            s.over_reason = "spawn_blocked"

    def lock_piece(self, s: GameSession) -> None:
        if s.current is None:
            raise ValueError("current piece must exist before lock")
        self._validate_board_shape(s.board)

        locked_piece = s.current
        locked_cells = occupied_cells(locked_piece)
        min_x = min(x for x, _ in locked_cells)
        max_x = max(x for x, _ in locked_cells)
        min_y = min(y for _, y in locked_cells)
        max_y = max(y for _, y in locked_cells)
        for x, y in locked_cells:
            if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
                raise ValueError(f"occupied cell out of board: {(x, y)}")
            s.board[y][x] = self._cell_value_for_piece(
                locked_piece.kind,
                locked_piece.rotation,
                x,
                y,
                min_x,
                max_x,
                min_y,
                max_y,
            )

        lines = detect_full_lines(s.board)
        tspin = is_tspin(s.board, locked_piece, locked_piece.last_successful_action)
        if lines:
            s.line_clear_rows = lines[:]
            s.line_clear_timer = LINE_CLEAR_DELAY

        s.lines += len(lines)
        s.score = apply_score(s.score, line_clear_points(s.level, len(lines), tspin) + s.soft_drop_cells)
        s.level = calc_level(s.start_level, s.lines)

        # T-Spin 成立をプレイヤーへ短時間通知するため 30フレーム表示する。
        s.tspin_flash = TSPIN_FLASH_FRAMES if tspin else 0
        # 固定済みピースを current に残すと、盤面セルと二重描画される。
        # 次ピースは仕様で定めた ARE 完了後に出現させる。
        s.current = None
        if not lines:
            s.are_timer = ARE_FRAMES

    def step_play(self, s: GameSession, inputs: set[str]) -> str:
        self._validate_board_shape(s.board)
        if s.tspin_flash > 0:
            s.tspin_flash -= 1

        if s.line_clear_timer > 0:
            s.line_clear_timer -= 1
            if s.line_clear_timer == 0:
                s.board = clear_lines(s.board, s.line_clear_rows)
                s.line_clear_rows = []
                s.are_timer = ARE_FRAMES
            return "continue"

        if s.are_timer > 0:
            s.are_timer -= 1
            if s.are_timer == 0:
                self.spawn_from_next(s)
                if s.over_reason:
                    return "gameover"
                return "spawned"
            return "continue"

        if s.current is None:
            raise ValueError("current piece is None outside line-clear/ARE wait")

        p = s.current

        # DOC-DSN-032 の優先順: START は最優先で他入力を無効化。
        if "start" in inputs:
            return "pause"

        if "select" in inputs:
            s.next_visible = not s.next_visible

        if "a" in inputs and "b" not in inputs:
            p, _ = rotate(s.board, p, True)
        elif "b" in inputs and "a" not in inputs:
            p, _ = rotate(s.board, p, False)

        if "left" in inputs and "right" not in inputs:
            p, _ = move(s.board, p, -1, 0, "move")
        elif "right" in inputs and "left" not in inputs:
            p, _ = move(s.board, p, 1, 0, "move")

        if "down" in inputs:
            # ソフトドロップと通常落下は別タイマで管理し、同一フレームの二重落下を防ぐ。
            s.soft_drop_counter += 1
            if s.soft_drop_counter >= SOFT_DROP_INTERVAL:
                s.soft_drop_counter = 0
                p, moved = move(s.board, p, 0, 1, "soft_drop")
                if moved:
                    # DOC-SPC-023: ソフトドロップ 1 マスごとに 1 点。
                    s.soft_drop_cells += 1
                else:
                    s.current = p
                    self.lock_piece(s)
                    return "locked"
        else:
            s.soft_drop_counter = 0
            s.fall_counter += 1
            if s.fall_counter >= self._safe_fall_interval(s.level):
                s.fall_counter = 0
                if can_move(s.board, p, 0, 1):
                    p, _ = move(s.board, p, 0, 1, "fall")
                else:
                    s.current = p
                    self.lock_piece(s)
                    return "locked"

        s.current = p
        return "continue"

    def _cell_value_for_piece(
        self,
        kind: str,
        rotation: int,
        x: int,
        y: int,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
    ) -> int:
        if kind != "I":
            return ord(kind)
        if rotation % 2 == 0:
            return 6 if x in (min_x, max_x) else 5
        return 6 if y in (min_y, max_y) else 5
