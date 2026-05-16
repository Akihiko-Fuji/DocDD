# 変更事例: T-Spin 採用 / Change Case: T-Spin Adoption

- 文書ID: DOC-REC-064
- 文書名: 変更事例: T-Spin 採用 / Change Case: T-Spin Adoption
- 最終更新日: 2026-03-23
- 目的: DocDD において、1 つの仕様変更が要求・仕様・設計・試験・記録へどう波及するかの見本を示す
- 関連文書:
  - `docs/01_requirements/11_scope_definition.md`
  - `docs/01_requirements/13_functional_requirements.md`
  - `docs/01_requirements/15_acceptance_criteria.md`
  - `docs/01_requirements/16_traceability_matrix.md`
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/24_piece_rotation_collision_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/04_quality_assurance/40_test_strategy.md`
  - `docs/04_quality_assurance/41_test_cases_game_rules.md`
  - `docs/04_quality_assurance/43_test_cases_edge_conditions.md`
  - `docs/06_records/60_decision_log.md`
  - `docs/06_records/61_change_log.md`
  - `docs/06_records/62_review_log.md`

---

## 1. 本書の目的

本書は、**「T-Spin を採用する」という 1 件の変更要求が、どの文書へどう波及したか** を時系列で示す見本である。

DocDD の強みは、変更が発生したときに「どこを読めば良いか」「何を更新すべきか」が追える点にある。本書ではその流れを具体化する。

---

## 2. 変更要求

### 2.1 背景
- 既存の見本では、Game Boy 版基準の簡潔さを重視していた
- 一方で、DocDD の説明資料としては「参照元をベースにした拡張仕様」の例があった方が分かりやすい

### 2.2 変更要求
- T-Spin を非採用から採用へ変更する
- 0 line を含む得点仕様を定義する
- 変更が要求・設計・試験へどう波及するかを読めるようにする

---

## 3. 時系列

| 段階 | 変更内容 | 更新文書 |
|---|---|---|
| 1. 意図整理 | T-Spin を教材価値の高い独自拡張として扱う方針を確認 | `11_scope_definition.md`, `60_decision_log.md` |
| 2. 要求更新 | T-Spin 判定・得点反映を FR として明文化 | `13_functional_requirements.md` |
| 3. 外部仕様更新 | ルール順序、得点表、判定前提を仕様化 | `20_game_rules_spec.md`, `23_scoring_level_spec.md`, `24_piece_rotation_collision_spec.md` |
| 4. 設計更新 | 固定後処理と T-Spin 責務位置を設計へ反映 | `32_state_machine_design.md`, `34_module_design.md` |
| 5. 試験更新 | 成立・不成立・0 line を試験ケース化 | `40_test_strategy.md`, `41_test_cases_game_rules.md`, `43_test_cases_edge_conditions.md` |
| 6. 追跡更新 | 上流から TC まで縦断トレースを追加 | `16_traceability_matrix.md`, `15_acceptance_criteria.md`, `45_definition_of_done.md` |
| 7. 記録更新 | 変更・レビュー履歴に反映 | `61_change_log.md`, `62_review_log.md` |

---

## 4. 変更前 / 変更後

| 観点 | 変更前 | 変更後 |
|---|---|---|
| スコープ | T-Spin は採用しない想定 | 独自拡張として採用 |
| 機能要求 | T-Spin 関連 FR が弱い / 不在 | FR-210, FR-211 を明示 |
| 外部仕様 | 通常ライン得点中心 | T-Spin 専用得点表と優先順を追加 |
| 回転仕様 | 回転可否中心 | T-Spin 判定前提を追加 |
| 設計 | 固定後処理の責務が粗い | `PL-SCORE`, `tspin_detector`, `scoring_service` を明示 |
| テスト | 通常ケース中心 | 成立 / 不成立 / 0 line を追加 |
| 記録 | 決定理由が散在 | Decision / Change / Review に記録 |

---

## 5. 影響文書の見方

### 5.1 上流側
- `11_scope_definition.md`: なぜ独自拡張として採用したか
- `13_functional_requirements.md`: 何を満たすべきか

### 5.2 外部仕様側
- `20_game_rules_spec.md`: 固定後処理順と T-Spin 優先適用
- `23_scoring_level_spec.md`: T-Spin 得点表、優先順、算定例
- `24_piece_rotation_collision_spec.md`: 成立条件、不成立条件、最終操作の定義

### 5.3 設計側
- `32_state_machine_design.md`: `PL-SCORE` で T-Spin 判定を行う理由
- `34_module_design.md`: `tspin_detector` と `scoring_service` の公開契約

### 5.4 試験側
- `40_test_strategy.md`: T-Spin を追加重点項目として扱う
- `41_test_cases_game_rules.md`: 成立 / 0 line / 不成立
- `43_test_cases_edge_conditions.md`: 対角 3 箇所未満の不成立

---

## 6. この変更で追加されたテスト

- TC-GR-005: T-Spin 0 line
- TC-GR-006: T-Spin 1 line
- TC-GR-007: T-Spin 不成立
- TC-EC-007: 対角 3 箇所未満で不成立

これにより、仕様変更がテストへどう導出されるかを説明できる。

---

## 7. DocDD 上の学び

1. 変更要求は、まずスコープ / 要求で意味付けする
2. 仕様化しないまま設計やテストへ進めない
3. 設計は責務配置として影響を受ける
4. テストは成立ケースだけでなく不成立ケースも必要になる
5. 記録文書を残すことで、後から「なぜこうなったか」を説明できる

---

## 8. 変更履歴

- 2026-03-23: T-Spin 採用を題材とした変更波及見本を新規作成
