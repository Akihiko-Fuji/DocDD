from src.DocDD_coding.falling_block_puzzle.pieces import spawn_piece
from src.DocDD_coding.falling_block_puzzle.active_piece_service import move, rotate


def test_wall_rotation_fail_no_kick():
    b = [[0] * 10 for _ in range(18)]
    p = spawn_piece("J")
    p.origin_x = 0

    old = (p.origin_x, p.origin_y, p.rotation)
    p2, ok = rotate(b, p, False)

    assert not ok
    assert (p2.origin_x, p2.origin_y, p2.rotation) == old


def test_automatic_fall_preserves_last_player_rotation():
    b = [[0] * 10 for _ in range(18)]
    p = spawn_piece("T")
    p.last_successful_action = "rotate"

    p2, ok = move(b, p, 0, 1, "fall")

    assert ok
    assert p2.last_successful_action == "rotate"
