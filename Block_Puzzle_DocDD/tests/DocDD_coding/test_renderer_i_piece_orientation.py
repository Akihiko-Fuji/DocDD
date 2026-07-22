from src.DocDD_coding.falling_block_puzzle.constants import (
    I_CENTER_HORIZONTAL,
    I_CENTER_VERTICAL,
    I_END_BOTTOM,
    I_END_LEFT,
    I_END_RIGHT,
    I_END_TOP,
)
from src.DocDD_coding.falling_block_puzzle.renderer import Renderer


def _renderer_without_display() -> Renderer:
    return Renderer.__new__(Renderer)


def test_fixed_i_piece_roles_map_to_axis_aligned_sprite_rotations():
    renderer = _renderer_without_display()

    assert renderer._board_cell_sprite(I_END_LEFT) == ("brick5end", 90)
    assert renderer._board_cell_sprite(I_CENTER_HORIZONTAL) == ("brick5center", 90)
    assert renderer._board_cell_sprite(I_END_RIGHT) == ("brick5end", -90)
    assert renderer._board_cell_sprite(I_END_TOP) == ("brick5end", 0)
    assert renderer._board_cell_sprite(I_CENTER_VERTICAL) == ("brick5center", 0)
    assert renderer._board_cell_sprite(I_END_BOTTOM) == ("brick5end", 180)


def test_active_i_piece_assigns_outward_end_caps_for_both_axes():
    renderer = _renderer_without_display()
    horizontal = [(3, 7), (4, 7), (5, 7), (6, 7)]
    vertical = [(4, 5), (4, 6), (4, 7), (4, 8)]

    assert [
        renderer._active_cell_sprite("I", 0, x, y, horizontal)
        for x, y in horizontal
    ] == [
        ("brick5end", 90),
        ("brick5center", 90),
        ("brick5center", 90),
        ("brick5end", -90),
    ]
    assert [
        renderer._active_cell_sprite("I", 1, x, y, vertical)
        for x, y in vertical
    ] == [
        ("brick5end", 0),
        ("brick5center", 0),
        ("brick5center", 0),
        ("brick5end", 180),
    ]


def test_next_i_piece_draws_horizontal_end_center_center_end_sequence():
    renderer = _renderer_without_display()
    drawn_cells = []
    renderer._draw_cell = (
        lambda x, y, size, key, angle=0: drawn_cells.append((key, angle))
    )

    renderer._draw_next_piece("I")

    assert drawn_cells == [
        ("brick5end", 90),
        ("brick5center", 90),
        ("brick5center", 90),
        ("brick5end", -90),
    ]
