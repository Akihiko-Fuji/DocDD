from src.DocDD_coding.falling_block_puzzle.pieces import spawn_piece
from src.DocDD_coding.falling_block_puzzle.tspin_detector import is_tspin


def test_tspin_true_and_false_cases():
    b = [[0] * 10 for _ in range(18)]

    p = spawn_piece("T")
    p.origin_x = 0
    p.origin_y = 0
    assert is_tspin(b, p, "rotate")

    p2 = spawn_piece("T")
    assert not is_tspin(b, p2, "move")

    p3 = spawn_piece("I")
    assert not is_tspin(b, p3, "rotate")
