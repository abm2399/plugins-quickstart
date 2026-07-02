"""PriceProvider — the seam that decouples the dashboard from its data source.

Swapping yfinance for the FactSet MCP feed later is a matter of adding a
provider and flipping the PRICE_PROVIDER env var. The calc logic (returns.py)
and the response shape (service.py) never change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Tuple

from ..quote import Quote


class PriceProvider(ABC):
    #: short identifier surfaced in the response envelope
    name: str = "base"

    @abstractmethod
    def get_quotes(
        self, tickers: List[str], as_of: date
    ) -> Tuple[Dict[str, Quote], Dict[str, str]]:
        """Fetch quotes for `tickers`.

        Returns a tuple of:
          - {ticker: Quote}   successfully resolved quotes
          - {ticker: reason}  tickers that could not be resolved, with a message

        `as_of` is the reference date for return windows. Live providers may
        ignore it (they use the real last trading day); the sample provider
        uses it to generate a deterministic series ending on that date.
        """
        raise NotImplementedError
