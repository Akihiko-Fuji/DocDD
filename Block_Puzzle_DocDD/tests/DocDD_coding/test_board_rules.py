from src.DocDD_coding.falling_block_puzzle.board_rules import in_bounds, detect_full_lines, clear_lines


def test_bounds():
    assert in_bounds(0, 0) and in_bounds(9, 17)
    assert not in_bounds(-1, 0) and not in_bounds(10, 0) and not in_bounds(0, 18)


def test_line_clear_pack():
    b = [[0] * 10 for _ in range(18)]
    b[17] = [1] * 10
    b[16] = [1] * 10

    lines = detect_full_lines(b)
    assert lines == [16, 17]

    nb = clear_lines(b, lines)
    assert nb[0] == [0] * 10 and nb[1] == [0] * 10
