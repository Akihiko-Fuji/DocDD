# ゲームルール試験項目 / Test Cases: Game Rules

- 文書ID: DOC-QA-041
- 最終更新日: 2026-03-23
- 関連文書:
  - `40_test_strategy.md`
  - `20_game_rules_spec.md`
  - `23_scoring_level_spec.md`
  - `23a_timing_constants_spec.md`
  - `23b_display_limits_spec.md`
  - `24_piece_rotation_collision_spec.md`
  - `24a_piece_shape_spawn_spec.md`
  - `32_state_machine_design.md`
  - `46_test_fixtures_catalog.md`

## 1. 目的
A-TYPE 主軸のゲーム進行、得点、レベル進行、T-Spin を代表ケースで検証する。

## 2. テスト運用ルール
- 本書は**試験仕様書**として扱い、実施結果は列または別記録へ残す
- 具体盤面は `46_test_fixtures_catalog.md` の Fixture ID を参照する
- 各ケースには `manual / automated`、`smoke / regression`、優先度を付与する
- 実施結果欄が未記入の場合、そのケースは「設計済み・未実施」と解釈する

## 3. カバレッジ方針
- 正常系の主要フローを優先する
- 得点とレベル進行は Game Boy 基準の速度表と整合することを確認する
- T-Spin は成立 / 不成立 / 0 line を分離する
- 盤面フィクスチャを再利用し、複数ケースで同一前提を再現可能にする

| TC-ID | 観点 | Fixture ID | 実行方式 | 区分 | 優先度 | 前提条件 | 入力 / 操作 | 実施手順 | 期待状態遷移 | pass 条件 | 実施結果欄 | 関連 FR / NFR / EXT / Design |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-GR-001 | 新規開始直後の初期値 | FX-GR-001 | manual/automated | smoke | high | タイトルから開始可能 | START -> A-TYPE 開始 | 1. タイトルから開始設定へ進む 2. 開始確定する 3. 初期値を確認する | `ST-TITLE -> ST-SETUP-A -> ST-PLAY` | SCORE=0, LINES=0, LEVEL=開始レベル, NEXT 1 個が成立する | 未実施/Pass/Fail を記録 | FR-001, FR-002, FR-003 / NFR-105 / DOC-SPC-020, DOC-SPC-021 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-002 | 1 ライン消去 | FX-BRD-101 | automated | regression | high | 完成目前の 1 行を持つ盤面 | 1 行消去を発生させる | 1. `FX-BRD-101` をロードする 2. 現在ピースを固定する 3. SCORE/LINES を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-CLEAR -> PL-SCORE` | 1 行消去得点が適用され、LINES が 1 増える | 未実施/Pass/Fail を記録 | FR-203, FR-204, FR-206, FR-207 / NFR-101 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-003 | 4 ライン同時消去 | FX-BRD-104 | automated | smoke/regression | critical | 4 行同時消去直前盤面 | 4 行消去を発生させる | 1. `FX-BRD-104` をロードする 2. 現在ピースを固定する 3. SCORE/LINES を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-CLEAR -> PL-SCORE` | 基本点 1200 × (level+1) が適用され、LINES が 4 増える | 未実施/Pass/Fail を記録 | FR-204, FR-206, FR-207 / NFR-101 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-004 | レベル上昇 | FX-GR-009 | automated | regression | high | 開始レベル 0、LINES=9 のプレイ状態 | 1 ライン消去を発生させる | 1. `FX-GR-009` をロードする 2. 1 ライン消去する 3. LEVEL と落下速度指標を確認する | `PL-CLEAR -> PL-SCORE -> PL-NEXT` | LEVEL が 1 に上昇し、以後の重力設定がレベル 1 扱いになる | 未実施/Pass/Fail を記録 | FR-207, FR-208, FR-209 / NFR-101, NFR-105 / DOC-SPC-020, DOC-SPC-023 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-005 | T-Spin 0 line | FX-TSP-201 | automated | regression | high | T ピース、最終成立操作が回転、対角 3 箇所以上占有、消去行なし | A または B で回転して固定 | 1. `FX-TSP-201` をロードする 2. 回転成功後に固定する 3. 得点表示を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-SCORE` | T-Spin 0 line の専用得点が適用され、通常得点表が使われない | 未実施/Pass/Fail を記録 | FR-210, FR-211 / NFR-101, NFR-203 / DOC-SPC-020, DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-006 | T-Spin 1 line | FX-TSP-202 | automated | regression | high | T ピース、最終成立操作が回転、T-Spin 成立かつ 1 行消去 | A または B で回転して固定 | 1. `FX-TSP-202` をロードする 2. 回転成功後に固定する 3. SCORE と LINES を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-CLEAR -> PL-SCORE` | T-Spin 1 line 得点が適用され、LINES が 1 増える | 未実施/Pass/Fail を記録 | FR-204, FR-206, FR-210, FR-211 / NFR-101, NFR-203 / DOC-SPC-020, DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-007 | T-Spin 不成立 | FX-TSP-203 | automated | regression | medium | T ピース固定盤面、対角占有 2 箇所以下または最終操作が回転でない | 左右移動またはソフトドロップ後に固定 | 1. `FX-TSP-203` をロードする 2. 回転以外を最終成立操作にする 3. 固定して得点を確認する | `PL-ACTIVE -> PL-LOCK-CHECK -> PL-SCORE` | T-Spin と判定されず、通常得点または加点なしとなる | 未実施/Pass/Fail を記録 | FR-206, FR-210 / NFR-101 / DOC-SPC-023, DOC-SPC-024 / DOC-DSN-032, DOC-DSN-034 |
| TC-GR-008 | 出現不能ゲームオーバー | FX-BRD-301 | automated | smoke/regression | critical | 出現位置が固定済みブロックで塞がれている | 次ピース出現を発生させる | 1. `FX-BRD-301` をロードする 2. 現在ピースを固定して次出現へ進める 3. 状態を確認する | `PL-NEXT -> PL-END-CHECK -> ST-GAMEOVER` | 新規出現失敗によりゲームオーバーへ遷移し、最終値が固定表示される | 未実施/Pass/Fail を記録 | FR-005, FR-405 / NFR-105 / DOC-SPC-020, DOC-SPC-025 / DOC-DSN-032, DOC-DSN-034 |

## 4. フィクスチャ運用補足
- `FX-BRD-*` は一般盤面、`FX-TSP-*` は T-Spin 専用、`FX-GR-*` は数値進行や初期状態向けとする
- 同一 Fixture を複数 TC で使う場合、差分手順を手順欄に明示する
- フィクスチャ更新時は本書と `46_test_fixtures_catalog.md` を同時更新する

## 5. 受入観点
- Game Boy 基準の基本ルールが正常系ケースで辿れること
- T-Spin 独自拡張が通常ルールと混ざらずに検証できること
- 実施結果欄、Fixture ID、実行方式、優先度により試験仕様として再利用可能であること
