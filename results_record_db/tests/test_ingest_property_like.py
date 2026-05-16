from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from ingest import _batch_id, ingest_file


@pytest.mark.parametrize(
    "file_name,header,row,expected_fragment",
    [
        (
            "INTASM_202601.csv",
            ["start_date", "start_time", "start_marker", "end_date", "end_time", "end_marker", "order_no"],
            {
                "start_date": "2026-01-05",
                "start_time": "08:00:00",
                "start_marker": "START",
                "end_date": "2026-01-05",
                "end_time": "08:10:00",
                "end_marker": "END",
                "order_no": "ORD1",
            },
            "Unknown file naming",
        ),
        (
            "RANDOM_FILE.csv",
            ["order_no", "product_name"],
            {"order_no": "O", "product_name": "P"},
            "Unknown file naming",
        ),
    ],
)
def test_invalid_file_naming_rejected_early(tmp_path: Path, session: Session, write_csv, file_name, header, row, expected_fragment) -> None:
    p = tmp_path / file_name
    write_csv(p, header, [row])
    with pytest.raises(ValueError, match=expected_fragment):
        ingest_file(session, str(p), order_product_map={"ORD1": "製品A"})


@pytest.mark.parametrize(
    "missing_column",
    ["order_no", "start_date", "start_time", "end_date", "end_time", "start_marker"],
)
def test_internal_missing_required_columns_are_rejected(tmp_path: Path, session: Session, write_csv, missing_column: str) -> None:
    p = tmp_path / "INTASM_TestWorker_202601.csv"
    row = {
        "order_no": "ORD1",
        "start_date": "2026-01-05",
        "start_time": "08:00:00",
        "start_marker": "START",
        "end_date": "2026-01-05",
        "end_time": "08:10:00",
        "end_marker": "END",
    }
    row[missing_column] = ""
    write_csv(p, list(row.keys()), [row])
    result = ingest_file(session, str(p), order_product_map={"ORD1": "製品A"})
    assert result.inserted == 0
    assert result.rejected == 1
    # start_marker は _missing_required 対象外だが、別ルール（START固定）で reject される。


@pytest.mark.parametrize(
    "start_ts,end_ts,expected_inserted,expected_rejected",
    [
        # start==end は0秒作業として有効（elapsed_sec=0, work_sec=0）で、仕様上は正常登録する。
        ("2026-01-05 08:00:00", "2026-01-05 08:00:00", 1, 0),
        ("2026-01-05 08:00:00", "2026-01-05 07:59:59", 0, 1),
        ("2026-01-05 16:59:59", "2026-01-05 17:00:00", 1, 0),
    ],
)
def test_external_boundary_timestamps(tmp_path: Path, session: Session, write_csv, start_ts: str, end_ts: str, expected_inserted: int, expected_rejected: int) -> None:
    p = tmp_path / "EXTASM_TestWorker_202601.csv"
    row = {
        "order_no": "ORD_EXT_1",
        "product_name": "製品X",
        "qr_read_ts": start_ts,
        "all_clear_ts": end_ts,
        "error_code": "",
    }
    write_csv(p, list(row.keys()), [row])
    result = ingest_file(session, str(p))
    assert result.inserted == expected_inserted
    assert result.rejected == expected_rejected


@pytest.mark.parametrize(
    "start_time,end_time,expected_inserted,expected_rejected",
    [
        ("16:50:00", "16:50:00", 1, 0),
        ("16:50:00", "08:10:00", 1, 0),
    ],
)
def test_shipping_boundary_time_handling(tmp_path: Path, session: Session, write_csv, start_time: str, end_time: str, expected_inserted: int, expected_rejected: int) -> None:
    p = tmp_path / "SHIPCHK_202601.csv"
    row = {
        "inspector_name": "InspectorA",
        "inspection_date": "2026-01-09",
        "start_time": start_time,
        "end_time": end_time,
        "order_no": "ORD_SHIP_1",
        "product_name": "製品S",
        "ng_total": "0",
    }
    write_csv(p, list(row.keys()), [row])
    result = ingest_file(session, str(p))
    assert result.inserted == expected_inserted
    assert result.rejected == expected_rejected


@pytest.mark.parametrize("legacy_name", ["shipping_inspection_log.csv", "shipping_inspection_log_invalid.csv"])
def test_legacy_shipping_sample_filenames_are_accepted(tmp_path: Path, session: Session, write_csv, legacy_name: str) -> None:
    p = tmp_path / legacy_name
    row = {
        "inspector_name": "InspectorA",
        "inspection_date": "2026-01-09",
        "start_time": "16:50:00",
        "end_time": "08:10:00",
        "order_no": "ORD_SHIP_LEGACY",
        "product_name": "製品S",
        "ng_total": "0",
    }
    write_csv(p, list(row.keys()), [row])
    result = ingest_file(session, str(p))
    assert result.inserted == 1
    assert result.rejected == 0



def test_external_split_filename_with_lane_and_non_ascii_worker_is_accepted(tmp_path: Path, session: Session, write_csv) -> None:
    p = tmp_path / "EXTASM_A_吉村宗樹_20260105.csv"
    row = {
        "order_no": "ORD_EXT_1",
        "product_name": "製品X",
        "qr_read_ts": "2026-01-05 08:00:00",
        "all_clear_ts": "2026-01-05 08:10:00",
        "error_code": "",
    }
    write_csv(p, list(row.keys()), [row])
    result = ingest_file(session, str(p))
    assert result.inserted == 1
    assert result.rejected == 0

def test_batch_id_stays_within_db_limit_for_large_seq() -> None:
    batch_id = _batch_id(12)
    assert len(batch_id) <= 30
    assert batch_id.endswith("_012")


def test_batch_id_format_matches_readme() -> None:
    batch_id = _batch_id(1)
    assert re.fullmatch(r"ING_\d{8}_\d{6}_001", batch_id)
    assert len(batch_id) <= 30
