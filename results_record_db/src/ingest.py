#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################################
# Name    : ingest.py
# Author  : Akihiko Fujita
# Update  : 2026-05-20
############################################################################

"""results_record_db のファイル取り込みロジックを実装するモジュール。

主な責務:
- CSV/XLSX の入力データを検証・正規化して取り込み計画を作成
- 業務ルールに基づくエラー判定とリジェクト理由の付与
- WorkLog / WorkLogReject への登録処理と取り込み集計結果の生成

"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from openpyxl import load_workbook  # type: ignore
except ImportError:  # pragma: no cover - 任意依存のため未導入を許容
    load_workbook = None

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from db import WorkLog, WorkLogReject

FILENAME_WORKER_RE = re.compile(
    r"^(INTASM|EXTASM)(?:_[^_]+)?_([^_]+)_\d{6}(?:\d{2})?\.(csv|xlsx|xlsm)$"
)
HOLIDAYS = {
    date(2026, 1, 12)
}  # セミナー向け簡易実装: 土日+固定祝日(2026-01-12)のみを非稼働日として扱う。
REJECT_MISSING_REQUIRED = "MISSING_REQUIRED"
REJECT_DATE_PARSE_ERROR = "DATE_PARSE_ERROR"
REJECT_END_BEFORE_START = "END_BEFORE_START"
REJECT_WORK_EXCEEDS_ELAPSED = "WORK_EXCEEDS_ELAPSED"
REJECT_INVALID_RESULT_CD = "INVALID_RESULT_CD"
REJECT_ERROR_CODE_PRESENT = "ERROR_CODE_PRESENT"
REJECT_INVALID_WORKER_NAME = "INVALID_WORKER_NAME"
REJECT_DUPLICATE_KEY = "DUPLICATE_KEY"
REJECT_MASTER_NOT_FOUND = "MASTER_NOT_FOUND"
REJECT_DB_CONSTRAINT_ERROR = "DB_CONSTRAINT_ERROR"

PROCESS_BY_PREFIX = {
    "INTASM": ("内装組立", "internal_assembly_tool"),
    "EXTASM": ("外装組立", "external_assembly_tool"),
}
# セミナー専用互換: 旧教材サンプル名を許容するための暫定ホワイトリスト。
# 本番転用時は削除し、SHIPCHK_* 命名規則のみを受け付けること。
LEGACY_SHIPPING_SAMPLE_NAMES = {
    "shipping_inspection_log.csv",
    "shipping_inspection_log_invalid.csv",
}


@dataclass
class RejectRecord:
    source_system: Optional[str]
    source_file_name: str
    source_row_no: int
    reject_reason_cd: str
    reject_reason_detail: str
    raw_payload_json: str
    ingest_batch_id: str


@dataclass
class IngestResult:
    source_file_name: str
    ingest_batch_id: str
    inserted: int
    rejected: int


@dataclass
class NormalizedWorkLogCandidate:
    order_no: str
    product_name: str
    process_name: str
    worker_name: str
    start_ts: datetime
    end_ts: datetime
    elapsed_sec: int
    work_sec: int
    result_cd: str
    source_system: str
    source_file_name: str
    source_row_no: int
    ingest_batch_id: str
    raw_payload_json: str


@dataclass
class IngestPlan:
    source_file_name: str
    ingest_batch_id: str
    candidates: List[NormalizedWorkLogCandidate]
    rejects: List[RejectRecord]


def load_order_product_master(path: Optional[str]) -> Dict[str, str]:
    """受注-製品マスタCSVを読み込み、必須列を検証して返す。"""
    if not path:
        return {}
    master_path = Path(path)
    if not master_path.exists():
        raise FileNotFoundError(f"order_product_master not found: {master_path}")

    with master_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required_columns = {"order_no", "product_name"}
        if not reader.fieldnames or not required_columns.issubset(
            set(reader.fieldnames)
        ):
            raise ValueError(
                "order_product_master.csv must contain order_no and product_name columns"
            )

        result: Dict[str, str] = {}
        for row in reader:
            order_no_raw = row.get("order_no")
            product_name_raw = row.get("product_name")
            order_no = "" if order_no_raw is None else str(order_no_raw).strip()
            product_name = (
                "" if product_name_raw is None else str(product_name_raw).strip()
            )
            if order_no and product_name:
                result[order_no] = product_name
                normalized_order_no = normalize_order_no(order_no)
                if normalized_order_no and normalized_order_no not in result:
                    result[normalized_order_no] = product_name
    return result


def normalize_worker_name(name: Optional[str]) -> str:
    """作業者名の空白を正規化して比較可能な文字列にする。"""
    if name is None:
        return ""
    return re.sub(r"[\s\u3000]+", "", str(name)).strip()


def normalize_order_no(order_no: Optional[str]) -> str:
    """受注番号を比較・保存用に正規化する(英数字以外を除去し大文字化)。"""
    if order_no is None:
        return ""
    txt = str(order_no).strip().upper()
    return re.sub(r"[^A-Z0-9]", "", txt)


def calc_work_sec(start_ts: datetime, end_ts: datetime) -> int:
    """妥当な時刻範囲に対する所定勤務時間内の実作業秒数を計算する。"""
    if end_ts < start_ts:
        raise ValueError("end_ts must be greater than or equal to start_ts")

    total = 0
    cur_day = start_ts.date()
    end_day = end_ts.date()
    one_day = timedelta(days=1)

    while cur_day <= end_day:
        if cur_day.weekday() < 5 and cur_day not in HOLIDAYS:
            slots = [
                (
                    datetime.combine(cur_day, time(8, 0)),
                    datetime.combine(cur_day, time(12, 0)),
                ),
                (
                    datetime.combine(cur_day, time(13, 0)),
                    datetime.combine(cur_day, time(17, 0)),
                ),
            ]
            for slot_start, slot_end in slots:
                overlap_start = max(start_ts, slot_start)
                overlap_end = min(end_ts, slot_end)
                if overlap_end > overlap_start:
                    total += int((overlap_end - overlap_start).total_seconds())
        cur_day += one_day
    return total


def _parse_datetime(value: str, fmts: Sequence[str]) -> Optional[datetime]:
    """複数フォーマット候補で日時文字列を解析する。"""
    txt = str(value).strip()
    if not txt:
        return None
    for fmt in fmts:
        try:
            return datetime.strptime(txt, fmt)
        except ValueError:
            continue
    return None


def _missing_required(raw: Dict[str, str], columns: Sequence[str]) -> Optional[str]:
    """必須列のうち空値の最初の列名を返す。"""
    for col in columns:
        if not str(raw.get(col, "")).strip():
            return col
    return None


def _iter_input_rows(file_path: Path) -> Iterable[Tuple[int, Dict[str, str]]]:
    """入力ファイルを行番号付き辞書行に変換して列挙する。"""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            header = [
                str(c).strip() if c is not None else ""
                for c in (reader.fieldnames or [])
            ]
            if (
                not header
                or any(not col for col in header)
                or len(set(header)) != len(header)
            ):
                raise ValueError(
                    "CSV header must be non-empty and contain unique column names"
                )
            # DictReader の辞書キーを検証後ヘッダーに統一し、strip 後ヘッダーとの乖離を防ぐ。
            reader.fieldnames = header
            for idx, row in enumerate(reader, start=1):
                yield idx, {k: (v if v is not None else "") for k, v in row.items()}
        return

    if suffix in {".xlsx", ".xlsm"}:
        if load_workbook is None:
            raise ImportError("openpyxl is required to read .xlsx/.xlsm files")
        wb = load_workbook(filename=file_path, data_only=True, read_only=True)
        try:
            ws = wb.active
            rows = ws.iter_rows(values_only=True)
            try:
                first_row = next(rows)
            except StopIteration:
                return
            header = [str(c).strip() if c is not None else "" for c in first_row]
            if (
                not header
                or any(not col for col in header)
                or len(set(header)) != len(header)
            ):
                raise ValueError(
                    "Spreadsheet header must be non-empty and contain unique column names"
                )
            width = len(header)
            for idx, values in enumerate(rows, start=1):
                padded = list(values) + [None] * max(0, width - len(values))
                row = {
                    header[i]: ("" if padded[i] is None else str(padded[i]))
                    for i in range(width)
                }
                yield idx, row
        finally:
            wb.close()
        return

    raise ValueError(f"Unsupported file extension: {file_path.suffix}")


def _batch_id(seq: int = 1, override: Optional[str] = None) -> str:
    """README互換の ingest_batch_id を生成する。"""
    normalized_override = None if override is None else str(override).strip()
    if normalized_override:
        if len(normalized_override) > 30:
            raise ValueError("ingest_batch_id must be 30 characters or fewer")
        return normalized_override
    normalized_seq = max(seq, 1)
    # 仕様合意: ingest_batch_id は DB の String(30) に収める。
    # 固定長20文字(ING_ + YYYYMMDD_HHMMSS + _)のため、seq は9桁以下に制限する。
    if normalized_seq >= 1_000_000_000:
        raise ValueError(
            "ingest sequence is too large for ingest_batch_id length limit (max 9 digits)"
        )
    return f"ING_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{normalized_seq:03d}"


def _next_business_day(d: date) -> date:
    """土日・固定祝日を除いた翌営業日を返す。"""
    cur = d + timedelta(days=1)
    while cur.weekday() >= 5 or cur in HOLIDAYS:
        cur += timedelta(days=1)
    return cur


def _append_reject(
    rejects: List[RejectRecord],
    *,
    source_system: Optional[str],
    source_file_name: str,
    source_row_no: int,
    reject_reason_cd: str,
    reject_reason_detail: str,
    raw_payload: Dict[str, str],
    ingest_batch_id: str,
) -> None:
    """reject レコードを1件追加する。"""
    rejects.append(
        RejectRecord(
            source_system=source_system,
            source_file_name=source_file_name,
            source_row_no=source_row_no,
            reject_reason_cd=reject_reason_cd,
            reject_reason_detail=reject_reason_detail,
            raw_payload_json=json.dumps(raw_payload, ensure_ascii=False),
            ingest_batch_id=ingest_batch_id,
        )
    )


def prepare_ingest_file(
    session: Session,
    file_path: str,
    order_product_map: Optional[Dict[str, str]] = None,
    ingest_batch_id: Optional[str] = None,
    ingest_seq: int = 1,
) -> IngestPlan:
    """単一ファイルの取り込み計画（候補/却下）を作成する。"""
    order_product_map = order_product_map or {}
    fp = Path(file_path)
    batch_id = _batch_id(ingest_seq, override=ingest_batch_id)

    m = FILENAME_WORKER_RE.match(fp.name)
    file_prefix = None
    file_worker = None
    if m:
        file_prefix, file_worker = m.group(1), normalize_worker_name(m.group(2))

    normalized_name = fp.name.lower()
    if (
        fp.name.startswith("SHIPCHK_")
        or normalized_name in LEGACY_SHIPPING_SAMPLE_NAMES
    ):
        log_type = "shipping"
    elif file_prefix == "INTASM":
        log_type = "internal"
    elif file_prefix == "EXTASM":
        log_type = "external"
    else:
        raise ValueError(f"Unknown file naming: {fp.name}")

    rejects: List[RejectRecord] = []
    candidates: List[NormalizedWorkLogCandidate] = []
    seen_keys: set[tuple[str, str]] = set()
    rows = list(_iter_input_rows(fp))
    candidate_order_nos = {
        raw.get("order_no", "").strip()
        for _, raw in rows
        if raw.get("order_no", "").strip()
    }
    existing_keys = set()
    if candidate_order_nos:
        chunk_size = 900
        order_no_list = sorted(candidate_order_nos)
        for i in range(0, len(order_no_list), chunk_size):
            chunk = order_no_list[i : i + chunk_size]
            existing_keys.update(
                {
                    (row.order_no, row.process_name)
                    for row in session.query(WorkLog.order_no, WorkLog.process_name)
                    .filter(WorkLog.order_no.in_(chunk))
                    .all()
                }
            )

    # 仕様合意: existing_keys は (order_no, process_name) で評価するため、
    # order_no ベースに候補抽出しても誤って別工程を重複扱いしない。
    for row_no, raw in rows:
        # 仕様合意: row_no/raw を引数既定値で束縛し、遅延キャプチャを回避する。
        def reject_row(
            code: str,
            detail: str,
            current_source_system: Optional[str],
            current_row_no: int = row_no,
            current_raw: Dict[str, str] = raw,
        ) -> None:
            """現在行を reject として記録する。"""
            _append_reject(
                rejects,
                source_system=current_source_system,
                source_file_name=fp.name,
                source_row_no=current_row_no,
                reject_reason_cd=code,
                reject_reason_detail=detail,
                raw_payload=current_raw,
                ingest_batch_id=batch_id,
            )

        if log_type == "internal":
            process_name, source_system = PROCESS_BY_PREFIX["INTASM"]
            order_no = raw.get("order_no", "").strip()
            if not order_no:
                reject_row(REJECT_MISSING_REQUIRED, "order_no is empty", source_system)
                continue
            missing = _missing_required(
                raw, ["start_date", "start_time", "end_date", "end_time"]
            )
            if missing:
                reject_row(
                    REJECT_MISSING_REQUIRED, f"{missing} is empty", source_system
                )
                continue
            if str(raw.get("start_marker", "")).strip() != "START":
                reject_row(
                    REJECT_MISSING_REQUIRED, "start_marker must be START", source_system
                )
                continue
            if str(raw.get("end_marker", "")).strip() != "END":
                reject_row(
                    REJECT_MISSING_REQUIRED, "end_marker must be END", source_system
                )
                continue
            start_ts = _parse_datetime(
                f"{raw['start_date']} {raw['start_time']}",
                ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"],
            )
            end_ts = _parse_datetime(
                f"{raw['end_date']} {raw['end_time']}",
                ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"],
            )
            if not start_ts or not end_ts:
                reject_row(
                    REJECT_DATE_PARSE_ERROR,
                    "failed to parse start/end timestamp",
                    source_system,
                )
                continue
            product_name = str(
                order_product_map.get(order_no, "")
                or order_product_map.get(normalize_order_no(order_no), "")
            ).strip()
            if not product_name:
                reject_row(
                    REJECT_MASTER_NOT_FOUND,
                    "product_name not found by order_no",
                    source_system,
                )
                continue
            row_worker = normalize_worker_name(raw.get("worker_name", ""))
            if file_worker and row_worker and file_worker != row_worker:
                reject_row(
                    REJECT_INVALID_WORKER_NAME,
                    "worker_name mismatch between file name and row",
                    source_system,
                )
                continue
            worker_name = normalize_worker_name(file_worker or row_worker)
            if not worker_name:
                reject_row(
                    REJECT_INVALID_WORKER_NAME,
                    "worker_name could not be resolved",
                    source_system,
                )
                continue
            result_cd = "OK"
        elif log_type == "external":
            process_name, source_system = PROCESS_BY_PREFIX["EXTASM"]
            order_no = raw.get("order_no", "").strip()
            product_name = raw.get("product_name", "").strip()
            if not order_no or not product_name:
                reject_row(
                    REJECT_MISSING_REQUIRED,
                    "order_no or product_name is empty",
                    source_system,
                )
                continue
            if (
                not raw.get("qr_read_ts", "").strip()
                or not raw.get("all_clear_ts", "").strip()
            ):
                reject_row(
                    REJECT_MISSING_REQUIRED,
                    "qr_read_ts or all_clear_ts is empty",
                    source_system,
                )
                continue
            start_ts = _parse_datetime(raw["qr_read_ts"], ["%Y-%m-%d %H:%M:%S"])
            end_ts = _parse_datetime(raw["all_clear_ts"], ["%Y-%m-%d %H:%M:%S"])
            if not start_ts or not end_ts:
                reject_row(
                    REJECT_DATE_PARSE_ERROR,
                    "failed to parse qr_read_ts/all_clear_ts",
                    source_system,
                )
                continue
            if raw.get("error_code", "").strip():
                reject_row(
                    REJECT_ERROR_CODE_PRESENT, "error_code must be empty", source_system
                )
                continue
            row_worker = normalize_worker_name(raw.get("worker_name", ""))
            if file_worker and row_worker and file_worker != row_worker:
                reject_row(
                    REJECT_INVALID_WORKER_NAME,
                    "worker_name mismatch between file name and row",
                    source_system,
                )
                continue
            worker_name = normalize_worker_name(file_worker or row_worker)
            if not worker_name:
                reject_row(
                    REJECT_INVALID_WORKER_NAME,
                    "worker_name could not be resolved",
                    source_system,
                )
                continue
            result_cd = "OK"
        else:
            process_name, source_system = "出荷検査", "shipping_inspection_tool"
            order_no = raw.get("order_no", "").strip()
            product_name = raw.get("product_name", "").strip()
            inspector = normalize_worker_name(raw.get("inspector_name", ""))
            if not order_no or not product_name or not inspector:
                reject_row(
                    REJECT_MISSING_REQUIRED,
                    "order_no/product_name/inspector_name is empty",
                    source_system,
                )
                continue
            missing = _missing_required(
                raw, ["inspection_date", "start_time", "end_time", "ng_total"]
            )
            if missing:
                reject_row(
                    REJECT_MISSING_REQUIRED, f"{missing} is empty", source_system
                )
                continue
            start_ts = _parse_datetime(
                f"{raw['inspection_date']} {raw['start_time']}", ["%Y-%m-%d %H:%M:%S"]
            )
            end_ts = _parse_datetime(
                f"{raw['inspection_date']} {raw['end_time']}", ["%Y-%m-%d %H:%M:%S"]
            )
            if not start_ts or not end_ts:
                reject_row(
                    REJECT_DATE_PARSE_ERROR,
                    "failed to parse inspection timestamp",
                    source_system,
                )
                continue
            # 出荷検査のみ: end_time < start_time は日付跨ぎとして翌営業日へ補正し、reject しない。
            if end_ts < start_ts:
                end_ts = datetime.combine(
                    _next_business_day(start_ts.date()), end_ts.time()
                )
                assert end_ts >= start_ts, "shipping end_ts correction must be non-decreasing"
            try:
                ng_total = int(str(raw["ng_total"]).strip())
            except ValueError:
                reject_row(
                    REJECT_INVALID_RESULT_CD, "ng_total is not integer", source_system
                )
                continue
            result_cd = "OK" if ng_total == 0 else "NG"
            worker_name = inspector

        # 仕様合意: 出荷検査の end<start は翌営業日に補正済み。ここは主に内装/外装向けガード。
        if end_ts < start_ts:
            reject_row(REJECT_END_BEFORE_START, "end_ts before start_ts", source_system)
            continue
        elapsed_sec = int((end_ts - start_ts).total_seconds())
        work_sec = calc_work_sec(start_ts, end_ts)
        # 仕様合意: calc_work_sec は elapsed_sec を超えない前提だが、将来変更に備えて防御する。
        if work_sec > elapsed_sec:
            reject_row(
                REJECT_WORK_EXCEEDS_ELAPSED, "work_sec > elapsed_sec", source_system
            )
            continue

        # セミナー向け実装として、重複は事前チェック+UNIQUE制約例外捕捉で扱う（同時実行競合は許容）。
        dedup_key = (order_no, process_name)
        if dedup_key in existing_keys or dedup_key in seen_keys:
            reject_row(
                REJECT_DUPLICATE_KEY,
                "UNIQUE(order_no, process_name) violation",
                source_system,
            )
            continue
        seen_keys.add(dedup_key)
        candidates.append(
            NormalizedWorkLogCandidate(
                order_no=order_no,
                product_name=product_name,
                process_name=process_name,
                worker_name=worker_name,
                start_ts=start_ts,
                end_ts=end_ts,
                elapsed_sec=elapsed_sec,
                work_sec=work_sec,
                result_cd=result_cd,
                source_system=source_system,
                source_file_name=fp.name,
                source_row_no=row_no,
                ingest_batch_id=batch_id,
                raw_payload_json=json.dumps(raw, ensure_ascii=False),
            )
        )
    return IngestPlan(
        source_file_name=fp.name,
        ingest_batch_id=batch_id,
        candidates=candidates,
        rejects=rejects,
    )


def apply_ingest_plan(session: Session, plan: IngestPlan) -> IngestResult:
    """取り込み計画をDBへ反映し、結果件数を返す。"""
    inserted = 0
    rejects = list(plan.rejects)
    for c in plan.candidates:
        obj = WorkLog(
            order_no=c.order_no,
            product_name=c.product_name,
            process_name=c.process_name,
            worker_name=c.worker_name,
            start_ts=c.start_ts,
            end_ts=c.end_ts,
            elapsed_sec=c.elapsed_sec,
            work_sec=c.work_sec,
            result_cd=c.result_cd,
            source_system=c.source_system,
            source_file_name=c.source_file_name,
            source_row_no=c.source_row_no,
            ingest_batch_id=c.ingest_batch_id,
        )
        try:
            with session.begin_nested():
                session.add(obj)
                session.flush()
                inserted += 1
        except IntegrityError as exc:
            orig = getattr(exc, "orig", None)
            detail = str(orig or exc)
            lower_detail = detail.lower()
            sqlstate = getattr(orig, "pgcode", None)
            is_duplicate = (
                sqlstate == "23505"
                or "duplicate key" in lower_detail
                or "unique constraint failed: work_log.order_no, work_log.process_name"
                in lower_detail
                or "uq_work_log_order_no_process_name" in lower_detail
            )
            code = REJECT_DUPLICATE_KEY if is_duplicate else REJECT_DB_CONSTRAINT_ERROR
            reject_detail = (
                "UNIQUE(order_no, process_name) violation"
                if code == REJECT_DUPLICATE_KEY
                else detail
            )
            rejects.append(
                RejectRecord(
                    c.source_system,
                    c.source_file_name,
                    c.source_row_no,
                    code,
                    reject_detail,
                    c.raw_payload_json,
                    c.ingest_batch_id,
                )
            )
        except SQLAlchemyError as exc:
            rejects.append(
                RejectRecord(
                    c.source_system,
                    c.source_file_name,
                    c.source_row_no,
                    REJECT_DB_CONSTRAINT_ERROR,
                    str(exc),
                    c.raw_payload_json,
                    c.ingest_batch_id,
                )
            )
    for r in rejects:
        session.add(
            WorkLogReject(
                source_system=r.source_system,
                source_file_name=r.source_file_name,
                source_row_no=r.source_row_no,
                reject_reason_cd=r.reject_reason_cd,
                reject_reason_detail=r.reject_reason_detail,
                raw_payload_json=r.raw_payload_json,
                ingest_batch_id=r.ingest_batch_id,
            )
        )
    session.flush()
    session.commit()
    return IngestResult(
        source_file_name=plan.source_file_name,
        ingest_batch_id=plan.ingest_batch_id,
        inserted=inserted,
        rejected=len(rejects),
    )


def ingest_file(
    session: Session,
    file_path: str,
    order_product_map: Optional[Dict[str, str]] = None,
    ingest_batch_id: Optional[str] = None,
    ingest_seq: int = 1,
) -> IngestResult:
    """単一ファイルを前処理からDB反映まで一括で実行する。"""
    plan = prepare_ingest_file(
        session,
        file_path,
        order_product_map=order_product_map,
        ingest_batch_id=ingest_batch_id,
        ingest_seq=ingest_seq,
    )
    return apply_ingest_plan(session, plan)


def ingest_files(
    session: Session,
    file_paths: Sequence[str],
    order_product_map: Optional[Dict[str, str]] = None,
) -> List[IngestResult]:
    """複数ファイルを順次取り込み、各ファイル結果を返す。"""
    results: List[IngestResult] = []
    for seq, file_path in enumerate(file_paths, start=1):
        results.append(
            ingest_file(
                session=session,
                file_path=file_path,
                order_product_map=order_product_map,
                ingest_seq=seq,
            )
        )
    return results
