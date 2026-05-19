"""
models/database.py
------------------
Uses Python's built-in SQLite — no external database server needed.
The database file (docverify.db) is created automatically in the backend folder.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "docverify.db")


def get_db():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL")  # better for concurrent reads
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_db()
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            full_name  TEXT,
            role       TEXT    DEFAULT 'user',
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Documents table ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            filename     TEXT    NOT NULL,
            doc_hash     TEXT    UNIQUE NOT NULL,
            tx_hash      TEXT,
            block_number INTEGER,
            fraud_score  REAL    DEFAULT 0.0,
            status       TEXT    DEFAULT 'pending',
            uploader_id  INTEGER NOT NULL,
            created_at   TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (uploader_id) REFERENCES users(id)
        )
    """)

    # ── Verification log table ────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verify_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_hash   TEXT    NOT NULL,
            found      INTEGER DEFAULT 0,
            checked_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("✓ SQLite database initialised — docverify.db")
