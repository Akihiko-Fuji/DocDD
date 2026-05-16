from src.DocDD_coding.falling_block_puzzle.pieces import PIECE_OFFSETS, spawn_piece, occupied_cells


def test_all_pieces_rotations():
    for k in "IOTJLSZ":
        assert set(PIECE_OFFSETS[k].keys()) == {0, 1, 2, 3}


def test_o_same_all_rotations():
    assert PIECE_OFFSETS["O"][0] == PIECE_OFFSETS["O"][1] == PIECE_OFFSETS["O"][2] == PIECE_OFFSETS["O"][3]


def test_spawn_rotation_zero_and_cells():
    p = spawn_piece("T")
    assert p.rotation == 0
    assert set(occupied_cells(p)) == {(3, 1), (4, 1), (5, 1), (4, 0)}
