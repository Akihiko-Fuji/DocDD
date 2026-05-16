"""Randomizer based on ADR-0002 and DOC-SPC-020.
非7-bagで seed 再現可能。"""
import random
from typing import Optional
PIECES=["I","O","T","J","L","S","Z"]
class PieceRandomizer:
    # ドキュメントで厳密なGB版乱数アルゴリズムが未規定のため、
    # Game Boy版同様に「7-bagではない」性質へ準拠する実装としている。
    def __init__(self, seed: Optional[int] = None):
        self.rng=random.Random(seed)
    def next_piece(self)->str:
        return self.rng.choice(PIECES)
