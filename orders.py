from __future__ import annotations

from typing import Any

from bot.client import BinanceClientError, BinanceFuturesClient
from bot.logging_config import setup_logger
from bot.validators import validate_all

logger = setup_logger("orders")


def _format_response(order: dict) -> str:
    lines = [
        "",
        "┌─────────────── ORDER RESPONSE ───────────────┐",
        f"│  Order ID    : {order.get('orderId', 'N/A')}",
        f"│  Symbol      : {order.get('symbol', 'N/A')}",
        f"│  Side        : {order.get('side', 'N/A')}",
        f"│  Type        : {order.get('type', 'N/A')}",
        f"│  Status      : {order.get('status', 'N/A')}",
        f"│  Quantity    : {order.get('origQty', 'N/A')}",
        f"│  Executed Qty: {order.get('executedQty', 'N/A')}",
        f"│  Avg Price   : {order.get('avgPrice', 'N/A')}",
        f"│  Price       : {order.get('price', 'N/A')}",
        f"│  Time in Frc : {order.get('timeInForce', 'N/A')}",
        f"│  Client OID  : {order.get('clientOrderId', 'N/A')}",
        "└──────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict[str, Any]:
    params = validate_all(symbol, side, "MARKET", quantity)

    logger.info(
        "Placing MARKET order | symbol=%s side=%s qty=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
    )

    order = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type="MARKET",
        quantity=params["quantity"],
    )

    logger.info("MARKET order placed successfully | orderId=%s", order.get("orderId"))
    print(_format_response(order))
    return order


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> dict[str, Any]:
    params = validate_all(symbol, side, "LIMIT", quantity, price=price)

    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
        params["price"],
        time_in_force,
    )

    order = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type="LIMIT",
        quantity=params["quantity"],
        price=params["price"],
        timeInForce=time_in_force,
    )

    logger.info("LIMIT order placed successfully | orderId=%s", order.get("orderId"))
    print(_format_response(order))
    return order


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> dict[str, Any]:
    params = validate_all(symbol, side, "STOP_MARKET", quantity, stop_price=stop_price)

    logger.info(
        "Placing STOP_MARKET order | symbol=%s side=%s qty=%s stopPrice=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
        params["stop_price"],
    )

    order = client.place_order(
        symbol=params["symbol"],
        side=params["side"],
        type="STOP_MARKET",
        quantity=params["quantity"],
        stopPrice=params["stop_price"],
    )

    logger.info(
        "STOP_MARKET order placed successfully | orderId=%s", order.get("orderId")
    )
    print(_format_response(order))
    return order
