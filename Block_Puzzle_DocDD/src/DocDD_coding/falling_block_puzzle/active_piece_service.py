"""Active piece operations.

Based on:
- DOC-SPC-024 Piece Rotation and Collision Specification
- DOC-DSN-034 Module Design
- DOC-DSN-039 Interface Contract
"""
from dataclasses import replace

from .board_rules import is_valid_position


def rotate(board, piece, clockwise: bool):
    # 仕様根拠: DOC-SPC-024 では「回転後位置が有効な場合のみ成立」とされる。
    # そのため、先に候補状態を作り、盤面妥当性を確認してから確定する。
    new_rot = (piece.rotation + 1) % 4 if clockwise else (piece.rotation + 3) % 4
    cand = replace(piece, rotation=new_rot, last_successful_action="rotate")

    if is_valid_position(board, cand):
        # 仕様根拠: T-Spin 判定では「最終成立操作が回転か」を参照するため、
        # 回転が成立した時だけ last_successful_action を rotate に更新する。
        return cand, True

    # 仕様根拠: DOC-SPC-024 では回転失敗時に位置・向き維持が必須。
    # 失敗時に元オブジェクトを返すことで、呼び出し側の誤更新を防止する。
    return piece, False


def move(board, piece, dx, dy, action: str):
    # 仕様根拠: 移動も回転と同様に「成立時のみ状態更新」を徹底し、
    # 不成立時は現在ピースを保持することで一貫した状態遷移にする。
    cand = replace(
        piece,
        origin_x=piece.origin_x + dx,
        origin_y=piece.origin_y + dy,
        # 自動落下はプレイヤー操作ではないため、T-Spin用の最終成立操作を上書きしない。
        last_successful_action=piece.last_successful_action if action == "fall" else action,
    )

    if is_valid_position(board, cand):
        # last_successful_action は T-Spin 判定・入力優先順検証で利用するため、
        # 成立した操作だけを明示的に記録する。
        return cand, True

    # 不成立時に元状態を返すことで wall kick 非採用仕様を保ち、
    # 呼び出し側が追加補正を行わない限り位置は変化しない。
    return piece, False
