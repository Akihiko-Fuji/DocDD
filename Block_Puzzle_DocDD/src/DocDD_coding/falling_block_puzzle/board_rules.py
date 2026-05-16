"""Board rules.
Based on DOC-SPC-020/024 and DOC-DSN-034.
"""
from .constants import BOARD_WIDTH, BOARD_HEIGHT
from .pieces import occupied_cells

def in_bounds(x:int,y:int)->bool:
    return 0<=x<BOARD_WIDTH and 0<=y<BOARD_HEIGHT

def is_valid_position(board:list[list[int]], piece)->bool:
    for x,y in occupied_cells(piece):
        if not in_bounds(x,y) or board[y][x]:
            return False
    return True

def can_move(board,piece,dx:int,dy:int)->bool:
    from dataclasses import replace
    return is_valid_position(board, replace(piece, origin_x=piece.origin_x+dx, origin_y=piece.origin_y+dy))

def detect_full_lines(board):
    return [y for y,row in enumerate(board) if all(row)]

def clear_lines(board, lines):
    kept=[row[:] for y,row in enumerate(board) if y not in lines]
    while len(kept)<BOARD_HEIGHT:
        kept.insert(0,[0]*BOARD_WIDTH)
    return kept
