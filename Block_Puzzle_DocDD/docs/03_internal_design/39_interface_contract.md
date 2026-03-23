# インターフェース契約 / Interface Contract

- 文書ID: DOC-DSN-039
- 最終更新日: 2026-03-24
- 目的: モジュール間で受け渡す主要インターフェースの引数型、戻り値、前提条件、事後条件を一覧化し、`34_module_design.md` の責務説明と `33_data_model.md` の型設計を橋渡しする
- 関連文書:
  - `docs/03_internal_design/30_architecture_design.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/03_internal_design/36_input_timing_design.md`
  - `docs/03_internal_design/37_error_handling_policy.md`

## 1. 本書の位置付け

- `30_architecture_design.md`: 層と依存方向の正本
- `34_module_design.md`: モジュール責務と公開契約の説明
- 本書: 主要 API の**データ契約**を一覧で確認するための正本

本書は実装言語の構文ではなく、DocDD 上の内部契約一覧として読む。ここで用いる `function_name(arg) -> ResultType` 形式は**契約記法**であり、特定言語の実装例を推奨するものではない。Python / C# / Java / C++ / Rust / Kotlin では、それぞれの命名規約・型宣言・戻り値表現へ読み替えてよい。



### 1.1 契約記法の読み替え規則
- シグネチャ欄は**疑似コード記法**であり、実装言語の予約語・文法とは切り離して読む。
- `snake_case` の識別子は文書内での参照名であり、実装時は `camelCase` や `PascalCase` へ変換してよい。
- `InputSnapshot`, `TransitionResult` などの型名は、class / struct / record / enum / interface など各言語の適切なデータ表現へ写像してよい。
- `->` は「戻り値契約を持つ」を意味し、単一戻り値、結果オブジェクト、`Result<T>`、out 引数、DTO など具体表現は実装言語側で選定してよい。
- 前提条件・事後条件が本書の正本であり、メソッド分割数や継承・所有モデルは各実装言語で最適化してよい。

## 2. 主要インターフェース一覧

| 契約ID | 呼出元 -> 呼出先 | シグネチャ | 主目的 |
|---|---|---|---|
| IF-001 | input source -> input_mapper | `map_physical_input(raw_input, frame, source) -> InputSnapshot` | 生入力を正規化する |
| IF-002 | replay adapter -> input_mapper | `map_replay_frame(replay_frame, frame) -> InputSnapshot` | replay を通常入力へ合流させる |
| IF-003 | state_controller caller -> state_controller | `dispatch(session, input_snapshot) -> TransitionResult` | 状態依存入力と遷移を判定する |
| IF-004 | state_controller -> active_piece_service | `apply_player_actions(board, current_piece, input_snapshot) -> ActivePieceResult` | プレイヤー操作を現在ピースへ適用する |
| IF-005 | gameplay flow -> lock_resolver | `resolve_lock(session) -> LockResolution` | 固定・消去・後処理起点を生成する |
| IF-006 | lock flow -> tspin_detector | `evaluate_tspin(board, piece_state, last_success_action, cleared_lines) -> TSpinResult` | T-Spin 判定を返す |
| IF-007 | lock flow -> scoring_service | `apply_score(score_state, cleared_lines, tspin_result, soft_drop_distance) -> ScoreState` | 得点状態を更新する |
| IF-008 | scoring flow -> level_progression_service | `update_level(score_state, start_level) -> ScoreState` | レベル更新を適用する |
| IF-009 | application -> renderer | `build_view_model(session, ui_message, next_visibility) -> ScreenViewModel` | 描画用 view model を生成する |
| IF-010 | boot flow -> config loader | `load_config(path) -> ConfigLoadResult` | Config を読込・正規化する |

## 3. 契約詳細

### 3.1 IF-001 `map_physical_input`
- 引数:
  - `raw_input`: キーボードまたはゲームパッドの生入力
  - `frame`: 0 起算フレーム番号
  - `source`: `keyboard` または `gamepad`
- 戻り値:
  - `InputSnapshot`
- 前提条件:
  - `frame` は当該 tick の `GameSession.frame` と一致可能であること
- 事後条件:
  - `pressed_buttons` は論理入力集合へ正規化されていること
  - 未知物理入力は論理入力へ昇格させないこと

### 3.2 IF-002 `map_replay_frame`
- 引数:
  - `replay_frame`: `ReplayFrame`
  - `frame`: 再生中の現在フレーム
- 戻り値:
  - `InputSnapshot`
- 前提条件:
  - replay 全体検証が事前に成功していること
- 事後条件:
  - 通常入力系と同じ `InputSnapshot` 形式へ変換されること
  - replay 専用の分岐を下流へ増やさないこと

### 3.3 IF-003 `dispatch`
- 引数:
  - `session`: `GameSession`
  - `input_snapshot`: `InputSnapshot`
- 戻り値:
  - `TransitionResult`（次状態、必要な gameplay 呼出の有無、UI イベントを含む）
- 前提条件:
  - `input_snapshot.frame == session.frame`
- 事後条件:
  - 無効状態でのプレイ入力は下流へ渡されないこと
  - `START` 優先規則が適用されること

### 3.4 IF-004 `apply_player_actions`
- 引数:
  - `board`: `Board`
  - `current_piece`: `CurrentPiece`
  - `input_snapshot`: `InputSnapshot`
- 戻り値:
  - `ActivePieceResult`（更新後 `CurrentPiece`、soft drop 距離、最終成立操作を含む）
- 前提条件:
  - `session.state == ST-PLAY` 相当の文脈で呼ばれること
- 事後条件:
  - 回転失敗時に `current_piece` を部分更新しないこと
  - 同時入力規則が `36_input_timing_design.md` と一致すること

### 3.5 IF-005 `resolve_lock`
- 引数:
  - `session`: `GameSession`
- 戻り値:
  - `LockResolution`（固定後 board、cleared lines、soft drop 距離などを含む）
- 前提条件:
  - 下移動不能がすでに観測されていること
- 事後条件:
  - board 更新、completed lines 抽出、後続評価用データが揃っていること

### 3.6 IF-006 `evaluate_tspin`
- 前提条件:
  - `piece_state` は固定直後の最終位置を表すこと
  - `cleared_lines` は同一固定イベントの結果であること
- 事後条件:
  - 得点値を返さず、判定結果のみ返すこと
  - T-Spin 不成立も正常な戻り値で表現すること

### 3.7 IF-007 `apply_score`
- 前提条件:
  - `tspin_result` は同一 lock イベントから導かれていること
- 事後条件:
  - `ScoreState.score`, `lines`, `level` のうち score/lines を整合的に更新した結果を返すこと
  - 副作用で board を変更しないこと

### 3.8 IF-008 `update_level`
- 前提条件:
  - `score_state.lines` が最新化済みであること
- 事後条件:
  - `23_scoring_level_spec.md` に従ったレベル更新結果を返すこと

### 3.9 IF-009 `build_view_model`
- 引数:
  - `session`: `GameSession`
  - `ui_message`: 任意短文
  - `next_visibility`: 真偽値（bool / boolean / Boolean 相当）
- 事後条件:
  - 640×576 基準座標の `ScreenViewModel` を返すこと
  - ルール計算を新規実行しないこと

### 3.10 IF-010 `load_config`
- 戻り値:
  - `ConfigLoadResult`（`Config`、診断情報、フォールバック有無を含む）
- 事後条件:
  - 不正 Config の部分適用を行わないこと
  - 継続可能なら正規化済み `Config` を返すこと

## 4. 受入観点

- `33_data_model.md` の主要型と `34_module_design.md` の主要公開契約が 1 対 1 に追跡できること
- 前提条件と事後条件がレビュー時のチェックリストとして使えること
- replay / config / renderer を含む横断契約が本文だけで確認できること
