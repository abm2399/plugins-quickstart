"""Tests for the return math. Runnable with pytest OR as a plain script:

    python tests/test_returns.py     # from seabridge/
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from price_service.returns import compute_returns, pct  # noqa: E402


def test_pct_basic():
    assert pct(110, 100) == 10.0
    assert pct(90, 100) == -10.0
    assert pct(100, 100) == 0.0


def test_pct_guards():
    assert pct(None, 100) is None
    assert pct(100, None) is None
    assert pct(100, 0) is None


def test_compute_returns_flat_series():
    # A perfectly flat series -> every return is 0.
    end = date(2026, 7, 2)
    series = [(end - timedelta(days=i), 100.0) for i in range(400)][::-1]
    r = compute_returns(series)
    assert r["last"] == 100.0
    assert r["chg"] == 0.0
    assert r["r5d"] == 0.0
    assert r["r30d"] == 0.0
    assert r["r12m"] == 0.0
    assert r["from52"] == 0.0
    assert r["as_of"] == "2026-07-02"


def test_compute_returns_known_windows():
    # Build a series where we control the exact close at each lookback point.
    end = date(2026, 7, 2)
    closes = {}
    # default everything to 100, then set specific historical anchors
    for i in range(400):
        closes[end - timedelta(days=i)] = 100.0
    closes[end] = 120.0                       # last
    closes[end - timedelta(days=1)] = 100.0   # prev close -> chg = +20%
    closes[end - timedelta(days=5)] = 96.0    # 5d base -> +25%
    closes[end - timedelta(days=30)] = 80.0   # 30d base -> +50%
    closes[end - timedelta(days=365)] = 60.0  # 12m base -> +100%
    closes[date(2025, 12, 31)] = 100.0        # ytd base -> +20%
    series = sorted(closes.items())

    r = compute_returns(series)
    assert r["last"] == 120.0
    assert r["chg"] == 20.0
    assert r["r5d"] == 25.0
    assert r["r30d"] == 50.0
    assert r["r12m"] == 100.0
    assert r["ytd"] == 20.0
    # 52wk high should be the 120 last (max close in window); from52 == 0
    assert r["high52"] == 120.0
    assert r["from52"] == 0.0


def test_from52_below_high():
    end = date(2026, 7, 2)
    series = [(end - timedelta(days=i), 100.0) for i in range(400)]
    series.append((end - timedelta(days=10), 200.0))  # a spike high in-window
    series = sorted(series)
    # replace the last point's value so last < high
    series[-1] = (end, 150.0)
    r = compute_returns(series)
    assert r["high52"] == 200.0
    assert r["from52"] == pct(150.0, 200.0) == -25.0


def test_empty_series():
    assert compute_returns([]) == {}


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
