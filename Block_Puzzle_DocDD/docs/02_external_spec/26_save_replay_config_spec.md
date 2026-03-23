# 保存・リプレイ・設定仕様 / Save, Replay, Config Specification

- 文書ID: DOC-SPC-026
- 最終更新日: 2026-03-23
- 関連文書:
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/34_module_design.md`
  - `specs/schemas/config_schema.json`
  - `specs/schemas/replay_schema.json`
  - `specs/examples/config_sample_01.yaml`
  - `specs/examples/replay_sample_01.json`

## 1. 方針
本プロジェクトでは保存・リプレイは将来拡張とする。ただし、再現性と設定既定値の説明責務を満たすため、**予約仕様として最低限の構造を固定**する。

## 2. Config 予約仕様
- `version`: 形式バージョン
- `start_level`: 既定開始レベル
- `keymap`: 論理入力と物理キーの対応
- `randomizer_seed`: テストや再現確認に用いる任意 seed

### 2.1 既定値
- `start_level` の既定値は `0`
- `keymap` の既定割当は `22_input_operation_spec.md` に準拠する
- `randomizer_seed` 未指定時は通常疑似乱数でよい

## 3. Replay 予約仕様
- `version`: 形式バージョン
- `start_level`: セッション開始条件
- `randomizer_seed`: 出現列再現用 seed
- `inputs`: frame ごとの入力列

## 4. スキーマとサンプル
- JSON Schema は `specs/schemas/*.json` を正本とする
- サンプルは `specs/examples/*` を参照する
- 将来拡張で項目を増やす場合も、既存必須項目は互換性観点で維持する

## 5. Acceptance-Driven 受入観点
- 設定未保存でも既定値で開始できること
- 同一 replay 条件で同一入力列を再現しやすい予約形式になっていること
- schema と sample が空でなく、予約仕様として読めること
