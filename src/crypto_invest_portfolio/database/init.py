"""Database initialization and schema management."""

import sqlite3

from ..constants.config import DB_FILE


def init_db():
    """Initialize SQLite database and create tables if necessary.

    Creates the ``portfolio`` and ``history`` tables in ``crypto_portfolio.db``
    if they don't already exist.

    Args:
        None

    Returns:
        None

    Side effects:
        - Creates/writes to SQLite file ``crypto_portfolio.db``.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY,
            coin TEXT,
            symbol TEXT,
            amount REAL,
            buy_price_cad REAL,
            fee_buy_percent REAL DEFAULT 0,
            fee_sell_percent REAL DEFAULT 0,
            type TEXT,
            wallet TEXT
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            coin TEXT,
            symbol TEXT,
            wallet TEXT,
            current_price_cad REAL,
            current_value_net_cad REAL,
            pct_change_net REAL
        )
    """
    )
    # Light migration: ensure columns exist

    def _ensure_column(table: str, column: str, ddl: str):
        c.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in c.fetchall()]
        if column not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

    _ensure_column("portfolio", "wallet", "wallet TEXT")
    _ensure_column("portfolio", "entry_kind", "entry_kind TEXT DEFAULT 'buy'")
    _ensure_column("history", "wallet", "wallet TEXT")
    conn.commit()
    conn.close()