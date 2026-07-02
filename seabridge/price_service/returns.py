"""Return math shared by every provider.

A provider's only real job is to produce a clean daily close series per ticker;
these helpers turn that series into the dashboard's return columns. Keeping the
math here (not in each provider) means yfinance, the sample feed, and a future
FactSet feed all compute returns identically.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional, Tuple

# A price series is a list of (date, close), sorted ascending by date.
Series = List[Tuple[date, float]]


def pct(current: Optional[float], base: Optional[float]) -> Optional[float]:
    """Percent change from base -> current, or None if not computable."""
    if current is None or base is None or base == 0:
        return None
    return round((current / base - 1.0) * 100.0, 2)


def _close_on_or_before(series: Series, cutoff: date) -> Optional[float]:
    """Latest close at or before `cutoff` (series must be date-ascending)."""
    chosen = None
    for d, c in series:
        if d <= cutoff:
            chosen = c
        else:
            break
    return chosen


def compute_returns(series: Series, high52: Optional[float] = None) -> dict:
    """Derive the price-driven dashboard fields from a daily close series.

    `high52` may be supplied by the provider (e.g. an official 52wk high); if
    omitted it is taken as the max close over the trailing ~1y of the series.
    """
    if not series:
        return {}
    series = sorted(series, key=lambda x: x[0])
    last_date, last = series[-1]
    prev_close = series[-2][1] if len(series) >= 2 else None

    def since(days: int) -> Optional[float]:
        base = _close_on_or_before(series, last_date - timedelta(days=days))
        return pct(last, base)

    # YTD base = last close of the prior calendar year.
    ytd_base = _close_on_or_before(series, date(last_date.year - 1, 12, 31))

    # 52wk high: prefer a provider-supplied value; else max close over ~1y.
    if high52 is None:
        one_year_ago = last_date - timedelta(days=365)
        window = [c for d, c in series if d >= one_year_ago]
        high52 = max(window) if window else last

    return {
        "last": round(last, 2) if last is not None else None,
        "chg": pct(last, prev_close),
        "r5d": since(5),
        "r30d": since(30),
        "ytd": pct(last, ytd_base),
        "r12m": since(365),
        "high52": round(high52, 2) if high52 is not None else None,
        "from52": pct(last, high52),
        "as_of": last_date.isoformat(),
    }
