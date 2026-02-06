"""Controller for sales operations."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from pos_app.database import DatabaseManager
from pos_app.models import SaleItem


class SaleController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create_sale(self, items: Iterable[SaleItem]) -> int:
        items = list(items)
        total = sum(item.total for item in items)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sale_cursor = self.db.execute(
            "INSERT INTO sales (total, created_at) VALUES (?, ?)",
            (total, timestamp),
        )
        sale_id = int(sale_cursor.lastrowid)
        for item in items:
            self.db.execute(
                """
                INSERT INTO sale_items (sale_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
                """,
                (sale_id, item.product_id, item.quantity, item.price),
            )
        return sale_id

    def list_sales(self) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT id, total, created_at FROM sales ORDER BY created_at DESC"
        )
        return [dict(row) for row in rows]

    def list_sale_items(self, sale_id: int) -> list[dict]:
        rows = self.db.fetch_all(
            """
            SELECT sale_items.quantity, sale_items.price, products.name
            FROM sale_items
            JOIN products ON products.id = sale_items.product_id
            WHERE sale_items.sale_id = ?
            """,
            (sale_id,),
        )
        return [dict(row) for row in rows]
