from falling_block_puzzle.game_session import SessionService
from falling_block_puzzle.models import GameSession, PieceState


def _new_session_with_piece(kind: str = "T") -> tuple[SessionService, GameSession]:
    svc = SessionService(seed=0)
    s = GameSession(start_level=0, level=0)
    s.current = PieceState(kind=kind, origin_x=4, origin_y=10, rotation=0)
    s.next_kind = "I"
    return svc, s


def _fill_tspin_corners(board, origin_x: int, origin_y: int, count: int) -> None:
    corners = [(origin_x - 1, origin_y - 1), (origin_x + 1, origin_y - 1), (origin_x + 1, origin_y + 1), (origin_x - 1, origin_y + 1)]
    for x, y in corners[:count]:
        board[y][x] = 1


def test_tspin_zero_line_scored_and_flagged():
    svc, s = _new_session_with_piece("T")
    _fill_tspin_corners(s.board, s.current.origin_x, s.current.origin_y, 3)
    s.current.last_successful_action = "rotate"

    svc.lock_piece(s)

    assert s.lines == 0
    assert s.score == 100
    assert s.tspin_flash == 30


def test_tspin_one_line_scored_and_cleared():
    svc, s = _new_session_with_piece("T")
    line_y = 16
    s.board[line_y] = [1] * 10
    s.board[line_y][s.current.origin_x] = 0

    s.current.origin_y = line_y
    _fill_tspin_corners(s.board, s.current.origin_x, s.current.origin_y, 3)
    s.current.last_successful_action = "rotate"
    svc.lock_piece(s)

    assert s.lines == 1
    assert s.score == 800
    assert s.tspin_flash == 30


def test_t_piece_with_two_corners_is_not_tspin():
    svc, s = _new_session_with_piece("T")
    _fill_tspin_corners(s.board, s.current.origin_x, s.current.origin_y, 2)
    s.current.last_successful_action = "rotate"

    svc.lock_piece(s)

    assert s.lines == 0
    assert s.score == 0
    assert s.tspin_flash == 0


def test_non_t_piece_is_not_tspin_even_after_rotate():
    svc, s = _new_session_with_piece("L")
    _fill_tspin_corners(s.board, s.current.origin_x, s.current.origin_y, 4)
    s.current.last_successful_action = "rotate"

    svc.lock_piece(s)

    assert s.lines == 0
    assert s.score == 0
    assert s.tspin_flash == 0


def test_t_piece_last_action_must_be_rotate():
    svc, s = _new_session_with_piece("T")
    _fill_tspin_corners(s.board, s.current.origin_x, s.current.origin_y, 4)
    s.current.last_successful_action = "soft_drop"

    svc.lock_piece(s)

    assert s.lines == 0
    assert s.score == 0
    assert s.tspin_flash == 0
