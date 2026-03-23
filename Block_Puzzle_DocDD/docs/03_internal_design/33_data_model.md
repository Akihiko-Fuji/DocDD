# データモデル / Data Model

- 文書ID: DOC-DSN-033
- 最終更新日: 2026-03-23
- 関連文書:
  - `31_domain_model.md`
  - `34_module_design.md`
  - `26_save_replay_config_spec.md`

## 1. 目的
モジュール間で受け渡す主要データ構造、主要属性、不変条件を定義し、実装判断のブレを防ぐ。

## 2. 主データ一覧
| データ | 主用途 | 主属性例 | 不変条件 |
|---|---|---|---|
| BoardCell | 盤面 1 マス | `x`, `y`, `occupied`, `color_id` | 可視盤面は 10×18 内に存在する |
| PieceState | 落下中または評価対象ピース | `piece_type`, `rotation`, `origin_x`, `origin_y`, `occupied_offsets` | `piece_type` は 7 種のみ |
| ScoreState | 得点・進行状態 | `score`, `lines`, `level`, `start_level` | `start_level` は 0～9、`level` は 0～20 |
| SessionState / GameSession | 1 セッションの集約 | `board`, `current_piece`, `next_piece`, `score_state`, `top_state`, `play_substate` | 表示値は内部正本と矛盾しない |
| InputSnapshot | 1 frame の入力状態 | `pressed_buttons`, `held_buttons`, `frame_index` | ボタン名は論理入力集合に一致する |
| TSpinResult | T-Spin 判定結果 | `is_tspin`, `cleared_lines`, `reason` | T 以外で `is_tspin=true` にならない |
| Config | 設定読込結果 | `start_level`, `keymap`, `randomizer_seed` | 未設定時は既定値へ正規化される |
| ReplayFrame | replay 入力 1 件 | `frame`, `buttons` | `frame` は 0 以上の整数 |

## 3. Game Boy 基準で固定する事項
- 盤面可視領域は 10×18
- NEXT は 1 個のみ
- 出現姿勢はピース種ごとに固定
- レベル進行と落下速度は `20_game_rules_spec.md` を正本とする

## 4. 更新責務
- `InputSnapshot`: `input_mapper`
- `PieceState`: `spawn_service`, `active_piece_service`
- `ScoreState`: `scoring_service`, `level_progression_service`
- `TSpinResult`: `tspin_detector`
- `SessionState / GameSession`: `game_session`
- `Config`: config loader または既定値初期化処理

## 5. Diagram-Driven 観点
状態遷移図や責務図で登場するデータ名は本書の表記を正本とする。`32_state_machine_design.md`、`34_module_design.md`、テスト文書で別名を導入してはならない。
