"""Domain models for the order system implemented with dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(slots=True)
class User:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class OrderItem:
    product_id: int
    quantity: int
    unit_price: float


@dataclass(slots=True)
class Order:
    id: int
    user_id: int
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    items: List[OrderItem] = field(default_factory=list)

    @property
    def total_amount(self) -> float:
        return round(sum(item.quantity * item.unit_price for item in self.items), 2)
