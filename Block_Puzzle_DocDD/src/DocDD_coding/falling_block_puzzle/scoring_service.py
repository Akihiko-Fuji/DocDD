"""Scoring based on DOC-SPC-023."""
from .constants import LINE_CLEAR_BASE,TSPIN_BASE,MAX_SCORE

def line_clear_points(level:int, lines:int, tspin:bool)->int:
    base=(TSPIN_BASE if tspin else LINE_CLEAR_BASE).get(lines,0)
    return base*(level+1)

def apply_score(total:int, add:int)->int:
    return min(MAX_SCORE,total+add)
