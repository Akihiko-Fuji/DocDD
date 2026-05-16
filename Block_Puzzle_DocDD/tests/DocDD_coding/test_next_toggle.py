from src.DocDD_coding.falling_block_puzzle.game_session import SessionService


def test_select_toggles_next():
    svc = SessionService(0)
    s = svc.new_play_session(0)
    s.state = "PLAY"
    old = s.next_visible
    svc.step_play(s, {"select"})
    assert s.next_visible != old
