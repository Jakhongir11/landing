"""Controller for product operations."""
from __future__ import annotations

from typing import Iterable

from pos_app.database import DatabaseManager


class ProductController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def list_products(self) -> list[dict]:
        rows = self.db.fetch_all(
            "SELECT id, name, price, category FROM products ORDER BY name"
        )
        return [dict(row) for row in rows]

    def search_products(self, query: str) -> list[dict]:
        like_query = f"%{query.strip()}%"
        rows = self.db.fetch_all(
            """
            SELECT id, name, price, category
            FROM products
            WHERE name LIKE ? OR category LIKE ?
            ORDER BY name
            """,
            (like_query, like_query),
        )
        return [dict(row) for row in rows]

    def add_product(self, name: str, price: float, category: str) -> None:
        self.db.execute(
            "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
            (name, price, category),
        )

    def delete_product(self, product_id: int) -> None:
        self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))

    def update_product(self, product_id: int, name: str, price: float, category: str) -> None:
        self.db.execute(
            "UPDATE products SET name = ?, price = ?, category = ? WHERE id = ?",
            (name, price, category, product_id),
        )

    def get_product(self, product_id: int) -> dict | None:
        rows = self.db.fetch_all(
            "SELECT id, name, price, category FROM products WHERE id = ?",
            (product_id,),
        )
        return dict(rows[0]) if rows else None
