# テスト方針 / Test Strategy

- 文書ID: DOC-QA-040
- 文書名: テスト方針 / Test Strategy
- 最終更新日: 2026-03-23
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: 品質確認方針、試験観点、追跡可能性の確保方法、および DocDD に基づくテスト設計の基本原則を定義する
- 関連文書:
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
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
本書は、本プロジェクトにおけるテストの基本思想と、要求・仕様・設計からテストへ至る追跡方法を定義する。

---

## 2. 基本原則
1. テストは文書起点で導出する
2. A-TYPE の主要プレイ体験を最優先で検証する
3. T-Spin 採用に伴う追加判定を明示的に試験対象へ入れる
4. Game Boy 系入力の PC 写像による齟齬を UI / 入力試験で補足する
5. B-TYPE は参考仕様のレビュー対象とし、初期実装の必須試験対象からは外す
6. 仕様の明確化に伴い、正常系・境界系・非採用確認を明示的に分ける
7. 少なくとも代表テストは、前提条件・入力・手順・判定基準まで明文化する

---

## 3. 追跡軸
```text
BR -> UC -> DM -> SR / NSR -> EXT -> Internal Contract -> TC
```

主な対応文書:
- BR: `01_project_charter.md`, `11_scope_definition.md`
- UC: `12_use_cases.md`
- DM: `31_domain_model.md`, `32_state_machine_design.md`
- SR/NSR: `13_functional_requirements.md`, `14_non_functional_requirements.md`
- EXT: `20`～`25` 系外部仕様
- Internal Contract: `34_module_design.md`
- TC: `41`～`43`

---

## 4. 優先試験対象
### 4.1 コアロジック
- 出現
- 落下
- 回転
- 接地
- 固定
- ライン消去
- 得点計算
- レベル進行
- ゲームオーバー判定

### 4.2 追加重点項目
- T-Spin 判定
- T-Spin 0 line 得点
- SELECT 相当入力の無害性
- Hard drop 非採用確認
- START 押下時の状態遷移優先順

### 4.3 UI / 状態
- タイトル
- A-TYPE 開始設定
- プレイ
- 一時停止
- ゲームオーバー / リザルト

### 4.4 境界条件
- 壁際回転失敗
- 床際回転失敗
- 積み上がり近傍回転失敗
- 出現不能
- 4 ライン同時消去
- 一時停止中入力無効
- 同時入力相殺規則

---

## 5. テストレベル
### 5.1 文書レビュー
整合性、用語、スコープ逸脱、トレーサビリティ確認を行う。

### 5.2 ルール単位試験
ゲームロジックをヘッドレスに検証する。得点、レベル進行、T-Spin 判定はこの層を主対象とする。

### 5.3 UI / 状態遷移試験
画面遷移と入力受理範囲を確認する。

### 5.4 統合プレイ試験
タイトルからゲームオーバーまでの一連の流れを確認する。

---

## 6. テストケース群の責務分離
- `41_test_cases_game_rules.md`: ルール・得点・進行
- `42_test_cases_ui_input.md`: 画面・入力・状態依存受付
- `43_test_cases_edge_conditions.md`: 境界条件・異常系・非採用機能確認

---

## 7. テストケース記述ルール

各テストケースは、少なくとも以下を保持する。

- テスト ID
- 観点
- 前提条件
- 入力 / 操作
- 実施手順
- 期待状態遷移
- pass 条件
- 関連 FR / NFR / EXT / Internal Contract

代表ケースでは、**どう導いたか** が分かるよう、関連文書の層を複数記載する。

---

## 8. カバレッジの最低基準
- 各必須 FR に対して少なくとも 1 件の主テストケースが存在する
- 主要 NFR に対して代表的な確認観点が存在する
- T-Spin は成立 / 不成立 / 0 line の 3 系列を最低限含む
- 非採用機能は「存在しないこと」を確認するテストを持つ
- ポーズ系は進入 / 継続 / 復帰 / 破棄の 4 観点を持つ
- Internal Contract で定義した公開契約のうち重要なものは TC に接続される

---

## 9. 完了条件の考え方
以下を満たして初期段階の受入候補とする。
1. A-TYPE 主軸の必須テストが完了している
2. T-Spin を含む主要得点ケースが確認済みである
3. Hard drop 非採用と Hold 非採用が実機挙動上も確認できる
4. 一時停止中およびゲームオーバー後の入力無効が確認できる
5. 文書間の矛盾がない
6. 主要テストが `16_traceability_matrix.md` と `34_module_design.md` に接続されている

---

## 10. 変更影響の見方
- 得点表変更: `23_scoring_level_spec.md`, `20_game_rules_spec.md`, `34_module_design.md`, `41_test_cases_game_rules.md`
- 入力変更: `22_input_operation_spec.md`, `21_ui_screen_spec.md`, `34_module_design.md`, `42_test_cases_ui_input.md`
- 回転仕様変更: `24_piece_rotation_collision_spec.md`, `34_module_design.md`, `43_test_cases_edge_conditions.md`
- 状態変更: `32_state_machine_design.md`, `25_pause_gameover_resume_spec.md`, `34_module_design.md`, `42_test_cases_ui_input.md`

---

## 11. 受入観点
1. テスト対象が文書から導出されていること
2. T-Spin のような独自拡張が漏れなく試験対象へ入っていること
3. B-TYPE が過剰に初期必須テストへ混入していないこと
4. 境界条件と非採用機能確認が含まれていること
5. 仕様明確化のために追加した優先順・相殺規則がテスト観点へ反映されていること
6. 代表ケースで前提条件、手順、判定基準が明示されていること

---

## 12. 変更履歴
- 2026-03-23: T-Spin、SELECT 相当入力、Hard drop 非採用確認を試験重点へ追加
- 2026-03-23: 同時入力、START 優先、カバレッジ最低基準を追記
- 2026-03-23: 代表テストの試験仕様列と Internal Contract 軸を追記
