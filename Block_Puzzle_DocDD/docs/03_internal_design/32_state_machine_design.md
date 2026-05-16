# ランタイム状態遷移設計 / State Machine Design

- 文書ID: DOC-DSN-032
- 文書名: ランタイム状態遷移設計 / State Machine Design
- 最終更新日: 2026-03-24
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: ランタイム状態、状態遷移条件、各状態で有効な入力および主要処理の責務境界を設計として定義する
- 関連文書:
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/27_runtime_flowchart_mermaid.md`
  - `docs/03_internal_design/38_runtime_state_transition_mermaid.md`
  - `docs/04_quality_assurance/40_test_strategy.md`
  - `adr/ADR-0001-game-loop-model.md`
  - `adr/ADR-0003-input-buffer-policy.md`

---

## 1. 本書の目的

本書は、ゲーム全体がどのような状態を持ち、どの条件で遷移し、各状態で何を受け付けるかを内部設計として定義する。画面状態とゲーム進行状態を接続し、図・本文・テストの基点とする。

---

## 2. 設計方針

1. 画面状態とゲーム進行状態を可能な限り一致させる
2. プレイ中のみ内部サブ状態を持つ
3. 一時停止・ゲームオーバー時に通常プレイ入力を流入させない
4. T-Spin 判定を固定後処理の一部として明示する
5. SELECT による NEXT 表示切替をゲーム進行と分離した UI 状態更新として扱う
6. B-TYPE は予約状態に留める
7. entry / exit の副作用を明文化する
8. 入力優先順は `START -> SELECT -> 回転 -> 左右 -> Down -> 自動落下` とする

---

## 3. 上位状態

| 状態ID | 状態名 | entry の主処理 | exit の主処理 |
|---|---|---|---|
| ST-BOOT | 起動準備 | 既定設定読込、初期化 | タイトル遷移準備 |
| ST-TITLE | タイトル | タイトル表示、開始導線表示 | 入力バッファ初期化 |
| ST-SETUP-A | A-TYPE 開始設定 | 開始レベル表示 | 開始値をセッションへ反映 |
| ST-PLAY | プレイ中 | プレイサブ状態開始、NEXT 表示フラグ既定化 | 停止理由または終了理由を確定 |
| ST-PAUSE | 一時停止 | プレイ進行停止、停止時画面固定 | 再開準備またはセッション破棄 |
| ST-GAMEOVER | ゲームオーバー / リザルト | 最終結果固定、導線表示 | 再試行またはタイトル遷移 |
| ST-MODE-SELECT | モード選択（予約） | 将来拡張。現行 build では遷移しない | - |
| ST-SETUP-B | B-TYPE 設定（予約） | 将来拡張。現行 build では遷移しない | - |

---

## 4. 上位遷移概要

```text
ST-BOOT -> ST-TITLE -> ST-SETUP-A -> ST-PLAY
ST-PLAY --START--> ST-PAUSE
ST-PAUSE --START--> ST-PLAY
ST-PAUSE --B/ESC--> ST-TITLE
ST-PLAY --game over--> ST-GAMEOVER
ST-GAMEOVER --retry--> ST-SETUP-A
ST-GAMEOVER --title--> ST-TITLE
```

状態遷移図は `38_runtime_state_transition_mermaid.md` を参照すること。

---

## 5. 各上位状態の責務

### 5.1 ST-TITLE

- タイトル表示
- START 相当入力受付
- 参照仕様表示の最小案内
- プレイ入力無効化

### 5.2 ST-SETUP-A

- 開始レベル変更（Left / Right）
- 開始確定
- タイトル復帰

### 5.3 ST-PLAY

- プレイ中サブ状態実行
- プレイ入力受付
- NEXT 表示フラグ更新
- 描画対象更新

### 5.4 ST-PAUSE

- プレイ進行停止
- 再開またはタイトル復帰入力受付
- 停止前状態保持

### 5.5 ST-GAMEOVER

- 終了結果表示
- 再試行またはタイトル復帰受付

---

## 6. ST-PLAY のサブ状態

| サブ状態ID | 名称 | 主責務 | 完了条件 |
|---|---|---|---|
| PL-SPAWN | 出現 | 現在ピース配置、出現不能判定 | 出現成功またはゲームオーバー確定 |
| PL-ACTIVE | 操作 / 落下 | 入力解釈、自動落下、移動・回転評価、NEXT 表示切替 | 下移動不能が観測される |
| PL-LOCK-CHECK | 接地 / 固定判定 | 下方向移動不能判定、固定決定 | 固定確定 |
| PL-CLEAR | ライン消去 | 完成ライン判定と消去 | 消去対象確定 |
| PL-SCORE | 得点処理 | T-Spin 判定、得点、ライン、レベル更新 | 数値更新完了 |
| PL-NEXT | 次ピース準備 | NEXT 繰上げ、新 NEXT 補充 | 次出現準備完了 |
| PL-END-CHECK | 終了判定 | 次出現可否、ゲームオーバー評価 | 継続 / 終了のどちらか確定 |

---

## 7. プレイ中サブ状態遷移

```text
PL-SPAWN
  -> PL-ACTIVE
PL-ACTIVE
  -> 下移動不能時 PL-LOCK-CHECK
PL-LOCK-CHECK
  -> 固定成立時 PL-CLEAR
PL-CLEAR
  -> PL-SCORE
PL-SCORE
  -> PL-NEXT
PL-NEXT
  -> PL-END-CHECK
PL-END-CHECK
  -> 継続可能なら PL-SPAWN
  -> 出現不能なら ST-GAMEOVER
```

---

## 8. プレイフレーム内の処理順

1. 入力スナップショット取得
2. 状態依存で有効入力を抽出
3. START があれば一時停止遷移を優先評価
4. SELECT があれば NEXT 表示フラグ切替を評価
5. 回転（A / B）を評価
6. 左右移動（Left / Right）を評価
7. Down を評価
8. 自動落下を評価
9. 下移動不能なら固定処理系列へ進む

補足:
- SELECT は UI 状態のみを更新し、現在ピース座標や進行順へ影響させない
- START と同時に押された他入力は反映しない

---

## 9. 入力有効範囲

| 入力 | TITLE | SETUP-A | PLAY | PAUSE | GAMEOVER |
|---|---|---|---|---|---|
| 左右 | 無効 | 値変更可 | 有効 | 無効 | 無効 |
| Down | 無効 | 無効 | 有効 | 無効 | 無効 |
| A/B | 無効 | A は確定補助、B は戻る | 有効 | B はタイトル復帰 | A は再試行補助、B はタイトル復帰 |
| START | 開始 | 開始確定 | 一時停止 | 再開 | 再試行 |
| SELECT | 無効 | 無効 | NEXT 切替 | 無効 | 無効 |

---

## 10. T-Spin の責務配置

T-Spin 判定は `PL-SCORE` サブ状態で行う。理由は以下の通り。

1. 固定完了後でないと最終位置が確定しない
2. ライン消去数と組み合わせて得点表を選ぶ必要がある
3. 回転可否そのものは `PL-ACTIVE` と `24_piece_rotation_collision_spec.md` の責務である

---

## 11. 一時停止設計

### 11.1 進入条件

ST-PLAY 中に START 相当入力を受けたとき、ST-PAUSE へ遷移する。

### 11.2 停止対象

- 自動落下タイマ
- 入力によるピース操作反映
- 固定、消去、得点、レベル更新
- NEXT 表示切替を含むプレイ中 UI 更新

### 11.3 維持対象

- 盤面表示
- SCORE / LINES / LEVEL 表示値
- 現在ピース位置
- NEXT 表示状態

### 11.4 再開時の注意

再開直後の同一押下で再度 ST-PAUSE に戻らないよう、入力バッファを整える設計を必須とする。

---

## 12. ゲームオーバー設計

新規現在ピースを規定位置に置けない場合、ST-GAMEOVER へ遷移する。

entry では以下を行う。

- 最終 SCORE / LINES / LEVEL を固定する
- 通常プレイ入力と SELECT を遮断する
- 再試行とタイトル復帰の導線を有効化する

---

## 13. 予約状態

### 13.1 ST-MODE-SELECT

A-TYPE / B-TYPE 選択を将来導入する場合の予約状態。現行 build では遷移不可。

### 13.2 ST-SETUP-B

B-TYPE の開始レベル / HIGH 設定を将来導入する場合の予約状態。現行 build では遷移不可。

---

## 14. Diagram-Driven / Acceptance-Driven 観点

1. タイトル、設定、プレイ、一時停止、ゲームオーバーの遷移が一貫していること
2. SELECT による NEXT 表示切替の責務位置が明確であること
3. T-Spin 判定の責務位置が明確であること
4. B-TYPE が予約状態として整理され、現行 build では遷移しないことが読めること
5. entry / exit の主要責務が読み取れること
6. プレイフレーム順が `22_input_operation_spec.md`、`27_runtime_flowchart_mermaid.md` および図文書と一致していること

---

## 15. 変更履歴

- 2026-03-23: SELECT/NEXT 切替の責務を ST-PLAY / PL-ACTIVE へ追加し、入力優先順を更新
- 2026-03-23: pause 中の維持対象とゲームオーバー時の遮断入力を補強

- 2026-03-24: `27_runtime_flowchart_mermaid.md` を内部設計補助図として参照追加し、図整合の参照先を更新
