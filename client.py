from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger("client")


class BinanceClientError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")

        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")

        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.info("BinanceClient initialised | base_url=%s", self._base_url)

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = False,
    ) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)

        url = f"{self._base_url}{endpoint}"
        logger.debug("REQUEST  %s %s | params=%s", method, url, params)

        try:
            response = self._session.request(method, url, params=params, timeout=10)
        except requests.exceptions.Timeout:
            logger.error("Request timed out | %s %s", method, url)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error | %s %s | %s", method, url, exc)
            raise

        logger.debug(
            "RESPONSE %s %s | status=%s | body=%s",
            method,
            url,
            response.status_code,
            response.text[:500],
        )

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response | body=%s", response.text[:200])
            raise BinanceClientError(f"Non-JSON response: {response.text[:200]}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            msg = data.get("msg", "Unknown API error")
            logger.error("API error | code=%s | msg=%s", data["code"], msg)
            raise BinanceClientError(f"[{data['code']}] {msg}")

        return data

    def get_server_time(self) -> int:
        data = self._request("GET", "/fapi/v1/time")
        return data["serverTime"]

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(self, **kwargs) -> dict:
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/fapi/v1/order", params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/fapi/v1/order", params=params, signed=True)

    def get_open_orders(self, symbol: str | None = None) -> list:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v1/openOrders", params=params, signed=True)
