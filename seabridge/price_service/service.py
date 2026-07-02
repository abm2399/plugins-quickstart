"""Service layer — parse a request, fetch quotes, build the JSON envelope.

Framework-agnostic on purpose: `serve()` takes plain inputs and returns a
(status, body) pair, so the local dev server (server.py) and the Vercel handler
(api/prices.py) are both thin wrappers around it.

Response shape:
    {
      "asOf": "2026-07-02",
      "provider": "yfinance",
      "count": 3,
      "quotes": {
        "NVDA": {"last": ..., "chg": ..., "r5d": ..., ..., "asOf": "..."},
        ...
      },
      "errors": {"BADTICK": "no data returned"}
    }
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple
from urllib.parse import parse_qs

from .config import MAX_TICKERS, get_provider


def parse_tickers(raw_query: str = "", body: Optional[bytes] = None) -> List[str]:
    """Accept tickers from ?tickers=A,B,C (GET) or a JSON body (POST).

    JSON body may be {"tickers": ["A","B"]} or {"tickers": "A,B"} or a bare list.
    """
    tickers: List[str] = []

    if raw_query:
        qs = parse_qs(raw_query)
        for key in ("tickers", "ticker", "symbols"):
            for chunk in qs.get(key, []):
                tickers.extend(chunk.split(","))

    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            payload = None
        if isinstance(payload, dict):
            val = payload.get("tickers") or payload.get("symbols")
            if isinstance(val, str):
                tickers.extend(val.split(","))
            elif isinstance(val, list):
                tickers.extend(str(x) for x in val)
        elif isinstance(payload, list):
            tickers.extend(str(x) for x in payload)

    # normalize: upper, strip, drop blanks, de-dupe preserving order
    seen = set()
    out: List[str] = []
    for t in tickers:
        t = t.strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def get_quotes_response(
    tickers: List[str],
    provider_name: Optional[str] = None,
    as_of: Optional[date] = None,
) -> dict:
    """Core entry point: resolve quotes and build the response dict."""
    as_of = as_of or datetime.now(timezone.utc).date()
    provider = get_provider(provider_name)

    if not tickers:
        return {
            "asOf": as_of.isoformat(),
            "provider": provider.name,
            "count": 0,
            "quotes": {},
            "errors": {},
        }

    dropped = tickers[MAX_TICKERS:]
    tickers = tickers[:MAX_TICKERS]

    quotes, errors = provider.get_quotes(tickers, as_of)

    for t in dropped:  # keep truncation visible, never silent
        errors[t] = f"dropped: exceeds PRICE_MAX_TICKERS={MAX_TICKERS}"

    return {
        "asOf": as_of.isoformat(),
        "provider": provider.name,
        "count": len(quotes),
        "quotes": {t: q.as_dict() for t, q in quotes.items()},
        "errors": errors,
    }


def serve(
    method: str,
    raw_query: str = "",
    body: Optional[bytes] = None,
    provider_name: Optional[str] = None,
) -> Tuple[int, str]:
    """Handle one request. Returns (http_status, json_body)."""
    method = (method or "GET").upper()

    if method == "OPTIONS":
        return 204, ""

    if method not in ("GET", "POST"):
        return 405, json.dumps({"error": f"method {method} not allowed"})

    try:
        tickers = parse_tickers(raw_query, body)
        payload = get_quotes_response(tickers, provider_name=provider_name)
        return 200, json.dumps(payload)
    except ValueError as exc:  # bad provider config, etc.
        return 400, json.dumps({"error": str(exc)})
    except NotImplementedError as exc:  # e.g. factset stub
        return 501, json.dumps({"error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return 500, json.dumps({"error": f"{type(exc).__name__}: {exc}"})
