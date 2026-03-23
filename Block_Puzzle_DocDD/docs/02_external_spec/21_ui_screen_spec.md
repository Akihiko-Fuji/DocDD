# UI画面仕様 / UI Screen Specification

- 文書ID: DOC-SPC-021
- 文書名: UI画面仕様 / UI Screen Specification
- 最終更新日: 2026-03-24
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 本プロジェクトにおける画面構成、画面ごとの表示要素、入力受付、および画面遷移を外部仕様として定義する
- 関連文書:
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/27_runtime_flowchart_mermaid.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/35_rendering_design.md`

---

## 1. 本書の目的

本書は、プレイヤーから見える主要画面、表示要素、入力受付、および画面遷移を定義する。Game Boy 版の簡潔な UI を基準としつつ、PC 実装として必要なキー表記と独自拡張表示を追加する。

---

## 2. UI 基本方針

1. 盤面視認性を最優先とする
2. Game Boy 版相当の情報量を維持する
3. PC 実装としてキー表記を併記できるようにする
4. NEXT の ON/OFF 状態を誤認させない
5. T-Spin 表示は必要最小限に留める
6. 画面案内キーは `22_input_operation_spec.md` と一致させる
7. 想定描画解像度 640×576 上で、PC 利用前提の画面構成を崩さない

---

## 3. 表示前提解像度

- 想定描画解像度は 640×576 とする
- 盤面、NEXT、SCORE、LINES、LEVEL はこの解像度上で重なりなく視認できること
- PC 利用前提の固定基準解像度として、ウィンドウ初期表示やレイアウト確認の基準に用いる
- Game Boy 版由来の情報量は維持するが、整数倍拡大そのものは前提としない

## 4. 対象画面

| 画面ID | 画面名 | 位置付け |
|---|---|---|
| SCR-001 | タイトル画面 | 必須 |
| SCR-002 | A-TYPE 開始設定画面 | 必須 |
| SCR-003 | プレイ画面 | 必須 |
| SCR-004 | 一時停止画面 | 必須 |
| SCR-005 | ゲームオーバー / リザルト画面 | 必須 |
| SCR-006 | モード選択画面 | 予約 |
| SCR-007 | B-TYPE 設定画面 | 予約 |

---

## 5. 画面遷移

- SCR-001 → SCR-002: START 相当入力
- SCR-002 → SCR-003: 開始確定
- SCR-002 → SCR-001: 戻る
- SCR-003 → SCR-004: START
- SCR-003 → SCR-005: ゲームオーバー成立
- SCR-004 → SCR-003: START
- SCR-004 → SCR-001: タイトル復帰
- SCR-005 → SCR-002: 再試行
- SCR-005 → SCR-001: タイトル復帰

補助図は `docs/03_internal_design/27_runtime_flowchart_mermaid.md` を参照すること。

---

## 6. SCR-001 タイトル画面

### 6.1 表示要素

- タイトル名
- A-TYPE 開始案内
- START 相当キー案内
- 必要に応じて参照仕様としての B-TYPE / 2P の存在注記

### 6.2 入力

- START 相当: SCR-002 へ遷移
- その他プレイ入力: 無効

---

## 7. SCR-002 A-TYPE 開始設定画面

### 7.1 表示要素

- `A-TYPE`
- `LEVEL`
- 現在の開始レベル（0〜9）
- 開始確定案内
- 戻る案内

### 7.2 入力

- Left / Right: レベル変更
- A または START: 開始確定
- B: タイトルへ戻る
- SELECT: 無効

### 7.3 表示ルール

- `Up / Down` をレベル変更へ使わない
- レベル値は 0〜9 の範囲外へ出ない
- 現在値が視認可能であること

---

## 8. SCR-003 プレイ画面

### 8.1 必須表示要素

- 10×18 盤面
- 現在ピース
- 固定済みブロック
- SCORE
- LINES
- LEVEL
- NEXT 領域または NEXT 状態表示

### 8.2 NEXT 表示仕様

- NEXT 表示が ON の場合、次ピース 1 個を表示する
- NEXT 表示が OFF の場合、空欄または `NEXT OFF` 相当の識別を表示してよい
- OFF 状態でもレイアウト崩壊を起こしてはならない

### 8.3 追加表示要素

- T-Spin 成立時の `T-SPIN` または同等表示
- キーガイド簡易表示

### 8.4 非表示要素

- Hold 枠
- Hard drop 案内
- ゴーストピース
- 対戦用 UI

### 8.5 入力

- Left / Right / Down / A / B / START / SELECT
- START: SCR-004 へ遷移
- SELECT: NEXT 表示切替

---

## 9. SCR-004 一時停止画面

### 10.1 表示要素

- `PAUSE`
- 再開方法
- タイトル復帰方法
- 停止中であることが分かる静的表示
- 停止前盤面の保持表示

### 10.2 入力

- START: プレイへ戻る
- B（PC では ESC 可）: タイトルへ戻る
- Left / Right / Down / A / SELECT: 無効

---

## 10. SCR-005 ゲームオーバー / リザルト画面

### 10.1 表示要素

- `GAME OVER`
- 最終 SCORE
- 最終 LINES
- 最終 LEVEL
- 再試行案内
- タイトル復帰案内

### 10.2 入力

- START または A: 再試行
- B（PC では ESC 可）: タイトルへ戻る
- プレイ中専用入力: 無効

---

## 11. 予約画面

### 11.1 SCR-006 モード選択画面（予約）

A-TYPE / B-TYPE / 2P を将来表示するための予約画面。現行 build では遷移しない。

### 11.2 SCR-007 B-TYPE 設定画面（予約）

LEVEL / HIGH を設定するための予約画面。現行 build では遷移しない。

---

## 12. 入力インターフェース表示方針

- 論理ボタン名は常に `Left / Right / Down / A / B / START / SELECT` を正本とする
- 物理入力の差異は `config.ini` で吸収し、画面上は論理ボタン名または論理名＋物理入力名の併記で案内する
- 主入力は HID キーボード（標準入力）とするが、ゲームパッド対応を許容する

| 論理入力 | キーボード表示例 | ゲームパッド表示例 |
|---|---|---|
| Left / Right / Down | Arrow Keys | D-Pad Left / Right / Down |
| A | X | Button 1 / South |
| B | Z | Button 2 / West |
| START | Enter | Start |
| SELECT | Right Shift | Select / Back |

ユーザー向け表示では `A (X)` や `START (Enter)` のような併記を許可する。

---

## 13. Diagram-Driven / Acceptance-Driven 観点

1. A-TYPE 主軸の最小画面群が揃っていること
2. 開始設定画面のレベル変更が Left / Right で一意に読めること
3. プレイ画面で NEXT ON/OFF のどちらも誤認しないこと
4. Hold 枠、Hard drop 表示が存在しないこと
5. 一時停止とゲームオーバーで通常プレイ入力が無効であること
6. 画面遷移が `32_state_machine_design.md` と矛盾しないこと

---

## 14. 変更履歴

- 2026-03-24: 32×32px セル前提の描画基準解像度を 640×576 として確定し、キーボード主入力＋ゲームパッド対応、および `config.ini` 前提を追加
- 2026-03-23: SELECT による NEXT 表示切替を画面仕様へ追加し、OFF 状態の表示要件を明記
- 2026-03-23: 予約画面と画面別入力の粒度を補強
