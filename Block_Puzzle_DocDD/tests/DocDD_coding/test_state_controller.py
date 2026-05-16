from src.DocDD_coding.falling_block_puzzle.state_controller import StateController
from src.DocDD_coding.falling_block_puzzle.models import GameSession, GameState


def test_main_transitions():
    c = StateController()
    s = GameSession(state=GameState.TITLE)

    c.transition(s, "start")
    assert s.state == GameState.SETUP_A

    c.transition(s, "start")
    assert s.state == GameState.PLAY

    c.transition(s, "start")
    assert s.state == GameState.PAUSE

    c.transition(s, "start")
    assert s.state == GameState.PLAY

    c.transition(s, "gameover")
    assert s.state == GameState.GAMEOVER

    c.transition(s, "retry")
    assert s.state == GameState.SETUP_A
