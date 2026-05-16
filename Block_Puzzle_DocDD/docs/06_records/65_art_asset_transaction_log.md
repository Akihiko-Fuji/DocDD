# アート資産トランザクション記録 / Art Asset Transaction Log

- 文書ID: DOC-REC-065
- 最終更新日: 2026-04-16
- 目的: `art/fontset` と `art/artwork` の現物資産を、実装作業に接続するための進捗トランザクションとして記録する
- 性質: 本書は設計文書ではなく、作業進捗と不足項目を管理するための記録文書である
- 関連文書:
  - `docs/02_external_spec/21_ui_screen_spec.md`
  - `docs/02_external_spec/27_image_asset_data_spec.md`

---

## 1. 運用ルール

1. 本書は「素材の有無」「利用予定」「不足項目」の更新履歴を管理する
2. 仕様や責務境界の定義は `docs/02_external_spec/27_image_asset_data_spec.md` を正本とし、本書は実務トラッキングに限定する
3. 素材追加時は、該当行の `状態` を更新し、必要に応じて不足一覧から除外する

---

## 2. 現在の素材棚卸し（2026-04-16）

### 2.1 fontset（文字グリフ）

| 区分 | 内容 | 状態 |
|---|---|---|
| 英大文字 | `A`〜`Z` | 利用可 |
| 数字 | `0`〜`9` | 利用可 |
| 記号 | `!` (`ex.png`), `?` (`qs.png`) | 利用可 |
| 元データ | `_photoshop.psd` | 参照可 |

### 2.2 artwork（画面・装飾）

| ファイル | 想定用途 | 状態 |
|---|---|---|
| `puzzle.png` / `puzzle-menu.png` | タイトル/メニュー候補背景 | 利用可 |
| `wall.png` / `sidewall.png` / `sidebar.png` | プレイ画面フレーム候補 | 利用可 |
| `brick1.png`〜`brick6.png` | ブロック/タイル素材候補 | 利用可 |
| `brick5center.png` / `brick5end.png` | 接続部表現候補 | 利用可 |
| `angleI.png` / `angle-.png` / `angle1.jpg`〜`angle4.jpg` | コーナー装飾候補 | 要選定 |

---

## 3. ゲーム画面開発で使用する文字と不足一覧

`21_ui_screen_spec.md` の現行表示文言（例: `A-TYPE`, `SCORE`, `LINES`, `LEVEL`, `NEXT OFF`, `T-SPIN`, `PAUSE`, `GAME OVER`）を描画する前提で、fontset の不足を整理する。

### 3.1 不足キャラクタ一覧（優先度順）

| 優先度 | 文字 | 主な利用想定 | 現在 | 対応方針 |
|---|---|---|---|---|
| P1 | `-` | `A-TYPE`, `B-TYPE`, `T-SPIN` | 不足 | `hyphen.png` を追加 |
| P1 | ` ` (space) | `GAME OVER`, `NEXT OFF` | 不足（専用ファイルなし） | `space.png` または描画時スペース幅定義を追加 |
| P2 | `:` | `SCORE:`, `LEVEL:` の表記拡張時 | 不足 | `colon.png` を追加 |
| P2 | `/` | キー案内 `A/B`, `ON/OFF` 表記時 | 不足 | `slash.png` を追加 |
| P3 | `(` `)` | キー併記 `A (X)` 形式時 | 不足 | `lparen.png`, `rparen.png` を追加 |

> 注記: 既存仕様は英大文字主体で運用可能だが、`-` と space が無いと必須文言の一部をそのまま表示できないため、最優先で補充する。

---

## 4. トランザクション記録

| 日付 | 種別 | 内容 | 影響 |
|---|---|---|---|
| 2026-04-16 | 棚卸し | `art/fontset` と `art/artwork` の現物を棚卸しし、利用可能資産を一覧化 | 画面実装の素材参照起点を確立 |
| 2026-04-16 | ギャップ抽出 | UI表示文言と fontset を突合し、不足文字を抽出 | 追加制作の優先順位を明確化 |

---

## 5. 次アクション

1. P1 不足文字（`-`, space）を追加制作する
2. 追加後、本書 3.1 の `現在` を `利用可` へ更新する
3. UI 実装側で採用した最終ファイル名を `27_image_asset_data_spec.md` の命名規則例へ反映する
