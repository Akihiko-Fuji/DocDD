# ADR-0003: 入力バッファ方針 / Input Buffer Policy

- ADR-ID: ADR-0003
- 最終更新日: 2026-03-23
- 状態: Accepted
- 目的: 入力競合時の解釈順と pause 再開直後のバッファ扱いを固定し、仕様ブレを防ぐ
- 関連文書:
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/03_internal_design/32_state_machine_design.md`
  - `docs/03_internal_design/36_input_timing_design.md`
  - `docs/04_quality_assurance/43_test_cases_edge_conditions.md`

## 1. 決定
- 入力は frame ごとに `InputSnapshot` として取得する
- 同一 frame で `START` とプレイ操作が競合した場合は `START` を優先する
- `Left + Right` は相殺、`A + B` は両方無効とする
- 再開直後は、同一押下継続による連続 pause を防ぐため `START` を 1 frame 再評価しない

## 2. 理由
- UI / 状態遷移 / TC を一貫させやすい
- pause トグル暴発を避けられる
- Game Boy 系の単純な入力モデルを維持しやすい

## 3. 影響
- `22_input_operation_spec.md` と `36_input_timing_design.md` の優先順記述はこの ADR を正本とする
- `42_test_cases_ui_input.md` と `43_test_cases_edge_conditions.md` に同時押下系ケースを接続する

## 4. 非採用
- 入力キューの多段バッファ
- 予約回転 (IRS)
- 予約ホールド

## 5. 変更履歴
- 2026-03-23: START 優先、相殺規則、pause 再開直後のバッファ抑止を採用決定
