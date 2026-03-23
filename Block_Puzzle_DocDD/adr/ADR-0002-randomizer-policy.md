# ADR-0002: ピース出現順方針 / Randomizer Policy

- ADR-ID: ADR-0002
- 最終更新日: 2026-03-23
- 状態: Accepted
- 目的: Game Boy 版を主要参照元とするピース出現順の扱いを固定し、再現性とテスト可能性を確保する
- 関連文書:
  - `docs/02_external_spec/20_game_rules_spec.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/02_external_spec/26_save_replay_config_spec.md`

## 1. 決定
初期実装では **Game Boy 版系の偏りを持つ疑似乱数ベース randomizer** を採用する。

- 7-bag は採用しない
- NEXT 1 個前提で、直近ピースとの関係を考慮する疑似乱数方式とする
- 同一 seed と同一入力列では同一出現列を再現できなければならない
- 実装詳細は `spawn_service` と `config/replay` 仕様へ落とし込む

## 2. 理由
- README と基準差分文書で掲げた Game Boy 版基準に整合する
- modern guideline 系 7-bag を避けることで参照元との差分が明確になる
- seed を固定すれば再現性要求を満たしやすい

## 3. 外部仕様上の固定事項
- 出現するピース種は I, O, T, J, L, S, Z の 7 種のみ
- NEXT は 1 個表示
- 出現列は完全均等分布を保証しない
- ただし同一 piece が極端に連続することを減らす再抽選を許容する

## 4. 影響
- `20_game_rules_spec.md` に 7-bag 非採用と seed 再現性を追記する
- `26_save_replay_config_spec.md` に `randomizer_seed` を予約項目として追加する
- `34_module_design.md` の `spawn_service` 契約に seed 入力を追加する

## 5. 未決としない事項
本 ADR により randomizer 方針は未決事項から外す。実装差し替え時は ADR 更新を必須とする。

## 6. 変更履歴
- 2026-03-23: Game Boy 版基準の randomizer 方針を固定
