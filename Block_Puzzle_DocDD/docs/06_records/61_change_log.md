# 変更履歴 / Change Log

- 文書ID: DOC-REC-061
- 最終更新日: 2026-03-24

## 2026-03-24
- 描画基準解像度の正本を 640×576 に修正し、README、overview、requirements、UI、architecture、rendering design、interface contract の表記を 32×32px セル前提へ統一した
- `26_save_replay_config_spec.md` を Stable へ格上げし、保存形式・互換性・失敗時挙動を現時点の正本として扱うことを明記した
- `39_interface_contract.md`、`41_test_cases_game_rules.md`、`42_test_cases_ui_input.md`、`43_test_cases_edge_conditions.md`、`46_test_fixtures_catalog.md` を Stable へ格上げし、現行文書群で実装判断可能な範囲を成熟度マトリクスへ反映した
- 直前改定で混入した 640×480 / 24×24px 前提は誤りとして取り消し、32×32px・640×576 を正とした

## 2026-03-23
- 32×32px セルを前提に、固定基準解像度を 640×480 から 640×576 へ改定
- 10×18 盤面が 320×576px で収まり、右側情報欄を含めて 640px 幅内へ収まるよう描画・契約文書を更新
- コア 10 文書を全面レビューし、Spec-Driven / Acceptance-Driven / Diagram-Driven 観点を補強
- Game Boy 基準の不足情報として SELECT による NEXT 表示切替を要求・仕様・設計・QA へ反映
- Game Boy 基準の速度表、B-TYPE/HIGH、隠し要素の扱いを明文化
- A-TYPE 主軸 / B-TYPE 参照の境界を再整理
- T-Spin 独自拡張と Game Boy ベースラインとの差分を再整理
- 受入基準とトレーサビリティに NEXT 表示切替の縦断追跡を追加
