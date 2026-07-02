# SeaBridge Price Service

Phase B of the SeaBridge Portfolio Dashboard: a small serverless function that
returns **live prices + returns as JSON**, keyed by ticker, so the dashboard can
refresh without a fresh FactSet export.

It owns *only* the price-derived fields. The CSV stays the source of truth for
positions + fundamentals; this layers prices on top:

```
FactSet / Tamarac CSV ─► positions, shares, weights, PE, MOIC, EV/EBITDA   (source of truth)
Price service (this)  ─► Last, %Chg, 5D, 30D, YTD, 12M, % from 52wk high    (refreshed on demand)
        merged by ticker on the frontend ─► live dashboard
```

## The data-source seam (the whole point)

Providers implement one interface (`price_service/providers/base.py`). The
return math (`returns.py`) and the JSON response shape (`service.py`) are shared,
so switching data sources is a **config change, not a rebuild**:

| `PRICE_PROVIDER` | Source | Use |
|---|---|---|
| `yfinance` *(default)* | Yahoo via the unofficial `yfinance` lib | Live retail prices, $0, daily refresh |
| `sample` | Deterministic synthetic series, **no network, no deps** | Dev / demo / tests |
| `factset` | FactSet MCP feed | Institutional data — **stub**, implement once entitlement confirmed |

Migrating to FactSet later: implement `providers/factset.py::get_quotes()`, set
`PRICE_PROVIDER=factset`. Nothing in the UI or calc changes — same `Quote` shape,
same returns math.

> **yfinance caveat:** it scrapes Yahoo — no SLA, informal rate limits, breaks
> periodically. Fine for a personal daily refresh; not for client-facing
> reporting. Confirm your FactSet entitlement covers a private internal tool
> before making the `factset` provider your daily driver.

## API

`GET /api/prices?tickers=NVDA,MSFT,AAPL`
`POST /api/prices` with body `{"tickers": ["NVDA","MSFT"]}`

```jsonc
{
  "asOf": "2026-07-02",
  "provider": "yfinance",
  "count": 3,
  "quotes": {
    "NVDA": {
      "ticker": "NVDA", "last": 131.40, "chg": 2.14,
      "r5d": 5.8, "r30d": 9.2, "ytd": 28.6, "r12m": 71.2,
      "high52": 140.4, "from52": -6.4, "currency": "USD",
      "asOf": "2026-07-01"
    }
  },
  "errors": { "BADTICK": "no data returned" }
}
```

Notes:
- Tickers are upper-cased, trimmed, de-duped. Dotted symbols (`BRK.B`) work.
- Bad/unknown tickers land in `errors` — one bad ticker never fails the batch.
- Batch is capped at `PRICE_MAX_TICKERS` (default 150); anything over is reported
  in `errors`, never silently dropped.
- CORS is open (`*`) so Retool (or any browser client) can call it directly.

## Run locally

Stdlib only — the `sample` provider and all tests need **no third-party deps**.

```bash
cd seabridge

# offline, deterministic — great for building the Retool query
PRICE_PROVIDER=sample python server.py

# live prices
pip install -r requirements.txt
PRICE_PROVIDER=yfinance python server.py

curl 'http://localhost:8787/api/prices?tickers=NVDA,MSFT,AAPL'
```

## Test

```bash
cd seabridge
python tests/test_returns.py     # return math
python tests/test_service.py     # parsing, provider selection, envelope, errors
# or, if you have pytest:  pytest tests/
```

## Deploy (Vercel)

`api/prices.py` is a Vercel Python function; `vercel.json` wires the route.

```bash
cd seabridge
vercel deploy            # set PRICE_PROVIDER in project env (defaults to yfinance)
```

The endpoint contract is identical to the local server, so a Retool REST query
built against `localhost` works unchanged against the deployment. Any host that
runs a `BaseHTTPRequestHandler`-style function (or the stdlib `server.py` on a
small box / Lambda behind an adapter) works too.

## Wiring into the Retool dashboard

1. **Resource / REST query** `getPrices` →
   `GET https://<deployment>/api/prices?tickers={{ fileDropzone1.parsedValue[0].map(r => r.Ticker).join(',') }}`
2. **Refresh button** → `getPrices.trigger()` (free-tier friendly; swap for a
   scheduled run on a paid plan later).
3. **Merge by ticker** in a transformer — CSV owns fundamentals, this owns prices:
   ```js
   const px = getPrices.data.quotes;
   return fileDropzone1.parsedValue[0].map(row => {
     const q = px[row.Ticker] || {};
     return {
       ...row,
       last: q.last, chg: q.chg,
       r5d: q.r5d, r30d: q.r30d, ytd: q.ytd, r12m: q.r12m,
       from52: q.from52,
     };
   });
   ```
4. **Recalc** on the merged rows: position market value (`shares * last`), live
   portfolio weights, and sector attribution vs benchmark. These map directly to
   the fields the prototype (`../seabridge_dashboard_v2.html`) already renders.

## Layout

```
seabridge/
  server.py                     # local dev server (stdlib only)
  vercel.json                   # deploy config
  requirements.txt              # yfinance (only needed for the live provider)
  api/prices.py                 # Vercel serverless entry point
  price_service/
    quote.py                    # Quote model (the price payload)
    returns.py                  # shared return math (5D/30D/YTD/12M/%chg/from52)
    service.py                  # parse -> fetch -> JSON envelope (framework-agnostic)
    config.py                   # provider selection via PRICE_PROVIDER
    providers/
      base.py                   # PriceProvider interface (the seam)
      sample.py                 # deterministic, no network
      yfinance_provider.py      # live retail prices
      factset.py                # institutional path (stub)
  tests/
    test_returns.py
    test_service.py
```
