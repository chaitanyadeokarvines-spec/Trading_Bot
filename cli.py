#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClientError, BinanceFuturesClient
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_market_order

load_dotenv()
logger = setup_logger("cli")

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║        Binance Futures Testnet — Trading Bot         ║
║              USDT-M  |  Python 3.x                  ║
╚══════════════════════════════════════════════════════╝
"""


def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        logger.error("Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET.")
        print(
            "\n[ERROR] API credentials not found.\n"
            "  Create a .env file (see .env.example) or export the variables:\n"
            "    export BINANCE_API_KEY=your_key\n"
            "    export BINANCE_API_SECRET=your_secret\n"
        )
        sys.exit(1)

    return BinanceFuturesClient(api_key, api_secret)


def _print_request_summary(**kwargs) -> None:
    print("\n┌─────────────── ORDER REQUEST ───────────────┐")
    for k, v in kwargs.items():
        if v is not None:
            print(f"│  {k:<14}: {v}")
    print("└──────────────────────────────────────────────┘")


def cmd_market(args: argparse.Namespace) -> None:
    _print_request_summary(
        Symbol=args.symbol,
        Side=args.side,
        Type="MARKET",
        Quantity=args.quantity,
    )
    logger.info("CLI → MARKET | symbol=%s side=%s qty=%s", args.symbol, args.side, args.quantity)
    client = _get_client()
    try:
        place_market_order(client, args.symbol, args.side, args.quantity)
        print("\n✅  Market order placed successfully.\n")
    except (ValueError, BinanceClientError) as exc:
        logger.error("Market order failed | %s", exc)
        print(f"\n❌  Order failed: {exc}\n")
        sys.exit(1)


def cmd_limit(args: argparse.Namespace) -> None:
    if args.price is None:
        print("\n❌  --price is required for LIMIT orders.\n")
        sys.exit(1)

    _print_request_summary(
        Symbol=args.symbol,
        Side=args.side,
        Type="LIMIT",
        Quantity=args.quantity,
        Price=args.price,
        TimeInForce=args.tif,
    )
    logger.info(
        "CLI → LIMIT | symbol=%s side=%s qty=%s price=%s tif=%s",
        args.symbol, args.side, args.quantity, args.price, args.tif,
    )
    client = _get_client()
    try:
        place_limit_order(client, args.symbol, args.side, args.quantity, args.price, args.tif)
        print("\n✅  Limit order placed successfully.\n")
    except (ValueError, BinanceClientError) as exc:
        logger.error("Limit order failed | %s", exc)
        print(f"\n❌  Order failed: {exc}\n")
        sys.exit(1)


def cmd_stop(args: argparse.Namespace) -> None:
    if args.stop_price is None:
        print("\n❌  --stop-price is required for STOP_MARKET orders.\n")
        sys.exit(1)

    _print_request_summary(
        Symbol=args.symbol,
        Side=args.side,
        Type="STOP_MARKET",
        Quantity=args.quantity,
        StopPrice=args.stop_price,
    )
    logger.info(
        "CLI → STOP_MARKET | symbol=%s side=%s qty=%s stopPrice=%s",
        args.symbol, args.side, args.quantity, args.stop_price,
    )
    client = _get_client()
    try:
        place_stop_market_order(client, args.symbol, args.side, args.quantity, args.stop_price)
        print("\n✅  Stop-Market order placed successfully.\n")
    except (ValueError, BinanceClientError) as exc:
        logger.error("Stop-Market order failed | %s", exc)
        print(f"\n❌  Order failed: {exc}\n")
        sys.exit(1)


def cmd_account(args: argparse.Namespace) -> None:
    logger.info("CLI → account info")
    client = _get_client()
    try:
        info = client.get_account()
        assets = [a for a in info.get("assets", []) if float(a.get("walletBalance", 0)) != 0]
        print("\n┌─────────────── ACCOUNT INFO ────────────────┐")
        print(f"│  Total Wallet Balance: {info.get('totalWalletBalance', 'N/A')}")
        print(f"│  Total Unrealised PnL: {info.get('totalUnrealizedProfit', 'N/A')}")
        print(f"│  Total Margin Balance: {info.get('totalMarginBalance', 'N/A')}")
        print("│  ── Non-zero Assets ──")
        for a in assets:
            print(f"│    {a['asset']}: {a['walletBalance']}")
        print("└──────────────────────────────────────────────┘\n")
    except BinanceClientError as exc:
        logger.error("Account fetch failed | %s", exc)
        print(f"\n❌  {exc}\n")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet CLI — place orders from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py market --symbol BTCUSDT --side BUY  --quantity 0.001\n"
            "  python cli.py limit  --symbol BTCUSDT --side SELL --quantity 0.001 --price 70000\n"
            "  python cli.py stop   --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 60000\n"
            "  python cli.py account\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", required=True)

    def _add_order_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--symbol",   required=True,             help="Trading pair, e.g. BTCUSDT")
        p.add_argument("--side",     required=True,             help="BUY or SELL", choices=["BUY", "SELL"])
        p.add_argument("--quantity", required=True, type=float, help="Order quantity (contracts)")

    p_market = sub.add_parser("market", help="Place a MARKET order")
    _add_order_args(p_market)
    p_market.set_defaults(func=cmd_market)

    p_limit = sub.add_parser("limit", help="Place a LIMIT order")
    _add_order_args(p_limit)
    p_limit.add_argument("--price", required=True, type=float, help="Limit price")
    p_limit.add_argument("--tif", default="GTC", choices=["GTC", "IOC", "FOK"], help="Time-in-force (default: GTC)")
    p_limit.set_defaults(func=cmd_limit)

    p_stop = sub.add_parser("stop", help="Place a STOP_MARKET order")
    _add_order_args(p_stop)
    p_stop.add_argument("--stop-price", required=True, type=float, dest="stop_price", help="Trigger price")
    p_stop.set_defaults(func=cmd_stop)

    p_acc = sub.add_parser("account", help="Show account balances and margin info")
    p_acc.set_defaults(func=cmd_account)

    return parser


def main() -> None:
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
