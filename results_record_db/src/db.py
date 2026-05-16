#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################################
# Name    : db.py
# Author  : Akihiko Fujita
# Update  : 2026-05-20
############################################################################

"""results_record_db の永続化層を定義するモジュール。

主な責務:
- PostgreSQL 向け SQLAlchemy Engine / Session ファクトリを提供
- 作業実績と取り込みリジェクトの ORM モデルを定義
- アプリ全体で共通利用する DB セッション管理ユーティリティを提供

"""
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

# 仕様合意: ローカル PostgreSQL 接続先は固定値を利用する。
DATABASE_URL = (
    "postgresql+psycopg://results_user:results_pass@localhost:5432/results_record_db"
)

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
    """正規化済み作業ログテーブル。"""

    __tablename__ = "work_log"
    __table_args__ = (
        UniqueConstraint(
            "order_no", "process_name", name="uq_work_log_order_no_process_name"
        ),
        CheckConstraint(
            "process_name IN ('内装組立', '外装組立', '出荷検査')",
            name="ck_work_log_process_name",
        ),
        CheckConstraint("result_cd IN ('OK', 'NG')", name="ck_work_log_result_cd"),
        CheckConstraint(
            "source_system IN ('internal_assembly_tool', 'external_assembly_tool', 'shipping_inspection_tool')",
            name="ck_work_log_source_system",
        ),
        CheckConstraint("end_ts >= start_ts", name="ck_work_log_end_gte_start"),
        CheckConstraint("elapsed_sec >= 0", name="ck_work_log_elapsed_non_negative"),
        CheckConstraint(
            "work_sec >= 0 AND work_sec <= elapsed_sec",
            name="ck_work_log_work_sec_range",
        ),
        Index("idx_work_log_process_end_ts", "process_name", "end_ts"),
        Index("idx_work_log_worker_end_ts", "worker_name", "end_ts"),
        Index("idx_work_log_order_process", "order_no", "process_name"),
    )

    work_log_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class WorkLogReject(Base):
    """取込却下行の監査テーブル。"""

    __tablename__ = "work_log_reject"

    reject_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    source_system: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_row_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reject_reason_cd: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reject_reason_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingest_batch_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


def create_all_tables() -> None:
    """ORMモデルで定義した全テーブルを作成する。

    仕様合意: 通常フローでは ddl/ddl_results_record_db.sql を先に適用する。
    この関数はローカル検証用途として残す。
    """
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """トランザクション付き SQLAlchemy セッションを提供する。"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
