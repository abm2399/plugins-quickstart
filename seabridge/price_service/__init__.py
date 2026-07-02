"""SeaBridge price service — live price/return layer for the dashboard.

Owns the price-derived fields (Last, %Chg, 5D/30D/YTD/12M, % from 52wk high)
that get merged by ticker onto the CSV's fundamentals on the frontend.
"""
from .service import get_quotes_response, parse_tickers, serve  # noqa: F401

__all__ = ["serve", "get_quotes_response", "parse_tickers"]
