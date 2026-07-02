"""Quote — the price-derived payload the dashboard layers on top of CSV fundamentals.

These are exactly the fields that change with price and therefore should come from
the live feed rather than the FactSet CSV export. Everything else (shares, cost,
weights, PE, MOIC, EV/EBITDA) stays owned by the CSV. Keyed by ticker on the
frontend, this Quote refreshes: Last, %Chg, 5D/30D/YTD/12M, and % from 52wk high.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Quote:
    ticker: str
    last: Optional[float] = None        # latest close / price
    chg: Optional[float] = None         # % change vs previous close ("%Chg")
    r5d: Optional[float] = None         # trailing 5-calendar-day return %
    r30d: Optional[float] = None        # trailing 30-calendar-day return %
    ytd: Optional[float] = None         # year-to-date return %
    r12m: Optional[float] = None        # trailing 12-month return %
    high52: Optional[float] = None      # trailing 52-week high
    from52: Optional[float] = None      # % from 52wk high (<= 0)
    currency: Optional[str] = None
    as_of: Optional[str] = None         # ISO date of the latest observation

    def as_dict(self) -> dict:
        # camelCase-friendly for the frontend; drop the redundant ticker key
        # (it is the map key in the response) but keep it queryable if needed.
        d = asdict(self)
        d["asOf"] = d.pop("as_of")
        return d
