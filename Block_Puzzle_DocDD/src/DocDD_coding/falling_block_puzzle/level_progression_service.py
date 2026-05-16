"""Level progression based on DOC-SPC-023."""
from .constants import MAX_LEVEL

def calc_level(start_level:int, total_lines:int)->int:
    threshold=start_level*10+10
    if total_lines<threshold:
        return start_level
    return min(MAX_LEVEL, start_level+1+((total_lines-threshold)//10))
