from __future__ import annotations

import csv
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db import Base


@pytest.fixture
def write_csv():
    def _write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
        with path.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(rows)

    return _write_csv


@pytest.fixture
def session() -> Session:
    e = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(e)
    s = Session(e)
    try:
        yield s
    finally:
        s.rollback()
        s.close()
