"""Domain models for the POS system."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Product:
    id: int
    name: str
    price: float
    category: str


@dataclass(slots=True)
class SaleItem:
    product_id: int
    name: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        return self.quantity * self.price


@dataclass(slots=True)
class Sale:
    id: int
    total: float
    created_at: str
