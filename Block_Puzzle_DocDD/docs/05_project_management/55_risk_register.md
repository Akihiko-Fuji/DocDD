# リスク登録簿 / Risk Register

- 文書ID: DOC-MGT-055
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/05_project_management/53_change_management.md`
  - `docs/05_project_management/54_issue_management.md`
  - `docs/04_quality_assurance/45_definition_of_done.md`

| ID | リスク | 発生確率 | 重大度 | 監視タイミング | オーナー | 影響 | 対応 / 緩和策 | 発火時の対応手順 | close 条件 |
|---|---|---|---|---|---|---|---|---|---|
| R-001 | Game Boy 準拠と独自拡張の混同 | medium | critical | 要求/仕様レビュー時 | product owner | 仕様矛盾 | 差分を `04_reference_baseline_and_deltas.md` と外部仕様へ明文化する | 差分未記載箇所を洗い出し、要求→仕様→テストを同期更新する | 基準差分と関連 TC が更新され、レビュー承認済み |
| R-002 | T-Spin 追加に伴う文書更新漏れ | high | high | T-Spin 関連変更時 | design owner | 追跡性低下 | 20/23/24/32/40/41/43 を同時更新する | 変更対象を `56_document_update_checklist.md` で点検し、traceability を更新する | 主要関連文書と TC が同期し review log が閉じている |
| R-003 | 言語選定が主題化する | medium | medium | マイルストーン計画時 | project owner | DocDD 主題が薄れる | 判断基準を先に固定する | 議論を `ISS-001` へ集約し、意思決定を Decision Log へ記録する | 技術選定理由が DocDD 目的と結びついて承認されている |
| R-004 | キーボード / ゲームパッド割当が曖昧 | medium | high | UI/入力レビュー時 | ux owner | UI 実装ぶれ | `22_input_operation_spec.md` と `config.ini` 仕様で固定する | 入力インターフェース設定と UI 表示差異を洗い出し、Config / UI / TC を同時修正する | `config.ini` と UI 表示が一致し TC が更新済み |
| R-005 | randomizer 方針が実装で独自解釈される | medium | high | replay/config 設計時 | design owner | 再現性低下 | `ADR-0002` と replay/config 仕様を正本化する | seed 条件、開始条件、入力列条件を再点検し replay 仕様へ反映する | ADR・仕様・schema/sample が一致している |
| R-006 | 図と本文が乖離する | high | high | 文書変更レビュー時 | doc owner | Diagram-Driven レビュー破綻 | 27 / 38 と 21 / 32 / 34 を同一変更で更新する | まず図を更新し、次に本文と test cases の語彙を一致させる | 図と本文の節点名が一致し、図レビューが完了している |
| R-007 | 空または薄い補助文書が成熟度を誤認させる | medium | medium | リリース/レビュー前 | doc owner | 実装ブレ | schema / sample / ADR / management 文書に最低構造を維持する | maturity matrix を見直し、Reserved/Draft を明示する | `05_document_maturity_matrix.md` が最新で誤認が解消されている |
| R-008 | 具体盤面 fixture 不足で試験再現性が低い | high | high | テスト設計時 | qa owner | テスト不能 | `46_test_fixtures_catalog.md` と TC を同時整備する | fixture ID と再利用関係を付与し、代表ケースを実行可能粒度へ更新する | 主要 TC が fixture ID を参照し再現手順が固定されている |

## 2. リスク評価基準
- 発生確率は `low / medium / high` の 3 段階で扱う
- 重大度は `medium / high / critical` の 3 段階で扱う
- 優先監視対象は、発生確率または重大度のいずれかが `high` 以上のものとする

## 3. 優先監視項目
- R-001, R-002, R-005, R-006, R-008 を高優先で監視する
- 変更要求レビュー時はまず R-001 と R-002 を確認する
- 実装着手前レビューでは R-005, R-007, R-008 を重点確認する

## 4. 監視・エスカレーションルール
- 優先監視対象は、変更要求レビュー、マイルストーンレビュー、実装着手前レビューの各タイミングで再確認する
- 同一リスクが review log で 2 回以上再発した場合は escalation 対象とし、Decision Log または ADR への格上げを検討する
- close 条件を満たさない限り、暫定対処だけで closed にしない

## 5. 受入観点
- register として必要な管理列（発生確率、重大度、監視タイミング、オーナー、対応手順、close 条件）が揃っていること
- project management 文書として即運用できること
- Issue 管理と DoD に接続できること

## 6. 変更履歴
- 2026-03-24: リスク評価基準、監視ルール、escalation 条件を追加
