"""Models.

Based on:
- DOC-DSN-031 Domain Model
- DOC-DSN-033 Data Model
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GameState(str, Enum):
    BOOT = "BOOT"
    TITLE = "TITLE"
    SETUP_A = "SETUP_A"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    GAMEOVER = "GAMEOVER"
    SETUP_B = "SETUP_B"


@dataclass
class PieceState:
    kind: str
    origin_x: int
    origin_y: int
    rotation: int = 0
    last_successful_action: str = "none"


@dataclass
class GameSession:
    state: GameState = GameState.TITLE
    start_level: int = 0
    level: int = 0
    lines: int = 0
    score: int = 0
    board: list[list[int]] = field(default_factory=lambda: [[0] * 10 for _ in range(18)])
    current: Optional[PieceState] = None
    next_kind: str = "I"
    next_visible: bool = True
    over_reason: str = ""
    soft_drop_cells: int = 0
    fall_counter: int = 0
    tspin_flash: int = 0
    line_clear_rows: list[int] = field(default_factory=list)
    line_clear_timer: int = 0
