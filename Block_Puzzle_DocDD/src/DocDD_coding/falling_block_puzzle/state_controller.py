"""State control based on DOC-DSN-032."""
from .models import GameState, GameSession


class StateController:
    def transition(self, s: GameSession, event: str) -> None:
        # TITLE で START を受けると、A-TYPE 初期設定画面へ進む。
        if s.state == GameState.TITLE and event == "start":
            s.state = GameState.SETUP_A

        # SETUP_A で START: 設定値を確定して PLAY へ。
        elif s.state == GameState.SETUP_A and event == "start":
            s.state = GameState.PLAY

        # SETUP_A で戻る: 設定を破棄して TITLE へ。
        elif s.state == GameState.SETUP_A and event in {"back", "b"}:
            s.state = GameState.TITLE

        # PLAY で START: 進行を止めて PAUSE へ。
        elif s.state == GameState.PLAY and event == "start":
            s.state = GameState.PAUSE

        # PAUSE で START: 直前プレイ状態を再開。
        elif s.state == GameState.PAUSE and event == "start":
            s.state = GameState.PLAY

        # PAUSE で戻る: セッションを終えて TITLE へ。
        elif s.state == GameState.PAUSE and event in {"back", "b"}:
            s.state = GameState.TITLE

        # PLAY 中に出現不能が発生したら GAMEOVER。
        elif s.state == GameState.PLAY and event == "gameover":
            s.state = GameState.GAMEOVER

        # GAMEOVER で retry/start: 同モードを再設定して再挑戦。
        elif s.state == GameState.GAMEOVER and event in {"start", "retry"}:
            s.state = GameState.SETUP_A

        # GAMEOVER で戻る: TITLE へ戻る。
        elif s.state == GameState.GAMEOVER and event in {"back", "b"}:
            s.state = GameState.TITLE
