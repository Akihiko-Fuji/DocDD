# 課題管理 / Issue Management

- 文書ID: DOC-MGT-054
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/05_project_management/53_change_management.md`
  - `docs/05_project_management/55_risk_register.md`
  - `docs/04_quality_assurance/45_definition_of_done.md`
  - `docs/05_project_management/56_document_update_checklist.md`
  - `docs/06_records/60_decision_log.md`
  - `docs/06_records/61_change_log.md`
  - `docs/06_records/62_review_log.md`
  - `adr/ADR-0001-game-loop-model.md`
  - `adr/ADR-0002-randomizer-policy.md`
  - `adr/ADR-0003-input-buffer-policy.md`

## 1. 目的
本書は、未解決事項、実装着手前に決めるべき事項、将来拡張へ送る事項を**DocDD 運用可能な Issue**として管理するためのルールを定義する。Issue は単なる作業メモではなく、要求・仕様・設計・試験・記録への更新起点として扱う。

本書の役割は **issue 運用ルールの正本** である。
個別変更時に実際へチェックを入れて使う手順は `56_document_update_checklist.md` に委ね、本書では分類、優先度、close 条件、記録責務を定義する。

## 2. 基本原則
1. **No behavior change without document change** を課題管理にも適用する
2. Issue は「何を直すか」だけでなく「どの文書が影響を受けるか」を必ず持つ
3. 仕様変更系 Issue は関連文書更新、関連 TC 更新、関連記録更新まで完了して初めて close できる
4. 未決事項を将来送りにする場合でも、現時点の非対象理由と再開条件を残す

## 3. Issue 分類
| 分類 | 用途 | 典型例 | close 時に最低限必要な更新 |
|---|---|---|---|
| `requirement` | 要求や対象範囲の変更 | scope 変更、必須機能追加 | 11/13/14/15/16 |
| `spec` | 外部挙動の変更 | 得点表変更、UI 挙動変更 | 20〜26, 16 |
| `design` | 内部責務や状態整理 | state machine 修正、データモデル補強 | 27〜39, 16 |
| `test` | 試験補強 | 新 TC 追加、fixture 追加 | 40〜46, 16 |
| `record` | 理由や履歴整理 | review 指摘、change log 反映 | 60〜64 |
| `bug` | 既定仕様との差異修正 | pause 中入力漏れ、回転不整合 | 原因層 + 下流文書 |
| `enhancement` | 将来拡張・改善 | replay UI 追加、B-TYPE 実装 | 要求/仕様/設計/試験を必要に応じて |

## 4. 優先度ルール
| 優先度 | 意味 | 例 | 期待応答 |
|---|---|---|---|
| `critical` | コア10文書の矛盾、DoD 破綻、主要挙動の誤定義 | 主要フロー欠落、得点表矛盾 | 次回変更で最優先対応 |
| `high` | 実装ブレやテスト不能を生む不備 | Data Model の曖昧さ、fixture 欠落 | 近いマイルストーン内で解消 |
| `medium` | 現時点では代替可能だが先で詰まる | replay 互換方針の詳細 | 計画して対応 |
| `low` | 補助的改善 | 表現揺れ、追記推奨 | 他作業と合わせて対応 |

## 5. DocDD 観点の必須項目
各 Issue には最低でも以下を保持する。

- Issue ID
- 分類
- 優先度
- 起点文書
- 影響文書（affected docs）
- 影響テストケース（affected test cases）
- 影響 ADR / Decision Log（affected ADR / record）
- close 条件
- オーナー
- 状態（open / in_progress / blocked / review / closed）

## 6. close 条件
Issue は以下を満たしたときのみ close できる。

1. 要求・仕様・設計・試験・記録のうち、影響対象文書が更新済みである
2. `16_traceability_matrix.md` が必要に応じて更新されている
3. 関連 TC または fixture が追加・更新されている
4. レビュー指摘がある場合は `62_review_log.md` に応答が残っている
5. 実装を伴う場合は DoD 上の未達項目が明示されていない限り残っていない

## 7. 変更波及確認欄のテンプレート
```markdown
- affected docs:
  - docs/xx_xxx.md
- affected test cases:
  - TC-XXX-001
- affected ADR / records:
  - ADR-000x
  - 60_decision_log.md
- close condition:
  - 文書更新
  - traceability 更新
  - review log 更新
```

## 8. 現在の主要論点
| Issue ID | 分類 | 優先度 | 論点 | 起点文書 | 影響文書 | オーナー | 状態 | close 条件 |
|---|---|---|---|---|---|---|---|---|
| ISS-001 | enhancement | medium | 実装言語選定の最終確定 | `03_assumptions_and_constraints.md` | `30_architecture_design.md`, `50_development_policy.md`, `60_decision_log.md` | project owner | open | 評価基準固定と採否記録 |
| ISS-002 | enhancement | medium | replay 永続化の実装タイミング | `26_save_replay_config_spec.md` | `33_data_model.md`, `34_module_design.md`, `40_test_strategy.md`, `60_decision_log.md` | project owner | open | 永続化スコープと UI 導線を固定 |
| ISS-003 | enhancement | low | B-TYPE 参考仕様をどのフェーズで具体化するか | `11_scope_definition.md` | `20_game_rules_spec.md`, `21_ui_screen_spec.md`, `52_milestones.md` | project owner | open | 非対象/対象化条件を記録 |
| ISS-004 | test | high | replay/board fixture の実体ファイル化方針 | `46_test_fixtures_catalog.md` | `41_test_cases_game_rules.md`, `42_test_cases_ui_input.md`, `43_test_cases_edge_conditions.md` | qa owner | open | fixture 保存形式と配置先を決定 |

## 9. 解決済み論点
- ピース出現アルゴリズム方針は `ADR-0002` で固定
- 入力バッファ方針は `ADR-0003` で固定
- ゲームループ方針は `ADR-0001` で固定

## 10. 受入観点
- Issue の分類、優先度、close 条件が本文だけで判断できること
- 仕様変更 Issue に文書更新義務が埋め込まれていること
- affected docs / tests / ADR を追えること
- 課題管理文書単体で DocDD の運用ルールとして機能すること


## 11. 変更履歴
- 2026-03-24: Issue 分類表の参照レンジを現行文書構成へ整合（spec: 20〜26 / design: 27〜39 / test: 40〜46）
- 2026-03-24: Issue 分類、優先度、必須記載項目、close 条件、変更波及テンプレートを補強
