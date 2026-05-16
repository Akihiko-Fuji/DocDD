# Block_Puzzle_DocDD — Quick Start & AI プロンプト例

> **目的**  
> `Block_Puzzle_DocDD` テーマを短時間で把握し、DocDD 文書から Python 実装・テストへどう接続されるかを確認するための **Quick Start** と、AI に実装・レビューを依頼する際の **プロンプト例** をまとめたドキュメント。
>
> 本テーマでは `docs/` 配下の文書群を一次情報として扱い、
> **要求 → 仕様 → 設計 → 実装 → テスト → 変更記録**
> の接続を確認することを目的とする。
>
> 本サンプルは教育用の DocDD 見本であり、商用ゲーム製品の複製を目的としない。

---

## 目次

1. [Quick Start](#1-quick-start)  
   1.1 [この題材で何を確認するのか](#11-この題材で何を確認するのか)  
   1.2 [最初に読むファイル](#12-最初に読むファイル)  
   1.3 [最短実行手順](#13-最短実行手順)  
   1.4 [実装ファイルの構成](#14-実装ファイルの構成)  
   1.5 [テスト実行](#15-テスト実行)  
   1.6 [この題材での実装原則](#16-この題材での実装原則)  
2. [AI に渡すプロンプト例](#2-ai-に渡すプロンプト例)  
   2.1 [文書読解・実装計画作成用](#21-文書読解実装計画作成用プロンプト)  
   2.2 [ピース形状・盤面ルール実装用](#22-ピース形状盤面ルール実装用プロンプト)  
   2.3 [状態遷移・入力処理実装用](#23-状態遷移入力処理実装用プロンプト)  
   2.4 [pygame 画面実装用](#24-pygame-画面実装用プロンプト)  
   2.5 [テスト追加用](#25-テスト追加用プロンプト)  
   2.6 [ドキュメント整合性レビュー用](#26-ドキュメント整合性レビュー用プロンプト)  
3. [使い方のコツ](#3-使い方のコツ)  
4. [このファイルの位置づけ](#4-このファイルの位置づけ)

---

## 1. Quick Start

### 1.1 この題材で何を確認するのか

`Block_Puzzle_DocDD` は、落下ブロックゲームを題材にした DocDD 見本である。

目的は、ゲームそのものの完成度ではなく、以下を確認することにある。

| 観点 | 確認したいこと |
|---|---|
| 要求 | 何を実現すべきかが ID 付きで定義されているか |
| 仕様 | プレイヤーから見える挙動が文書化されているか |
| 設計 | 状態遷移・モジュール責務・データ構造へ落ちているか |
| 実装 | 文書を一次情報として Python コードへ写像できているか |
| テスト | 文書からテスト観点を導出できているか |
| 変更 | 仕様変更時に影響文書・実装・テストを追えるか |

---

### 1.2 最初に読むファイル

まずは、以下のファイルを読む。

| ファイル | 目的 |
|---|---|
| `Block_Puzzle_DocDD/readme.md` | この題材全体の目的・位置づけ・読む順番を把握する |
| `Block_Puzzle_DocDD/docs/00_overview/00_document_map.md` | 文書体系とコア文書を把握する |
| `Block_Puzzle_DocDD/docs/01_requirements/11_scope_definition.md` | 実装対象・参照保持・対象外を把握する |
| `Block_Puzzle_DocDD/docs/01_requirements/13_functional_requirements.md` | 機能要求を把握する |
| `Block_Puzzle_DocDD/docs/02_external_spec/20_game_rules_spec.md` | ゲームルールの外部仕様を把握する |
| `Block_Puzzle_DocDD/docs/02_external_spec/21_ui_screen_spec.md` | 画面と表示要素を把握する |
| `Block_Puzzle_DocDD/docs/02_external_spec/24_piece_rotation_collision_spec.md` | 回転・衝突・T-Spin 前提を把握する |
| `Block_Puzzle_DocDD/docs/02_external_spec/24a_piece_shape_spawn_spec.md` | ピース形状・出現座標の数値正本を把握する |
| `Block_Puzzle_DocDD/docs/03_internal_design/32_state_machine_design.md` | 状態遷移を把握する |
| `Block_Puzzle_DocDD/docs/03_internal_design/34_module_design.md` | モジュール責務を把握する |
| `Block_Puzzle_DocDD/docs/04_quality_assurance/40_test_strategy.md` | テスト方針を把握する |
| `Block_Puzzle_DocDD/src/DocDD_coding/README.md` | 現在の Python 実装範囲・実行方法・制限を把握する |

---

### 1.3 最短実行手順

#### Step 1 — 利用ライブラリを確認する

本題材の実行・テストには以下の Python ライブラリを利用する。

| ライブラリ | 用途 |
|---|---|
| `pygame-ce` | ゲーム画面描画、入力処理、実行ループの制御 |
| `pytest` | `tests/DocDD_coding/` 配下の自動テスト実行 |

#### Step 2 — 依存パッケージをインストールする

```bash
cd Block_Puzzle_DocDD
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Step 3 — テストを実行する

```bash
cd Block_Puzzle_DocDD
python -m pytest tests/DocDD_coding
```

#### Step 4 — 実装を起動する

```bash
cd Block_Puzzle_DocDD
python src/DocDD_coding/main.py
```

#### Step 5 — 最低限の画面遷移を確認する

| 操作 | 期待する動き |
|---|---|
| Enter | TITLE → SETUP_A |
| Left / Right | A-TYPE 開始レベル変更 |
| Enter | SETUP_A → PLAY |
| Arrow keys | ピース移動 |
| X / Z | A/B 回転 |
| Right Shift | NEXT 表示 ON/OFF |
| Enter | PLAY ↔ PAUSE |
| ESC または Z | 戻る / タイトル復帰 |

---

### 1.4 実装ファイルの構成

```text
Block_Puzzle_DocDD/
├── requirements.txt
├── src/
│   └── DocDD_coding/
│       ├── README.md
│       ├── main.py
│       └── falling_block_puzzle/
│           ├── constants.py
│           ├── models.py
│           ├── pieces.py
│           ├── randomizer.py
│           ├── board_rules.py
│           ├── active_piece_service.py
│           ├── tspin_detector.py
│           ├── scoring_service.py
│           ├── level_progression_service.py
│           ├── game_session.py
│           ├── state_controller.py
│           ├── input_mapper.py
│           ├── renderer.py
│           └── app.py
└── tests/
    └── DocDD_coding/
```

---

### 1.5 テスト実行

テストは `tests/DocDD_coding/` 配下に配置する。

主な確認観点は以下である。

| テスト観点 | 対応する文書 |
|---|---|
| ピース形状・出現座標 | `DOC-SPC-024a` |
| 盤面内・盤面外・衝突判定 | `DOC-SPC-024` |
| ライン検出・ライン消去 | `DOC-SPC-020` |
| 回転成立・回転失敗 | `DOC-SPC-024` |
| T-Spin 判定 | `DOC-SPC-024`, `DOC-SPC-024a` |
| 得点・レベル進行 | `DOC-SPC-023` |
| 状態遷移 | `DOC-DSN-032` |
| 非採用機能の不在 | `DOC-REQ-011`, `DOC-SPC-020` |

---

### 1.6 この題材での実装原則

| 原則 | 内容 |
|---|---|
| 文書を一次情報にする | コード都合で仕様を決めない |
| `src/DocDD_coding/` を正本実装にする | `src/vibe_coding/` は比較用として扱う |
| 責務を分ける | 入力、状態、盤面ルール、得点、描画を分離する |
| pygame 依存を閉じ込める | ロジックテストで pygame 起動を不要にする |
| 非採用機能を勝手に足さない | Hold / Hard drop / Ghost / 7-bag などは追加しない |
| 仕様補完は明示する | 文書に未定義の補完は README やコメントに残す |
| テストは文書由来にする | 実装都合ではなく、要求・仕様・設計から導出する |

---

## 2. AI に渡すプロンプト例

### 2.1 文書読解・実装計画作成用プロンプト

```text
あなたは DocDD に基づいて実装計画を作成する coding agent です。

`Block_Puzzle_DocDD/docs/` 配下の文書を一次情報として読み、
`src/DocDD_coding/` に実装すべき Python コードの構成案を作成してください。

## 必ず読む文書

- `Block_Puzzle_DocDD/readme.md`
- `docs/00_overview/00_document_map.md`
- `docs/01_requirements/11_scope_definition.md`
- `docs/01_requirements/13_functional_requirements.md`
- `docs/02_external_spec/20_game_rules_spec.md`
- `docs/02_external_spec/21_ui_screen_spec.md`
- `docs/02_external_spec/22_input_operation_spec.md`
- `docs/02_external_spec/23_scoring_level_spec.md`
- `docs/02_external_spec/24_piece_rotation_collision_spec.md`
- `docs/02_external_spec/24a_piece_shape_spawn_spec.md`
- `docs/03_internal_design/32_state_machine_design.md`
- `docs/03_internal_design/34_module_design.md`
- `docs/04_quality_assurance/40_test_strategy.md`

## 出力してほしいもの

- 実装対象範囲
- 実装しない範囲
- モジュール構成案
- テスト構成案
- 文書とコードの対応表
- 仕様が曖昧または未定義に見える箇所
- 実装時の注意点

## 重要ルール

- 文書にない機能を勝手に追加しない
- `src/vibe_coding/` は比較用として扱い、正本実装にしない
- ゲームとしての完成度より、DocDD教材としての追跡性を優先する
```

---

### 2.2 ピース形状・盤面ルール実装用プロンプト

```text
あなたは Python で落下ブロックゲームのルールロジックを実装するエンジニアです。

`DOC-SPC-024a` と `DOC-SPC-024` を一次情報として、
ピース形状、出現座標、盤面判定、ライン消去を実装してください。

## 作成対象

- `src/DocDD_coding/falling_block_puzzle/pieces.py`
- `src/DocDD_coding/falling_block_puzzle/board_rules.py`
- 対応する pytest

## 必須要件

- 盤面は 10×18
- I/O/T/J/L/S/Z の 7 種
- rotation は 0,1,2,3
- 出現時 rotation は 0
- 出現 origin は `24a_piece_shape_spawn_spec.md` に従う
- occupied_offsets は `24a_piece_shape_spawn_spec.md` に従う
- 有効位置は盤面内かつ固定済みブロックと重ならない位置
- wall kick / floor kick は実装しない
- ライン完成判定とライン消去を実装する
- ロジックは pygame に依存させない

## テスト

- 全ピース・全 rotation の offsets が存在する
- 出現セルが文書と一致する
- O ピースは全 rotation で形状が同一
- 盤面外は invalid
- 固定済みブロックとの衝突は invalid
- 1〜4 ライン消去ができる
```

---

### 2.3 状態遷移・入力処理実装用プロンプト

```text
あなたは Python でゲーム状態遷移と入力処理を実装するエンジニアです。

`DOC-DSN-032 State Machine Design` と `DOC-SPC-022 Input Operation Specification` を一次情報として、
状態遷移と入力マッピングを実装してください。

## 作成対象

- `src/DocDD_coding/falling_block_puzzle/models.py`
- `src/DocDD_coding/falling_block_puzzle/state_controller.py`
- `src/DocDD_coding/falling_block_puzzle/input_mapper.py`
- 対応する pytest

## 必須状態

- TITLE
- SETUP_A
- PLAY
- PAUSE
- GAMEOVER

## 必須入力

- Left
- Right
- Down
- A
- B
- START
- SELECT
- Back

## 入力優先順

1. START
2. SELECT
3. 回転
4. 左右
5. Down
6. 自動落下

## 必須要件

- TITLE で START → SETUP_A
- SETUP_A で START → PLAY
- PLAY で START → PAUSE
- PAUSE で START → PLAY
- PLAY で gameover → GAMEOVER
- GAMEOVER で retry/start → SETUP_A
- SELECT は PLAY 中だけ NEXT 表示切替
- PAUSE / GAMEOVER 中は通常プレイ入力を反映しない
- Hard drop / Hold 入力は定義しない
```

---

### 2.4 pygame 画面実装用プロンプト

```text
あなたは pygame-ce で簡易ゲーム画面を実装するエンジニアです。

`DOC-SPC-021 UI Screen Specification` と `DOC-DSN-035 Rendering Design` を一次情報として、
`src/DocDD_coding/` 配下の実装を起動できるようにしてください。

## 作成対象

- `src/DocDD_coding/main.py`
- `src/DocDD_coding/falling_block_puzzle/app.py`
- `src/DocDD_coding/falling_block_puzzle/renderer.py`

## 必須要件

- 640×576 のウィンドウを開く
- TITLE / SETUP_A / PLAY / PAUSE / GAMEOVER を表示する
- 10×18 盤面を描画する
- 現在ピースと固定済みブロックを描画する
- SCORE / LINES / LEVEL / NEXT を表示する
- SELECT による NEXT ON/OFF を表示に反映する
- PAUSE / GAME OVER 表示を行う
- 画像アセットがない場合も矩形と標準フォントでフォールバック表示する
- 外部著作物・商用ゲーム由来素材を追加しない
- ロジック層を pygame に依存させない
```

---

### 2.5 テスト追加用プロンプト

```text
あなたは DocDD 文書からテストを導出するテストエンジニアです。

`Block_Puzzle_DocDD/docs/04_quality_assurance/40_test_strategy.md`、
`41_test_cases_game_rules.md`、
`42_test_cases_ui_input.md`、
`43_test_cases_edge_conditions.md` を一次情報として、
`tests/DocDD_coding/` に pytest を追加してください。

## 必須テスト観点

- ピース形状・出現座標
- 盤面内・盤面外判定
- 固定済みブロック衝突
- ライン完成判定
- ライン消去
- 回転成立・失敗
- wall kick / floor kick が行われないこと
- T-Spin 成立 / 不成立
- T-Spin 0 line
- 通常得点
- T-Spin 得点
- レベル進行
- SELECT による NEXT 表示切替
- START 優先
- PAUSE 中入力無効
- GAMEOVER 中入力無効
- Hard drop / Hold / Ghost / 7-bag が存在しないこと

## 重要ルール

- pygame 画面を起動しなくてもテストできる構成にする
- 実装都合ではなく文書由来の観点としてテスト名を付ける
- 必要に応じて、テストコメントに参照文書IDを記載する
```

---

### 2.6 ドキュメント整合性レビュー用プロンプト

```text
あなたは DocDD リポジトリのレビュー担当者です。

`Block_Puzzle_DocDD/docs/` と `src/DocDD_coding/` を読み、
文書・実装・テストの整合性をレビューしてください。

## 確認したいこと

- README の説明と実装状態が一致しているか
- scope definition と実装範囲が一致しているか
- 実装対象外の機能が混入していないか
- ピース形状・出現座標が `DOC-SPC-024a` と一致しているか
- 状態遷移が `DOC-DSN-032` と一致しているか
- モジュール責務が `DOC-DSN-034` と大きくズレていないか
- テストが `DOC-QA-040` の方針に沿っているか
- README に記載すべき implementation note が漏れていないか

## 出力形式

- P0: すぐ直すべき重大不整合
- P1: 公開前に直した方がよい不整合
- P2: 改善するとよい点
- Good: 良い点

各指摘には、該当ファイル、理由、修正案を含めてください。
```

---

## 3. 使い方のコツ

1. **最初に文書を読む**  
   `readme.md` と `00_document_map.md` で全体像を確認する。

2. **コードだけを先に見ない**  
   この題材の主目的は、コードそのものではなく、文書からコードへどう写像されるかを見ることにある。

3. **`src/vibe_coding/` と比較する**  
   短い依頼で生成したコードと、DocDD文書を一次情報にした実装の違いを見る。

4. **テストを見る**  
   テストが実装都合ではなく、文書由来の確認観点になっているかを見る。

5. **変更時の波及を見る**  
   ルール変更やT-Spin変更が、どの仕様・設計・テストに影響するかを確認する。

---

## 4. このファイルの位置づけ

本ファイルは、`Block_Puzzle_DocDD/readme.md` を補助する **実装確認・AI橋渡し用ガイド** である。

| ドキュメント | 役割 |
|---|---|
| `readme.md` | 題材全体の目的・文書体系・DocDD上の位置づけを説明する |
| `quickstart.md` | 最短で読み、動かし、AIに作業依頼するための入口 |
| `src/DocDD_coding/README.md` | 実装済み範囲・実行方法・制限を説明する |
| `docs/` | 要求・仕様・設計・試験・記録の一次情報 |
| `src/DocDD_coding/` | DocDD文書に基づく正本実装 |
| `src/vibe_coding/` | 比較用のバイブコーディング成果物 |

DocDD の観点では、`docs/` を一次情報、`src/DocDD_coding/` を文書から導出された実装例、本ファイルを **人間とAIが最短で流れを把握するための橋渡し** として位置づける。