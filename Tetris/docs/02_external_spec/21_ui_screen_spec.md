# UI画面仕様 / UI Screen Specification

- 文書ID: DOC-SPC-021
- 文書名: UI画面仕様 / UI Screen Specification
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 本プロジェクトにおける画面構成、画面ごとの表示要素、入力受付、および画面遷移を外部仕様として定義する
- 関連文書:
  - `docs/00_overview/00_document_map.md`
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`

---

## 1. 本書の目的

本書は、プレイヤーから見える主要画面、表示要素、入力受付、および画面遷移を定義する。

---

## 2. UI 基本方針

1. Game Boy 版相当の簡潔さを維持する
2. PC 実装としてキー表記を併記できるようにする
3. 盤面視認性を最優先とする
4. 情報過多 UI にしない
5. T-Spin 採用に伴う結果表示は必要最小限に留める

---

## 3. 対象画面

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

## 4. 画面遷移

- SCR-001 → SCR-002: START 相当入力
- SCR-002 → SCR-003: 開始確定
- SCR-002 → SCR-001: 戻る
- SCR-003 → SCR-004: START
- SCR-003 → SCR-005: ゲームオーバー成立
- SCR-004 → SCR-003: START
- SCR-004 → SCR-001: タイトル復帰
- SCR-005 → SCR-002: 再試行
- SCR-005 → SCR-001: タイトル復帰

---

## 5. SCR-001 タイトル画面

### 表示要素
- タイトル名
- 開始案内
- START 相当キー案内

### 入力
- START 相当: SCR-002 へ遷移
- その他プレイ入力: 無効

---

## 6. SCR-002 A-TYPE 開始設定画面

### 表示要素
- `A-TYPE`
- `LEVEL`
- 現在の開始レベル（0～9）
- 開始確定案内
- 戻る案内

### 入力
- 左 / 右 または 上 / 下: レベル変更
- A または START: 開始確定
- B: タイトルへ戻る
- SELECT: 予約入力として無視してよい

---

## 7. SCR-003 プレイ画面

### 7.1 必須表示要素
- 10×18 盤面
- 現在ピース
- 固定済みブロック
- NEXT 1 個
- SCORE
- LINES
- LEVEL

### 7.2 任意表示要素
- 直近の T-Spin 表示
- PAUSE 解除案内
- キーガイド簡易表示

### 7.3 非表示要素
- Hold 枠
- Hard drop 案内
- ゴーストピース
- 対戦用 UI

---

## 8. SCR-004 一時停止画面

### 表示要素
- `PAUSE`
- 再開方法
- タイトル復帰方法
- 停止中であることが分かる静的表示

### 入力
- START: プレイへ戻る
- B または ESC 相当: タイトルへ戻る
- 左右移動、回転、ソフトドロップ: 無効

---

## 9. SCR-005 ゲームオーバー / リザルト画面

### 表示要素
- `GAME OVER`
- 最終 SCORE
- 最終 LINES
- 最終 LEVEL
- 再試行案内
- タイトル復帰案内

### 入力
- START または A: 再試行
- B: タイトルへ戻る
- プレイ中専用入力: 無効

---

## 10. PC 向けキー表記方針

Game Boy 由来の入力名称は維持しつつ、PC 表示では以下のような対応付けを併記してよい。

| 論理入力 | PC 表示例 |
|---|---|
| 十字キー | Arrow Keys |
| A | X |
| B | Z |
| START | Enter / P |
| SELECT | Right Shift |

---

## 11. T-Spin 表示方針

T-Spin 採用に伴い、プレイ画面またはリザルト表示で `T-SPIN` の文字列を短時間表示してよい。ただし、派手な演出は必須としない。

---

## 12. 受入観点

1. A-TYPE 主軸の最小画面群が揃っていること
2. Hold 枠、Hard drop 表示が存在しないこと
3. NEXT 1 個、SCORE、LINES、LEVEL がプレイ画面で確認できること
4. 一時停止とゲームオーバーで通常プレイ入力が無効であること

---

## 13. 変更履歴

- 2026-03-23: A-TYPE 主軸化、SELECT 相当入力、T-Spin 表示方針、非採用 UI 要素整理を反映
