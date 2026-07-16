from src.DocDD_coding.falling_block_puzzle.game_session import SessionService
from src.DocDD_coding.falling_block_puzzle.constants import ARE_FRAMES, LINE_CLEAR_DELAY, SOFT_DROP_INTERVAL
from src.DocDD_coding.falling_block_puzzle.models import GameSession, PieceState


def test_start_level_is_clamped_to_a_type_range():
    svc = SessionService(0)
    s_low = svc.new_play_session(-5)
    s_high = svc.new_play_session(99)
    assert s_low.start_level == 0 and s_low.level == 0
    assert s_high.start_level == 9 and s_high.level == 9


def test_invalid_runtime_level_does_not_crash_fall_lookup():
    svc = SessionService(0)
    s = svc.new_play_session(0)
    s.level = 999
    assert svc.step_play(s, set()) in {"continue", "locked", "gameover"}


def test_soft_drop_uses_independent_three_frame_timer_without_double_fall():
    svc = SessionService(0)
    s = svc.new_play_session(0)
    start_y = s.current.origin_y
    s.fall_counter = 7

    for _ in range(SOFT_DROP_INTERVAL - 1):
        assert svc.step_play(s, {"down"}) == "continue"
        assert s.current.origin_y == start_y

    assert svc.step_play(s, {"down"}) == "continue"
    assert s.current.origin_y == start_y + 1
    assert s.soft_drop_cells == 1
    # Down中は通常落下タイマを停止し、離した後に残りから再開する。
    assert s.fall_counter == 7


def test_piece_spawns_only_after_are_wait():
    svc = SessionService(0)
    s = GameSession(current=PieceState("O", 4, 16), next_kind="I")

    svc.lock_piece(s)

    assert s.current is None
    assert s.are_timer == ARE_FRAMES
    for _ in range(ARE_FRAMES - 1):
        assert svc.step_play(s, set()) == "continue"
        assert s.current is None

    assert svc.step_play(s, set()) == "spawned"
    assert s.current is not None
    assert s.are_timer == 0


def test_a_and_b_pressed_together_do_not_rotate():
    svc = SessionService(0)
    s = svc.new_play_session(0)
    original_rotation = s.current.rotation

    assert svc.step_play(s, {"a", "b"}) == "continue"
    assert s.current.rotation == original_rotation


def test_moved_i_piece_keeps_end_tiles_at_relative_ends_when_locked():
    svc = SessionService(0)
    s = GameSession(current=PieceState("I", 6, 14, rotation=0), next_kind="O")

    svc.lock_piece(s)

    occupied = [(x, value) for x, value in enumerate(s.board[15]) if value]
    assert occupied == [(5, 6), (6, 5), (7, 5), (8, 6)]


def test_line_clear_wait_is_followed_by_are_before_spawn():
    svc = SessionService(0)
    s = GameSession(current=PieceState("I", 4, 16, rotation=0), next_kind="O")
    s.board[17] = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1]

    svc.lock_piece(s)

    assert s.line_clear_timer == LINE_CLEAR_DELAY
    for _ in range(LINE_CLEAR_DELAY):
        assert svc.step_play(s, set()) == "continue"
    assert s.line_clear_timer == 0
    assert s.are_timer == ARE_FRAMES
    assert s.current is None

    for _ in range(ARE_FRAMES - 1):
        assert svc.step_play(s, set()) == "continue"
    assert svc.step_play(s, set()) == "spawned"
