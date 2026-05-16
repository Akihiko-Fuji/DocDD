# 表示上限・数値上限補完仕様 / Display Limits and Numeric Bounds Specification

- 文書ID: DOC-SPC-023b
- 文書名: 表示上限・数値上限補完仕様 / Display Limits and Numeric Bounds Specification
- 最終更新日: 2026-03-24
- 対象プロジェクト: 仮称 `falling-block-puzzle`
- 目的: `23_scoring_level_spec.md` が「設計へ委譲する」とした SCORE 内部保持上限、および未定義のままだった LINES 表示上限・LEVEL 表示上限・replay の frame=0 前提状態を外部仕様として確定する。
- 関連文書:
  - `docs/02_external_spec/23_scoring_level_spec.md`
  - `docs/02_external_spec/26_save_replay_config_spec.md`
  - `docs/03_internal_design/33_data_model.md`
  - `docs/03_internal_design/35_rendering_design.md`

---

## 1. 本書の目的

以下の 3 項目は `23_scoring_level_spec.md` または `26_save_replay_config_spec.md` で「設計へ委譲」または「未記載」となっており、renderer の数値パネル設計・replay サンプルの読解・内部 score 保持判断に影響する。本書はこれらを外部仕様として確定する。

1. SCORE の内部保持値の扱い（上限キャップか否か）
2. LINES および LEVEL の表示最大桁数
3. replay 記録の基点となる frame=0 の意味

---

## 2. SCORE の内部保持値上限

### 2.1 方針

`23_scoring_level_spec.md` §6 では「表示上限は 999,999 とする。内部保持値を上限以上まで持つかどうかは設計へ委譲する」と定めている。

本書では以下の通り確定する。

| 項目 | 決定値 |
|---|---|
| 表示上限 | 999,999（`23_scoring_level_spec.md` §6 から継承）|
| 内部保持上限 | **999,999 でキャップ**（内部値も上限で固定する）|
| 根拠 | Game Boy 版の SCORE は 6 桁整数であり、999,999 を超えるとカウンタが意図しない状態になる。本プロジェクトでもこの上限を内部まで一貫させることで replay 再現性を保つ。|

### 2.2 実装への影響

- `scoring_service.apply_score` はスコア計算後、999,999 を超えていれば 999,999 へ丸めてから `ScoreState` へ書き込む
- replay 再現においてスコア計算結果は常に同一となり、内部値が異なることによる再現失敗を防ぐ

---

## 3. LINES 表示上限

### 3.1 A-TYPE における LINES

A-TYPE ではゲームオーバーまで累計消去ライン数を表示し続ける。理論上の上限はないが、renderer の数値パネル設計のために表示桁数を確定する。

| 項目 | 決定値 |
|---|---|
| LINES 表示最大桁数 | **3 桁（最大 999）** |
| 表示上限値 | **999** |
| 表示オーバー時 | `999` 表示で固定してよい |
| 根拠 | Game Boy 版は LINES が 3 桁表示（最大 999）。3 桁を超えるプレイは本プロジェクトの対象想定外とする。|

### 3.2 内部保持値

- LINES の内部保持値は 999 でキャップしてよい
- レベル進行の閾値計算（`23_scoring_level_spec.md` §7.2）は LINES 内部値に依存するが、Level 上限が 20（100〜200 ライン程度で到達）のため、999 キャップはレベル計算に影響しない

---

## 4. LEVEL 表示上限

### 4.1 確定値

Level は `23_scoring_level_spec.md` §7.2 で「上限は 20」と定められており、表示もこれに従う。

| 項目 | 決定値 |
|---|---|
| LEVEL 最大値 | **20**（`23_scoring_level_spec.md` §7.2 から継承）|
| LEVEL 表示桁数 | **2 桁（最大 20）** |
| 表示オーバー | 発生しない（上限 20 のため）|

### 4.2 renderer パネル設計への指示

`35_rendering_design.md` §3.2 の `level_panel` は 2 桁分の数値描画領域で十分である。

---

## 5. 数値パネル桁数まとめ

| 値 | 表示最大桁数 | 上限値 | 上限超過時 |
|---|---:|---|---|
| SCORE | 6 桁 | 999,999 | `999999` 固定 |
| LINES | 3 桁 | 999 | `999` 固定 |
| LEVEL | 2 桁 | 20 | 発生しない |

---

## 6. replay の frame=0 前提状態

### 6.1 問題の背景

`replay_sample_01.json` の最初のレコードが `{ "frame": 0, "buttons": ["START"] }` となっているが、ゲームはタイトル画面（ST-TITLE）から始まり、frame=0 でどの状態が有効かが不明確だった。

### 6.2 確定方針

replay の frame 番号は**ゲームセッション（`GameSession`）が生成された時点を frame=0** とする。

| 項目 | 確定内容 |
|---|---|
| frame=0 の定義 | `GameSession` 生成直後の最初のフレーム |
| frame=0 時の前提状態 | `ST-TITLE` ではなく、**`ST-PLAY` の `PL-SPAWN` 直前**を起点とする |
| 根拠 | replay は「セッション内の入力列」であり、タイトル画面のナビゲーションを記録する責務を持たない。`start_level` と `randomizer_seed` が replay に含まれるのはこのため。|

### 6.3 `replay_sample_01.json` の読み方

```json
{ "frame": 0, "buttons": ["START"] }
```

このレコードは「セッション開始直後の frame=0 で START が入力された」ことを意味する。  
ゲームセッションは `start_level` と `randomizer_seed` を参照して開始準備が済んだ状態であり、START は「プレイ開始確定」ではなく「最初のフレームで START が押された」という記録として扱う。

実際の再生では、この入力は `32_state_machine_design.md` §9 の入力有効範囲に従い処理される。

### 6.4 replay 記録スコープ

replay が記録する範囲は以下の通り。

| 記録対象 | 説明 |
|---|---|
| 含む | GameSession の `PL-SPAWN` 以降のプレイ中入力すべて |
| 含む | 一時停止・再開に使った START 入力 |
| 含まない | タイトル画面・開始設定画面でのナビゲーション入力 |
| 含まない | ゲームオーバー後の再試行・タイトル復帰入力 |

---

## 7. Spec-Driven / Acceptance-Driven 観点

1. SCORE・LINES・LEVEL の表示上限と桁数が renderer 実装判断なしに決定できること
2. SCORE 内部保持値のキャップが replay 再現性の一部として機能すること
3. replay の frame=0 がどの状態を指すかが、このドキュメントだけで追跡できること
4. `35_rendering_design.md` の数値パネル設計がこの桁数定義と矛盾しないこと

---

## 8. 変更履歴

- 2026-03-24: 新規作成。`23_scoring_level_spec.md` の委譲項目（SCORE 内部上限）と未定義項目（LINES・LEVEL 桁数、replay frame=0 前提）を確定
