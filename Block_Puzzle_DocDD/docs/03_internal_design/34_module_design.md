# モジュール設計 / Module Design

- 文書ID: DOC-DSN-034
- 文書名: モジュール設計 / Module Design
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 外部仕様を内部契約へ落とし込むために、各モジュールの責務、入出力、依存、公開契約、試験単位を定義する
- 関連文書:
  - `docs/03_internal_design/30_architecture_design.md`
  - `docs/03_internal_design/31_domain_model.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/04_quality_assurance/40_test_strategy.md`

---

## 1. 本書の目的

本書は、外部仕様で定義された振る舞いを、**実装しやすく試験しやすい内部契約**へ分解するための設計文書である。

DocDD 上では、EXT と TC の間にある「どの責務がどこへ落ちたか」を明示する役割を持つ。

---

## 2. 設計方針

1. 入力、状態遷移、ルール処理、得点、描画を分離する
2. ルール評価は可能な限り純粋関数的に扱い、ヘッドレス試験しやすくする
3. 画面状態の遷移は `state_controller` に集約する
4. GameSession はランタイム状態の単一集約点とするが、詳細ルールを抱え込みすぎない
5. T-Spin 判定や得点計算は独立サービスへ分ける

---

## 3. 責務の流れ

```text
physical input
  -> input_mapper
  -> state_controller
  -> game_session
  -> active_piece_service / board_rules / lock_resolver
  -> tspin_detector / scoring_service / level_progression_service
  -> renderer
```

補足:
- `input_mapper` は物理キーを論理入力へ変換する
- `state_controller` は現在状態に応じて有効入力のみを次段へ流す
- `game_session` は 1 プレイ単位の状態を保持する
- ルール処理群は `game_session` を読み書きするが、責務を分割して単体試験可能にする
  - 設定未指定時は既定値 0 と既定 keymap へ正規化する
- `renderer` は状態を描画表現へ写像する
- `spawn_service` は seed 指定時に再現可能な出現列を生成できる

---

## 4. モジュール一覧

| モジュール | 主責務 | 主入力 | 主出力 | 主依存 |
|---|---|---|---|---|
| input_mapper | 物理入力から論理入力への変換 | キー押下イベント / ポーリング結果 | `InputSnapshot` | なし |
| state_controller | 上位状態・サブ状態の遷移制御 | `InputSnapshot`, `GameSession`, 現在状態 | 次状態、状態遷移イベント | `game_session` |
| game_session | 盤面、スコア、現在状態の集約保持 | 初期設定、状態遷移要求、ルール処理結果 | 参照可能なセッション状態 | 各サービス |
| spawn_service | 現在ピース出現、NEXT 補充、出現不能判定 | `GameSession`, 乱数 / 出現源, `randomizer_seed` | 新 current piece, game over event | `board_rules` |
| active_piece_service | 移動・回転・ソフトドロップの適用 | `InputSnapshot`, `CurrentPiece`, `Board` | 更新後 `CurrentPiece`, 最終操作種別 | `board_rules` |
| board_rules | 盤面内判定、衝突判定、ライン完成判定 | `Board`, `CurrentPiece` | 真偽値、完成ライン一覧、更新後盤面 | なし |
| lock_resolver | 接地・固定・固定後処理の進行 | `GameSession`, `CurrentPiece`, `Board` | 固定済み盤面、消去行数、固定イベント | `board_rules` |
| tspin_detector | T-Spin 成立評価 | `CurrentPiece`, 最終操作, `Board`, 消去行数 | `TSpinResult` | `board_rules` |
| scoring_service | 得点加算、表示上限処理 | `ScoreState`, 消去行数, `TSpinResult`, ソフトドロップ距離 | 更新後 `ScoreState` | なし |
| level_progression_service | A-TYPE レベル更新、落下速度参照値計算 | `ScoreState`, 開始レベル | 更新後 `ScoreState`, 速度指標 | なし |
| renderer | セッション状態から描画データ生成 | `GameSession`, UI 状態 | 描画命令 / view model | なし |

---

## 5. 各モジュールの公開契約

### 5.1 input_mapper
- 公開契約
  - `map_physical_input(raw_input) -> InputSnapshot`
- 契約要点
  - Hard drop を表す論理入力を公開してはならない
  - SELECT は予約入力として表現できるが、進行系コマンドへ変換してはならない
- テスト観点
  - 論理入力への写像
  - 同時入力の保持
  - 非採用入力の不在

### 5.2 state_controller
- 公開契約
  - `dispatch(session, input_snapshot) -> transition_result`
- 契約要点
  - START 優先の状態遷移を実現する
  - 一時停止中 / ゲームオーバー中にプレイ入力を下流へ渡してはならない
- テスト観点
  - ST-TITLE / ST-SETUP-A / ST-PLAY / ST-PAUSE / ST-GAMEOVER の遷移
  - START 優先
  - 無効入力遮断

### 5.3 game_session
- 公開契約
  - `create_new_game(config) -> GameSession`
  - `apply_rule_result(session, rule_result) -> GameSession`
  - `snapshot(session) -> SessionView`
  - `normalize_defaults(config) -> Config`
- 契約要点
  - セッション集約として状態を保持するが、ルール計算そのものは外へ委譲する
- テスト観点
  - 初期化
  - リトライ時再初期化
  - 表示値と内部値の整合

### 5.4 active_piece_service
- 公開契約
  - `apply_player_actions(board, current_piece, input_snapshot) -> ActivePieceResult`
- 契約要点
  - 回転・左右移動・ソフトドロップの結果と「最終成立操作」を返す
- テスト観点
  - 左右移動
  - A/B 回転
  - 同時入力相殺

### 5.5 board_rules
- 公開契約
  - `is_valid_position(board, piece_state) -> bool`
  - `find_completed_lines(board) -> line_indexes`
  - `clear_lines(board, line_indexes) -> Board`
- 契約要点
  - wall kick / floor kick を含めない
  - 盤面外・衝突判定の基準を一元化する
- テスト観点
  - 壁際 / 床際 / 積み上がり近傍
  - 1〜4 ライン消去

### 5.6 lock_resolver
- 公開契約
  - `resolve_lock(session) -> LockResolution`
- 契約要点
  - 固定、ライン消去、後続サービスに必要なイベントデータを生成する
- テスト観点
  - 接地から固定への遷移
  - 固定後処理順序

### 5.7 tspin_detector
- 公開契約
  - `evaluate_tspin(board, piece_state, last_success_action, cleared_lines) -> TSpinResult`
- 契約要点
  - T ピース、最終成立操作が回転、対角 3 箇所以上占有の条件を評価する
  - Mini は区別しない
- テスト観点
  - 成立 / 不成立 / 0 line

### 5.8 scoring_service
- 公開契約
  - `apply_score(score_state, cleared_lines, tspin_result, soft_drop_distance) -> ScoreState`
- 契約要点
  - T-Spin 得点表優先
  - ソフトドロップ加点を最後に合算
  - 表示上限方針に従う
- テスト観点
  - 通常消去
  - T-Spin 1 line
  - T-Spin 0 line

### 5.9 level_progression_service
- 公開契約
  - `update_level(score_state, start_level) -> ScoreState`
  - `gravity_for_level(level) -> gravity_profile`
- 契約要点
  - A-TYPE の閾値計算を一元化する
- テスト観点
  - 初回閾値
  - 10 ライン刻み上昇
  - 上限 20

### 5.10 renderer
- 公開契約
  - `build_view_model(session) -> ScreenViewModel`
- 契約要点
  - Hold 枠や Hard drop 案内を生成してはならない
  - 必須表示要素を状態に応じて欠落させない
- テスト観点
  - プレイ画面必須表示
  - ポーズ / ゲームオーバー表示

---

## 6. 依存関係ルール

1. `renderer` はルール判定を持たない
2. `input_mapper` は状態遷移を持たない
3. `scoring_service` は盤面衝突判定を持たない
4. `tspin_detector` は得点値そのものを持たず、成立結果のみ返してよい
5. `game_session` は巨大な神クラスにしないため、判定ロジックを各サービスへ委譲する

---

## 7. 外部仕様との対応例

| 外部仕様 | 主な内部契約 |
|---|---|
| `22_input_operation_spec.md` の論理入力 | `input_mapper`, `state_controller` |
| `24_piece_rotation_collision_spec.md` の回転・衝突 | `active_piece_service`, `board_rules` |
| `23_scoring_level_spec.md` の得点・レベル | `tspin_detector`, `scoring_service`, `level_progression_service` |
| `25_pause_gameover_resume_spec.md` の状態遷移 | `state_controller`, `game_session`, `renderer` |

---

## 8. 試験しやすさの方針

- `board_rules`, `tspin_detector`, `scoring_service`, `level_progression_service` は純粋データ入出力に近づける
- `state_controller` は状態遷移表どおりの入出力契約を持たせる
- UI 試験は `renderer` の view model と統合挙動に分離する
- 非採用機能確認も `input_mapper` と `renderer` の公開契約で検証できるようにする

---

## 9. 変更履歴

- 2026-03-23: 想定モジュール列挙のみの状態から、責務・入出力・依存・公開契約・試験観点を追加
- 2026-03-23: T-Spin、得点、状態遷移、非採用機能を内部契約へ接続する責務フローを明記
