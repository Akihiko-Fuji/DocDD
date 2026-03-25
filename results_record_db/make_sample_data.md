# Codexへの依頼: `results_record_db` 用デモサンプルデータの生成

## 目的

`results_record_db` テーマのデモ用として、  
**異なる3種類の元ログフォーマット**から、最終的に共通テーブル `work_log` へ正規化できる  
**実績サンプルデータ一式**を作成してください。

今回の主題は、**フォーマットが異なる設備・業務ログを、共通ルールで取り込み、KPIへ落とし込むこと**です。  
単なるCSV作成ではなく、**後で PostgreSQL へ投入し、Streamlit で KPI を可視化できる前提**で作ってください。

---

## 作成してほしい成果物

以下を作成してください。

1. **サンプルデータ生成スクリプト**
   - `results_record_db/sample_data/generate_sample_data.py`

2. **生成される正常系CSV**
   - `results_record_db/sample_data/internal_assembly_log.csv`
   - `results_record_db/sample_data/external_assembly_log.csv`
   - `results_record_db/sample_data/shipping_inspection_log.csv`
   - `results_record_db/sample_data/order_product_master.csv`

3. **生成される正規化後の期待結果CSV**
   - `results_record_db/sample_data/expected_work_log.csv`

4. **生成される異常系CSV（reject用）**
   - `results_record_db/sample_data/internal_assembly_log_invalid.csv`
   - `results_record_db/sample_data/external_assembly_log_invalid.csv`
   - `results_record_db/sample_data/shipping_inspection_log_invalid.csv`

5. **README 追記用の説明Markdown**
   - `results_record_db/sample_data/README_sample_data.md`

---

## 業務モデル

- 1製番 = 1台の個別受注生産
- 1製番を1台の個体識別単位とし、各工程の作業完了ごとに1レコード記録する
- 製品は 1個流し
- 生産工程は直線ラインで以下の3工程
  1. 内装組立
  2. 外装組立
  3. 出荷検査
- 1製番あたり最大3件の実績レコードが登録される
- **工程間を繋ぐキー情報は `order_no` とする**
- **正常系データでは、同じ `order_no` が3つのログすべてに登場すること**
- ただし、工程間滞留を表現するため、**同一営業日内に3工程すべて完了しない製番が一部あってよい**
- 一部は翌営業日に持ち越してよい

---

## 対象期間と稼働カレンダー

- データ期間: `2026-01-05` ～ `2026-01-30`
- 休業日:
  - 土日
  - `2026-01-12`
- 営業日は **19日**
- 稼働時間:
  - `08:00:00` ～ `17:00:00`
- 休憩時間:
  - `12:00:00` ～ `13:00:00`
- 残業なし
- 正常系データは、**この稼働カレンダーを逸脱しないこと**
- 異常系データには、あえて逸脱データを含めてよい

---

## 日次の生産量前提

- 日次の生産指示量ターゲットは **225台/日 ± 50台**
- つまり、営業日ごとの投入量は **175～275台/日** の範囲でランダムに作成してください
- ただし、極端に乱高下せず、製造業のデモとして不自然でない分布にしてください
- 19営業日全体で見たとき、総製番数は自然な規模になるようにしてください

---

## 工程能力の前提

### 1. 内装組立
- ログ種別: **文脈補完が必要な設備生ログ**
- 工程名: `内部組立`
- `source_system`: `internal_assembly_tool`
- 自動装置っぽいログ
- 2台稼働
- 標準サイクル: **150秒/台**
- ばらつき: 小さめ（例: ±10～15秒程度）
- 比較的規則的に処理される

### 2. 外装組立
- ログ種別: **業務列が多い実績ログ**
- 工程名: `外部組立`
- `source_system`: `external_assembly_tool`
- 人作業
- 3ライン
- 標準サイクル: **240秒/台**
- ばらつき: 中程度（例: ±20～30秒程度）
- 少し待ち時間やライン差があってよい

### 3. 出荷検査
- ログ種別: **判定を丸める検査ログ**
- 工程名: `出荷検査`
- `source_system`: `shipping_inspection_tool`
- 4ライン
- 標準サイクル: **340秒/台**
- ばらつき: 中程度（例: ±20～30秒程度）
- この工程はやや遅く、**工程間仕掛り（滞留）が見えるようにする**
- 一部は翌営業日へ持ち越してよい
- `ng_total = 0` を `OK`
- `ng_total > 0` を `NG`
- NG率は **1～3%程度**

---

## 3つの元ログフォーマット

### 1. 内装組立ログ（設備生ログ）
このログは、**そのままでは業務文脈が足りない** 形式にしてください。  
`worker_name`、`process_name`、`source_system` は、主に**ファイル名や補助規則から補完**する前提です。

#### CSVヘッダ
```csv
start_date,start_time,start_marker,end_date,end_time,end_marker,order_no
```

#### ルール
- `start_marker` は `START`
- `end_marker` は `END`
- `order_no` は必須
- `product_name` はこのCSVには持たせない
- `product_name` は `order_product_master.csv` から補完する

#### 想定ファイル名例
```text
INTASM_YamadaTaro_202601.csv
```

### 2. 外装組立ログ（業務列が多い実績ログ）
このログは、**業務列が多く、比較的そのまま使いやすい** 形式にしてください。  
ただし、KPIに不要な列も含めてください。

#### CSVヘッダ
```csv
production_date_yymmdd,check_no,qr_read_ts,all_clear_ts,production_date,packing_date,tehai_no,order_no,product_name,width_mm,height_mm,material_code1,material_name1,material_qty1,material_code2,material_name2,material_qty2,qr_clear_count,initial_clear_count,forced_clear_count,material_pick_count,error_code
```

#### ルール
- `order_no` は必須
- `product_name` は必須
- `qr_read_ts` を `start_ts` に使う
- `all_clear_ts` を `end_ts` に使う
- `process_name` は固定で `外部組立`
- `worker_name` はファイル名または補助規則から補完してよい
- `error_code` が空なら正常
- 異常系データでは `error_code` に致命値を入れてよい

#### 想定ファイル名例
```text
EXTASM_SatoKen_202601.csv
```

### 3. 出荷検査ログ（判定丸め込み型）
このログは、**不良明細から `OK / NG` を丸める** 形式にしてください。

#### CSVヘッダ
```csv
inspector_name,inspection_date,slip_no,product_name,start_time,end_time,work_minutes,tehai_no,order_no,bottom_ng_count,slat_ng_count,balance_ng_count,ng_total
```

#### ルール
- `order_no` は必須
- `product_name` は必須
- `inspector_name` は `worker_name` に使う
- `inspection_date + start_time` を `start_ts` に使う
- `inspection_date + end_time` を `end_ts` に使う
- `process_name` は固定で `出荷検査`
- `ng_total = 0` → `OK`
- `ng_total > 0` → `NG`

#### 想定ファイル名例
```text
SHIPCHK_202601.csv
```

---

## 補助マスタ

### `order_product_master.csv`
内装組立ログに `product_name` が無いため、以下の補助マスタを作成してください。

#### CSVヘッダ
```csv
order_no,product_name
```

#### ルール
- 正常系データの `order_no` は、すべてこのマスタに存在すること
- 3つの元ログに出る `order_no` は、このマスタと整合すること

---

## 正規化先の期待テーブル `work_log`

以下の列に正規化できるよう、CSVを生成してください。

```text
work_log_id         処理シーケンスNo.（期待結果CSVでは不要）
order_no            受注No.
product_name        製品名
process_name        工程名
worker_name         作業者名
start_ts            開始時間
end_ts              終了時間
elapsed_sec         純粋な end_ts - start_ts 差分秒
work_sec            稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒
result_cd           OK / NG
source_system       入力元種別
source_file_name    ファイル名
source_row_no       行番号
ingest_batch_id     取込実行ID
created_at          取込時間（期待結果CSVでは固定値でもよい）
```

### 正規化ルール
- `elapsed_sec` は必ず `end_ts - start_ts` の単純差分秒
- `work_sec` は昼休み・非稼働時間を除外した秒
- 正常系では `work_sec >= 0`
- 正常系では `work_sec <= elapsed_sec`
- 正常系では `end_ts >= start_ts`
- 同一 `order_no` は、工程ごとに1回のみ出現する
- したがって、正常系の期待結果では **`UNIQUE(order_no, process_name)` を満たすこと**

---

## 工程間のつながり

これは非常に重要です。

### 必須要件
- 正常系データでは、**同じ `order_no` が3つのログを通して一貫して使われること**
- 内装組立 → 外装組立 → 出荷検査 の順で時系列が成立すること
- 正常系データでは、後工程の `start_ts` は前工程の `end_ts` より前であってはいけない
- ただし、待ち時間はあってよい
- 一部は翌営業日に持ち越してよい
- この待ち時間や持ち越しにより、**工程間仕掛り（滞留）** が自然に見えるようにすること

---

## 異常系データの作り方

異常系CSVは、**主テーブルに入れてはいけないデータ** をサンプルとして作成してください。  
正常系CSVに混ぜず、別ファイルにしてください。

### 必ず含める異常例
- 同じデータの二重取り込み対象
- 必須列欠損
- 日時変換失敗
- `end_ts < start_ts`
- `elapsed_sec < 0` 相当になるデータ
- `work_sec < 0` または `work_sec > elapsed_sec` になり得る異常時刻
- 不正コード
- 数値変換失敗
- `UNIQUE(order_no, process_name)` 違反
- 列ズレ / 桁ズレを疑うデータ

### 工程ごとの異常例
#### 内装組立
- `start_marker` が `START` でない
- `end_marker` が `END` でない
- `order_no` が空

#### 外装組立
- `order_no` が空
- `product_name` が空
- `qr_read_ts` または `all_clear_ts` が不正
- `error_code` が致命エラー値

#### 出荷検査
- `order_no` が空
- `product_name` が空
- `inspector_name` が空
- `ng_total` が数値でない
- `inspection_date` / `start_time` / `end_time` が不正

---

## データの自然さ

生成するデータは、以下を満たしてください。

- 単にランダムではなく、**製造業の実績ログらしく**見えること
- 営業日・休業日・休憩時間を守ること
- 明らかに不自然な大量空き時間や極端な秒数を避けること
- ただし、工程間滞留が少し見えるように、待ち時間や翌営業日持ち越しを適度に入れること
- 品質検査は他工程より遅めなので、自然に仕掛りが溜まりやすい状態を作ること

---

## 出力時のお願い

### `generate_sample_data.py` について
- Python で実装してください
- なるべく標準ライブラリ中心で実装してください
- コメントを適度に入れてください
- 乱数シードを固定できるようにしてください
- 実行すると毎回同じサンプルが再現できるようにしてください

### `README_sample_data.md` について
以下を簡潔にまとめてください。

- 生成したファイル一覧
- 各ログの役割
- 正常系と異常系の違い
- `order_no` が3工程を繋ぐキーであること
- どのように `expected_work_log.csv` を作ったか
- どの異常データが reject 想定か

---

## 受入条件

以下を満たしてください。

1. 3種類の正常系CSVが生成される
2. `order_product_master.csv` が生成される
3. 正規化後期待結果 `expected_work_log.csv` が生成される
4. 異常系CSVが3種類生成される
5. 正常系では、同じ `order_no` が3工程を一貫して繋いでいる
6. 正常系では、営業日・休憩時間・残業なしルールを守る
7. 正常系では、工程順の時系列が成立する
8. 異常系では、reject 対象にしたい誤りが分かる
9. 品質検査を 340秒/台・4ライン相当にすることで、工程間滞留が自然に見える
10. 後で PostgreSQL と Streamlit デモへつなげやすい構成になっている

---

## 実装上の注意

- 今回はまず **サンプルデータの生成** が目的です
- PostgreSQL のDDLや Streamlit 実装までは不要です
- ただし、後でそこへ自然に接続できる列構成・粒度にしてください
- コードよりも **データの整合性と説明のしやすさ** を優先してください
