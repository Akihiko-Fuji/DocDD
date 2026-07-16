# results_record_db 仕様書・設計ガイド

## この文書の位置づけ

本書は `results_record_db` の**開発仕様に関する一次情報（source of truth）**である。
異なる3種類の実績ログを共通形式へ変換し、PostgreSQLへ登録して、StreamlitでKPIを表示するまでを定義する。

初めて読む場合は、先に「第I部 仕様」を読めば、何を作るかを一通り把握できる。
「第II部 解説」は、仕様をなぜこの形にしたかを理解するための補足であり、実装判断で迷った場合は第I部を優先する。

- **第I部 仕様**：実装・テストで守る内容
- **第II部 解説**：初学者向けの背景説明
- 環境構築：[`WINDOWS_SETUP.md`](./WINDOWS_SETUP.md)
- 最短実行手順：[`quickstart.md`](./quickstart.md)

---

# 第I部 仕様

## 1. 目的と対象範囲

工程ごとに形式が異なるCSVまたはExcelログを、共通テーブル `work_log` へ正規化して登録する。
登録できない行は、理由付きで `work_log_reject` へ記録する。

対象工程は次の固定3工程である。

```text
内装組立 → 外装組立 → 出荷検査
```

本教材で実現するKPIは次の3つである。

| KPI | 内容 | 主な集計軸 |
|---|---|---|
| KPI1 | 工程別・時間別の完了台数 | `process_name` × `end_ts` の時間帯 |
| KPI2 | 工程間で次工程未着手の製番数 | `order_no` × 前工程完了・次工程開始 |
| KPI3 | 作業者別・日別の完了台数 | `worker_name` × `process_name` × `end_ts` の日付 |

### 対象外

- 手戻り・再加工・同一工程の複数回実績
- 稼働カレンダーマスタとの連携
- 認証・認可、冗長化、監視、バックアップなどの本番運用機能
- 複数タイムゾーン
- 同時取込の厳密な排他制御

## 2. 業務モデル

| 項目 | 仕様 |
|---|---|
| 個体識別単位 | 1製番（`order_no`）= 1台 |
| 生産方式 | 1個流し |
| 実績粒度 | 1製番 × 1工程 = 1レコード |
| 最大実績数 | 1製番あたり3レコード |
| 工程順 | 内装組立 → 外装組立 → 出荷検査 |
| 対象期間 | 2026-01-05〜2026-01-30 |
| 休業日 | 土日、2026-01-12 |
| 稼働時間 | 08:00〜12:00、13:00〜17:00 |
| タイムゾーン | 日本の工場現地時刻。DB型は教材簡略化のため `TIMESTAMP` |

### `order_no` の定義

`order_no` は3工程を結ぶ業務キーである。サンプルデータでは次の形式を使用する。

```text
ORD-YYMMDD-NNN
例: ORD-260105-001
```

取込時に行う正規化は**前後空白の除去だけ**とする。

- ハイフンを保持する
- 英字の大文字・小文字を保持する
- 記号を除去しない
- `ORD260105001` と `ORD-260105-001` は別の値として扱う

これは、表記を過度に変換して異なる業務キーを同一視することを防ぐためである。

## 3. 入力ファイル仕様

### 3.1 ファイル名規則

| 工程 | 受理する基本形式 | 作業者の取得元 |
|---|---|---|
| 内装組立 | `INTASM_<作業者>_<YYYYMMまたはYYYYMMDD>.<拡張子>` | ファイル名 |
| 外装組立 | `EXTASM_<作業者>_<YYYYMMまたはYYYYMMDD>.<拡張子>` | ファイル名 |
| 外装組立（ライン付き） | `EXTASM_<ライン>_<作業者>_<YYYYMMまたはYYYYMMDD>.<拡張子>` | ファイル名 |
| 出荷検査 | `SHIPCHK_<任意識別子>.<拡張子>` | `inspector_name` 列 |

拡張子は `.csv`、`.xlsx`、`.xlsm` を受理する。
作業者名は英字に限定せず、日本語も許容する。ただし `_` は区切り文字のため作業者名には使用しない。

旧教材との互換性のため、`shipping_inspection_log.csv` と
`shipping_inspection_log_invalid.csv` も受理するが、新規データでは `SHIPCHK_...` を使用する。

### 3.2 内装組立ログ

代表ファイル：`INTASM_HanaYamada_202601.csv`

| 元列 | 必須 | 正規化先・処理 |
|---|:---:|---|
| `start_date` | ○ | `start_time` と結合して `start_ts` |
| `start_time` | ○ | `start_date` と結合して `start_ts` |
| `start_marker` | ○ | `START` 固定。保存しない |
| `end_date` | ○ | `end_time` と結合して `end_ts` |
| `end_time` | ○ | `end_date` と結合して `end_ts` |
| `end_marker` | ○ | `END` 固定。保存しない |
| `order_no` | ○ | 前後空白を除去して保持 |

補完値：

- `product_name`：`order_product_master.csv` から `order_no` 完全一致で取得
- `worker_name`：ファイル名から取得し、空白を除去
- `process_name`：`内装組立`
- `source_system`：`internal_assembly_tool`
- `result_cd`：`OK`

### 3.3 外装組立ログ

代表ファイル：`EXTASM_MunekiYoshimura_202601.csv`

| 元列 | 必須 | 正規化先・処理 |
|---|:---:|---|
| `order_no` | ○ | 前後空白を除去して保持 |
| `product_name` | ○ | 前後空白を除去して保持 |
| `qr_read_ts` | ○ | `start_ts` |
| `all_clear_ts` | ○ | `end_ts` |
| `error_code` | △ | 空なら正常。値があれば reject |

補完値：

- `worker_name`：ファイル名から取得し、空白を除去
- `process_name`：`外装組立`
- `source_system`：`external_assembly_tool`
- `result_cd`：`OK`

資材、寸法、消込数等の余剰列は `work_log` へ保存しないが、reject時の `raw_payload_json` には元行の全列を保存する。

### 3.4 出荷検査ログ

代表ファイル：`SHIPCHK_202601.csv`

| 元列 | 必須 | 正規化先・処理 |
|---|:---:|---|
| `inspector_name` | ○ | 空白を除去して `worker_name` |
| `inspection_date` | ○ | `start_time`、`end_time` と結合 |
| `start_time` | ○ | `start_ts` |
| `end_time` | ○ | `end_ts` |
| `order_no` | ○ | 前後空白を除去して保持 |
| `product_name` | ○ | 前後空白を除去して保持 |
| `ng_total` | ○ | `0`なら `OK`、1以上なら `NG` |

補完値：

- `process_name`：`出荷検査`
- `source_system`：`shipping_inspection_tool`

`end_time < start_time` の場合に限り、出荷検査の夜間跨ぎとして、終了日を翌営業日に補正する。
土日と2026-01-12を飛ばす。内装組立・外装組立ではこの補正を行わず reject とする。

## 4. 共通正規化仕様

### 4.1 `worker_name`

- 前後空白、半角空白、全角空白を除去する
- 漢字とローマ字の自動変換はしない
- 英字の大文字・小文字は保持する
- 行に `worker_name` があり、ファイル名由来の値と一致しない場合は reject

### 4.2 時間

```text
elapsed_sec = end_ts - start_ts の単純差分秒
```

`work_sec` は、期間中の次の稼働時間だけを積算する。

```text
08:00〜12:00
13:00〜17:00
```

土日と2026-01-12は0秒とする。日をまたぐ場合は日ごとに計算する。

| 例 | `elapsed_sec` | `work_sec` |
|---|---:|---:|
| 07:50〜08:10 | 1,200 | 600 |
| 11:50〜13:10 | 4,800 | 1,200 |
| 16:50〜17:10 | 1,200 | 600 |
| 金曜16:50〜翌営業日08:10 | 経過全秒 | 1,200 |

### 4.3 `source_row_no`

CSV・Excelともに、ヘッダを除いた最初のデータ行を1として記録する。

### 4.4 `ingest_batch_id`

1ファイルの取込ごとに1つ発行する。

```text
ING_YYYYMMDD_HHMMSS_連番
例: ING_20260105_081530_001
```

- 1回のCLI実行で複数ファイルを扱う場合もファイルごとに別ID
- 最大30文字
- 連番はアプリケーション実行内で採番
- 本番用途のグローバル一意性は保証しない

## 5. DB仕様

### 5.1 `work_log`

| カラム | 型 | NULL | 内容 |
|---|---|:---:|---|
| `work_log_id` | `BIGSERIAL` | 不可 | 主キー |
| `order_no` | `VARCHAR(30)` | 不可 | 製番 |
| `product_name` | `VARCHAR(100)` | 不可 | 製品名 |
| `process_name` | `VARCHAR(30)` | 不可 | 工程名 |
| `worker_name` | `VARCHAR(50)` | 不可 | 作業者名 |
| `start_ts` | `TIMESTAMP` | 不可 | 開始日時 |
| `end_ts` | `TIMESTAMP` | 不可 | 終了日時 |
| `elapsed_sec` | `INTEGER` | 不可 | 経過秒 |
| `work_sec` | `INTEGER` | 不可 | 正味作業秒 |
| `result_cd` | `VARCHAR(10)` | 不可 | `OK` / `NG` |
| `source_system` | `VARCHAR(50)` | 不可 | 入力元 |
| `source_file_name` | `VARCHAR(255)` | 不可 | 元ファイル名 |
| `source_row_no` | `INTEGER` | 不可 | 元行番号 |
| `ingest_batch_id` | `VARCHAR(30)` | 不可 | 取込ID |
| `created_at` | `TIMESTAMP` | 不可 | 取込日時 |

主要制約：

```sql
UNIQUE (order_no, process_name)
CHECK (process_name IN ('内装組立', '外装組立', '出荷検査'))
CHECK (result_cd IN ('OK', 'NG'))
CHECK (end_ts >= start_ts)
CHECK (elapsed_sec >= 0)
CHECK (work_sec >= 0 AND work_sec <= elapsed_sec)
```

### 5.2 `work_log_reject`

| カラム | 型 | 内容 |
|---|---|---|
| `reject_id` | `BIGSERIAL` | 主キー |
| `source_system` | `VARCHAR(50)` | 入力元 |
| `source_file_name` | `VARCHAR(255)` | 元ファイル名 |
| `source_row_no` | `INTEGER` | 元行番号 |
| `reject_reason_cd` | `VARCHAR(50)` | 理由コード |
| `reject_reason_detail` | `TEXT` | 詳細 |
| `raw_payload_json` | `TEXT` | 元入力行の全列をJSON化したもの |
| `ingest_batch_id` | `VARCHAR(30)` | 取込ID |
| `created_at` | `TIMESTAMP` | reject記録日時 |

## 6. reject・重複仕様

| 理由コード | 条件 |
|---|---|
| `MISSING_REQUIRED` | 必須値が空、START/ENDマーカー不正 |
| `DATE_PARSE_ERROR` | 日時変換失敗 |
| `END_BEFORE_START` | 補正対象外で終了が開始より前 |
| `WORK_EXCEEDS_ELAPSED` | `work_sec > elapsed_sec` |
| `INVALID_RESULT_CD` | `ng_total` 等を結果へ変換できない |
| `ERROR_CODE_PRESENT` | 外装ログの `error_code` が空でない |
| `INVALID_WORKER_NAME` | 作業者を解決できない、または不一致 |
| `DUPLICATE_KEY` | 同じ `order_no`・`process_name` が既存または同一ファイル内に存在 |
| `MASTER_NOT_FOUND` | 内装ログの `order_no` が補助マスタに存在しない |
| `DB_CONSTRAINT_ERROR` | その他のDB登録エラー |

同じ正常ファイルを2回取り込んだ場合、2回目は `work_log` を増やさず、各行を `DUPLICATE_KEY` として記録する。
事前判定に加えてDBのUNIQUE制約を最終防衛とする。

## 7. KPI仕様

### 7.1 KPI1：工程別・時間別完了台数

- `end_ts` の日付を期間条件に使用
- `end_ts` の時を `08:00`〜`17:00` の1時間枠へ分類
- 工程・作業者フィルタを適用
- データがない時間枠も0件で表示

### 7.2 KPI2：工程間滞留

工程間滞留は、**前工程が完了し、次工程がまだ開始されていない製番**と定義する。

対象区間：

```text
内装組立.end_ts → 外装組立.start_ts
外装組立.end_ts → 出荷検査.start_ts
```

評価時刻 `ts` で次を満たす製番を1件として数える。

```text
from_end <= ts
かつ
to_start が存在しない、または to_start > ts
```

- 15分間隔で集計
- 表示時刻は08:00以上17:00未満
- 前日以前に完了し、当日開始した持越しも含む
- `to_start < from_end` は時系列異常として明細に残し、推移件数から除外
- 次工程で作業中の製番は工程間滞留に含めない
- 1製番・1工程・1レコード前提のため、複数候補からの選択処理は行わない

明細列：

```text
order_no, pair, from_end, to_start, is_invalid_sequence
```

### 7.3 KPI3：作業者別・日別完了台数

- `end_ts` の日付を使用
- `work_date`、`process_name`、`worker_name` 単位で件数集計
- 期間・工程・作業者フィルタを適用

## 8. サンプルデータ仕様

`sample_data/generate_sample_data.py` を生成物の正本とする。

| 項目 | 生成仕様 |
|---|---|
| 乱数シード | 固定 |
| 営業日 | 19日 |
| 日別台数 | 194〜244台（仕様範囲175〜275台） |
| 総製番数 | 4,321件 |
| 正常実績 | 3工程すべてに同一 `order_no` が1回ずつ登場 |
| `order_no` | 全正常CSV・マスタ・期待結果でハイフン付き形式を保持 |
| 工程順 | `内装終了 <= 外装開始`、`外装終了 <= 出荷検査開始` |
| NG率 | 約2% |

作業者能力差は件数比と作業時間係数で表現する。

| 工程 | 作業者 | 目標件数比 |
|---|---|---:|
| 外装 | MunekiYoshimura | 20.0% |
| 外装 | ShuheiYamashita | 43.3% |
| 外装 | ToshioAndo | 36.7% |
| 出荷検査 | 加藤葵 | 17.5% |
| 出荷検査 | 小林陽 | 27.5% |
| 出荷検査 | 田中玲 | 35.0% |
| 出荷検査 | 鈴木ミカ | 20.0% |

再生成：

```bash
cd results_record_db
python sample_data/generate_sample_data.py
```

生成後、`order_product_master.csv` に正常ログで使わない旧製番を残してはならない。

## 9. 実装構成

```text
results_record_db/
├─ README.md                         # 本仕様書（一次情報）
├─ quickstart.md                     # 最短実行・AIプロンプト例
├─ WINDOWS_SETUP.md                  # Windows準備
├─ results_record_db_LOCAL_POSTGRESQL_SETUP.md
├─ requirements.txt
├─ pytest.ini
├─ ddl/
│  └─ ddl_results_record_db.sql
├─ sample_data/
│  ├─ generate_sample_data.py        # サンプル生成の正本
│  ├─ INTASM_*.csv
│  ├─ EXTASM_*.csv
│  ├─ SHIPCHK_*.csv
│  └─ order_product_master.csv
├─ sample_expected_work_log.csv
├─ src/
│  ├─ db.py                          # DB接続・ORM
│  ├─ ingest.py                      # 共通取込ロジック
│  ├─ ingest_cli.py                  # CLI入口
│  └─ streamlit_app.py               # Web入口・KPI
└─ tests/
   ├─ conftest.py
   ├─ test_ingest.py
   ├─ test_ingest_property_like.py
   ├─ test_duplicate.py
   └─ test_kpi.py
```

入口がCLIでもWebでも、変換・検証・reject・登録は `ingest.py` を使用する。
`ingest_core.py` という別ファイルは存在しない。

## 10. テスト・受入条件

### 自動テスト

通常の `pytest` はSQLiteインメモリDBを使用する。目的は、取込規則、制約、重複、KPI計算を高速かつ繰り返し可能に確認することである。

```bash
pytest -q
```

### PostgreSQL確認

SQLiteとPostgreSQLには型・DDL・ドライバの差があるため、セミナー前に別途、実際のPostgreSQLで次を確認する。

- DDLがエラーなく適用できる
- 正常6ファイルを取り込める
- 正常件数・reject件数が期待どおり
- Streamlitが起動し、KPI3種を表示できる

### 最低受入条件

- 正常行が仕様どおり正規化される
- 異常行が理由付きで `work_log_reject` に入る
- `order_no` のハイフン等が保持される
- 同一データの再投入で `work_log` が増えない
- KPI2が次工程の**開始**で滞留を終了する
- サンプル生成を繰り返して同じデータを得られる
- 3工程、マスタ、期待結果の `order_no` が一致する

---

# 第II部 初学者向け解説

## 11. なぜ正規化するのか

3工程のログは同じ製品を扱っていても、列名や時刻の持ち方が異なる。
そのままグラフを作ると、工程ごとに別の変換処理が必要になり、同じ意味の値でも判定がずれやすい。

そこで、取込時に次の共通形へ変換する。

```text
異なる元ログ
  ↓ 列を選ぶ・意味を補う・検証する
work_log（共通形式）
  ↓
同じ定義でKPIを計算
```

## 12. rejectを残す理由

異常行を黙って捨てると、元データが何件あり、なぜ件数が減ったかを説明できない。
`work_log_reject` に元行と理由を残すことで、次の確認ができる。

- どのファイルの何行目か
- なぜ登録されなかったか
- どの取込実行で発生したか
- 元行にはどの値が入っていたか

## 13. KPI2で「次工程開始」を使う理由

前工程が終わった製品は、次工程が始まるまで工程間の仕掛品である。
次工程が始まった後は、製品は工程内で作業中であり、工程間滞留ではない。

```text
前工程作業中 ─ 前工程完了 ── 工程間滞留 ── 次工程開始 ─ 次工程作業中
```

次工程完了まで数えてしまうと、「工程間で待っている時間」と「次工程で作業している時間」が混ざる。
本教材では両者を分離する。

## 14. 仕様・実装・テストの関係

DocDDで重要なのは、文書を作ること自体ではなく、判断基準を固定することである。

```text
仕様書：何を正しいとするか
実装　：仕様を処理へ変換する
テスト：実装が仕様どおりか確認する
```

例えば `order_no` を「trimのみ」と決めたなら、実装がハイフンを削除してはいけない。
また、その違いをテストで確認できなければ、後の変更で同じ不整合が再発する。

## 15. 教材を実運用へ展開する場合

本教材は設計から実装・検証までを説明するための簡略モデルである。
実運用では少なくとも次を追加検討する。

- 稼働カレンダーマスタ
- 作業者ID・製品マスタの履歴管理
- 再加工・訂正・取消の履歴
- 取込実行管理テーブルとUUID等の一意な実行ID
- 認証・認可
- 監視、バックアップ、復旧手順
- PostgreSQLを使用した結合テストとCI
- タイムゾーン方針

これらを最初から教材へすべて入れると主題がぼやけるため、本テーマでは対象外として明示している。
