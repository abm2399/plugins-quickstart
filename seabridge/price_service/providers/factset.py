"""FactsetProvider — placeholder for the institutional data path (Option 2).

This is the seam made concrete: when the FactSet entitlement is confirmed for a
private internal tool, implement get_quotes() here to pull prices/returns through
the FactSet MCP connection, then set PRICE_PROVIDER=factset. Nothing else in the
service or the dashboard changes — same Quote shape, same returns math.

Two integration shapes are possible:
  1. This process calls the FactSet MCP tools directly and builds a close series
     per ticker, then reuses returns.compute_returns() exactly like yfinance.
  2. FactSet returns pre-computed returns; map them straight onto Quote fields
     and skip compute_returns().

Prefer (1) for parity with the other providers unless FactSet's precomputed
windows are authoritative for this book.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from ..quote import Quote
from .base import PriceProvider


class FactsetProvider(PriceProvider):
    name = "factset"

    def get_quotes(
        self, tickers: List[str], as_of: date
    ) -> Tuple[Dict[str, Quote], Dict[str, str]]:
        raise NotImplementedError(
            "FactSet MCP provider not implemented yet. Confirm the FactSet "
            "entitlement covers feeding data into a private internal tool, then "
            "implement get_quotes() here and set PRICE_PROVIDER=factset. "
            "See this module's docstring for the two integration shapes."
        )
