"""SampleProvider — deterministic synthetic quotes, zero network.

Purpose: develop and demo the dashboard's price-refresh path without depending
on Yahoo being up (or reachable behind a proxy), and give tests a stable series
that exercises the same returns.compute_returns() code path as the live feed.

Data is derived from a hash of the ticker, so a given ticker always produces the
same series for a given as_of date — reproducible, no randomness.
"""
from __future__ import annotations

import hashlib
import math
from datetime import date, timedelta
from typing import Dict, List, Tuple

from ..quote import Quote
from ..returns import compute_returns
from .base import PriceProvider


def _seed(ticker: str) -> int:
    return int(hashlib.sha256(ticker.encode("utf-8")).hexdigest()[:12], 16)


def _series(ticker: str, as_of: date, days: int = 400):
    """Build a deterministic daily close series ending on `as_of`."""
    s = _seed(ticker)
    base = 20.0 + (s % 900)                 # starting price 20..920
    drift = ((s >> 8) % 60 - 20) / 10000.0   # small per-day drift, -0.0020..0.0040
    amp = 0.05 + ((s >> 16) % 25) / 100.0    # cyclical amplitude 0.05..0.30
    period = 30 + (s % 90)                    # cycle length in days
    phase = (s % 360) * math.pi / 180.0

    out = []
    price = base
    for i in range(days):
        d = as_of - timedelta(days=days - 1 - i)
        # deterministic wiggle: slow cycle + a shorter hash-driven ripple
        wiggle = amp * math.sin(2 * math.pi * i / period + phase)
        ripple = 0.015 * math.sin(2 * math.pi * i / 7.0 + phase)
        price = base * (1 + drift * i + wiggle + ripple)
        out.append((d, round(price, 4)))
    return out


class SampleProvider(PriceProvider):
    name = "sample"

    def get_quotes(
        self, tickers: List[str], as_of: date
    ) -> Tuple[Dict[str, Quote], Dict[str, str]]:
        quotes: Dict[str, Quote] = {}
        errors: Dict[str, str] = {}
        for t in tickers:
            series = _series(t, as_of)
            fields = compute_returns(series)
            if not fields:
                errors[t] = "no data"
                continue
            quotes[t] = Quote(ticker=t, currency="USD", **fields)
        return quotes, errors
