"""Application service containing the business logic of the order system."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

from .exceptions import BusinessRuleError, NotFoundError, ValidationError
from .models import Order, OrderItem, Product, User
from .repository import InMemoryRepository


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(slots=True)
class OrderItemInput:
    product_id: int
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValidationError("quantity must be greater than zero")


class OrderService:
    """High-level operations for managing users, products, and orders."""

    def __init__(self, repository: InMemoryRepository | None = None) -> None:
        self._repository = repository or InMemoryRepository()

    # Users ---------------------------------------------------------------
    def register_user(self, name: str, email: str) -> User:
        name = name.strip()
        email = email.strip().lower()
        if not name:
            raise ValidationError("name is required")
        if not EMAIL_PATTERN.match(email):
            raise ValidationError("email is invalid")
        if self._repository.get_user_by_email(email):
            raise BusinessRuleError("email already registered")
        return self._repository.add_user(name, email)

    def list_users(self) -> List[User]:
        return self._repository.list_users()

    # Products ------------------------------------------------------------
    def register_product(self, name: str, description: str, price: float, stock: int) -> Product:
        name = name.strip()
        description = description.strip()
        if not name:
            raise ValidationError("product name is required")
        if price <= 0:
            raise ValidationError("price must be greater than zero")
        if stock < 0:
            raise ValidationError("stock cannot be negative")
        if self._repository.get_product_by_name(name):
            raise BusinessRuleError("product name already exists")
        return self._repository.add_product(name, description, round(price, 2), stock)

    def list_products(self) -> List[Product]:
        return self._repository.list_products()

    # Orders --------------------------------------------------------------
    def create_order(self, user_id: int, items: Iterable[OrderItemInput], status: str = "pending") -> Order:
        user = self._repository.get_user(user_id)
        if user is None:
            raise NotFoundError("user not found")

        items = list(items)
        if not items:
            raise ValidationError("order must contain at least one item")

        order_items: List[OrderItem] = []
        for item in items:
            product = self._repository.get_product(item.product_id)
            if product is None:
                raise NotFoundError(f"product {item.product_id} not found")
            if item.quantity > product.stock:
                raise BusinessRuleError(
                    f"insufficient stock for product {product.id}: requested {item.quantity}, available {product.stock}"
                )
            product.stock -= item.quantity
            self._repository.update_product(product)
            order_items.append(
                OrderItem(product_id=product.id, quantity=item.quantity, unit_price=product.price)
            )

        return self._repository.add_order(user_id=user.id, status=status, items=order_items)

    def list_orders(self) -> List[Order]:
        return self._repository.list_orders()

    def get_order(self, order_id: int) -> Order:
        order = self._repository.get_order(order_id)
        if order is None:
            raise NotFoundError("order not found")
        return order
