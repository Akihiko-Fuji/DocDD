# Falling Block Puzzle DocDD Sample

本ディレクトリは、**Document-Driven Development（DocDD）の解説用見本**として、テトリス系落下ブロックゲームを題材に文書体系を整備したサンプルです。

本リポジトリの主目的は、ゲーム実装そのものの巧拙ではなく、**要求・仕様・設計・試験・記録がどのように接続されるかを説明できる状態を保つこと**です。

ここでいう DocDD の価値は「完全な言語非依存」をうたうことではなく、**特定の実装言語へ文書が過度に引きずられないこと**、および **仕様・設計を Python / C# / Java / C++ / Rust / Kotlin など複数言語へ落とし込める契約として記述すること**にあります。

---

## 1. このリポジトリの目的

本サンプルは、以下を GitHub 上でひと目で把握できるようにすることを目的とします。

- このリポジトリが何の見本なのか
- どの文書から読めば DocDD の流れを理解しやすいか
- Game Boy 準拠部分と独自拡張部分が何か
- コア 10 文書がどこにあるか
- 実装はどの段階か、何が未着手か

---

## 2. 現在の到達点

### 2.1 完成しているもの
- DocDD のコア 10 文書を含む文書骨格
- A-TYPE 主軸の要求・外部仕様・内部設計・試験方針
- T-Spin 採用を含む変更記録・決定記録
- 上流から下流へ辿るためのトレーサビリティ文書

### 2.2 これから行うもの
- 実装基盤の最終確定
- 文書に従った実装着手（実装言語を問わず契約から着手可能な状態の維持）
- テストケースの実行記録蓄積
- B-TYPE 参考仕様の必要に応じた具体化
- replay / config の永続化実装
- 実施記録と将来拡張差分を継続的に蓄積すること

### 2.3 実装ステータス
**実装は未着手、または本格着手前の文書整備フェーズ**です。現時点では、コード完成物を示すリポジトリではなく、DocDD の見本として文書体系を先に成立させる段階にあります。

ただし、`docs/` 配下は `00_overview` から `06_records` まで一式が揃っており、内部設計も `30〜38`、品質保証も `40〜45`、プロジェクト管理も `50〜55` が並んでいます。したがって現段階は「骨格不足」ではなく、**主要な内部契約・保存仕様・試験仕様まで含めて実装判断可能な文書群を揃え、実施記録と将来拡張差分を積み上げる段階**と位置付けます。

### 2.4 コード成果物ディレクトリ方針
- DocDD に基づいて制作するコード成果物は `src/DocDD_coding/` に配置する。
- `src/vibe_coding/vibe_code_tetris.py` は、短いリクエストを入力として生成した**比較用のバイブコーディング成果物**であり、DocDD 正本実装ではない。
- さらに同ファイルは、**DocDD に基づかない実装では SHAPES 定義と文書座標系のズレが生じうる**ことを示す教材として保持する。
- したがって、仕様適合や受入判定の根拠は `docs/` 群および `src/DocDD_coding/` を優先し、`src/vibe_coding/` は比較・検討用途として扱う。

---

## 3. 題材の前提

このサンプルでは、題材としてテトリス系ゲームを用いますが、商用製品の複製を目的としません。

### 3.1 Game Boy 準拠の主な要素
- 十字キー + A/B + SELECT + START の論理入力
- A-TYPE を主軸とする整理
- 10×18 盤面
- NEXT 1 個
- Hold なし
- Hard drop なし
- シンプルな画面構成
- 想定描画解像度 640×576（32×32px の 10×18 盤面を収める固定基準解像度）
- ゲーム中フォントは Early GameBoy を採用候補とし、TTF を実行時に直接読むのではなく 32×32 の PNG グリフへ変換した素材として利用する

### 3.2 本サンプルでの独自整理・拡張
- HID キーボード（標準入力）を主入力としつつ、ゲームパッド対応を前提に論理ボタンへ写像する
- `config.ini` による入力インターフェースとボタン割当の切替を明文化
- T-Spin を独自拡張として採用
- B-TYPE は参考仕様として保持するが初期実装必須から外す
- DocDD の解説に必要なトレーサビリティ、記録、変更波及例を文書化

差分の一覧は `docs/00_overview/04_reference_baseline_and_deltas.md` を参照してください。

---

## 4. 読む順番

### 4.1 最短ルート
1. `docs/00_overview/00_document_map.md`
2. `docs/00_overview/01_project_charter.md`
3. `docs/01_requirements/11_scope_definition.md`
4. `docs/01_requirements/16_traceability_matrix.md`
5. `docs/03_internal_design/34_module_design.md`
6. `docs/04_quality_assurance/40_test_strategy.md`
7. `docs/06_records/64_change_case_tspin_adoption.md`

### 4.2 文書体系を順に読むルート
1. Overview
2. Requirements
3. External Specification
4. Internal Design
5. Quality Assurance
6. Records

---

## 5. コア 10 文書

本サンプルでは、以下を **DocDD 骨格を支えるコア 10 文書**として扱います。

1. `docs/00_overview/00_document_map.md`
2. `docs/00_overview/01_project_charter.md`
3. `docs/01_requirements/11_scope_definition.md`
4. `docs/01_requirements/13_functional_requirements.md`
5. `docs/01_requirements/14_non_functional_requirements.md`
6. `docs/02_external_spec/20_game_rules_spec.md`
7. `docs/02_external_spec/21_ui_screen_spec.md`
8. `docs/02_external_spec/24_piece_rotation_collision_spec.md`
9. `docs/03_internal_design/32_state_machine_design.md`
10. `docs/04_quality_assurance/40_test_strategy.md`

この 10 文書を起点に、追加文書で詳細化・補助・記録を行います。

---

## 5.1 文書の読み手

本サンプルの文書は、**人間のレビュー担当者**と**AI による支援・評価系エージェント**の双方が読んで理解できることを意図しています。

そのため、以下を重視します。

- 文書の役割を明確に分ける
- 用語を固定する
- 参照元と独自拡張を分離する
- 曖昧な箇所は未決事項として残すか、主要参照元に基づき補完方針を明記する

### 5.2 不明瞭な箇所の補完方針

Game Boy 版由来の操作感やルールのうち、文書化時点で判断が不足する箇所は、**Game Boy 版テトリスを主要参照元のひとつとして補完**します。

ただし、単に暗黙前提として実装へ押し込むのではなく、補完した場合は以下のいずれかへ反映する方針とします。

- `11_scope_definition.md`
- `20_game_rules_spec.md`
- `22_input_operation_spec.md`
- `24_piece_rotation_collision_spec.md`
- `60_decision_log.md`

---

## 6. DocDD として見てほしいポイント

- **入口**: README から文書地図へ到達できること
- **役割分離**: 要求・仕様・設計・試験が混ざっていないこと
- **実装接続性**: 文書中の契約記述が Python を含む実装例の一つに閉じず、Python / C# / Java / C++ / Rust / Kotlin へ写像しやすいこと
- **追跡性**: BR → UC → DM → SR/NSR → EXT → Internal Contract → TC を辿れること
- **変更管理**: T-Spin 採用のような変更がどの文書へ波及したか確認できること
- **受入/完了**: プロダクト受入、文書完了、追跡完了を分けて説明していること

---

## 7. 主な参照先

- 文書地図: `docs/00_overview/00_document_map.md`
- 基準差分: `docs/00_overview/04_reference_baseline_and_deltas.md`
- スコープ: `docs/01_requirements/11_scope_definition.md`
- 追跡表: `docs/01_requirements/16_traceability_matrix.md`
- 内部契約: `docs/03_internal_design/34_module_design.md`
- 試験方針: `docs/04_quality_assurance/40_test_strategy.md`
- 変更見本: `docs/06_records/64_change_case_tspin_adoption.md`
