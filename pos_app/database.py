"""Database layer for the POS system."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class DatabaseManager:
    """SQLite manager responsible for schema and connections."""

    def __init__(self, db_path: Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parent
        self.db_path = db_path or base_dir / "pos.db"
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()
        self._seed_demo_products()

    def _ensure_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )
        self.connection.commit()

    def _seed_demo_products(self) -> None:
        cursor = self.connection.cursor()
        existing = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if existing:
            return
        demo_products = [
            ("Эспрессо", 120.0, "Кофе"),
            ("Капучино", 180.0, "Кофе"),
            ("Американо", 140.0, "Кофе"),
            ("Чай", 90.0, "Напитки"),
            ("Круассан", 160.0, "Выпечка"),
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
            demo_products,
        )
        self.connection.commit()

    def execute(self, query: str, params: Iterable | None = None) -> sqlite3.Cursor:
        cursor = self.connection.cursor()
        cursor.execute(query, params or [])
        self.connection.commit()
        return cursor

    def fetch_all(self, query: str, params: Iterable | None = None) -> list[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute(query, params or [])
        return cursor.fetchall()

    def close(self) -> None:
        self.connection.close()
