from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from streamlit_app import build_kpi1, build_kpi2, build_kpi3


def _df() -> pd.DataFrame:
    rows = [
        {"order_no":"O1","product_name":"P1","process_name":"内装組立","worker_name":"W1","start_ts":datetime(2026,1,5,7,55),"end_ts":datetime(2026,1,5,8,0),"elapsed_sec":300,"work_sec":0,"result_cd":"OK"},
        {"order_no":"O1","product_name":"P1","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,8,30),"end_ts":datetime(2026,1,5,9,0),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
        {"order_no":"O1","product_name":"P1","process_name":"出荷検査","worker_name":"W3","start_ts":datetime(2026,1,5,9,30),"end_ts":datetime(2026,1,5,10,0),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
        {"order_no":"O2","product_name":"P2","process_name":"内装組立","worker_name":"W1","start_ts":datetime(2026,1,5,8,0),"end_ts":datetime(2026,1,5,8,30),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
        {"order_no":"O2","product_name":"P2","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,9,0),"end_ts":datetime(2026,1,5,9,45),"elapsed_sec":2700,"work_sec":2700,"result_cd":"OK"},
    ]
    df = pd.DataFrame(rows)
    df['work_date'] = df['end_ts'].dt.date
    df['hour_bucket'] = df['end_ts'].dt.floor('h')
    return df


def test_kpi1_changes_with_filters() -> None:
    df = _df()
    allv = build_kpi1(df, date(2026,1,5), date(2026,1,5), ["内装組立","外装組立","出荷検査"], ["W1","W2","W3"])
    sub = build_kpi1(df, date(2026,1,5), date(2026,1,5), ["内装組立"], ["W1"])
    assert len(sub) < len(allv)
    target = sub[(sub['hour_slot'] == '08:00') & (sub['process_name'].astype(str) == '内装組立')].iloc[0]
    assert target['work_count'] == 2


def test_kpi3_changes_with_worker_filter() -> None:
    df = _df()
    allv = build_kpi3(df, date(2026,1,5), date(2026,1,5), ["内装組立","外装組立","出荷検査"], ["W1","W2","W3"])
    sub = build_kpi3(df, date(2026,1,5), date(2026,1,5), ["内装組立","外装組立","出荷検査"], ["W1"])
    assert len(sub) < len(allv)


def test_kpi2_returns_both_stagnation_pairs() -> None:
    df = _df()
    trend, detail = build_kpi2(df, date(2026,1,5), date(2026,1,5))
    assert not detail.empty
    assert not trend.empty
    assert set(detail['pair'].unique()) == {'内装組立 → 外装組立','外装組立 → 出荷検査'}


def test_kpi2_long_stagnation_is_counted_across_multiple_buckets() -> None:
    df = _df()
    # O3 は 08:00 に内装完了し、外装開始は 09:30。
    # 08:00 〜 09:15 の各15分バケットで滞留として継続カウントされることを確認する。
    extra = pd.DataFrame([
        {"order_no":"O3","product_name":"P3","process_name":"内装組立","worker_name":"W1","start_ts":datetime(2026,1,5,7,30),"end_ts":datetime(2026,1,5,8,0),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
        {"order_no":"O3","product_name":"P3","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,9,30),"end_ts":datetime(2026,1,5,10,0),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
    ])
    extra["work_date"] = extra["end_ts"].dt.date
    extra["hour_bucket"] = extra["end_ts"].dt.floor("h")
    df = pd.concat([df, extra], ignore_index=True)

    trend, _ = build_kpi2(df, date(2026,1,5), date(2026,1,5))
    pair = trend[trend["pair"] == "内装組立 → 外装組立"].set_index("timestamp")

    assert pair.loc[pd.Timestamp("2026-01-05 08:00:00"), "stagnation_count"] >= 1
    assert pair.loc[pd.Timestamp("2026-01-05 09:15:00"), "stagnation_count"] >= 1
    assert pair.loc[pd.Timestamp("2026-01-05 09:30:00"), "stagnation_count"] <= pair.loc[pd.Timestamp("2026-01-05 09:15:00"), "stagnation_count"]


def test_kpi2_carryover_before_previous_day_is_included() -> None:
    df = _df()
    extra = pd.DataFrame([
        {"order_no":"O9","product_name":"P9","process_name":"内装組立","worker_name":"W1","start_ts":datetime(2026,1,2,8,0),"end_ts":datetime(2026,1,2,9,0),"elapsed_sec":3600,"work_sec":3600,"result_cd":"OK"},
        {"order_no":"O9","product_name":"P9","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,8,30),"end_ts":datetime(2026,1,5,9,0),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
    ])
    extra["work_date"] = extra["end_ts"].dt.date
    extra["hour_bucket"] = extra["end_ts"].dt.floor("h")
    df = pd.concat([df, extra], ignore_index=True)
    trend, detail = build_kpi2(df, date(2026,1,5), date(2026,1,5))
    assert (detail["order_no"] == "O9").any()
    pair = trend[trend["pair"] == "内装組立 → 外装組立"].set_index("timestamp")
    assert pair.loc[pd.Timestamp("2026-01-05 08:00:00"), "stagnation_count"] >= 1


def test_kpi2_invalid_sequence_remains_in_detail_but_not_counted() -> None:
    df = _df()
    extra = pd.DataFrame([
        {"order_no":"OX","product_name":"PX","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,8,0),"end_ts":datetime(2026,1,5,8,10),"elapsed_sec":600,"work_sec":600,"result_cd":"OK"},
        {"order_no":"OX","product_name":"PX","process_name":"出荷検査","worker_name":"W3","start_ts":datetime(2026,1,5,7,0),"end_ts":datetime(2026,1,5,7,50),"elapsed_sec":3000,"work_sec":3000,"result_cd":"OK"},
    ])
    extra["work_date"] = extra["end_ts"].dt.date
    extra["hour_bucket"] = extra["end_ts"].dt.floor("h")
    df = pd.concat([df, extra], ignore_index=True)
    trend, detail = build_kpi2(df, date(2026,1,5), date(2026,1,5))
    invalid = detail[(detail["order_no"] == "OX") & (detail["pair"] == "外装組立 → 出荷検査")]
    assert not invalid.empty
    assert bool(invalid.iloc[0]["is_invalid_sequence"]) is True
    pair = trend[trend["pair"] == "外装組立 → 出荷検査"]
    assert (pair["stagnation_count"] >= 0).all()

def test_kpi2_uses_next_process_start_not_end() -> None:
    df = _df()
    extra = pd.DataFrame([
        {"order_no":"OY","product_name":"PY","process_name":"内装組立","worker_name":"W1","start_ts":datetime(2026,1,5,8,0),"end_ts":datetime(2026,1,5,8,30),"elapsed_sec":1800,"work_sec":1800,"result_cd":"OK"},
        {"order_no":"OY","product_name":"PY","process_name":"外装組立","worker_name":"W2","start_ts":datetime(2026,1,5,8,45),"end_ts":datetime(2026,1,5,9,0),"elapsed_sec":900,"work_sec":900,"result_cd":"OK"},
    ])
    extra["work_date"] = extra["end_ts"].dt.date
    extra["hour_bucket"] = extra["end_ts"].dt.floor("h")
    df = pd.concat([df, extra], ignore_index=True)

    trend, detail = build_kpi2(df, date(2026,1,5), date(2026,1,5))
    row = detail[(detail["order_no"] == "OY") & (detail["pair"] == "内装組立 → 外装組立")].iloc[0]
    assert bool(row["is_invalid_sequence"]) is False
    assert row["to_start"] == pd.Timestamp("2026-01-05 08:45:00")

    pair = trend[trend["pair"] == "内装組立 → 外装組立"].set_index("timestamp")
    # 08:30 完了から08:45開始までだけ滞留としてカウントする。
    assert pair.loc[pd.Timestamp("2026-01-05 08:30:00"), "stagnation_count"] >= 1
    assert pair.loc[pd.Timestamp("2026-01-05 08:45:00"), "stagnation_count"] <= pair.loc[pd.Timestamp("2026-01-05 08:30:00"), "stagnation_count"]
