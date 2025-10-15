from __future__ import annotations

import pytest

from backend.app import OrderItemInput, OrderService
from backend.app.exceptions import BusinessRuleError, NotFoundError, ValidationError


def test_create_order_flow():
    service = OrderService()

    user = service.register_user("Alice", "alice@example.com")
    widget = service.register_product("Widget", "Useful widget", price=12.5, stock=5)
    gadget = service.register_product("Gadget", "Handy gadget", price=3.0, stock=8)

    order = service.create_order(
        user_id=user.id,
        items=[
            OrderItemInput(product_id=widget.id, quantity=2),
            OrderItemInput(product_id=gadget.id, quantity=3),
        ],
    )

    assert order.user_id == user.id
    assert len(order.items) == 2
    assert order.total_amount == pytest.approx(2 * widget.price + 3 * gadget.price)

    orders = service.list_orders()
    assert len(orders) == 1
    assert orders[0].id == order.id

    fetched = service.get_order(order.id)
    assert fetched.total_amount == order.total_amount

    # Stock should be reduced after order creation
    remaining_widget = next(p for p in service.list_products() if p.id == widget.id)
    remaining_gadget = next(p for p in service.list_products() if p.id == gadget.id)
    assert remaining_widget.stock == 3
    assert remaining_gadget.stock == 5


def test_validations_and_errors():
    service = OrderService()

    with pytest.raises(ValidationError):
        service.register_user("", "missing@example.com")

    service.register_user("Bob", "bob@example.com")
    with pytest.raises(BusinessRuleError):
        service.register_user("Bob", "bob@example.com")

    with pytest.raises(ValidationError):
        service.register_product("", "desc", price=1.0, stock=1)
    with pytest.raises(ValidationError):
        service.register_product("Thing", "desc", price=-1.0, stock=1)
    with pytest.raises(ValidationError):
        service.register_product("Thing", "desc", price=1.0, stock=-1)

    product = service.register_product("Thing", "desc", price=10.0, stock=2)

    with pytest.raises(NotFoundError):
        service.create_order(user_id=99, items=[OrderItemInput(product_id=product.id, quantity=1)])

    user = service.register_user("Carol", "carol@example.com")

    with pytest.raises(NotFoundError):
        service.create_order(user_id=user.id, items=[OrderItemInput(product_id=999, quantity=1)])

    with pytest.raises(BusinessRuleError):
        service.create_order(user_id=user.id, items=[OrderItemInput(product_id=product.id, quantity=5)])

    with pytest.raises(ValidationError):
        service.create_order(user_id=user.id, items=[])

    with pytest.raises(ValidationError):
        OrderItemInput(product_id=product.id, quantity=0)
