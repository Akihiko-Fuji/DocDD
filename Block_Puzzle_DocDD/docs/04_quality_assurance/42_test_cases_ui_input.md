# UI・入力試験項目 / Test Cases: UI and Input

- 文書ID: DOC-QA-042
- 最終更新日: 2026-03-23
- 関連文書:
  - `40_test_strategy.md`
  - `21_ui_screen_spec.md`
  - `22_input_operation_spec.md`
  - `32_state_machine_design.md`

## 1. 目的
画面遷移、入力受付範囲、Game Boy 由来入力の PC 写像、START 優先ルールを検証する。

## 2. カバレッジ方針
- タイトルからゲームオーバーまでの主要画面を対象にする
- UI 表示と入力仕様の整合を確認する
- 非採用入力や予約入力の無害性も確認する

| TC-ID | 観点 | 前提条件 | 入力 / 操作 | 実施手順 | 期待状態遷移 | pass 条件 | 関連 FR / NFR / EXT / Design |
|---|---|---|---|---|---|---|---|
| TC-UI-001 | タイトルから開始設定へ遷移 | タイトル画面表示中 | START | 1. タイトル画面を表示する 2. START を 1 回入力する 3. 表示画面を確認する | `ST-TITLE -> ST-SETUP-A` | A-TYPE 開始設定画面へ遷移し、プレイ盤面はまだ開始されない | FR-001, FR-301, FR-405 / NFR-003 / DOC-SPC-021, DOC-SPC-022 / DOC-DSN-032, DOC-DSN-034 |
| TC-UI-002 | 開始レベル変更 | A-TYPE 開始設定画面表示中 | Left / Right | 1. 開始設定画面を開く 2. Left / Right でレベル値を変更する 3. 範囲を確認する | `ST-SETUP-A` 維持 | 0～9 の範囲で開始レベルが変更でき、範囲外へは出ない | FR-002, FR-302 / NFR-003 / DOC-SPC-021, DOC-SPC-022 / DOC-DSN-032, DOC-DSN-034 |
| TC-UI-003 | プレイ画面に NEXT / SCORE / LINES / LEVEL 表示 | ゲーム開始直後 | なし（表示確認） | 1. A-TYPE を開始する 2. プレイ画面を表示する 3. 必須表示を確認する | `ST-SETUP-A -> ST-PLAY` | 盤面、NEXT、SCORE、LINES、LEVEL が揃い、Hold 枠が表示されない | FR-003, FR-106, FR-303 / NFR-105 / DOC-SPC-020, DOC-SPC-021 / DOC-DSN-034 |
| TC-UI-004 | START で一時停止 | プレイ中、落下可能状態 | START | 1. プレイを開始する 2. 任意のタイミングで START を押す 3. PAUSE 表示と進行停止を確認する | `ST-PLAY -> ST-PAUSE` | PAUSE 表示へ遷移し、自動落下とピース操作が停止する | FR-401, FR-402, FR-405 / NFR-003 / DOC-SPC-021, DOC-SPC-022, DOC-SPC-025 / DOC-DSN-032, DOC-DSN-034 |
| TC-UI-005 | 一時停止から再開 | 一時停止中 | START | 1. 一時停止状態に入る 2. START を押す 3. 停止前状態に戻ることを確認する | `ST-PAUSE -> ST-PLAY` | 同一セッションを引き継いでプレイへ復帰する | FR-403, FR-405 / NFR-003, NFR-105 / DOC-SPC-021, DOC-SPC-022, DOC-SPC-025 / DOC-DSN-032, DOC-DSN-034 |
| TC-UI-006 | SELECT 相当入力が進行へ影響しない | プレイ中 | SELECT | 1. プレイ中に SELECT を押す 2. 盤面、状態、スコア変化を確認する | `ST-PLAY` 維持 | 盤面・状態・得点に影響を与えない | FR-109 / NFR-002, NFR-003 / DOC-SPC-022 / DOC-DSN-034 |
| TC-UI-007 | Hard drop 用入力が存在しない | タイトル、設定、プレイの各状態 | 想定キー割当一覧の確認およびプレイ入力 | 1. 入力一覧を表示する 2. プレイ中に専用落下キーを探索する 3. 即時最下段落下が起きないことを確認する | 各状態維持 | Hard drop 専用入力が定義されず、1 操作で最下段まで即時落下しない | FR-212 / NFR-206 / DOC-SPC-020, DOC-SPC-022 / DOC-DSN-034 |
| TC-UI-008 | ゲームオーバーから再試行 | ゲームオーバー画面表示中 | START または A | 1. ゲームオーバーにする 2. START または A を押す 3. 画面遷移を確認する | `ST-GAMEOVER -> ST-SETUP-A` | 開始設定へ戻り、新規セッション開始準備状態になる | FR-006, FR-305, FR-405 / NFR-105 / DOC-SPC-021, DOC-SPC-025 / DOC-DSN-032, DOC-DSN-034 |

## 3. 受入観点
- 画面遷移と入力受付範囲が一致していること
- PC 表示キーと論理入力名の対応が曖昧でないこと
