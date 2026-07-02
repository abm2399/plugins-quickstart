"""YfinanceProvider — live prices via the (unofficial) yfinance library.

Caveats worth remembering: yfinance scrapes Yahoo, has no SLA, and rate-limits
informally. Fine for a personal daily refresh; not for client-facing reporting.
See seabridge/README.md for the tradeoff vs. the FactSet MCP path.

`yfinance` is imported lazily inside get_quotes so the rest of the package (and
the sample provider used in tests) works without the dependency installed.
"""
from __future__ import annotations

import time
from datetime import date
from typing import Dict, List, Tuple

from ..quote import Quote
from ..returns import compute_returns
from .base import PriceProvider

# Warm-invocation cache: {ticker: (epoch_seconds, Quote)}. Helps avoid hammering
# Yahoo when a serverless container stays warm across refreshes. Stateless-safe:
# a cold start simply starts empty.
_CACHE: Dict[str, Tuple[float, Quote]] = {}
_TTL_SECONDS = 60


class YfinanceProvider(PriceProvider):
    name = "yfinance"

    def __init__(self, ttl_seconds: int = _TTL_SECONDS):
        self.ttl = ttl_seconds

    def get_quotes(
        self, tickers: List[str], as_of: date
    ) -> Tuple[Dict[str, Quote], Dict[str, str]]:
        quotes: Dict[str, Quote] = {}
        errors: Dict[str, str] = {}

        now = time.time()
        pending = []
        for t in tickers:
            cached = _CACHE.get(t)
            if cached and (now - cached[0]) < self.ttl:
                quotes[t] = cached[1]
            else:
                pending.append(t)

        if not pending:
            return quotes, errors

        try:
            import yfinance as yf  # noqa: WPS433 (lazy import by design)
        except ImportError:
            for t in pending:
                errors[t] = "yfinance not installed (pip install yfinance)"
            return quotes, errors

        for t in pending:
            try:
                hist = yf.Ticker(t).history(period="1y", interval="1d",
                                            auto_adjust=False)
                if hist is None or hist.empty or "Close" not in hist:
                    errors[t] = "no data returned"
                    continue
                closes = hist["Close"].dropna()
                series = [
                    (idx.date(), float(val))
                    for idx, val in closes.items()
                ]
                if not series:
                    errors[t] = "empty price series"
                    continue
                # Yahoo 52wk high, if available, beats a series-derived max.
                high52 = None
                if "High" in hist:
                    highs = hist["High"].dropna()
                    if not highs.empty:
                        high52 = float(highs.max())
                fields = compute_returns(series, high52=high52)
                q = Quote(ticker=t, currency="USD", **fields)
                quotes[t] = q
                _CACHE[t] = (now, q)
            except Exception as exc:  # noqa: BLE001 keep one bad ticker from failing the batch
                errors[t] = f"{type(exc).__name__}: {exc}"

        return quotes, errors
