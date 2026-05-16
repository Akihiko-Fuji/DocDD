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
from .constants import FRAMES_PER_ROW, SOFT_DROP_INTERVAL, BOARD_HEIGHT, BOARD_WIDTH
from .constants import LINE_CLEAR_DELAY


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

        # 出現直後に衝突する場合はゲームオーバー理由を保持する。
        if not is_valid_position(s.board, s.current):
            s.over_reason = "spawn_blocked"

    def lock_piece(self, s: GameSession) -> None:
        if s.current is None:
            raise ValueError("current piece must exist before lock")
        self._validate_board_shape(s.board)

        for x, y in occupied_cells(s.current):
            if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
                raise ValueError(f"occupied cell out of board: {(x, y)}")
            s.board[y][x] = self._cell_value_for_piece(s.current.kind, s.current.rotation, x, y)

        lines = detect_full_lines(s.board)
        tspin = is_tspin(s.board, s.current, s.current.last_successful_action)
        if lines:
            s.line_clear_rows = lines[:]
            s.line_clear_timer = LINE_CLEAR_DELAY

        s.lines += len(lines)
        s.score = apply_score(s.score, line_clear_points(s.level, len(lines), tspin) + s.soft_drop_cells)
        s.level = calc_level(s.start_level, s.lines)

        # T-Spin 成立をプレイヤーへ短時間通知するため 30フレーム表示する。
        s.tspin_flash = 30 if tspin else 0
        if not lines:
            self.spawn_from_next(s)

    def step_play(self, s: GameSession, inputs: set[str]) -> str:
        if s.current is None:
            raise ValueError("current piece is None; call spawn_from_next/new_play_session first")
        self._validate_board_shape(s.board)
        if s.line_clear_timer > 0:
            s.line_clear_timer -= 1
            if s.line_clear_timer == 0:
                s.board = clear_lines(s.board, s.line_clear_rows)
                s.line_clear_rows = []
                self.spawn_from_next(s)
                if s.over_reason:
                    return "gameover"
                return "locked"
            return "continue"

        p = s.current

        # DOC-DSN-032 の優先順: START は最優先で他入力を無効化。
        if "start" in inputs:
            return "pause"

        if "select" in inputs:
            s.next_visible = not s.next_visible

        if "a" in inputs:
            p, _ = rotate(s.board, p, True)
        elif "b" in inputs:
            p, _ = rotate(s.board, p, False)

        if "left" in inputs and "right" not in inputs:
            p, _ = move(s.board, p, -1, 0, "move")
        elif "right" in inputs and "left" not in inputs:
            p, _ = move(s.board, p, 1, 0, "move")

        if "down" in inputs:
            p, moved = move(s.board, p, 0, 1, "soft_drop")
            if moved:
                # DOC-SPC-023: ソフトドロップ 1 マスごとに 1 点。
                s.soft_drop_cells += 1

        s.fall_counter += 1
        interval = SOFT_DROP_INTERVAL if "down" in inputs else self._safe_fall_interval(s.level)

        if s.fall_counter >= interval:
            s.fall_counter = 0
            if can_move(s.board, p, 0, 1):
                p, _ = move(s.board, p, 0, 1, "fall")
            else:
                s.current = p
                self.lock_piece(s)
                if s.over_reason:
                    return "gameover"
                return "locked"

        s.current = p
        if s.tspin_flash > 0:
            s.tspin_flash -= 1
        return "continue"

    def _cell_value_for_piece(self, kind: str, rotation: int, x: int, y: int) -> int:
        if kind != "I":
            return ord(kind)
        if rotation % 2 == 0:
            return 6 if x in (3, 6) else 5
        return 6 if y in (0, 3) else 5
