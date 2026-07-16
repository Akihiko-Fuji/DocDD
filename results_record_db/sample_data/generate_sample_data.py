"""results_record_db のセミナー用サンプルを再現可能な形で生成する。

このスクリプトをサンプルデータの正本とする。生成物は次を満たす。

- 2026-01-05〜2026-01-30 の19営業日（土日と1月12日を除く）
- 1日175〜275台、1製番につき3工程各1レコード
- order_no は ``ORD-YYMMDD-NNN`` 形式を全ファイルで保持
- 内装2台、外装3ライン、出荷検査4ラインの能力差を再現
- 同じ乱数シードから同じCSVを再生成できる
"""

from __future__ import annotations

import csv
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

SEED = 20260717
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
HOLIDAYS = {date(2026, 1, 12)}
WORK_START = time(8, 0)
LUNCH_START = time(12, 0)
LUNCH_END = time(13, 0)
WORK_END = time(17, 0)

# すべて仕様範囲（175〜275台）内。極端な乱高下を避ける。
DAILY_COUNTS = {
    date(2026, 1, 5): 194,
    date(2026, 1, 6): 225,
    date(2026, 1, 7): 232,
    date(2026, 1, 8): 218,
    date(2026, 1, 9): 240,
    date(2026, 1, 13): 224,
    date(2026, 1, 14): 231,
    date(2026, 1, 15): 219,
    date(2026, 1, 16): 226,
    date(2026, 1, 19): 235,
    date(2026, 1, 20): 228,
    date(2026, 1, 21): 242,
    date(2026, 1, 22): 221,
    date(2026, 1, 23): 230,
    date(2026, 1, 26): 238,
    date(2026, 1, 27): 216,
    date(2026, 1, 28): 244,
    date(2026, 1, 29): 227,
    date(2026, 1, 30): 231,
}

PRODUCTS = [
    ("RS-90X180-WH", 900, 1800),
    ("RS-120X200-GY", 1200, 2000),
    ("VB-50-80X150-IV", 800, 1500),
    ("VT-80X200-LG", 800, 2000),
    ("RS-180X220-BK", 1800, 2200),
    ("VB-60-90X160-BR", 900, 1600),
]

INTERNAL_WORKERS = ["HanaYamada", "KentoTakahashi"]
EXTERNAL_WEIGHTS = {
    "MunekiYoshimura": 0.200,
    "ShuheiYamashita": 0.433,
    "ToshioAndo": 0.367,
}
SHIPPING_WEIGHTS = {
    "加藤葵": 0.175,
    "小林陽": 0.275,
    "田中玲": 0.350,
    "鈴木ミカ": 0.200,
}
EXTERNAL_FACTORS = {
    "MunekiYoshimura": 0.6,
    "ShuheiYamashita": 1.3,
    "ToshioAndo": 1.1,
}
SHIPPING_FACTORS = {"加藤葵": 0.7, "小林陽": 1.1, "田中玲": 1.4, "鈴木ミカ": 0.8}


@dataclass
class OrderRecord:
    order_no: str
    product_name: str
    width_mm: int
    height_mm: int
    internal_worker: str
    external_worker: str
    inspector_name: str
    internal_start: datetime
    internal_end: datetime
    external_start: datetime
    external_end: datetime
    shipping_start: datetime
    shipping_end: datetime
    result_ng: int


def _next_business_day(day: date) -> date:
    current = day + timedelta(days=1)
    while current.weekday() >= 5 or current in HOLIDAYS:
        current += timedelta(days=1)
    return current


def _schedule_nonpreemptive(
    ready: datetime, release: datetime, duration_sec: int
) -> tuple[datetime, datetime]:
    """昼休みをまたがず、営業時間内に1作業を配置する。"""
    start = max(ready, release)
    while True:
        day = start.date()
        if day.weekday() >= 5 or day in HOLIDAYS:
            start = datetime.combine(_next_business_day(day), WORK_START)
            continue
        if start.time() < WORK_START:
            start = datetime.combine(day, WORK_START)
        elif LUNCH_START <= start.time() < LUNCH_END:
            start = datetime.combine(day, LUNCH_END)
        elif start.time() >= WORK_END:
            start = datetime.combine(_next_business_day(day), WORK_START)
            continue

        end = start + timedelta(seconds=duration_sec)
        lunch = datetime.combine(day, LUNCH_START)
        close = datetime.combine(day, WORK_END)
        if start < lunch < end:
            start = datetime.combine(day, LUNCH_END)
            continue
        if end > close:
            start = datetime.combine(_next_business_day(day), WORK_START)
            continue
        return start, end


def _weighted_labels(total: int, weights: dict[str, float], rng: random.Random) -> list[str]:
    """最大剰余法で総数を配分し、並び順だけを再現可能にシャッフルする。"""
    raw = {name: total * weight for name, weight in weights.items()}
    counts = {name: int(value) for name, value in raw.items()}
    remainder = total - sum(counts.values())
    order = sorted(weights, key=lambda name: raw[name] - counts[name], reverse=True)
    for name in order[:remainder]:
        counts[name] += 1
    labels = [name for name, count in counts.items() for _ in range(count)]
    rng.shuffle(labels)
    return labels


def build_orders() -> list[OrderRecord]:
    rng = random.Random(SEED)
    orders: list[OrderRecord] = []

    for day, count in DAILY_COUNTS.items():
        # 日ごとに能力比へ近づけ、特定日の一ラインへの偏りと翌日持越しを防ぐ。
        external_labels = iter(_weighted_labels(count, EXTERNAL_WEIGHTS, rng))
        shipping_labels = iter(_weighted_labels(count, SHIPPING_WEIGHTS, rng))
        internal_ready = {
            worker: datetime.combine(day, WORK_START) for worker in INTERNAL_WORKERS
        }
        external_ready = {
            worker: datetime.combine(day, WORK_START) for worker in EXTERNAL_WEIGHTS
        }
        shipping_ready = {
            worker: datetime.combine(day, WORK_START) for worker in SHIPPING_WEIGHTS
        }

        for index in range(1, count + 1):
            order_no = f"ORD-{day.strftime('%y%m%d')}-{index:03d}"
            product_name, width_mm, height_mm = PRODUCTS[(index + day.day) % len(PRODUCTS)]

            internal_worker = INTERNAL_WORKERS[(index - 1) % len(INTERNAL_WORKERS)]
            internal_duration = rng.randint(138, 162)
            internal_start, internal_end = _schedule_nonpreemptive(
                internal_ready[internal_worker],
                datetime.combine(day, WORK_START),
                internal_duration,
            )
            internal_ready[internal_worker] = internal_end + timedelta(seconds=rng.randint(5, 15))

            external_worker = next(external_labels)
            external_duration = max(
                120,
                int(rng.triangular(220, 290, 240) / EXTERNAL_FACTORS[external_worker]),
            )
            external_release = internal_end + timedelta(minutes=rng.randint(5, 15))
            external_start, external_end = _schedule_nonpreemptive(
                external_ready[external_worker], external_release, external_duration
            )
            external_ready[external_worker] = external_end + timedelta(seconds=rng.randint(5, 20))

            inspector_name = next(shipping_labels)
            shipping_duration = max(
                150,
                int(rng.gauss(340, 25) / SHIPPING_FACTORS[inspector_name]),
            )
            shipping_release = external_end + timedelta(minutes=rng.randint(10, 25))
            shipping_start, shipping_end = _schedule_nonpreemptive(
                shipping_ready[inspector_name], shipping_release, shipping_duration
            )
            shipping_ready[inspector_name] = shipping_end + timedelta(seconds=rng.randint(5, 20))

            # 約2%。再現性を優先し、order_noから決める。
            result_ng = 1 if (len(orders) + 1) % 53 == 0 else 0
            orders.append(
                OrderRecord(
                    order_no=order_no,
                    product_name=product_name,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    internal_worker=internal_worker,
                    external_worker=external_worker,
                    inspector_name=inspector_name,
                    internal_start=internal_start,
                    internal_end=internal_end,
                    external_start=external_start,
                    external_end=external_end,
                    shipping_start=shipping_start,
                    shipping_end=shipping_end,
                    result_ng=result_ng,
                )
            )
    validate_orders(orders)
    return orders


def validate_orders(orders: Iterable[OrderRecord]) -> None:
    records = list(orders)
    expected = sum(DAILY_COUNTS.values())
    assert len(records) == expected
    assert len({record.order_no for record in records}) == expected
    for record in records:
        assert record.order_no.startswith("ORD-")
        assert record.internal_end <= record.external_start
        assert record.external_end <= record.shipping_start
        for ts in (
            record.internal_start,
            record.internal_end,
            record.external_start,
            record.external_end,
            record.shipping_start,
            record.shipping_end,
        ):
            assert ts.date().weekday() < 5 and ts.date() not in HOLIDAYS
            assert WORK_START <= ts.time() <= WORK_END


def _write_rows(path: Path, header: list[str], rows: Iterable[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_normal_files(orders: list[OrderRecord]) -> None:
    internal_header = [
        "start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"
    ]
    for worker in INTERNAL_WORKERS:
        rows = []
        for order in orders:
            if order.internal_worker == worker:
                rows.append([
                    order.internal_start.strftime("%Y-%m-%d"),
                    order.internal_start.strftime("%H:%M:%S"),
                    "START",
                    order.internal_end.strftime("%Y-%m-%d"),
                    order.internal_end.strftime("%H:%M:%S"),
                    "END",
                    order.order_no,
                ])
        _write_rows(BASE_DIR / f"INTASM_{worker}_202601.csv", internal_header, rows)

    external_header = [
        "production_date_yymmdd", "check_no", "qr_read_ts", "all_clear_ts", "production_date",
        "packing_date", "tehai_no", "order_no", "product_name", "width_mm", "height_mm",
        "material_code1", "material_name1", "material_qty1", "material_code2", "material_name2",
        "material_qty2", "qr_clear_count", "initial_clear_count", "forced_clear_count",
        "material_pick_count", "error_code",
    ]
    for worker in EXTERNAL_WEIGHTS:
        rows = []
        for order in orders:
            if order.external_worker == worker:
                suffix = order.order_no[-10:].replace("-", "")
                rows.append([
                    order.external_start.strftime("%y%m%d"), f"CHK-{suffix}",
                    order.external_start.strftime("%Y-%m-%d %H:%M:%S"),
                    order.external_end.strftime("%Y-%m-%d %H:%M:%S"),
                    order.external_start.strftime("%Y-%m-%d"),
                    order.external_start.strftime("%Y-%m-%d"), f"TEH-{suffix}", order.order_no,
                    order.product_name, order.width_mm, order.height_mm, "MAT-001", "Frame", 1,
                    "MAT-002", "Panel", 1, 1, 1, 0, 2, "",
                ])
        _write_rows(BASE_DIR / f"EXTASM_{worker}_202601.csv", external_header, rows)

    shipping_header = [
        "inspector_name", "inspection_date", "slip_no", "product_name", "start_time", "end_time",
        "work_minutes", "tehai_no", "order_no", "bottom_ng_count", "slat_ng_count",
        "balance_ng_count", "ng_total",
    ]
    shipping_rows = []
    for order in orders:
        suffix = order.order_no[-10:].replace("-", "")
        shipping_rows.append([
            order.inspector_name, order.shipping_start.strftime("%Y-%m-%d"), f"SLIP-{suffix}",
            order.product_name, order.shipping_start.strftime("%H:%M:%S"),
            order.shipping_end.strftime("%H:%M:%S"),
            round((order.shipping_end - order.shipping_start).total_seconds() / 60, 1),
            f"TEH-{suffix}", order.order_no, order.result_ng, 0, 0, order.result_ng,
        ])
    _write_rows(BASE_DIR / "SHIPCHK_202601.csv", shipping_header, shipping_rows)

    _write_rows(
        BASE_DIR / "order_product_master.csv",
        ["order_no", "product_name"],
        ([order.order_no, order.product_name] for order in orders),
    )


def write_invalid_files(orders: list[OrderRecord]) -> None:
    first = orders[:6]
    internal_header = [
        "start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"
    ]
    internal_rows = [
        ["2026-01-05", "09:00:00", "START", "2026-01-05", "08:59:00", "END", first[0].order_no],
        ["2026-01-05", "09:00:00", "BEGIN", "2026-01-05", "09:03:00", "END", first[1].order_no],
        ["2026-01-05", "09:00:00", "START", "2026-01-05", "09:03:00", "FIN", first[2].order_no],
        ["2026-01-05", "09:00:00", "START", "2026-01-05", "09:03:00", "END", ""],
        ["2026-01-05", "09:00:00", "START", "2026-01-05", "09:03:00", "END", "ORD-260105-999"],
        ["2026-01-05", "09:00:00", "START", "2026-01-05", "09:03:00", "END", first[5].order_no],
    ]
    _write_rows(BASE_DIR / "INTASM_HanaYamadaInvalid_202601.csv", internal_header, internal_rows)

    external_header = ["order_no", "product_name", "qr_read_ts", "all_clear_ts", "error_code"]
    external_rows = [
        [first[0].order_no, first[0].product_name, "2026-01-05 09:00:00", "2026-01-05 09:05:00", "E001"],
        [first[1].order_no, first[1].product_name, "2026-01-05 09:10:00", "2026-01-05 09:05:00", ""],
        ["", first[2].product_name, "2026-01-05 09:00:00", "2026-01-05 09:05:00", ""],
        [first[3].order_no, first[3].product_name, "2026-99-05 09:00:00", "2026-01-05 09:05:00", ""],
        [first[4].order_no, "", "2026-01-05 09:00:00", "2026-01-05 09:05:00", ""],
    ]
    _write_rows(BASE_DIR / "EXTASM_MunekiYoshimuraInvalid_202601.csv", external_header, external_rows)

    shipping_header = [
        "inspector_name", "inspection_date", "product_name", "start_time", "end_time", "order_no", "ng_total"
    ]
    shipping_rows = [
        ["", "2026-01-05", first[0].product_name, "09:00:00", "09:05:00", first[0].order_no, 0],
        ["田中玲", "2026-01-05", first[1].product_name, "09:00:00", "09:05:00", "", 0],
        ["田中玲", "2026-99-05", first[2].product_name, "09:00:00", "09:05:00", first[2].order_no, 0],
        ["田中玲", "2026-01-05", first[3].product_name, "bad", "09:05:00", first[3].order_no, 0],
        ["田中玲", "2026-01-05", first[4].product_name, "09:00:00", "09:05:00", first[4].order_no, "未記入"],
    ]
    _write_rows(BASE_DIR / "SHIPCHK_202601_invalid.csv", shipping_header, shipping_rows)


def write_expected_file(orders: list[OrderRecord]) -> None:
    header = [
        "order_no", "product_name", "process_name", "worker_name", "start_ts", "end_ts",
        "elapsed_sec", "work_sec", "result_cd", "source_system", "source_file_name",
    ]
    rows: list[list[object]] = []
    for order in orders[:3]:
        stages = [
            ("内装組立", order.internal_worker, order.internal_start, order.internal_end, "OK",
             "internal_assembly_tool", f"INTASM_{order.internal_worker}_202601.csv"),
            ("外装組立", order.external_worker, order.external_start, order.external_end, "OK",
             "external_assembly_tool", f"EXTASM_{order.external_worker}_202601.csv"),
            ("出荷検査", order.inspector_name, order.shipping_start, order.shipping_end,
             "NG" if order.result_ng else "OK", "shipping_inspection_tool", "SHIPCHK_202601.csv"),
        ]
        for process, worker, start, end, result, source, file_name in stages:
            elapsed = int((end - start).total_seconds())
            rows.append([
                order.order_no, order.product_name, process, worker,
                start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"),
                elapsed, elapsed, result, source, file_name,
            ])
    _write_rows(ROOT_DIR / "sample_expected_work_log.csv", header, rows)


def print_summary(orders: list[OrderRecord]) -> None:
    print(f"generated orders: {len(orders)}")
    print(f"daily range: {min(DAILY_COUNTS.values())}..{max(DAILY_COUNTS.values())}")
    print("external:", dict(Counter(order.external_worker for order in orders)))
    print("shipping:", dict(Counter(order.inspector_name for order in orders)))
    by_day = defaultdict(int)
    for order in orders:
        by_day[order.shipping_start.date()] += 1
    assert by_day == DAILY_COUNTS


def main() -> None:
    orders = build_orders()
    write_normal_files(orders)
    write_invalid_files(orders)
    write_expected_file(orders)
    print_summary(orders)


if __name__ == "__main__":
    main()
