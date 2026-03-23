# テスト方針 / Test Strategy

- 文書ID: DOC-QA-040
- 文書名: テスト方針 / Test Strategy
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 品質確認方針、試験観点、追跡可能性の確保方法、および DocDD に基づくテスト設計の基本原則を定義する
- 関連文書:
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/01_requirements/15_acceptance_criteria.md`
  - `docs/01_requirements/16_traceability_matrix.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/02_external_spec/25_pause_gameover_resume_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/04_quality_assurance/41_test_cases_game_rules.md`
  - `docs/04_quality_assurance/42_test_cases_ui_input.md`
  - `docs/04_quality_assurance/43_test_cases_edge_conditions.md`
  - `docs/04_quality_assurance/45_definition_of_done.md`

---

## 1. 本書の目的

本書は、本プロジェクトにおけるテストの基本思想と、要求・仕様・設計からテストへ至る追跡方法を定義する。目的は「後からテストを書く」ことではなく、「文書からテストを導出し、不明瞭な仕様を早期発見する」ことである。

---

## 2. 基本原則

1. テストは文書起点で導出する
2. A-TYPE の主要プレイ体験を最優先で検証する
3. Game Boy 基準の速度、得点、SELECT/NEXT、B-TYPE 参照条件を明示的に確認する
4. T-Spin 採用に伴う追加判定を独立観点として扱う
5. B-TYPE は初期実装の必須試験対象から外すが、参照仕様レビュー対象には含める
6. 正常系・境界系・非採用確認・参照仕様レビューを分ける
7. 図面は本文の要約として、図と本文の整合性もテスト対象とする

---

## 3. 評価視点

### 3.1 Spec-Driven

- 外部仕様の正本を `20`〜`25` 系文書に置き、TC はその拘束条件を検証する
- 暗黙仕様を認めず、Game Boy 基準で補完した事項も文書へ明記する
- SELECT による NEXT 表示切替、速度表、B-TYPE/HIGH のような見落としやすい項目を重点確認する

### 3.2 Acceptance-Driven

- 各コア文書はレビューで完了判定できる受入観点を持つ
- 実装前でも、文書だけで受入可否を議論できる状態を目指す
- テストケースは pass/fail 判定条件を文書レビューの観点へ落とし込む

### 3.3 Diagram-Driven

- 状態遷移図やフローチャートは説明用図ではなく、仕様・設計の要約表現として扱う
- 図と本文に差異がある場合は defect とみなす
- 図からテストケースを逆算できることを品質目標に含める

---

## 4. 追跡軸

```text
BR -> UC -> DM -> SR / NSR -> EXT -> Internal Contract -> TC
```

主な対応文書:
- BR: `01_project_charter.md`, `11_scope_definition.md`
- UC: `12_use_cases.md`
- DM: `31_domain_model.md`, `32_state_machine_design.md`
- SR/NSR: `13_functional_requirements.md`, `14_non_functional_requirements.md`
- EXT: `20`〜`25` 系外部仕様
- Internal Contract: `34_module_design.md`
- TC: `41`〜`43`

---

## 5. 優先試験対象

### 5.1 コアロジック

- 出現
- 落下
- 回転
- 接地
- 固定
- ライン消去
- 得点計算
- レベル進行
- ゲームオーバー判定

### 5.2 Game Boy 基準重点項目

- 10×18 盤面
- NEXT 1 個
- SELECT による NEXT 表示 ON/OFF
- A-TYPE 開始レベル 0〜9
- B-TYPE 25 lines / HIGH 0〜5 の参照妥当性
- 速度表（Level 0〜20）
- Hard drop 非採用

### 5.3 独自拡張重点項目

- T-Spin 判定
- T-Spin 0 line 得点
- T-Spin と通常ライン消去得点の優先順

### 5.4 UI / 状態

- タイトル
- A-TYPE 開始設定
- プレイ
- 一時停止
- ゲームオーバー / リザルト

### 5.5 境界条件

- 壁際回転失敗
- 床際回転失敗
- 天井近傍回転判定
- 出現不能
- 4 ライン同時消去
- 一時停止中入力無効
- 同時入力相殺規則
- NEXT 表示 OFF 中も内部キューが維持されること

---

## 6. テストレベル

### 6.1 文書レビュー

整合性、用語、スコープ逸脱、トレーサビリティ、図同期を確認する。

### 6.2 ルール単位試験

ゲームロジックをヘッドレスに検証する。得点、速度、レベル進行、T-Spin 判定、NEXT キュー維持はこの層を主対象とする。

### 6.3 UI / 状態遷移試験

画面遷移、入力受理範囲、NEXT 表示切替、pause / gameover 中入力無効を確認する。

### 6.4 統合プレイ試験

タイトルからゲームオーバーまでの一連の流れを確認する。

---

## 7. テストケース群の責務分離

- `41_test_cases_game_rules.md`: ルール・得点・進行・速度
- `42_test_cases_ui_input.md`: 画面・入力・NEXT 表示切替・状態依存受付
- `43_test_cases_edge_conditions.md`: 境界条件・異常系・非採用機能確認

---

## 8. テストケース記述ルール

各テストケースは少なくとも以下を保持する。

- テスト ID
- 観点
- 前提条件
- 入力 / 操作
- 実施手順
- 期待状態遷移
- pass 条件
- 関連 FR / NFR / EXT / Internal Contract

代表ケースでは、**どの文書から導出したか** が分かるよう複数層を明記する。

---

## 9. カバレッジ最低基準

- 各必須 FR に対して少なくとも 1 件の主テストケースが存在する
- 主要 NFR に対して代表的な確認観点が存在する
- T-Spin は成立 / 不成立 / 0 line の 3 系列を最低限含む
- NEXT 表示は ON / OFF / 切替後維持の 3 観点を含む
- 非採用機能は「存在しないこと」を確認するテストを持つ
- ポーズ系は進入 / 継続 / 復帰 / 破棄の 4 観点を持つ
- 図文書は本文整合レビューを持つ

---

## 10. 完了条件の考え方

以下を満たして初期段階の受入候補とする。

1. A-TYPE 主軸の必須テストが完了している
2. Game Boy 基準の得点・速度・NEXT 表示仕様が確認済みである
3. T-Spin を含む主要得点ケースが確認済みである
4. Hard drop 非採用と Hold 非採用が実機挙動上も確認できる
5. 一時停止中およびゲームオーバー後の入力無効が確認できる
6. 文書間および図面との矛盾がない

---

## 11. 変更影響の見方

- 得点表変更: `23_scoring_level_spec.md`, `20_game_rules_spec.md`, `34_module_design.md`, `41_test_cases_game_rules.md`
- 入力変更: `22_input_operation_spec.md`, `21_ui_screen_spec.md`, `34_module_design.md`, `42_test_cases_ui_input.md`
- NEXT 表示仕様変更: `20_game_rules_spec.md`, `21_ui_screen_spec.md`, `22_input_operation_spec.md`, `32_state_machine_design.md`, `42_test_cases_ui_input.md`
- 回転仕様変更: `24_piece_rotation_collision_spec.md`, `34_module_design.md`, `43_test_cases_edge_conditions.md`
- 状態変更: `32_state_machine_design.md`, `25_pause_gameover_resume_spec.md`, `34_module_design.md`, `42_test_cases_ui_input.md`

---

## 12. 受入観点

1. テスト対象が文書から導出されていること
2. Game Boy 基準と独自拡張の両方が漏れなく試験対象へ入っていること
3. B-TYPE が過剰に初期必須テストへ混入していないこと
4. 境界条件、非採用機能、図同期確認が含まれていること
5. NEXT 表示切替や入力優先順のような見落としやすい仕様がテスト観点へ反映されていること
6. 代表ケースで前提条件、手順、判定基準が明示されていること

---

## 13. 変更履歴

- 2026-03-23: Game Boy 基準の速度・SELECT/NEXT・B-TYPE/HIGH を試験重点へ追加
- 2026-03-23: 図同期レビューと NEXT 表示 ON/OFF カバレッジ基準を追加
