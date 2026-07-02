"""Provider selection — the one place the data source is chosen.

Flip PRICE_PROVIDER to move between data layers without touching calc or UI:
    PRICE_PROVIDER=yfinance   # live retail prices (default)
    PRICE_PROVIDER=sample     # deterministic offline data (dev / demo / tests)
    PRICE_PROVIDER=factset    # institutional feed (once implemented + entitled)
"""
from __future__ import annotations

import os

from .providers.base import PriceProvider

DEFAULT_PROVIDER = "yfinance"

# Cap the batch so a stray/huge request can't fan out into hundreds of Yahoo hits.
MAX_TICKERS = int(os.environ.get("PRICE_MAX_TICKERS", "150"))


def get_provider(name: str = None) -> PriceProvider:
    name = (name or os.environ.get("PRICE_PROVIDER") or DEFAULT_PROVIDER).lower()

    if name == "sample":
        from .providers.sample import SampleProvider
        return SampleProvider()
    if name == "yfinance":
        from .providers.yfinance_provider import YfinanceProvider
        return YfinanceProvider()
    if name == "factset":
        from .providers.factset import FactsetProvider
        return FactsetProvider()

    raise ValueError(
        f"Unknown PRICE_PROVIDER {name!r}. "
        f"Expected one of: sample, yfinance, factset."
    )
