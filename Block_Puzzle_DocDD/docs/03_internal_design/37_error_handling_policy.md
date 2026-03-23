# エラーハンドリング方針 / Error Handling Policy

- 文書ID: DOC-DSN-037
- 最終更新日: 2026-03-24
- 関連文書:
  - `docs/00_overview/05_document_maturity_matrix.md`
  - `docs/01_requirements/14_non_functional_requirements.md`
  - `docs/02_external_spec/26_save_replay_config_spec.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/34_module_design.md`
  - `docs/03_internal_design/39_interface_contract.md`

## 1. 目的
想定内不整合や設定不備が発生した場合の扱いを定義し、進行不能や silent failure を防ぐ。本書は「どの異常をどの層がどう処理するか」を決める設計文書であり、個別モジュールの API 仕様そのものは `39_interface_contract.md` へ委譲する。

## 2. 基本方針

1. 想定内不整合は、継続可能なら安全側へ正規化して継続する
2. 継続不能な内部矛盾は、黙殺せず検出可能にする
3. replay / config の外部入力は部分適用よりも全体検証を優先する
4. UI は可能な限り破綻しない表示を維持しつつ、異常を隠蔽しすぎない
5. エラー処理責務は input / state / rule / persistence / rendering に分離する

## 3. 異常分類

| 区分 | 例 | 基本対応 | 主責務層 |
|---|---|---|---|
| 設定値異常 | `start_level` 範囲外、未知キー割当 | 既定値または正規化値へフォールバック | input / persistence |
| replay 異常 | schema 不一致、frame 逆行、未知 version | 読込拒否し、再生開始しない | persistence |
| 状態遷移異常 | `ST-PAUSE` 中にプレイ更新要求が来る | 遷移拒否し、検出可能にする | state |
| ルール整合性異常 | T-Spin 判定前提不一致、盤面外セル生成 | 開発時 assertion またはエラー記録 | gameplay |
| 描画入力異常 | 必須表示データ欠落、状態と overlay の不整合 | 破綻しない代替表示へ退避しつつ検出 | rendering |

## 4. 層別責務

### 4.1 Input / Config 層
- `config.ini` の欠落、未知項目、範囲外値を検出する
- 継続可能な場合は既定値へ正規化する
- 正規化結果は `Config` として下流へ渡し、生の曖昧入力を残さない

### 4.2 State 層
- 現状態で許可されない入力や遷移要求を遮断する
- pause/resume や game over でプレイ更新を誤って通さない
- 状態遷移表に存在しない分岐は検出可能にする

### 4.3 Gameplay 層
- 盤面境界、衝突、固定、得点更新の整合性を守る
- 回転失敗時に current piece を部分更新しない
- T-Spin 不成立はエラーではなく、正常な非成立結果として扱う

### 4.4 Persistence 層
- replay は開始前に全体検証し、途中まで再生して黙って止めない
- 非対応 version は明示的に失敗扱いとする
- Config / replay の正本が schema か仕様書かを文書で追跡できるようにする

### 4.5 Rendering 層
- score/lines/level の一部欠落時は空欄やプレースホルダより、最後に確定している安全値の表示を優先してよい
- ただし renderer は自らルール計算を補完してはならない
- pause / game over overlay と state の不一致は検出可能にする

## 5. 異常別対応ルール

### 5.1 Config 読込失敗
- INI 構文不正、必須項目欠落、範囲外値、重複割当を検出対象とする
- 不正 Config は部分適用せず、既定値で起動する
- 読込失敗はログまたは UI で確認可能であることが望ましい

### 5.2 Replay 読込失敗
- schema 不一致、未知 version、`frame` 逆行、未知ボタン名は失敗とする
- replay は開始前検証で失敗とし、途中停止挙動は採らない
- 失敗 replay を通常入力経路へ流さない

### 5.3 入力異常
- 未知論理入力は無効として破棄する
- `START + 他入力` はエラーではなく、優先規則に従う正常系として扱う
- `Left + Right`, `A + B` もエラーではなく、仕様化された相殺 / 不成立とする

### 5.4 状態遷移異常
- `ST-PAUSE` 中のプレイ更新、`ST-GAMEOVER` 中の current piece 更新は内部異常とみなす
- 実装では assertion、診断ログ、またはテスト失敗として検出できることを優先する
- 異常検出時に壊れた状態でプレイ継続しない

### 5.5 ルール計算異常
- 盤面外セル生成、負の lines、定義外レベルなどは継続不能な内部異常である
- 開発時は早期失敗を優先し、製品モードでは検出情報を残して安全停止または安全画面復帰を選ぶ
- T-Spin 不成立、回転失敗、ラインなし固定は異常ではなく正常系であることを明記する

## 6. ログ / 検出ポリシー

- 外部入力起因の失敗は「何を拒否したか」がわかる粒度で記録する
- 内部整合性異常は「どの状態・どの frame・どの session で起きたか」を追跡可能にする
- ただし通常プレイヤー向け UI に詳細診断を過剰露出する必要はない

## 7. 受入観点

- NFR-301, NFR-302, NFR-303, NFR-304 と追跡できること
- Config / replay / 状態遷移 / ルール / 描画の異常責務分担が読めること
- 正常な非成立ケースと、本当に異常なケースが区別されていること
- `34_module_design.md` および `39_interface_contract.md` と矛盾しないこと
