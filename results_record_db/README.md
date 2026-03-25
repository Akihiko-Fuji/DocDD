# results_record_db

## 概要

本テーマは、**複数の設備機器から異なるフォームで出力される実績データ**を、
共通ルールで正規化して PostgreSQL に取り込み、
最終的に Streamlit で KPI を可視化するための設計見本である。

今回の題材では、現場でよくある

- 工程ごとに利用ツールが異なる = ログのフォーマットが異なる
- ログの列名や時刻表現、粒度が揃っていない
- そのままでは KPI 評価に使えない

という状況を模している。

---

## 今回の業務モデル

- 1製番を1台の個体識別単位とし、各工程の作業完了ごとに1レコード記録する
- 製品は 1個流し
- 工程は固定で3つ
  - 内装組立
  - 外装組立
  - 出荷検査
- 1製番あたり最大3件の実績レコードが登録される
- 生産工程は直線ラインで `内装組立 → 外装組立 → 出荷検査`
- 意図的に、それぞれが異なるログフォーマットを持つようにする
- データ期間は `2026-01-05` から `2026-01-30` まで
- 土日と `2026-01-12` の祝日は休業とし、1月の営業日は19日
- 生産は1直で、工程稼働時間は `08:00-17:00`
- `12:00-13:00` は休憩時間とする
- モデル簡略化のため、残業はないものとする
- 意図的に誤った作業ログデータを設けてDBレコード登録処理の段階で除外する ※

※ kpiテーブルの正しさを求めることが目的なので、不正な値をフラグ付きで取り込んだ場合、除外漏れなどの懸念がある

---

## 最終的な評価KPI

本テーマで最終的に評価する KPI は次の3点とする。

1. 工程別時間別の作業台数実績
2. 工程間の滞留状態（15分毎データ）
3. 作業者ごとの日別作業台数

---

## 設計方針

### 1. 記録単位

データベースへの登録単位は **1作業記録1レコード** とする。

- 1製番 = 1台
- 各工程の作業完了ごとに1レコード
- したがって、1製番あたり最大3レコード

### 2. ログ統合の考え方

内装組立、外装組立、出荷検査はそれぞれ別ツールで管理されているため、
元ログの出力フォーマットは異なる。

しかし KPI 評価のためには、工程差・ツール差を吸収し、
**1つの正規化済み実績テーブル** に集約する必要がある。

### 3. 時間項目の扱い

- `start_ts` / `end_ts` は元ログに基づく事実として保持する
- `elapsed_sec` は単純な `end_ts - start_ts` 差分秒
- `work_sec` は、稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒とする

`work_sec` は取込時に計算して保持することで、
後続の集計処理や可視化を簡素化する。

### 4. 値の固定方針

本テーマでは、集計と説明を簡潔にするため、
一部の値は自由入力とせず、あらかじめ許容値を固定する。

#### `process_name`
- `内装組立`
- `外装組立`
- `出荷検査`

#### `result_cd`
- `OK`
- `NG`

#### `source_system`
- `internal_assembly_tool`
- `external_assembly_tool`
- `shipping_inspection_tool`

### 5. 作業者名の扱い

本テーマでは `worker_name` をそのまま保持する。  
実務では `worker_id` の方が安全であるが、今回はセミナー題材のため、
**まずは作業者名で可視化・集計できること** を優先する。

ただし、元ログ側の表記ゆれは取込時に吸収する前提とする。

例:
- `山田太郎`
- `山田　太郎`
- `Yamada Taro`

のような揺れは、正規化時に統一する。

---

## 主テーブル

### テーブル名
`work_log`

### カラム定義

| 物理名 | 論理名 |
|---|---|
| `work_log_id` | 処理シーケンスNo. |
| `order_no` | 受注No.（1台を識別する業務キー） |
| `product_name` | 製品名 |
| `process_name` | 工程名 |
| `worker_name` | 作業者名 |
| `start_ts` | 開始時間 (`YYYY-MM-DD hh:mm:ss`) |
| `end_ts` | 終了時間 (`YYYY-MM-DD hh:mm:ss`) |
| `elapsed_sec` | 純粋な `end_ts - start_ts` 差分秒 |
| `work_sec` | 稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒 |
| `result_cd` | 作業結果（`OK / NG` のいずれか） |
| `source_system` | 入力元種別 |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行数 |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | 取込時間 (`YYYY-MM-DD hh:mm:ss`) |

---

## PostgreSQL の型定義

| 物理名 | 型 |
|---|---|
| `work_log_id` | `BIGSERIAL` |
| `order_no` | `VARCHAR(30)` |
| `product_name` | `VARCHAR(100)` |
| `process_name` | `VARCHAR(30)` |
| `worker_name` | `VARCHAR(50)` |
| `start_ts` | `TIMESTAMP` |
| `end_ts` | `TIMESTAMP` |
| `elapsed_sec` | `INTEGER` |
| `work_sec` | `INTEGER` |
| `result_cd` | `VARCHAR(10)` |
| `source_system` | `VARCHAR(50)` |
| `source_file_name` | `VARCHAR(255)` |
| `source_row_no` | `INTEGER` |
| `ingest_batch_id` | `VARCHAR(30)` |
| `created_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |

---

## NOT NULL 方針

本テーマでは、主テーブルの主要列には強めに `NOT NULL` を付与する。

対象列は以下を想定する。

- `order_no`
- `product_name`
- `process_name`
- `worker_name`
- `start_ts`
- `end_ts`
- `elapsed_sec`
- `work_sec`
- `result_cd`
- `source_system`
- `source_file_name`
- `source_row_no`
- `ingest_batch_id`

`work_log_id` は主キーのため `NOT NULL` 相当、
`created_at` は `DEFAULT CURRENT_TIMESTAMP` により必須値を持つ前提とする。

---

## 制約の初期案

### 主キー・一意制約

```sql
PRIMARY KEY (work_log_id)
UNIQUE (order_no, process_name)
```

本テーマでは、

- 1製番 = 1台
- 各工程は1回だけ記録
- `result_cd` は `OK / NG` のみ

という前提のため、`UNIQUE (order_no, process_name)` を採用する。

### CHECK 制約

```sql
CHECK (process_name IN ('内装組立', '外装組立', '出荷検査'))
CHECK (result_cd IN ('OK', 'NG'))
CHECK (source_system IN (
  'internal_assembly_tool',
  'external_assembly_tool',
  'shipping_inspection_tool'
))
CHECK (end_ts >= start_ts)
CHECK (elapsed_sec >= 0)
CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)
```

---

## reject テーブル

主テーブルに登録できなかった行については、
**別テーブルに reject 理由付きで記録する** 方針とする。

### テーブル名
`work_log_reject`

### カラム定義

| 物理名 | 論理名 |
|---|---|
| `reject_id` | rejectシーケンスNo. |
| `source_system` | 入力元種別 |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行数 |
| `reject_reason_cd` | reject理由コード |
| `reject_reason_detail` | reject理由詳細 |
| `raw_payload_json` | 元行データ |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | reject記録時間 |

### reject テーブルの目的

- 取込できなかった行を捨てっぱなしにしない
- どの入力元のどの行が問題だったかを追跡できる
- KPI に載らなかった理由を説明できる

### reject 理由の例

- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `process_name` 不正
- `result_cd` 不正
- 一意制約違反（重複）

---

## ingest_batch_id の生成ルール

`ingest_batch_id` は **1回の取込実行単位を識別するID** とする。

生成ルールは簡易な文字列ルールでよい。

例:

```text
ING_YYYYMMDD_HH24MISS_連番
```

具体例:

```text
ING_20260105_081530_001
```

この形式とすることで、

- 同じファイルを再取込した場合でも別実行として識別できる
- 主テーブルと reject テーブルを batch 単位で追跡できる
- セミナーで意味を説明しやすい

---

## インデックス方針

最終KPIを効率よく集計するため、初期段階から最低限のインデックスを意識する。

### 推奨インデックス

```sql
CREATE INDEX idx_work_log_process_end_ts ON work_log (process_name, end_ts);
CREATE INDEX idx_work_log_worker_end_ts  ON work_log (worker_name, end_ts);
CREATE INDEX idx_work_log_order_process  ON work_log (order_no, process_name);
```

### 目的

- `process_name + end_ts`
  - 工程別時間別の作業台数実績
- `worker_name + end_ts`
  - 作業者ごとの日別作業台数
- `order_no + process_name`
  - 工程間滞留判定
  - 工程別進捗確認

---

## 補足ルール

### `work_sec` の考え方

`work_sec` は以下を除外した正味作業時間とする。

- 昼休み `12:00-13:00`
- 非稼働時間帯（`08:00` より前、`17:00` より後）

### 稼働カレンダー前提

- 稼働日: `2026-01-05` ～ `2026-01-30` のうち、土日と `2026-01-12` を除く日
- 1月営業日数: 19日
- 稼働時間: `08:00-17:00`
- 休憩時間: `12:00-13:00`
- 残業: なし

---

## このテーマで扱う課題

本テーマで解決すべき課題は、単に CSV を読み込むことではない。

- 異なるログフォーマットを共通カラムへマッピングすること
- 同じ意味のデータを同じ定義で扱えるようにすること
- KPI に不要な揺れや曖昧さを取込時点で吸収すること
- 不正行や重複行を reject として明示的に扱うこと
- Streamlit で見せたい分析指標へつながる形で DB 設計すること

---

## この後に設計するもの

- 工程別の元ログフォーマット定義
  - 内装組立ログ
  - 外装組立ログ
  - 出荷検査ログ
- 元ログから `work_log` へのマッピング定義
- reject 条件定義
- PostgreSQL DDL
- Streamlit での KPI 可視化要件

---

## ゴール

最終的には、異なる設備ログを取り込み、正規化済みテーブル `work_log` を元に、

- 工程別時間別の作業台数
- 工程間滞留
- 作業者別日次実績

を Streamlit 上で確認できる状態を目指す。

---

---
# 取り込む予定の実績ログデータの設計指針

## フォーマット
  - 内装組立ログ
  - 外装組立ログ
  - 出荷検査ログ
の3種をそれぞれ異なるフォーマットとする。また、取り込む必要のないカラムなども設定する。具体的にはこれから検討をおこなう。

## 不正データの扱い

本テーマでは、**不正データは主テーブル `work_log` には取り込まず、取込時に除外して reject テーブルへ記録する** 方針とする。

理由は以下のとおりである。

- `work_log` を KPI 集計専用の正規データに保ちたい
- 集計SQLや可視化画面で毎回 `error_flag = 0` のような条件を要求しないようにしたい
- 不正データを残す場合でも、主テーブルではなく reject 側で理由付き管理した方が追跡しやすい
- `NOT NULL` や `CHECK` 制約を素直に強く掛けられる

したがって、取込結果は次の2系統に分かれる。

- 正常データ: `work_log` に登録する
- 不正データ: `work_log_reject` に登録する

---

## reject テーブルの位置付け

`work_log_reject` は、単に「捨てたデータ」を置く場所ではない。  
**どのファイルのどの行が、なぜ主テーブルへ取り込まれなかったのか** を残すための監査・再確認用テーブルである。

このため、reject テーブルには少なくとも以下を記録する。

- 入力元種別
- ファイル名
- 行番号
- reject 理由コード
- reject 理由詳細
- 元行データ
- 取込実行ID
- reject 記録時間

これにより、

- KPI に含まれなかった理由を説明できる
- 元ファイルの修正対象を追跡できる
- 同一バッチの取込結果をまとめて確認できる

---

## 入力不正と業務異常の切り分け

本テーマでは、**入力不正** と **業務異常** を分けて扱う。

### 入力不正
入力形式や値として成立しておらず、主テーブルへ登録してはいけないもの。  
これらは reject 対象とする。

例:
- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `work_sec > elapsed_sec`
- `process_name` が未定義値
- `result_cd` が未定義値
- `source_system` が未定義値
- `UNIQUE (order_no, process_name)` に抵触する重複データ

### 業務異常
形式上は正しく、主テーブルへ登録可能だが、現場改善や分析上は注意が必要なもの。  
これらは reject せず、`work_log` に登録したうえで KPI や個別分析で扱う。

例:
- 作業時間が極端に長い
- 作業時間が極端に短い
- 特定工程だけ NG が多い
- 同一作業者に負荷が偏っている
- 工程間滞留が偏在している

---

## サンプルデータに意図的に含める誤り

セミナー用のサンプルデータには、正常データだけでなく、実務で起こりやすい誤りを意図的に混ぜる。

### 必ず含めたい誤り
- 同じデータを2回取り込むケース
- 必須列欠損
- 日付変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0`
- `work_sec < 0`
- `work_sec > elapsed_sec`
- `process_name` の誤記
- `result_cd` の誤記
- 列ズレ / 桁ズレにより値が想定列へ入っていないケース

### 二重取込の扱い
同じファイルを2回取り込んでも、`work_log` の件数は増加しないことを確認する。  
これにより、一意制約と重複排除処理が正しく機能していることを示す。

---

## 取込処理の設計方針

本テーマでは、取込処理は **入口と中核ロジックを分離** する方針とする。

### 入口
- CLI: 定時バッチや大量処理向け
- Web / Streamlit: 手動アップロード、エラー確認、例外対応向け

### 中核
- `ingest_core` に変換・検証・登録ロジックを集約する

この構成により、

- 入口が違っても同じ判定基準で取り込める
- 仕様変更時の修正箇所を一箇所に集約できる
- 製造業でありがちな「定時自動取込」と「手動再取込」を同じルールで扱える

---

## 推奨する取込フロー

1. ファイル受領
2. `source_system` 判定
3. 元フォーマットごとの列名マッピング
4. 型変換
5. 必須チェック
6. 値域チェック
7. `elapsed_sec` / `work_sec` 計算
8. 正常データと reject データへ振り分け
9. 取込実行IDを付与
10. `work_log` へ登録
11. `work_log_reject` へ登録
12. 取込サマリを記録・表示

> 補足:
> 実務では取込実行単位を管理する `import_run` テーブルを設けると便利である。
> ただし本テーマでは説明を簡潔にするため省略し、`ingest_batch_id` を主テーブルと reject テーブルの両方に保持することで代替する。

---

## 取込実行単位の記録

`ingest_batch_id` は、1回の取込実行を識別するためのIDである。  
主テーブルと reject テーブルの両方に保持することで、同一取込の結果をまとめて追跡できるようにする。

形式は簡易な文字列ルールで十分とする。

例:

```text
ING_20260105_081530_001
```

## 想定する3種の元ログフォーマット

本テーマでは、工程ごとに性格の異なる3種類の元ログを想定する。  
採用順は以下とする。

1. 文脈補完が必要な設備生ログ → 内装組立
2. 業務列が多い実績ログ → 外装組立
3. 判定を丸める検査ログ → 出荷検査

この順にする理由は、取込難易度と業務意味付けの差を明確に見せやすいためである。  
特に 1つ目は「そのままでは KPI に使えないログ」、2つ目は「比較的そのまま使いやすいログ」、
3つ目は「判定を共通コードへ丸める必要があるログ」として役割が分かれる。

---

## 1. 内装組立ログ（文脈補完が必要な設備生ログ）

### 位置付け
設備から直接出力された生ログを想定する。  
ログ自体は START / END の時刻情報が中心で、業務的な意味を十分に持たない。  
そのため、ファイル名規則や補助情報を用いて、工程名・作業者名・入力元種別を補完して取り込む。

### 想定するファイル形式
- 形式: CSV またはテキスト
- 文字コード: UTF-8 または Shift-JIS を想定
- ログ粒度: 1開始・1終了のイベント対
- 行単位の意味: 1作業記録の開始終了

### 想定する生ログカラム
| カラム名 | 型 | 説明 |
|---|---|---|
| `log_date` | DATE相当文字列 | 作業日 |
| `start_marker` | 文字列 | `START` 固定 |
| `start_time` | TIME相当文字列 | 開始時刻 |
| `end_date` | DATE相当文字列 | 作業日 |
| `end_time` | TIME相当文字列 | 終了時刻 |
| `end_marker` | 文字列 | `END` 固定 |
| `order_no` | 文字列 | 受注No.（補助的に付与済み） |

### ファイル名から補完する想定項目
| 補完項目 | 補完方法 |
|---|---|
| `process_name` | ファイル名規則から `内部組立` を固定付与 |
| `worker_name` | ファイル名規則から作業者名を付与 |
| `source_system` | ファイル名規則から `internal_assembly_tool` を付与 |

### 取込時の変換
- `log_date + start_time` → `start_ts`
- `end_date + end_time` → `end_ts`
- `end_ts - start_ts` → `elapsed_sec`
- 稼働カレンダー控除後 → `work_sec`
- `result_cd` は原則 `OK` 固定とする
- `process_name` は `内部組立` 固定とする

### このログで見せたい論点
- 生ログだけでは KPI に必要な項目が足りない
- ファイル名や補助ルールで業務文脈を補完する必要がある
- 「設備データをそのまま入れる」のではなく、「業務データへ変換する」ことが必要

---

## 2. 外装組立ログ（業務列が多い実績ログ）

### 位置付け
比較的整った実績ログを想定する。  
受注No.、製品名、開始時刻、終了時刻、作業時間、資材関連情報などを持ち、
主テーブル `work_log` へ比較的素直にマッピングできる。

### 想定するファイル形式
- 形式: CSV または Excel 出力
- 文字コード: Shift-JIS または UTF-8
- ログ粒度: 1作業記録1行
- 行単位の意味: 1製番の外装組立完了実績

### 想定する主な元ログカラム
| カラム名 | 型 | 説明 |
|---|---|---|
| `生産日` | DATE相当文字列 | 作業対象日 |
| `チェックNo.` | 文字列 | 管理用連番 |
| `加工指示書QRコード読出時刻` | DATETIME相当文字列 | 開始寄りの時刻 |
| `全消込終了時刻` | DATETIME相当文字列 | 終了寄りの時刻 |
| `生産手配No.` | 文字列 | 手配番号 |
| `受注No.` | 文字列 | 受注No. |
| `製品名` | 文字列 | 製品名 |
| `幅` | 整数/文字列 | 製品幅 |
| `丈` | 整数/文字列 | 製品丈 |
| `資材CODE1〜6` | 文字列 | 資材コード |
| `資材CODE1名〜6名` | 文字列 | 資材名 |
| `CD1数〜CD6数` | 数値 | 資材数量 |
| `処理1〜処理12` | 数値 | 処理回数/処理結果系 |
| `QR読消込数` | 数値 | 読込数 |
| `初期消込数` | 数値 | 初期処理数 |
| `強制消込数` | 数値 | 強制処理数 |
| `品揃資材数` | 数値 | 品揃数 |
| `ERROR CODE` | 文字列 | エラーコード |

### 取込時に主に採用する項目
| `work_log` 側 | 元ログ側 |
|---|---|
| `order_no` | `受注No.` |
| `product_name` | `製品名` |
| `process_name` | `外部組立` 固定 |
| `worker_name` | ファイル名、または補助列から付与 |
| `start_ts` | `加工指示書QRコード読出時刻` |
| `end_ts` | `全消込終了時刻` |
| `elapsed_sec` | `end_ts - start_ts` または元ログ時間差 |
| `work_sec` | 稼働カレンダー控除後時間 |
| `result_cd` | 原則 `OK`、エラー条件があれば reject 判定 |
| `source_system` | `external_assembly_tool` 固定 |

### 捨てる／今回のKPIには使わない項目
- 資材コード詳細
- 資材名称詳細
- 各処理カウント詳細
- 幅丈詳細
- 品揃数
- 個別のエラー内訳列

これらは現場ログらしさを出すために残してよいが、
今回のKPI算出には直接使わない。

### このログで見せたい論点
- 業務列が多いログは、そのまま使えそうに見える
- ただし KPI に必要な列と不要な列を切り分ける必要がある
- 「全部使う」のではなく、「必要な列だけを共通契約へ落とす」ことが重要

---

## 3. 出荷検査ログ（判定を丸める検査ログ）

### 位置付け
検査工程の帳票・検査システム出力を想定する。  
作業時刻や受注No.に加えて、不良明細や不適合内訳を多く持つ。  
そのまま主テーブルへ入れるのではなく、判定結果を `OK / NG` へ丸めて取り込む。

### 想定するファイル形式
- 形式: CSV または Excel 出力
- 文字コード: Shift-JIS または UTF-8
- ログ粒度: 1製番1検査記録
- 行単位の意味: 1製番の出荷検査結果

### 想定する主な元ログカラム
| カラム名 | 型 | 説明 |
|---|---|---|
| `担当者` | 文字列 | 検査担当者名 |
| `検査日` | DATE相当文字列 | 検査日 |
| `伝票No.` | 文字列 | 帳票番号 |
| `製品名` | 文字列 | 製品名 |
| `開始時間` | TIME相当文字列 | 作業開始 |
| `終了時間` | TIME相当文字列 | 作業終了 |
| `作業時間` | 数値/文字列 | 作業分または秒 |
| `生産手配ＮＯ` | 文字列 | 手配番号 |
| `受注ＮＯ` | 文字列 | 受注No. |
| `ボトム不適合` | 数値 | 不適合数 |
| `スラット不適合` | 数値 | 不適合数 |
| `バランス不適合` | 数値 | 不適合数 |
| `不良合計` | 数値 | 不良合計 |

### 取込時の変換
| `work_log` 側 | 元ログ側 |
|---|---|
| `order_no` | `受注ＮＯ` |
| `product_name` | `製品名` |
| `process_name` | `出荷検査` 固定 |
| `worker_name` | `担当者` |
| `start_ts` | `検査日 + 開始時間` |
| `end_ts` | `検査日 + 終了時間` |
| `elapsed_sec` | `end_ts - start_ts` |
| `work_sec` | 稼働カレンダー控除後時間 |
| `result_cd` | `不良合計 = 0` → `OK`、`不良合計 > 0` → `NG` |
| `source_system` | `shipping_inspection_tool` 固定 |

### 今回のKPIに直接使わない項目
- 不適合内訳詳細
- 資材寸法詳細
- 製作所コード
- 本籍品番
- QR文字列
- 個別不良分類列

これらは検査ログの“現場らしさ”を出すためには有効だが、
今回の共通実績テーブルでは保持しない。

### このログで見せたい論点
- 検査ログは「OK / NG」を直接持たない場合がある
- 明細値から共通結果コードへ丸める必要がある
- 業務ごとの判定ロジックを共通コードへ落とすことが、KPI化の前提である

---

## 4. 3ログ共通の正規化先

3種類の元ログは最終的に、以下の共通テーブル `work_log` へ統合する。

| 物理名 | 論理名 |
|---|---|
| `work_log_id` | 処理シーケンスNo. |
| `order_no` | 受注No.（1台を識別する業務キー） |
| `product_name` | 製品名 |
| `process_name` | 工程名 |
| `worker_name` | 作業者名 |
| `start_ts` | 開始時間 |
| `end_ts` | 終了時間 |
| `elapsed_sec` | 単純差分秒 |
| `work_sec` | 正味作業時間秒 |
| `result_cd` | 作業結果 |
| `source_system` | 入力元種別 |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行番号 |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | 取込時間 |

---

## 5. 採用順の意図

今回の採用順は以下の学習順にも対応する。

1. **文脈補完**
   - 設備生ログを業務データへ変換する
2. **列の選別**
   - 多項目実績ログから必要列だけを採用する
3. **判定の丸め込み**
   - 検査明細から `OK / NG` を導出する

この順にすることで、
「異なるログフォーマットを共通契約へ落とす」というテーマを段階的に説明しやすくする。

---

## 取り込む予定の実績ログデータの詳細設計

本テーマでは、工程ごとに性格の異なる3種類の元ログを想定する。  
採用順は以下とする。

1. 文脈補完が必要な設備生ログ → 内装組立
2. 業務列が多い実績ログ → 外装組立
3. 判定を丸める検査ログ → 出荷検査

この順にする理由は、取込難易度と業務意味付けの差を明確に見せやすいためである。  
特に1つ目は「そのままでは KPI に使えないログ」、2つ目は「比較的そのまま使いやすいログ」、3つ目は「判定を共通コードへ丸める必要があるログ」として役割が分かれる。

---

## 1. 内装組立ログ（文脈補完が必要な設備生ログ）

### 1.1 位置付け

設備から直接出力された生ログを想定する。  
ログ自体は START / END の時刻情報が中心で、業務的な意味を十分に持たない。  
そのため、ファイル名規則や補助情報を用いて、工程名・作業者名・入力元種別を補完して取り込む。

### 1.2 想定するサンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|---:|---|
| `start_date` | DATE相当文字列 | ○ | 作業開始日 |
| `start_time` | TIME相当文字列 | ○ | 作業開始時刻 |
| `start_marker` | 文字列 | ○ | `START` 固定 |
| `end_date` | DATE相当文字列 | ○ | 作業終了日 |
| `end_time` | TIME相当文字列 | ○ | 作業終了時刻 |
| `end_marker` | 文字列 | ○ | `END` 固定 |
| `order_no` | 文字列 | ○ | 受注No.（補助的に付与済み） |

### 1.3 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `start_date` + `start_time` | `start_ts` | 連結して TIMESTAMP 化 |
| 採用 | `end_date` + `end_time` | `end_ts` | 連結して TIMESTAMP 化 |
| 採用 | ファイル名 | `worker_name` | ファイル名規則から補完 |
| 採用 | ファイル名 | `process_name` | `内部組立` を付与 |
| 採用 | ファイル名 | `source_system` | `internal_assembly_tool` を付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | 固定値 | `result_cd` | `OK` を付与 |
| 捨て列 | `start_marker` | なし | `START` 固定確認後は保持しない |
| 捨て列 | `end_marker` | なし | `END` 固定確認後は保持しない |

### 1.4 reject 条件の例

- `order_no` が空
- `start_date` / `start_time` / `end_date` / `end_time` のいずれかが空
- `start_marker <> 'START'`
- `end_marker <> 'END'`
- 日時変換失敗
- `end_ts < start_ts`
- `UNIQUE (order_no, process_name)` 違反

### 1.5 サンプルデータ作成時の注意

- ファイル名に作業者名を含める  
  例: `INTASM_20260105_Yamada_01.csv`
- 行データには `order_no` のみ付与する
- `product_name` は別途オーダー別に補完するか、サンプルでは別マスタから引く
- START/END のみで「そのままでは KPI に使えない」雰囲気を残す

---

## 2. 外装組立ログ（業務列が多い実績ログ）

### 2.1 位置付け

比較的整った実績ログを想定する。  
受注No.、製品名、開始時刻、終了時刻、資材コード、各種処理数などを多く持ち、主テーブル `work_log` へ比較的素直にマッピングできる。

### 2.2 想定するサンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|---:|---|
| `production_date_yymmdd` | 文字列 | ○ | 生産日（YYMMDD） |
| `check_no` | 文字列 | ○ | チェックNo. |
| `qr_read_ts` | DATETIME相当文字列 | ○ | 加工指示書QRコード読出時刻 |
| `all_clear_ts` | DATETIME相当文字列 | ○ | 全消込終了時刻 |
| `production_date` | DATE相当文字列 | △ | 生産日 |
| `packing_date` | DATE相当文字列 | △ | 梱包作業日 |
| `tehai_no` | 文字列 | △ | 生産手配No. |
| `order_no` | 文字列 | ○ | 受注No. |
| `product_name` | 文字列 | ○ | 製品名 |
| `width_mm` | 数値 | △ | 製品幅 |
| `height_mm` | 数値 | △ | 製品丈 |
| `material_code1` ～ `material_code6` | 文字列 | × | 資材コード |
| `material_name1` ～ `material_name6` | 文字列 | × | 資材名称 |
| `material_qty1` ～ `material_qty6` | 数値 | × | 資材数量 |
| `process_count1` ～ `process_count12` | 数値 | × | 処理数 |
| `qr_clear_count` | 数値 | × | QR読消込数 |
| `initial_clear_count` | 数値 | × | 初期消込数 |
| `forced_clear_count` | 数値 | × | 強制消込数 |
| `material_pick_count` | 数値 | × | 品揃資材数 |
| `error_code` | 文字列 | △ | エラーコード |

### 2.3 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `product_name` | `product_name` | trim のみ |
| 採用 | `qr_read_ts` | `start_ts` | DATETIME 変換 |
| 採用 | `all_clear_ts` | `end_ts` | DATETIME 変換 |
| 採用 | ファイル名または補助規則 | `worker_name` | ファイル名規則または固定表で補完 |
| 採用 | 固定値 | `process_name` | `外部組立` を付与 |
| 採用 | 固定値 | `source_system` | `external_assembly_tool` を付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | `error_code` | `result_cd` | `error_code` が空なら `OK`、致命エラーなら reject |
| 捨て列 | `production_date_yymmdd` | なし | 参考情報のため保持しない |
| 捨て列 | `production_date` | なし | `start_ts` / `end_ts` から代替可能 |
| 捨て列 | `packing_date` | なし | 今回のKPIでは未使用 |
| 捨て列 | `tehai_no` | なし | 今回の主表では保持しない |
| 捨て列 | `width_mm`, `height_mm` | なし | 今回のKPIでは未使用 |
| 捨て列 | `material_code1` ～ `material_code6` | なし | KPI に未使用 |
| 捨て列 | `material_name1` ～ `material_name6` | なし | KPI に未使用 |
| 捨て列 | `material_qty1` ～ `material_qty6` | なし | KPI に未使用 |
| 捨て列 | `process_count1` ～ `process_count12` | なし | KPI に未使用 |
| 捨て列 | `qr_clear_count` | なし | KPI に未使用 |
| 捨て列 | `initial_clear_count` | なし | KPI に未使用 |
| 捨て列 | `forced_clear_count` | なし | KPI に未使用 |
| 捨て列 | `material_pick_count` | なし | KPI に未使用 |

### 2.4 reject 条件の例

- `order_no` が空
- `product_name` が空
- `qr_read_ts` または `all_clear_ts` が空
- 日時変換失敗
- `end_ts < start_ts`
- `error_code` が致命エラー扱い
- `UNIQUE (order_no, process_name)` 違反

### 2.5 サンプルデータ作成時の注意

- 実ログ感を出すため、捨て列もファイル上には残す
- ただし値は新規に作る
- 一部に `error_code` あり行を混ぜ、reject 例として使う
- `worker_name` はファイル名補完でも、別列補完でもよいが、方式は固定する

---

## 3. 出荷検査ログ（判定を丸める検査ログ）

### 3.1 位置付け

検査工程の帳票・検査システム出力を想定する。  
作業時刻や受注No.に加えて、不良明細や不適合内訳を多く持つ。  
そのまま主テーブルへ入れるのではなく、判定結果を `OK / NG` へ丸めて取り込む。

### 3.2 想定するサンプル列名

| サンプル列名 | 型 | 必須 | 説明 |
|---|---|---:|---|
| `inspector_name` | 文字列 | ○ | 担当者 |
| `inspection_date` | DATE相当文字列 | ○ | 検査日 |
| `slip_no` | 文字列 | △ | 伝票No. |
| `product_name` | 文字列 | ○ | 製品名 |
| `start_time` | TIME相当文字列 | ○ | 開始時間 |
| `end_time` | TIME相当文字列 | ○ | 終了時間 |
| `work_minutes` | 数値 | △ | 作業時間（分） |
| `tehai_no` | 文字列 | △ | 生産手配ＮＯ |
| `order_no` | 文字列 | ○ | 受注ＮＯ |
| `bottom_ng_count` | 数値 | △ | ボトム不適合 |
| `slat_ng_count` | 数値 | △ | スラット不適合 |
| `balance_ng_count` | 数値 | △ | バランス不適合 |
| `ng_total` | 数値 | ○ | 不良合計 |
| その他不適合明細列 | 数値/文字列 | × | 詳細内訳 |

### 3.3 採用列 / 捨て列 / 変換ルール

| 区分 | 元ログ列 | 正規化先 | 変換ルール |
|---|---|---|---|
| 採用 | `order_no` | `order_no` | trim のみ |
| 採用 | `product_name` | `product_name` | trim のみ |
| 採用 | `inspector_name` | `worker_name` | trim のみ |
| 採用 | `inspection_date` + `start_time` | `start_ts` | 連結して TIMESTAMP 化 |
| 採用 | `inspection_date` + `end_time` | `end_ts` | 連結して TIMESTAMP 化 |
| 採用 | 固定値 | `process_name` | `出荷検査` を付与 |
| 採用 | 固定値 | `source_system` | `shipping_inspection_tool` を付与 |
| 変換 | `start_ts`, `end_ts` | `elapsed_sec` | 単純差分秒を計算 |
| 変換 | `start_ts`, `end_ts` | `work_sec` | 稼働カレンダー控除後秒を計算 |
| 変換 | `ng_total` | `result_cd` | `ng_total = 0` → `OK`、`ng_total > 0` → `NG` |
| 捨て列 | `slip_no` | なし | 今回のKPIでは未使用 |
| 捨て列 | `tehai_no` | なし | 今回の主表では保持しない |
| 捨て列 | `work_minutes` | なし | `start_ts` / `end_ts` から再計算可能 |
| 捨て列 | `bottom_ng_count` | なし | `result_cd` 丸め後は未使用 |
| 捨て列 | `slat_ng_count` | なし | `result_cd` 丸め後は未使用 |
| 捨て列 | `balance_ng_count` | なし | `result_cd` 丸め後は未使用 |
| 捨て列 | その他不適合明細列 | なし | KPI に未使用 |

### 3.4 reject 条件の例

- `order_no` が空
- `product_name` が空
- `inspector_name` が空
- `inspection_date` / `start_time` / `end_time` のいずれかが空
- 日時変換失敗
- `ng_total` が数値変換できない
- `end_ts < start_ts`
- `UNIQUE (order_no, process_name)` 違反

### 3.5 サンプルデータ作成時の注意

- 不良明細列は残しつつ、最終的には `ng_total` から `result_cd` へ丸める
- `ng_total = 0` の正常検査行を多数派にする
- `ng_total > 0` の行を少数混ぜ、`NG` 例として使う
- 一部に `ng_total` 欠損や文字混入を混ぜ、reject 例を作る

---

## 4. 3ログ共通の採用先

3種類の元ログは最終的に、以下の共通テーブル `work_log` へ統合する。

| 物理名 | 論理名 |
|---|---|
| `work_log_id` | 処理シーケンスNo. |
| `order_no` | 受注No.（1台を識別する業務キー） |
| `product_name` | 製品名 |
| `process_name` | 工程名 |
| `worker_name` | 作業者名 |
| `start_ts` | 開始時間 |
| `end_ts` | 終了時間 |
| `elapsed_sec` | 純粋な `end_ts - start_ts` 差分秒 |
| `work_sec` | 稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒 |
| `result_cd` | 作業結果（`OK / NG`） |
| `source_system` | 入力元種別 |
| `source_file_name` | ファイル名 |
| `source_row_no` | 行数 |
| `ingest_batch_id` | 取込実行ID |
| `created_at` | 取込時間 |

---

## 5. サンプルデータ作成までの段取り

サンプルデータ作成は、以下の順で進める。

### Step 1. サンプル列名を固定する
まず本書のサンプル列名を確定し、3フォーマットの雛形CSVを作る。

### Step 2. 採用列と捨て列を確定する
どの列を `work_log` に入れ、どの列を説明用に残すだけかを固定する。

### Step 3. 変換ルールを確定する
- 日付・時刻の結合方法
- `worker_name` の補完方法
- `result_cd` の丸め方
- `elapsed_sec` / `work_sec` の計算方法
を先に固定する。

### Step 4. reject 条件を確定する
サンプルに混ぜる誤りを、reject 条件と対応付けて定義する。

### Step 5. 正常データを先に作る
まず 2026-01-05 ～ 2026-01-30 の営業日19日分について、正常データだけを作る。

### Step 6. 異常データを後から差し込む
正常データ作成後に、以下のような誤りを少量混ぜる。

- 同一ファイルの二重取込
- 必須列欠損
- 時刻逆転
- 不正コード
- 数値変換失敗
- 列ズレ / 桁ズレ

### Step 7. 正規化結果を確認する
各ログから `work_log` へ正しく正規化できるかを確認し、
KPI の3指標が問題なく算出できる状態にする。

---

## 6. 本段階の到達点

本段階の目的は、まだ PostgreSQL DDL や Streamlit 画面を作ることではない。  
まずは、

- 3種類の元ログフォーマットを固定する
- 各ログの採用列 / 捨て列 / 変換ルールを決める
- サンプルデータ生成に迷わない状態を作る

ことを到達点とする。

## 実績ログデータサンプルcsvイメージ

# 1. 内装組立ログ（文脈補完が必要な設備生ログ）
# 想定ファイル名: INTASM_YamadaTaro_202601.csv
start_date,start_time,start_marker,end_date,end_time,end_marker,order_no
2026-01-05,08:12:10,START,2026-01-05,08:24:40,END,ORD-260105-001
2026-01-05,08:28:05,START,2026-01-05,08:43:15,END,ORD-260105-002
2026-01-05,08:47:20,START,2026-01-05,09:05:00,END,ORD-260105-003
2026-01-06,08:05:45,START,2026-01-06,08:21:30,END,ORD-260106-001
2026-01-06,08:26:10,START,2026-01-06,08:44:55,END,ORD-260106-002

# 2. 外装組立ログ（業務列が多い実績ログ）
# 想定ファイル名: EXTASM_SatoKen_202601.csv
production_date_yymmdd,check_no,qr_read_ts,all_clear_ts,production_date,packing_date,tehai_no,order_no,product_name,width_mm,height_mm,material_code1,material_name1,material_qty1,material_code2,material_name2,material_qty2,qr_clear_count,initial_clear_count,forced_clear_count,material_pick_count,error_code
260105,CHK0001,2026-01-05 09:18:10,2026-01-05 09:33:20,2026-01-05,2026-01-05,TH-260105-001,ORD-260105-001,RS-90X180-WH,900,1800,MAT-A01,HeadRail-WH,1,MAT-B11,Fabric-WH,1,1,1,0,2,
260105,CHK0002,2026-01-05 09:37:40,2026-01-05 09:54:10,2026-01-05,2026-01-05,TH-260105-002,ORD-260105-002,RS-120X200-GY,1200,2000,MAT-A01,HeadRail-WH,1,MAT-B12,Fabric-GY,1,1,1,0,2,
260105,CHK0003,2026-01-05 10:02:05,2026-01-05 10:20:25,2026-01-05,2026-01-05,TH-260105-003,ORD-260105-003,VB-50-80X150-IV,800,1500,MAT-C21,Slat-IV,24,MAT-C31,LadderTape-IV,2,1,1,0,2,
260106,CHK0004,2026-01-06 09:11:30,2026-01-06 09:28:00,2026-01-06,2026-01-06,TH-260106-001,ORD-260106-001,RS-90X180-BE,900,1800,MAT-A01,HeadRail-WH,1,MAT-B13,Fabric-BE,1,1,1,0,2,
260106,CHK0005,2026-01-06 09:36:50,2026-01-06 09:55:40,2026-01-06,2026-01-06,TH-260106-002,ORD-260106-002,VT-80X200-LG,800,2000,MAT-D11,CarrierSet,1,MAT-D21,Louver-LG,8,1,1,0,2,

# 3. 出荷検査ログ（判定を丸める検査ログ）
# 想定ファイル名: SHIPCHK_202601.csv
inspector_name,inspection_date,slip_no,product_name,start_time,end_time,work_minutes,tehai_no,order_no,bottom_ng_count,slat_ng_count,balance_ng_count,ng_total
SuzukiMika,2026-01-05,SLP-260105-001,RS-90X180-WH,10:05:00,10:14:00,9,TH-260105-001,ORD-260105-001,0,0,0,0
SuzukiMika,2026-01-05,SLP-260105-002,RS-120X200-GY,10:18:00,10:28:00,10,TH-260105-002,ORD-260105-002,0,0,0,0
SuzukiMika,2026-01-05,SLP-260105-003,VB-50-80X150-IV,10:34:00,10:46:00,12,TH-260105-003,ORD-260105-003,0,0,0,0
SuzukiMika,2026-01-06,SLP-260106-001,RS-90X180-BE,10:02:00,10:11:00,9,TH-260106-001,ORD-260106-001,0,0,0,0
SuzukiMika,2026-01-06,SLP-260106-002,VT-80X200-LG,10:18:00,10:30:00,12,TH-260106-002,ORD-260106-002,0,0,0,0

# 補助マスタ（内装組立ログの product_name 補完用）
# 想定ファイル名: order_product_master.csv
order_no,product_name
ORD-260105-001,RS-90X180-WH
ORD-260105-002,RS-120X200-GY
ORD-260105-003,VB-50-80X150-IV
ORD-260106-001,RS-90X180-BE
ORD-260106-002,VT-80X200-LG
