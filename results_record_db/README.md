## 今回の業務モデル
- 1製番を1台の個体識別単位とし、各工程の作業完了ごとに1レコード記録する。
- 製品は 1個流し
- 工程は固定で3つ。
 - 内部組立
 - 外部組立
 - 出荷検査
- 1製番あたり最大3件の実績レコードが登録される。

- 生産工程は直線ラインで"内部組立→外部組立→出荷検査"
- 意図的に、それぞれが違うログフォーマットを持つようにする
- データは2026-01-05から2026-01-30 までを用意する。
- 土日と1/12の祝日はお休みなので、1月は19営業日です。
- 生産は1直で8:00-17:00が工程稼働時間。
-  12:00-13:00までを休憩時間とします。モデルのため残業はありません。

- 最終的な評価KPIは3点
 - ①工程別時間別の作業台数実績
 - ②工程間の滞留状態を15分毎データ
 - ③作業者ごとの日別作業台数

### データを取り込むデータベーステーブルは下記を想定する
物理名               論理名
work_log_id         処理シーケンスNo.
order_no            受注No.(1台を識別する業務キー)
product_name        製品名
process_name        工程名
worker_name         作業者名
start_ts            開始時間(YYYY-MM-DD hh:mm:ss)
end_ts              終了時間(YYYY-MM-DD hh:mm:ss)
elapsed_sec         純粋なend_ts - start_ts差分秒
work_sec            稼働カレンダーに基づいて昼休み・非稼働時間を除いた正味作業時間秒
result_cd           作業結果 (OK / NG のいずれか)
source_system       入力元種別 (internal_assembly_tool / external_assembly_tool / shipping_inspection_tool のいずれか)
source_file_name    ファイル名
source_row_no       行数
ingest_batch_id     取込実行ID
created_at          取込時間(YYYY-MM-DD hh:mm:ss)

### PostgreSQL の型
work_log_id         BIGSERIAL
order_no            VARCHAR(30)
product_name        VARCHAR(100)
process_name        VARCHAR(30)
worker_name         VARCHAR(50)
start_ts            TIMESTAMP
end_ts              TIMESTAMP
elapsed_sec         INTEGER
work_sec            INTEGER
result_cd           VARCHAR(10)
source_system       VARCHAR(50)
source_file_name    VARCHAR(255)
source_row_no       INTEGER
ingest_batch_id     VARCHAR(30)
created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### 制約の初期案
PRIMARY KEY (work_log_id)
UNIQUE (order_no, process_name)
CHECK (process_name IN ('内部組立', '外部組立', '出荷検査'))
CHECK (end_ts >= start_ts)
CHECK (elapsed_sec >= 0)
CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)
CHECK (result_cd IN ('OK', 'NG'))
CHECK (source_system IN (
  'internal_assembly_tool',
  'external_assembly_tool',
  'shipping_inspection_tool'
))

### reject_id
source_system
source_file_name
source_row_no
reject_reason_cd
reject_reason_detail
raw_payload_json
ingest_batch_id
created_at

必須列欠損,日付変換失敗,稼働時間外,重複 はリジェクトする

### ingest_batch_id の生成ルール
ING_YYYYMMDD_HH24MISS_連番
例: ING_20260105_081530_001

### KPIを意識したindex
CREATE INDEX idx_work_log_process_end_ts ON work_log (process_name, end_ts);
CREATE INDEX idx_work_log_worker_end_ts  ON work_log (worker_name, end_ts);
CREATE INDEX idx_work_log_order_process  ON work_log (order_no, process_name);
