from src.DocDD_coding.falling_block_puzzle.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.DocDD_coding.falling_block_puzzle import renderer


def test_play_layout_rectangles_fit_screen():
    board_left = renderer.BOARD_ORIGIN_X - renderer.CELL_SIZE
    board_top = renderer.BOARD_ORIGIN_Y
    board_width = (renderer.BOARD_COLS + 2) * renderer.CELL_SIZE
    board_height = renderer.BOARD_ROWS * renderer.CELL_SIZE

    assert board_left >= 0
    assert board_top >= 0
    assert board_left + board_width <= SCREEN_WIDTH
    assert board_top + board_height <= SCREEN_HEIGHT

    assert renderer.SIDEBAR_X >= 0
    assert renderer.SIDEBAR_Y >= 0
    assert renderer.SIDEBAR_X + renderer.SIDEBAR_W <= SCREEN_WIDTH
    assert renderer.SIDEBAR_Y + renderer.SIDEBAR_H <= SCREEN_HEIGHT


def test_board_and_sidebar_do_not_overlap():
    board_right = renderer.BOARD_ORIGIN_X + (renderer.BOARD_COLS + 1) * renderer.CELL_SIZE
    assert renderer.SIDEBAR_X >= board_right + 8


def test_next_box_area_fits_screen():
    assert renderer.NEXT_BOX_X >= 0
    assert renderer.NEXT_BOX_Y >= 0
    assert renderer.NEXT_BOX_X + renderer.NEXT_BOX_W <= SCREEN_WIDTH
    assert renderer.NEXT_BOX_Y + renderer.NEXT_BOX_H <= SCREEN_HEIGHT


def test_sidebar_value_positions_stay_inside_sidebar():
    value_positions = [
        (renderer.SCORE_VALUE_X, renderer.SCORE_VALUE_Y),
        (renderer.LEVEL_VALUE_X, renderer.LEVEL_VALUE_Y),
        (renderer.LINES_VALUE_X, renderer.LINES_VALUE_Y),
    ]
    for x, y in value_positions:
        assert renderer.SIDEBAR_X <= x <= renderer.SIDEBAR_X + renderer.SIDEBAR_W
        assert renderer.SIDEBAR_Y <= y <= renderer.SIDEBAR_Y + renderer.SIDEBAR_H


def test_next_layout_points_stay_inside_next_box():
    assert renderer.NEXT_BOX_X <= renderer.NEXT_LABEL_X <= renderer.NEXT_BOX_X + renderer.NEXT_BOX_W
    assert renderer.NEXT_BOX_Y <= renderer.NEXT_LABEL_Y <= renderer.NEXT_BOX_Y + renderer.NEXT_BOX_H
    assert renderer.NEXT_BOX_X <= renderer.NEXT_PIECE_CENTER_X <= renderer.NEXT_BOX_X + renderer.NEXT_BOX_W
    assert renderer.NEXT_BOX_Y <= renderer.NEXT_PIECE_CENTER_Y <= renderer.NEXT_BOX_Y + renderer.NEXT_BOX_H
