from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from db import WorkLog, WorkLogReject
from ingest import ingest_file
def test_duplicate_db_and_same_file(session: Session, tmp_path: Path, write_csv) -> None:
    p = tmp_path / 'INTASM_YamadaTaro_202601.csv'
    h = ["start_date","start_time","start_marker","end_date","end_time","end_marker","order_no"]
    write_csv(p, h, [
        {"start_date":"2026-01-05","start_time":"08:00:00","start_marker":"START","end_date":"2026-01-05","end_time":"08:05:00","end_marker":"END","order_no":"ORD10"},
        {"start_date":"2026-01-05","start_time":"08:10:00","start_marker":"START","end_date":"2026-01-05","end_time":"08:15:00","end_marker":"END","order_no":"ORD10"},
    ])
    r1 = ingest_file(session, str(p), order_product_map={"ORD10": "製品X"}, ingest_batch_id='B1')
    session.commit()
    assert r1.inserted == 1 and r1.rejected == 1

    r2 = ingest_file(session, str(p), order_product_map={"ORD10": "製品X"}, ingest_batch_id='B2')
    session.commit()
    assert r2.inserted == 0
    assert r2.rejected == 2
    assert session.query(WorkLog).count() == 1
    assert session.query(WorkLogReject).filter_by(reject_reason_cd='DUPLICATE_KEY').count() >= 2
