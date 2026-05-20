#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""results_record_db セミナー用の DB 永続化層定義。"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Iterator, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# セミナー要件: 接続情報はハードコードする。
DATABASE_URL = "postgresql+psycopg://results_user:results_pass@localhost:5432/results_record_db"

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """SQLAlchemy ORM モデルの基底クラス。"""


class WorkLog(Base):
    """README 定義に準拠した主テーブル。"""

    __tablename__ = "work_log"
    __table_args__ = (
        UniqueConstraint("order_no", "process_name", name="uq_work_log_order_no_process_name"),
        CheckConstraint("process_name IN ('内装組立', '外装組立', '出荷検査')", name="ck_work_log_process_name"),
        CheckConstraint("result_cd IN ('OK', 'NG')", name="ck_work_log_result_cd"),
        CheckConstraint(
            "source_system IN ('internal_assembly_tool', 'external_assembly_tool', 'shipping_inspection_tool')",
            name="ck_work_log_source_system",
        ),
        CheckConstraint("end_ts >= start_ts", name="ck_work_log_end_ts_gte_start_ts"),
        CheckConstraint("elapsed_sec >= 0", name="ck_work_log_elapsed_sec_non_negative"),
        CheckConstraint("work_sec >= 0 AND work_sec <= elapsed_sec", name="ck_work_log_work_sec_range"),
        Index("idx_work_log_process_end_ts", "process_name", "end_ts"),
        Index("idx_work_log_worker_end_ts", "worker_name", "end_ts"),
        Index("idx_work_log_order_process", "order_no", "process_name"),
    )

    work_log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(30), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    process_name: Mapped[str] = mapped_column(String(30), nullable=False)
    worker_name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    elapsed_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    work_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    result_cd: Mapped[str] = mapped_column(String(10), nullable=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_row_no: Mapped[int] = mapped_column(Integer, nullable=False)
    ingest_batch_id: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())


class WorkLogReject(Base):
    """README 定義に準拠した reject 監査テーブル。"""

    __tablename__ = "work_log_reject"

    reject_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    source_file_name: Mapped[Optional[str]] = mapped_column(String(255))
    source_row_no: Mapped[Optional[int]] = mapped_column(Integer)
    reject_reason_cd: Mapped[Optional[str]] = mapped_column(String(50))
    reject_reason_detail: Mapped[Optional[str]] = mapped_column(Text)
    raw_payload_json: Mapped[Optional[str]] = mapped_column(Text)
    ingest_batch_id: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())


def create_all_tables() -> None:
    """ORM モデル定義に基づきテーブルを作成する。"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """コミット/ロールバック付きセッション管理関数。"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
