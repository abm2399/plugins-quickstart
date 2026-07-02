"""Tests for the service layer + sample provider (no network). Run:

    python tests/test_service.py     # from seabridge/
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from price_service.service import (  # noqa: E402
    get_quotes_response,
    parse_tickers,
    serve,
)

AS_OF = date(2026, 7, 2)


def test_parse_from_query():
    assert parse_tickers("tickers=NVDA,MSFT,AAPL") == ["NVDA", "MSFT", "AAPL"]


def test_parse_normalizes_and_dedupes():
    got = parse_tickers("tickers= nvda , MSFT,nvda,,aapl ")
    assert got == ["NVDA", "MSFT", "AAPL"]


def test_parse_from_json_body():
    body = json.dumps({"tickers": ["nvda", "msft"]}).encode()
    assert parse_tickers("", body) == ["NVDA", "MSFT"]


def test_parse_from_json_string_and_list():
    assert parse_tickers("", b'{"tickers":"a,b"}') == ["A", "B"]
    assert parse_tickers("", b'["x","y"]') == ["X", "Y"]


def test_sample_response_shape():
    resp = get_quotes_response(["NVDA", "MSFT", "AAPL"],
                              provider_name="sample", as_of=AS_OF)
    assert resp["provider"] == "sample"
    assert resp["count"] == 3
    assert resp["asOf"] == "2026-07-02"
    assert set(resp["quotes"]) == {"NVDA", "MSFT", "AAPL"}
    for q in resp["quotes"].values():
        # every price-derived field the dashboard expects is present
        for k in ("last", "chg", "r5d", "r30d", "ytd", "r12m",
                  "high52", "from52", "asOf"):
            assert k in q
        assert q["last"] > 0
        assert q["from52"] <= 0.0  # can't be above the 52wk high


def test_sample_is_deterministic():
    a = get_quotes_response(["NVDA"], provider_name="sample", as_of=AS_OF)
    b = get_quotes_response(["NVDA"], provider_name="sample", as_of=AS_OF)
    assert a["quotes"]["NVDA"] == b["quotes"]["NVDA"]


def test_empty_request():
    resp = get_quotes_response([], provider_name="sample", as_of=AS_OF)
    assert resp["count"] == 0
    assert resp["quotes"] == {}


def test_max_tickers_truncation_is_visible():
    os.environ["PRICE_MAX_TICKERS"] = "2"
    # config reads the env at import; re-import to pick up the override
    import importlib
    import price_service.config as cfg
    import price_service.service as svc
    importlib.reload(cfg)
    importlib.reload(svc)
    try:
        resp = svc.get_quotes_response(["A", "B", "C", "D"],
                                       provider_name="sample", as_of=AS_OF)
        assert resp["count"] == 2
        assert "C" in resp["errors"] and "D" in resp["errors"]
        assert "dropped" in resp["errors"]["C"]
    finally:
        del os.environ["PRICE_MAX_TICKERS"]
        importlib.reload(cfg)
        importlib.reload(svc)


def test_serve_get_ok():
    status, body = serve("GET", "tickers=NVDA", provider_name="sample")
    assert status == 200
    payload = json.loads(body)
    assert "NVDA" in payload["quotes"]


def test_serve_options_preflight():
    status, body = serve("OPTIONS")
    assert status == 204
    assert body == ""


def test_serve_method_not_allowed():
    status, body = serve("DELETE")
    assert status == 405


def test_serve_bad_provider():
    status, body = serve("GET", "tickers=NVDA", provider_name="nope")
    assert status == 400
    assert "Unknown PRICE_PROVIDER" in json.loads(body)["error"]


def test_serve_factset_not_implemented():
    status, body = serve("GET", "tickers=NVDA", provider_name="factset")
    assert status == 501
    assert "not implemented" in json.loads(body)["error"].lower()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
