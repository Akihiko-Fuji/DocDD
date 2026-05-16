# 開発進捗トランザクション記録（不足情報集約） / Development Progress Transaction Log (Missing Information)

- 文書ID: DOC-REC-066
- 最終更新日: 2026-04-17
- 目的: `Block_Puzzle_DocDD` に整理済みの要求・仕様・設計・QA 文書を実装着手へ接続するため、現時点で不足している意思決定情報を単独ファイルで集約する
- 性質: 本書は「未決事項の進捗トランザクション記録」であり、要件・仕様・設計そのものの正本ではない
- 関連文書:
  - `docs/05_project_management/54_issue_management.md`
  - `docs/00_overview/05_document_maturity_matrix.md`
  - `docs/06_records/65_art_asset_transaction_log.md`

---

## 1. 運用ルール

1. 本書は、実装開始・試験実行・受入判定の前提になる「不足情報」をトランザクション単位で追跡する
2. 内容を確定する際は、該当する正本文書（requirements / external spec / internal design / QA）を更新し、本書では状態を `closed` へ変更する
3. `open` のまま残る項目は、close 条件・次アクション・影響文書を必ず維持する
4. 実装判断に使う前提は `05_document_maturity_matrix.md` の成熟度と矛盾しないように管理する

---

## 2. 不足情報サマリ（2026-04-17 時点）

| 区分 | 件数 | 実装への影響 | 最優先項目 |
|---|---:|---|---|
| 実装方針確定 | 1 | 技術選定と着手計画が固定できない | 言語・基盤の最終確定 |
| 機能スコープ確定 | 2 | 実装対象境界が揺れやすい | replay 永続化のフェーズ確定 |
| 試験実行基盤 | 1 | TC 実行の再現性が不足 | fixture 実体ファイル化方針 |
| 画面資産実装 | 1 | UI 文言を仕様どおり表示できない | `-` と space の追加 |

---

## 3. トランザクション一覧（不足情報詳細）

| TX-ID | 不足情報 | 現在値 / 既知情報 | 追加で必要な決定 | 影響レイヤ | 影響文書 | 優先度 | 状態 | close 条件 | 次アクション |
|---|---|---|---|---|---|---|---|---|---|
| TX-066-001 | 実装言語・基盤の最終確定 | 候補として Lua + LÖVE 検討履歴あり。複数言語へ写像可能な契約記述は整備済み | 初期実装で採用する言語・実行基盤・採否理由を固定 | design / record | `03_assumptions_and_constraints.md`, `30_architecture_design.md`, `50_development_policy.md`, `60_decision_log.md` | medium | open | 評価軸・採否・理由が記録され、関連文書が同期更新される | ISS-001 として選定レビューを実施し、DEC 採番で確定する |
| TX-066-002 | replay 永続化の実装タイミングと UI 導線 | 保存形式と schema は定義済み。実装フェーズ位置が未固定 | 初期リリース範囲に含めるか、後続フェーズへ送るかを確定 | spec / design / test | `26_save_replay_config_spec.md`, `33_data_model.md`, `34_module_design.md`, `40_test_strategy.md`, `60_decision_log.md` | medium | open | 実装フェーズ・UI 導線・試験観点が一致して更新される | ISS-002 をマイルストーンに紐づけ、phase 境界を決定する |
| TX-066-003 | B-TYPE 参考仕様の具体化タイミング | A-TYPE 主軸は固定。B-TYPE は参照保持だが対象化条件が未確定 | B-TYPE をどのマイルストーンで仕様詳細化するかを確定 | scope / spec / planning | `11_scope_definition.md`, `20_game_rules_spec.md`, `21_ui_screen_spec.md`, `52_milestones.md` | low | open | 非対象継続または対象化条件が明文化される | ISS-003 の再開条件をマイルストーンへ反映する |
| TX-066-004 | replay / board fixture の実体ファイル化方式 | fixture カタログはあるが、保存形式・配置規約が未確定 | fixture の拡張子、配置先、命名規約、CI 実行時参照方式を確定 | test / design | `46_test_fixtures_catalog.md`, `41_test_cases_game_rules.md`, `42_test_cases_ui_input.md`, `43_test_cases_edge_conditions.md` | high | open | fixture 実体が配置され、TC 参照先が固定される | ISS-004 を最優先で処理し、最小 fixture セットを先行確定する |
| TX-066-005 | UI 必須文言を満たすフォント記号の不足 | 英大文字・数字は利用可。`-` と space が不足 | `hyphen` と space の扱い（画像追加または幅定義）を確定 | spec / asset / implementation | `21_ui_screen_spec.md`, `27_image_asset_data_spec.md`, `65_art_asset_transaction_log.md` | high | open | P1 不足文字が補充され、画面実装で利用可能になる | アート資産追加後に 65 の不足一覧を更新し、UI 実装へ接続する |

---

## 4. 実装着手ゲート（不足情報ベース）

### 4.1 Go 判定に必要な最小条件

1. `TX-066-001` が `closed`（実装基盤の固定）
2. `TX-066-004` が `closed`（TC 実行の再現条件固定）
3. `TX-066-005` が `closed`（UI 必須文言の表示阻害要因解消）

### 4.2 条件付き着手で許容する項目

- `TX-066-002` は「永続化を後続フェーズへ送る」判断が明示されていれば、コアゲームループ実装は先行可
- `TX-066-003` は A-TYPE 主軸方針を維持する限り、初期実装の blocking にはしない

---

## 5. 更新トランザクション履歴

| 日付 | 種別 | 内容 | 結果 |
|---|---|---|---|
| 2026-04-17 | 集約作成 | issue 管理、成熟度、資産進捗から「実装着手に不足する情報」を単独記録へ統合 | 不足情報の優先度・close 条件・次アクションを可視化 |

---

## 6. 次回レビュー観点

1. `TX-066-004` の close を最優先とし、TC 実行の再現可能性を先に固める
2. `TX-066-001` の採否記録を DEC として残し、設計・方針文書の参照先を固定する
3. `TX-066-005` の解消後、UI 文言の表示確認を test case へ接続する
4. `TX-066-002` / `TX-066-003` はマイルストーン連動で「いつ決めるか」を明文化する
