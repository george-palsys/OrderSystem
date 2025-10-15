"""In-memory repository handling persistence for the order system."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .models import Order, OrderItem, Product, User


class InMemoryRepository:
    """Simple repository storing entities in dictionaries."""

    def __init__(self) -> None:
        self._users: Dict[int, User] = {}
        self._products: Dict[int, Product] = {}
        self._orders: Dict[int, Order] = {}
        self._user_seq = 1
        self._product_seq = 1
        self._order_seq = 1

    # User operations -----------------------------------------------------
    def list_users(self) -> List[User]:
        return [self._users[key] for key in sorted(self._users)]

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self._users.values() if user.email == email), None)

    def add_user(self, name: str, email: str) -> User:
        user = User(id=self._user_seq, name=name, email=email)
        self._users[user.id] = user
        self._user_seq += 1
        return user

    # Product operations --------------------------------------------------
    def list_products(self) -> List[Product]:
        return [self._products[key] for key in sorted(self._products)]

    def get_product(self, product_id: int) -> Optional[Product]:
        return self._products.get(product_id)

    def get_product_by_name(self, name: str) -> Optional[Product]:
        return next((product for product in self._products.values() if product.name == name), None)

    def add_product(self, name: str, description: str, price: float, stock: int) -> Product:
        product = Product(
            id=self._product_seq,
            name=name,
            description=description,
            price=price,
            stock=stock,
        )
        self._products[product.id] = product
        self._product_seq += 1
        return product

    def update_product(self, product: Product) -> Product:
        self._products[product.id] = product
        return product

    # Order operations ----------------------------------------------------
    def list_orders(self) -> List[Order]:
        return [self._orders[key] for key in sorted(self._orders)]

    def get_order(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)

    def add_order(self, user_id: int, status: str, items: Iterable[OrderItem]) -> Order:
        order = Order(id=self._order_seq, user_id=user_id, status=status, items=list(items))
        self._orders[order.id] = order
        self._order_seq += 1
        return order

    def replace_order(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order
