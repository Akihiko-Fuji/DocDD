from src.DocDD_coding.falling_block_puzzle.scoring_service import line_clear_points
from src.DocDD_coding.falling_block_puzzle.level_progression_service import calc_level

def test_line_scores():
    assert line_clear_points(0,1,False)==40
    assert line_clear_points(0,4,False)==1200

def test_multiplier_and_tspin_separate():
    assert line_clear_points(4,1,True)==4000

def test_level_progression():
    assert calc_level(0,9)==0 and calc_level(0,10)==1
    assert calc_level(9,100)==10 and calc_level(9,300)==20
