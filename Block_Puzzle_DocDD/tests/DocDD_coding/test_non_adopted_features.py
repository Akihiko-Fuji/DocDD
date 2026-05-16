from src.DocDD_coding.falling_block_puzzle.input_mapper import KEY_BINDINGS
from src.DocDD_coding.falling_block_puzzle.randomizer import PieceRandomizer
from src.DocDD_coding.falling_block_puzzle.models import GameSession, GameState
from src.DocDD_coding.falling_block_puzzle.state_controller import StateController


def test_no_harddrop_hold():
    assert "hard_drop" not in KEY_BINDINGS and "hold" not in KEY_BINDINGS


def test_not_7_bag_like_perfect_cycle():
    r = PieceRandomizer(1)
    seq = [r.next_piece() for _ in range(14)]
    assert len(set(seq[:7])) != 7 or len(set(seq[7:14])) != 7


def test_no_b_type_transition():
    s = GameSession(state=GameState.TITLE)
    StateController().transition(s, "mode_b")
    assert s.state == GameState.TITLE
