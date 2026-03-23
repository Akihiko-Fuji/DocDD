# レビューログ / Review Log

- 文書ID: DOC-REC-062
- 最終更新日: 2026-03-23

## 1. 目的
レビューで確認した論点、指摘事項、方針反映結果を記録し、後続の再レビューで同じ論点を見失わないようにする。

## 2. 2026-03-23 コア10文書レビュー
- `00_document_map` は入口として有効だったが、今回のレビュー観点と補強対象が弱かったため、コア10文書の読み方と重点論点を追加
- `01_project_charter` はプロジェクト目的は明瞭だったが、成功条件とベースライン定義が弱かったため補強
- `11_scope_definition` は A-TYPE 主軸は読めたが、実装対象 / 参照保持 / 対象外の 3 層分離が不足していたため再編
- `13_functional_requirements` は Game Boy 固有の SELECT/NEXT 切替が要求化されていなかったため追加
- `14_non_functional_requirements` は Game Boy 基準逸脱防止、図同期、NEXT 切替安全性が薄かったため追加
- `20_game_rules_spec` は速度表、ARE、SELECT、隠し要素の扱いが暗黙だったため明文化
- `21_ui_screen_spec` は NEXT OFF 時の表示要件がなく、UI 誤認リスクがあったため補強
- `24_piece_rotation_collision_spec` は回転/移動競合と天井近傍の扱いが薄かったため補強
- `32_state_machine_design` は SELECT の責務位置が未定義だったため、UI 状態更新として責務分離した
- `40_test_strategy` は Game Boy 基準の確認観点が弱かったため、速度表・SELECT/NEXT・B-TYPE 参照を重点追加

## 3. 次回レビュー観点
- B-TYPE を実装対象へ昇格する場合の上流更新順
- replay 永続化を実装対象へ入れるタイミング
- 実装言語確定後の `34_module_design.md` の内部契約粒度妥当性
