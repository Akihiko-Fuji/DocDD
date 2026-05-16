"""T-Spin detector based on DOC-SPC-024 and DOC-SPC-024a."""
from .constants import BOARD_WIDTH, BOARD_HEIGHT


def is_tspin(board, piece, last_action: str) -> bool:
    # 仕様根拠: T-Spin は T ピース限定かつ「直前の成立操作が回転」である必要がある。
    if piece.kind != "T" or last_action != "rotate":
        return False

    # 仕様根拠: 3-corner rule（対角4点のうち3点以上が占有/盤外）を採用。
    occupied_corners = 0
    for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        x, y = piece.origin_x + dx, piece.origin_y + dy
        is_outside = x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT
        if is_outside or board[y][x]:
            occupied_corners += 1

    return occupied_corners >= 3
