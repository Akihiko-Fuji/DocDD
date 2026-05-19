from src.DocDD_coding.falling_block_puzzle.board_rules import (
    can_move,
    clear_lines,
    detect_full_lines,
    in_bounds,
    is_valid_position,
)
from src.DocDD_coding.falling_block_puzzle.pieces import spawn_piece


def _empty_board():
    return [[0] * 10 for _ in range(18)]


def test_bounds():
    assert in_bounds(0, 0) and in_bounds(9, 17)
    assert not in_bounds(-1, 0) and not in_bounds(10, 0) and not in_bounds(0, 18)


def test_is_valid_position_checks_wall_and_occupied_cell():
    board = _empty_board()

    # 左壁外に出るように原点をずらす
    piece = spawn_piece("O")
    piece = piece.__class__(kind=piece.kind, origin_x=-1, origin_y=piece.origin_y, rotation=piece.rotation)
    assert not is_valid_position(board, piece)

    # 既存ブロック衝突
    piece2 = spawn_piece("O")
    hit_x, hit_y = piece2.origin_x, piece2.origin_y
    board[hit_y][hit_x] = 1
    assert not is_valid_position(board, piece2)


def test_can_move_reflects_next_position_collision():
    board = _empty_board()
    piece = spawn_piece("O")
    assert can_move(board, piece, 0, 1)

    # 1マス下に障害物を置く
    board[piece.origin_y + 1][piece.origin_x] = 1
    assert not can_move(board, piece, 0, 1)


def test_line_clear_pack():
    b = _empty_board()
    b[17] = [1] * 10
    b[16] = [1] * 10

    lines = detect_full_lines(b)
    assert lines == [16, 17]

    nb = clear_lines(b, lines)
    assert nb[0] == [0] * 10 and nb[1] == [0] * 10
    assert len(nb) == 18
