from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if len(symbol) < 3:
        raise ValueError(f"Symbol '{symbol}' looks too short. Example: BTCUSDT")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}. Got: '{side}'")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type must be one of {VALID_ORDER_TYPES}. Got: '{order_type}'"
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity must be a number. Got: '{quantity}'")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Price must be a number. Got: '{price}'")

    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}")

    return p


def validate_stop_price(
    stop_price: str | float | None, order_type: str
) -> float | None:
    if order_type != "STOP_MARKET":
        return None

    if stop_price is None:
        raise ValueError("Stop price is required for STOP_MARKET orders.")

    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Stop price must be a number. Got: '{stop_price}'")

    if sp <= 0:
        raise ValueError(f"Stop price must be greater than 0. Got: {sp}")

    return sp


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> dict:
    clean = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }
    clean["price"] = validate_price(price, clean["order_type"])
    clean["stop_price"] = validate_stop_price(stop_price, clean["order_type"])
    return clean
