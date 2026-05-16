from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from db import WorkLog, WorkLogReject
from ingest import (
    REJECT_DB_CONSTRAINT_ERROR,
    _batch_id,
    _next_business_day,
    apply_ingest_plan,
    calc_work_sec,
    ingest_file,
    ingest_files,
    prepare_ingest_file,
)
def test_internal_start_marker_reject(session: Session, tmp_path: Path, write_csv) -> None:
    """内装組立で start_marker 不正時に reject されることを確認する。"""
    p = tmp_path / 'INTASM_TestWorker_202601.csv'
    write_csv(p,["start_date","start_time","start_marker","end_date","end_time","end_marker","order_no","discard_col"],[
        {"start_date":"2026-01-05","start_time":"08:00:00","start_marker":"BAD","end_date":"2026-01-05","end_time":"08:10:00","end_marker":"END","order_no":"ORD1","discard_col":"x"},
    ])
    r = ingest_file(session, str(p), order_product_map={"ORD1":"製品A"}, ingest_batch_id='B1')
    session.commit()
    assert r.inserted == 0 and r.rejected == 1
    reject = session.query(WorkLogReject).one()
    assert reject.reject_reason_cd == 'MISSING_REQUIRED'
    payload = json.loads(reject.raw_payload_json)
    assert payload['discard_col'] == 'x'


def test_internal_end_marker_reject(session: Session, tmp_path: Path, write_csv) -> None:
    """内装組立で end_marker 不正時に reject されることを確認する。"""
    p = tmp_path / 'INTASM_TestWorker_202601.csv'
    write_csv(p,["start_date","start_time","start_marker","end_date","end_time","end_marker","order_no"],[
        {"start_date":"2026-01-05","start_time":"08:00:00","start_marker":"START","end_date":"2026-01-05","end_time":"08:10:00","end_marker":"BAD","order_no":"ORD1"},
    ])
    r = ingest_file(session, str(p), order_product_map={"ORD1":"製品A"}, ingest_batch_id='B1')
    session.commit()
    assert r.inserted == 0 and r.rejected == 1
    assert session.query(WorkLogReject).one().reject_reason_cd == 'MISSING_REQUIRED'


def test_internal_master_not_found_reject(session: Session, tmp_path: Path, write_csv) -> None:
    """内装組立でマスタ未登録 order_no が reject されることを確認する。"""
    p = tmp_path / 'INTASM_TestWorker_202601.csv'
    write_csv(p,["start_date","start_time","start_marker","end_date","end_time","end_marker","order_no"],[
        {"start_date":"2026-01-05","start_time":"08:00:00","start_marker":"START","end_date":"2026-01-05","end_time":"08:10:00","end_marker":"END","order_no":"ORD_MISSING"},
    ])
    r = ingest_file(session, str(p), order_product_map={"ORD1":"製品A"}, ingest_batch_id='B1')
    session.commit()
    assert r.inserted == 0 and r.rejected == 1
    assert session.query(WorkLogReject).one().reject_reason_cd == 'MASTER_NOT_FOUND'


def test_external_error_and_end_before_start(session: Session, tmp_path: Path, write_csv) -> None:
    """外装組立で異常行がそれぞれ reject されることを確認する。"""
    p = tmp_path/'EXTASM_SatoKen_202601.csv'
    write_csv(p,["order_no","product_name","qr_read_ts","all_clear_ts","error_code"],[
        {"order_no":"ORD2","product_name":"製品B","qr_read_ts":"2026-01-05 09:10:00","all_clear_ts":"2026-01-05 09:00:00","error_code":""},
        {"order_no":"ORD3","product_name":"製品C","qr_read_ts":"2026-01-05 09:00:00","all_clear_ts":"2026-01-05 09:10:00","error_code":"E1"},
    ])
    r = ingest_file(session, str(p), ingest_batch_id='B2')
    session.commit()
    assert r.inserted == 0 and r.rejected == 2


def test_shipping_next_business_day(session: Session, tmp_path: Path, write_csv) -> None:
    """出荷検査の日跨ぎ終了時刻が翌営業日に補正されることを確認する。"""
    p = tmp_path/'SHIPCHK_202601.csv'
    write_csv(p,["inspector_name","inspection_date","start_time","end_time","order_no","product_name","ng_total"],[{"inspector_name":"I","inspection_date":"2026-01-09","start_time":"16:50:00","end_time":"08:10:00","order_no":"O","product_name":"P","ng_total":"0"}])
    ingest_file(session, str(p), ingest_batch_id='B3')
    session.commit()
    row = session.query(WorkLog).one()
    # 2026-01-12 は ingest.HOLIDAYS のため、翌営業日は 2026-01-13。
    assert row.end_ts.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-13 08:10:00'


def test_calc_work_sec_cases() -> None:
    """calc_work_sec の代表ケースを確認する。"""
    assert calc_work_sec(datetime(2026,1,5,8,0), datetime(2026,1,5,8,10)) == 600
    assert calc_work_sec(datetime(2026,1,5,11,50), datetime(2026,1,5,13,10)) == 1200
    # 7:50〜8:10 は営業時間前10分を除外し、8:00〜8:10 の600秒のみを計上。
    assert calc_work_sec(datetime(2026,1,5,7,50), datetime(2026,1,5,8,10)) == 600
    assert calc_work_sec(datetime(2026,1,5,16,50), datetime(2026,1,5,17,10)) == 600
    assert calc_work_sec(datetime(2026,1,10,8,0), datetime(2026,1,10,8,10)) == 0
    assert calc_work_sec(datetime(2026,1,12,8,0), datetime(2026,1,12,8,10)) == 0
    assert calc_work_sec(datetime(2026,1,9,16,50), datetime(2026,1,13,8,10)) == 1200


def test_calc_work_sec_end_before_start_raises_value_error() -> None:
    """calc_work_sec が end<start で ValueError を送出することを確認する。"""
    with pytest.raises(ValueError):
        calc_work_sec(datetime(2026, 1, 5, 8, 10), datetime(2026, 1, 5, 8, 0))


def test_external_worker_name_mismatch_reject(session: Session, tmp_path: Path, write_csv) -> None:
    """外装組立で作業者名不一致が reject されることを確認する。"""
    p = tmp_path/'EXTASM_SatoKen_202601.csv'
    # 実運用の外装組立CSVに worker_name 列は通常ないが、
    # 余剰列が存在した異常入力でもファイル名由来 worker_name との不一致を reject できることを確認する。
    write_csv(p,["order_no","product_name","qr_read_ts","all_clear_ts","error_code","worker_name"],[
        {"order_no":"ORD9","product_name":"製品Z","qr_read_ts":"2026-01-05 09:00:00","all_clear_ts":"2026-01-05 09:10:00","error_code":"","worker_name":"YamadaTaro"},
    ])
    r = ingest_file(session, str(p), ingest_batch_id='B9')
    session.commit()
    assert r.inserted == 0 and r.rejected == 1
    reject = session.query(WorkLogReject).one()
    assert reject.reject_reason_cd == 'INVALID_WORKER_NAME'


def test_batch_id_accepts_max_9_digits() -> None:
    """ingest_batch_id の seq 境界(9桁)を受理することを確認する。"""
    batch_id = _batch_id(999_999_999)
    assert len(batch_id) <= 30


def test_batch_id_rejects_10_digits() -> None:
    """ingest_batch_id の seq 境界(10桁)を拒否することを確認する。"""
    with pytest.raises(ValueError):
        _batch_id(1_000_000_000)


def test_batch_id_empty_override_falls_back_to_generated_id() -> None:
    """空文字 override は未指定扱いとして自動採番にフォールバックする。"""
    batch_id = _batch_id(7, override="")
    assert batch_id.startswith("ING_")


def test_batch_id_whitespace_override_falls_back_to_generated_id() -> None:
    """空白のみ override は未指定扱いとして自動採番にフォールバックする。"""
    batch_id = _batch_id(8, override="   ")
    assert batch_id.startswith("ING_")


def test_apply_ingest_plan_records_non_integrity_sqlalchemy_error(
    session: Session, tmp_path: Path, write_csv, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = tmp_path / "INTASM_TestWorker_202601.csv"
    write_csv(
        p,
        ["start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"],
        [{"start_date": "2026-01-05", "start_time": "08:00:00", "start_marker": "START", "end_date": "2026-01-05", "end_time": "08:10:00", "end_marker": "END", "order_no": "ORD1"}],
    )
    plan = prepare_ingest_file(
        session, str(p), order_product_map={"ORD1": "製品A"}, ingest_batch_id="B_ERR"
    )

    original_flush = session.flush
    state = {"raised": False}

    def flaky_flush(*args, **kwargs) -> None:
        from sqlalchemy.exc import SQLAlchemyError

        if not state["raised"]:
            state["raised"] = True
            raise SQLAlchemyError("simulated db failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(session, "flush", flaky_flush)
    result = apply_ingest_plan(session, plan)
    session.rollback()

    assert result.inserted == 0
    assert result.rejected == 1
    reject = session.query(WorkLogReject).one()
    assert reject.reject_reason_cd == REJECT_DB_CONSTRAINT_ERROR


def test_ingest_files_assigns_incremental_ingest_seq(
    session: Session, tmp_path: Path, write_csv
) -> None:
    p1 = tmp_path / "INTASM_W1_202601.csv"
    p2 = tmp_path / "INTASM_W2_202601.csv"
    write_csv(
        p1,
        ["start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"],
        [{"start_date": "2026-01-05", "start_time": "08:00:00", "start_marker": "START", "end_date": "2026-01-05", "end_time": "08:10:00", "end_marker": "END", "order_no": "ORD1"}],
    )
    write_csv(
        p2,
        ["start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"],
        [{"start_date": "2026-01-05", "start_time": "08:20:00", "start_marker": "START", "end_date": "2026-01-05", "end_time": "08:30:00", "end_marker": "END", "order_no": "ORD2"}],
    )
    results = ingest_files(
        session,
        [str(p1), str(p2)],
        order_product_map={"ORD1": "製品A", "ORD2": "製品B"},
    )
    session.commit()
    assert len(results) == 2
    assert results[0].ingest_batch_id.endswith("_001")
    assert results[1].ingest_batch_id.endswith("_002")
    batches = {r.ingest_batch_id for r in session.query(WorkLog).all()}
    assert results[0].ingest_batch_id in batches
    assert results[1].ingest_batch_id in batches


def test_next_business_day_skips_weekend_and_holiday() -> None:
    assert _next_business_day(datetime(2026, 1, 9).date()).isoformat() == "2026-01-13"
