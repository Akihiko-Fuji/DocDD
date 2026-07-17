from src.DocDD_coding.falling_block_puzzle.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.DocDD_coding.falling_block_puzzle import renderer


def test_play_layout_rectangles_fit_screen():
    # sidewall.png はセル幅ではなく素材幅32pxで盤面外側へ配置する。
    board_left = renderer.BOARD_ORIGIN_X - renderer.SIDEWALL_WIDTH
    board_top = renderer.BOARD_ORIGIN_Y
    board_width = renderer.BOARD_COLS * renderer.CELL_SIZE + 2 * renderer.SIDEWALL_WIDTH
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


def test_sidebar_keeps_source_aspect_ratio_with_rounding():
    # 252x648 を幅170へ縮小したときの縦横比を1px以内で維持する。
    expected_height = round(648 * renderer.SIDEBAR_W / 252)
    assert abs(renderer.SIDEBAR_H - expected_height) <= 1


def test_next_layout_points_stay_inside_next_box():
    assert renderer.NEXT_BOX_X <= renderer.NEXT_LABEL_X <= renderer.NEXT_BOX_X + renderer.NEXT_BOX_W
    assert renderer.NEXT_BOX_Y <= renderer.NEXT_LABEL_Y <= renderer.NEXT_BOX_Y + renderer.NEXT_BOX_H
    assert renderer.NEXT_BOX_X <= renderer.NEXT_PIECE_CENTER_X <= renderer.NEXT_BOX_X + renderer.NEXT_BOX_W
    assert renderer.NEXT_BOX_Y <= renderer.NEXT_PIECE_CENTER_Y <= renderer.NEXT_BOX_Y + renderer.NEXT_BOX_H


def test_sidebar_values_share_right_alignment_and_use_their_own_panels():
    # SCORE の最下位桁を見出しの R 付近へ置き、3項目を同じ右端で揃える。
    assert renderer.HUD_VALUE_RIGHT_X == renderer.SIDEBAR_X + 132
    assert renderer.SCORE_VALUE_X == renderer.HUD_VALUE_RIGHT_X
    assert renderer.LEVEL_VALUE_X == renderer.HUD_VALUE_RIGHT_X
    assert renderer.LINES_VALUE_X == renderer.HUD_VALUE_RIGHT_X

    # LEVEL / LINES の値は、それぞれのラベル枠内の下段へ配置する。
    assert renderer.LEVEL_VALUE_Y == renderer.SIDEBAR_Y + 176
    assert renderer.LINES_VALUE_Y == renderer.SIDEBAR_Y + 249
    assert renderer.SCORE_VALUE_Y < renderer.LEVEL_VALUE_Y < renderer.LINES_VALUE_Y
