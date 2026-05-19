from src.DocDD_coding.falling_block_puzzle.level_progression_service import calc_level
from src.DocDD_coding.falling_block_puzzle.scoring_service import apply_score, line_clear_points


def test_line_scores():
    assert line_clear_points(0, 1, False) == 40
    assert line_clear_points(0, 4, False) == 1200


def test_multiplier_and_tspin_separate():
    assert line_clear_points(4, 1, True) == 4000


def test_invalid_line_count_returns_zero():
    assert line_clear_points(0, 5, False) == 0
    assert line_clear_points(0, 99, True) == 0


def test_apply_score_clamps_to_maximum():
    assert apply_score(999_000, 2_000) == 999_999
    assert apply_score(100, 20) == 120


def test_level_progression():
    assert calc_level(0, 9) == 0 and calc_level(0, 10) == 1
    assert calc_level(9, 100) == 10 and calc_level(9, 300) == 20


def test_level_progression_threshold_and_cap():
    # start_level=3 なら閾値は 40
    assert calc_level(3, 39) == 3
    assert calc_level(3, 40) == 4
    assert calc_level(20, 9999) == 20
