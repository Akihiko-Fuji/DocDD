# 文書成熟度マトリクス / Document Maturity Matrix

- 文書ID: DOC-OVW-005
- 最終更新日: 2026-03-23
- 目的: 各文書の成熟度と利用目的を明示し、未完成と予約仕様を区別できるようにする

## 1. 本書の位置付け

本書は、文書群の入口側で**各文書をどの程度の確からしさで読めばよいか**を明示する overview 文書である。

ここで扱う成熟度は、単なる文量や完成感ではなく、
**その文書をどこまで実装判断・レビュー判断・変更判断に使ってよいか**を示す運用ラベルとする。

---

## 2. 成熟度定義

| 成熟度 | 意味 | 実装判断に使ってよいか |
|---|---|---|
| `Stable` | 当面の正本として維持され、実装判断に直接使える | Yes |
| `Reference` | 正本補助。本文理解や基準確認に使う | Conditional |
| `Reserved` | 将来拡張用に最低構造のみ固定 | Limited |
| `Draft` | 方向性はあるが今後厚くする前提 | Caution |
| `Skeleton` | 骨格のみ。単独で判断してはいけない | No |

### 2.1 判断基準

- `Stable`
  - 役割境界、主要定義、参照関係が固定されている
  - 実装判断・レビュー判断の正本として直接参照できる
- `Reference`
  - 正本の補助説明や図示として有用である
  - 単独で仕様確定せず、必ず対応する正本文書と対で読む
- `Reserved`
  - 将来拡張のために枠だけ先に確保している
  - 現行 build の実装根拠にはしない
- `Draft`
  - 現時点でも運用可能だが、今後の詳細化や実施記録の蓄積を前提とする
  - close 条件や DoD 判定では、補助文書や上位正本との併読を前提とする
- `Skeleton`
  - 見出しや最小構造のみ存在する段階であり、レビューの入口情報としてのみ使う

---

## 3. 更新ルール

### 3.1 更新責任

- 文書を追加・再配置・大幅改定した担当者は、必要に応じて本マトリクスも更新する
- maturity の変更理由は、`61_change_log.md` または `62_review_log.md` に残す
- review で「現ラベルでは誤読を招く」と判断された場合は、本書のラベル更新を優先する

### 3.2 格上げ・格下げの目安

- `Draft -> Stable`
  - 主要節が埋まり、上位文書との矛盾が解消されている
  - 受入観点または運用観点が本文で読める
  - traceability 上の参照先として運用可能である
- `Reserved -> Draft`
  - 将来枠ではなく、現行検討対象として本文詳細を書き始めた
- `Stable -> Draft`
  - 大幅な再設計中で、一時的に正本としての確度が落ちた
- `Skeleton` 維持
  - 将来の場所取り以外の用途を持たない限り、単独判断禁止を明示する

### 3.3 変更時の確認項目

- 実装判断に使えるかどうかが、現ラベルと本文内容で一致しているか
- 将来拡張の予約文書が、誤って現行仕様と読まれないか
- `56_document_update_checklist.md` の「未成熟文書」確認と整合しているか

---

## 4. 主要文書マトリクス

| 文書 | 目的 | 成熟度 | 実装判断に使ってよいか | 次に厚くすべき項目 |
|---|---|---|---|---|
| `00_document_map.md` | 入口、役割整理 | Stable | Yes | 変更時に追加文書反映 |
| `11_scope_definition.md` | 対象/非対象範囲 | Stable | Yes | B-TYPE 対象化条件 |
| `13_functional_requirements.md` | 機能要求 | Stable | Yes | 将来拡張 FR の段階化 |
| `14_non_functional_requirements.md` | 非機能要求 | Stable | Yes | replay 永続化時の品質条件 |
| `20_game_rules_spec.md` | 外部ルール仕様 | Stable | Yes | B-TYPE 詳細化時の分離 |
| `21_ui_screen_spec.md` | 画面仕様 | Stable | Yes | 保存 UI 採用時の画面追加 |
| `24_piece_rotation_collision_spec.md` | 回転・衝突 | Stable | Yes | 実装検証結果反映 |
| `26_save_replay_config_spec.md` | 保存/再現予約仕様 | Reserved | Limited | 永続化タイミング、version 戦略 |
| `docs/03_internal_design/27_runtime_flowchart_mermaid.md` | 処理順図 | Reference | Conditional | 実装名との同期維持 |
| `32_state_machine_design.md` | 状態設計 | Stable | Yes | B-TYPE 予約状態の扱い |
| `33_data_model.md` | データ構造設計 | Stable | Yes | enum 詳細と validation 規約 |
| `34_module_design.md` | モジュール責務 | Stable | Yes | 実装契約粒度の追加 |
| `40_test_strategy.md` | QA 方針 | Stable | Yes | automation 境界の詳細化 |
| `41_test_cases_game_rules.md` | ルール試験仕様 | Draft | Yes | 実施結果の蓄積 |
| `42_test_cases_ui_input.md` | UI/入力試験仕様 | Draft | Yes | usability 記録欄の蓄積 |
| `43_test_cases_edge_conditions.md` | 境界試験仕様 | Draft | Yes | replay ベース手順の具体化 |
| `45_definition_of_done.md` | 完了条件 | Stable | Yes | フェーズ別 DoD 派生 |
| `46_test_fixtures_catalog.md` | fixture 正本 | Draft | Yes | 外部ファイル化規約 |
| `docs/05_project_management/56_document_update_checklist.md` | 実行用 checklist | Stable | Yes | 自動化導線 |
| `54_issue_management.md` | 課題運用 | Stable | Yes | 運用実績例の追記 |
| `55_risk_register.md` | リスク運用 | Stable | Yes | 指標化・レビュー履歴 |

---

## 5. 運用ルール

- `Reserved`, `Draft`, `Skeleton` の文書は、単独で仕様確定に使わず上位正本文書と組み合わせて参照する
- 成熟度を変更したときは `61_change_log.md` または `62_review_log.md` に記録する
- `Skeleton` が残る場合は DoD の未達理由として明示する

---

## 6. 受入観点

- 「薄い文書」が未完成なのか意図的な予約なのかを一目で判断できること
- 実装判断に使ってよい文書かどうかが明示されていること
- 成熟度の判断基準と更新ルールが本文で読めること
- 次に厚くすべき項目がレビューの起点になること

---

## 7. 変更履歴

- 2026-03-23: 成熟度定義の判断基準、更新責任、格上げ・格下げルールを追加
- 2026-03-23: `05_document_maturity_matrix.md` として overview 配下へ再配置し、成熟度マトリクスを文書入口側へ移動
