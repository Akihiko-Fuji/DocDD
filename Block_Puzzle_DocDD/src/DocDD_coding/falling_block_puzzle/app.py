"""Pygame app entry based on DOC-DSN-030."""
import pygame

from .models import GameState
from .renderer import Renderer
from .game_session import SessionService
from .state_controller import StateController
from .constants import FPS, SOFT_DROP_INTERVAL
from .input_mapper import map_pressed


def run():
    pygame.init()
    pygame.display.set_caption("DocDD Block Puzzle")

    try:
        clock = pygame.time.Clock()
        r = Renderer()
        ctrl = StateController()
        svc = SessionService()
        s = svc.new_play_session(0)
        s.state = GameState.TITLE
        down_hold_frames = 0
        left_hold_frames = 0
        right_hold_frames = 0

        running = True
        while running:
            edge_inputs = set()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_x:
                        edge_inputs.add("a")
                    elif e.key == pygame.K_z:
                        edge_inputs.add("b")
                    elif e.key == pygame.K_RETURN:
                        edge_inputs.add("start")
                    elif e.key == pygame.K_RSHIFT:
                        edge_inputs.add("select")
                    elif e.key == pygame.K_ESCAPE:
                        edge_inputs.add("back")

            pressed = pygame.key.get_pressed()
            down_is_held = bool(pressed[pygame.K_DOWN])
            left_is_held = bool(pressed[pygame.K_LEFT])
            right_is_held = bool(pressed[pygame.K_RIGHT])
            if down_is_held:
                down_hold_frames += 1
            else:
                down_hold_frames = 0
            if left_is_held:
                left_hold_frames += 1
            else:
                left_hold_frames = 0
            if right_is_held:
                right_hold_frames += 1
            else:
                right_hold_frames = 0

            # 左右は押下直後を必ず受理し、初回遅延後は緩めの間隔でリピートする。
            left_repeat = left_is_held and (left_hold_frames == 1 or (left_hold_frames >= 8 and left_hold_frames % 3 == 0))
            right_repeat = right_is_held and (right_hold_frames == 1 or (right_hold_frames >= 8 and right_hold_frames % 3 == 0))

            held_inputs = map_pressed(
                {
                    "left": left_repeat,
                    "right": right_repeat,
                    # step_play 側の soft_drop 処理は "down" 入力1回で1マス進めるため、
                    # 押しっぱなし時は 3 フレームごとに 1 回だけ伝える。
                    "down": down_is_held and down_hold_frames % SOFT_DROP_INTERVAL == 0,
                }
            )
            inputs = held_inputs | edge_inputs

            if s.state == GameState.TITLE and "start" in inputs:
                ctrl.transition(s, "start")
            elif s.state == GameState.SETUP_A:
                if "left" in inputs:
                    s.start_level = max(0, s.start_level - 1)
                if "right" in inputs:
                    s.start_level = min(9, s.start_level + 1)
                if "start" in inputs:
                    ns = svc.new_play_session(s.start_level)
                    ns.state = GameState.PLAY
                    s = ns
                elif "back" in inputs or "b" in inputs:
                    ctrl.transition(s, "back")
            elif s.state == GameState.PLAY:
                out = svc.step_play(s, inputs)
                if out == "pause":
                    ctrl.transition(s, "start")
                elif out == "gameover":
                    ctrl.transition(s, "gameover")
            elif s.state == GameState.PAUSE:
                if "start" in inputs:
                    ctrl.transition(s, "start")
                elif "back" in inputs or "b" in inputs:
                    ctrl.transition(s, "back")
            elif s.state == GameState.GAMEOVER:
                if "start" in inputs:
                    ctrl.transition(s, "start")
                elif "back" in inputs or "b" in inputs:
                    ctrl.transition(s, "back")

            r.draw(s)
            clock.tick(FPS)

    except pygame.error as exc:
        # 画面生成や描画の SDL 系障害はカテゴリを分けて通知する。
        print(f"[RUNTIME][PYGAME_ERROR] {exc}")
        raise
    except ValueError as exc:
        # セッション値不正などの入力・設定由来エラー。
        print(f"[RUNTIME][VALUE_ERROR] {exc}")
        raise
    except Exception as exc:
        # 想定外例外は握りつぶさず、診断可能な形で再送出する。
        print(f"[RUNTIME][UNEXPECTED] {type(exc).__name__}: {exc}")
        raise
    finally:
        pygame.quit()
