from src.DocDD_coding.falling_block_puzzle.pieces import spawn_piece
from src.DocDD_coding.falling_block_puzzle.active_piece_service import rotate


def test_wall_rotation_fail_no_kick():
    b = [[0] * 10 for _ in range(18)]
    p = spawn_piece("J")
    p.origin_x = 0

    old = (p.origin_x, p.origin_y, p.rotation)
    p2, ok = rotate(b, p, False)

    assert not ok
    assert (p2.origin_x, p2.origin_y, p2.rotation) == old
