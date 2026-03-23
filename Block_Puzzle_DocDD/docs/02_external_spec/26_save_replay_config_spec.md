# 保存・リプレイ・設定仕様 / Save, Replay, Config Specification

- 文書ID: DOC-SPC-026
- 最終更新日: 2026-03-24
- 文書ステータス: Stable（schema 正本、本文は解説と運用条件の正本）
- 関連文書:
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/02_external_spec/22_input_operation_spec.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/04_quality_assurance/40_test_strategy.md`
  - `docs/04_quality_assurance/46_test_fixtures_catalog.md`
  - `specs/schemas/config_schema.json`
  - `specs/schemas/replay_schema.json`
  - `specs/examples/config_sample_01.ini`
  - `specs/examples/replay_sample_01.json`

## 1. 方針
本プロジェクトでは保存・リプレイは将来拡張とする。ただし、再現性と設定既定値の説明責務を満たすため、**現時点で必要な構造・互換条件・失敗時挙動を正本として固定**する。将来拡張であっても、実装判断がぶれないように以下を明文化する。

- Config は「ユーザー設定と既定値の保存形式」を扱い、保存ファイル名は `config.ini` を前提とする
- Replay は「同一セッション条件を再実行するための再現形式」を扱う
- スキーマは `specs/schemas/*.json`、サンプルは `specs/examples/*` を正本補助とする
- 互換性、読込失敗、再現条件を予約段階でも定義しておく

## 2. 対象範囲
- 本書は `config.ini` による設定保存と replay 保存形式を扱う
- `config.ini` では少なくとも開始レベル、入力インターフェース、利用ボタン定義を保持する
- replay は別ファイルとして扱い、`config.ini` とは責務を分離する

## 3. Config 保存仕様
### 3.1 保存媒体と構造
- 設定ファイル名は `config.ini` とする
- `config.ini` は INI 形式とし、少なくとも `[gameplay]`, `[input]`, `[keyboard]`, `[gamepad]` を持てる構造とする
- 実装は `input_interface` の値に応じて `[keyboard]` または `[gamepad]` の割当定義を参照する

### 3.2 必須/任意項目
| セクション | 項目 | 必須 | 意味 |
|---|---|---|---|
| `[gameplay]` | `version` | 必須 | 形式バージョン |
| `[gameplay]` | `start_level` | 必須 | 既定開始レベル。0〜9 |
| `[gameplay]` | `randomizer_seed` | 任意 | テストや再現確認に用いる任意 seed |
| `[input]` | `input_interface` | 必須 | `keyboard` または `gamepad` |
| `[keyboard]` | `left/right/down/a/b/start/select` | 条件付き必須 | キーボード運用時の物理キーコード |
| `[gamepad]` | `left/right/down/a/b/start/select` | 条件付き必須 | ゲームパッド運用時の物理ボタン名 |

### 3.3 既定値
- `start_level` の既定値は `0`
- `input_interface` の既定値は `keyboard` とする
- キーボード既定割当は `22_input_operation_spec.md` に準拠する
- `randomizer_seed` 未指定時は通常疑似乱数でよい
- 読込不能時は Config 全体を破棄し、安全既定値へフォールバックする

### 3.4 保存単位
- 保存単位は**論理入力名 -> 物理キーコード/物理ボタン名**とする
- 論理入力名は `left/right/down/a/b/start/select` に固定する
- キーボード時は HID キーコード相当の文字列表現、ゲームパッド時はボタン識別子文字列を用いる
- 1 つの論理入力に対し複数入力源を同時割当する拡張は予約とし、version 1 では単一値のみを許可する

## 4. Replay 保存仕様
### 4.1 必須項目
- `version`: 形式バージョン
- `start_level`: セッション開始条件
- `randomizer_seed`: 出現列再現用 seed
- `inputs`: フレーム単位の入力列

### 4.2 replay の粒度
- replay は**入力変化時のみを記録する sparse 形式**とする
- `inputs[].frame` はセッション開始からの 0 起算フレーム番号とする
- `inputs[].buttons` はそのフレームで成立した論理入力集合とする
- 入力変化がないフレームは記録不要とし、再生時は直前フレームとの差分ではなく「そのフレームで発生した押下イベント」として扱う
- 同一フレームで複数入力がある場合は 1 レコード内の配列で表現する

### 4.3 再現条件
同一 replay から同一結果を再現するには、少なくとも以下が一致している必要がある。

1. `version`
2. `start_level`
3. `randomizer_seed`
4. `inputs`
5. `22_input_operation_spec.md` と `36_input_timing_design.md` に定義された入力解釈規則
6. `23_scoring_level_spec.md` の速度表と `24_piece_rotation_collision_spec.md` の回転/衝突規則

したがって、**seed が一致するだけでは十分ではない**。開始条件と入力解釈規則も固定されている必要がある。

## 5. version 方針
### 5.1 version の扱い
- version 1 を初版とする
- マイナーな任意項目追加は、旧読込系が未知項目を無視できる場合のみ許可する
- 必須項目追加、既存項目の意味変更、入力解釈変更は新 version とする

## 6. 互換性方針
### 6.1 後方互換
- 実装初期段階では**同一 major version のみ読込保証**とする
- 旧 version を読めない場合は明示的に読込失敗として扱い、黙って部分適用しない
- version 非対応時は、どの項目が非対応なのかをログまたは UI で確認できることが望ましい

## 7. load failure 時の扱い
### 7.1 Config
- INI 構文不正、必須セクション欠落、必須項目欠落、範囲外値、物理キー/ボタン重複などがあれば不正 Config とみなす
- 不正 Config は部分適用せず、安全既定値で起動する
- 読込失敗はユーザー向け通知またはログへ残す

### 7.2 Replay
- schema 不一致、未知 version、`frame` 逆行、未知ボタン名があれば不正 Replay とみなす
- 不正 Replay は再生を開始しない
- 途中まで再生してから黙って停止する挙動は採らず、開始前検証で失敗扱いにする

## 8. schemas / examples との対応
| 外部項目 | schema / sample | 設計上の主対応型 | 備考 |
|---|---|---|---|
| Config 全体 | `config_schema.json` / `config_sample_01.ini` | `Config` | 正本は schema |
| `input_interface` / bindings | `config_schema.json#properties.input_interface`, `keyboard_bindings`, `gamepad_bindings` | `Config.input_interface`, `Config.keyboard_bindings`, `Config.gamepad_bindings` | `config.ini` の入力定義を正規化したもの |
| Replay 全体 | `replay_schema.json` / `replay_sample_01.json` | `ReplayFrame[]` を含む replay aggregate | `33_data_model.md` と同期する |
| `inputs[]` | `replay_schema.json#properties.inputs` | `ReplayFrame` | `frame` は 0 起算 |

## 9. 実装前に固定すべき判断
以下は将来拡張時に追加決定が必要な項目だが、本文で定義した保存形式・互換性・失敗時挙動自体は現時点の正本として扱う。

1. Config 保存先パスと永続化タイミング
2. Replay の出力タイミングとファイル命名規則
3. 読込失敗の UI 表示文言
4. version 上げ時の移行戦略

未決事項は `54_issue_management.md` で管理し、決定時は ADR または Decision Log に格上げする。

## 10. Acceptance-Driven 受入観点
- 設定未保存でも既定値で開始できること
- 同一 replay 条件で同一入力列を再現しやすい正本形式になっていること
- schema と sample が空でなく、本文と矛盾せず正本補助として読めること
- replay の粒度、`config.ini` の保存単位、入力インターフェース切替、読込失敗時挙動、互換性方針が本文だけで判断できること
- `33_data_model.md` と schema/sample の接続が追跡できること


## 11. 変更履歴
- 2026-03-24: `config.ini` 前提、HID キーボード主入力、ゲームパッド対応、INI ベース保存仕様を追加
