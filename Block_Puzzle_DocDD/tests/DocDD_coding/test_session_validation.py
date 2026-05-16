from src.DocDD_coding.falling_block_puzzle.game_session import SessionService


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
