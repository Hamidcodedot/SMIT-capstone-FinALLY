from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Generator

# By default, use db/finally.db located at project root or environment variable
DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "db"
DB_PATH = Path(os.getenv("FINALLY_DB_PATH", str(DEFAULT_DB_DIR / "finally.db")))


def get_db_path() -> Path:
    return Path(DB_PATH)


def init_db() -> None:
    """Initialize database directory and tables if they do not exist."""
    db_file = get_db_path()
    db_file.parent.mkdir(parents=True, exist_ok=True)

    schema_file = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)
        from .seed import seed_default_data
        seed_default_data(conn)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with foreign keys and WAL mode enabled."""
    db_file = get_db_path()
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
