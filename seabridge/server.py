"""Local dev server for the SeaBridge dashboard + price service (stdlib only).

    cd seabridge
    PRICE_PROVIDER=sample python server.py            # offline, deterministic
    PRICE_PROVIDER=yfinance python server.py          # live (needs `pip install yfinance`)

Then just open http://localhost:8787 in your browser — the server serves the
dashboard page itself, so there are no file paths to hunt for and the
"Refresh prices" button talks to /api/prices on the same origin.

API only:
    curl 'http://localhost:8787/api/prices?tickers=NVDA,MSFT,AAPL'
    curl -X POST http://localhost:8787/api/prices -d '{"tickers":["NVDA","MSFT"]}'

The /api/prices contract mirrors the deployed Vercel function exactly, so a
Retool REST query built against localhost works unchanged against production.
"""
from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from price_service.service import serve

PORT = int(os.environ.get("PORT", "8787"))

# Locate the dashboard HTML robustly: normally it sits one level up from this
# file (repo root); also accept it sitting right next to server.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
_HTML_CANDIDATES = [
    os.path.join(_HERE, "..", "seabridge_dashboard_v2.html"),
    os.path.join(_HERE, "seabridge_dashboard_v2.html"),
]
_DASHBOARD_PATHS = {"/", "/dashboard", "/index.html", "/seabridge_dashboard_v2.html"}


def _find_html() -> str | None:
    for c in _HTML_CANDIDATES:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def _cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class Handler(BaseHTTPRequestHandler):
    def _serve_dashboard(self) -> None:
        html_path = _find_html()
        if not html_path:
            self.send_response(404)
            _cors(self)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"seabridge_dashboard_v2.html not found next to the server.\n"
                b"The API still works at /api/prices, but to see the dashboard\n"
                b"keep server.py inside the seabridge/ folder with the HTML one\n"
                b"level up (the repo layout), or place the HTML beside server.py.\n"
            )
            return
        with open(html_path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        _cors(self)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _dispatch(self, method: str) -> None:
        parts = urlsplit(self.path)

        # Serve the dashboard page for GET on the root / dashboard paths.
        if method == "GET" and parts.path in _DASHBOARD_PATHS:
            self._serve_dashboard()
            return

        # Everything else is the price API.
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None

        status, payload = serve(method, parts.query, body)

        self.send_response(status)
        _cors(self)
        if payload:
            self.send_header("Content-Type", "application/json")
        self.end_headers()
        if payload:
            self.wfile.write(payload.encode("utf-8"))

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_OPTIONS(self):
        self._dispatch("OPTIONS")

    def log_message(self, fmt, *args):  # quieter default logging
        return


if __name__ == "__main__":
    provider = os.environ.get("PRICE_PROVIDER", "yfinance")
    print("=" * 56)
    print("  SeaBridge dashboard is running.")
    print(f"  Open this in your browser:  http://localhost:{PORT}")
    print(f"  (price provider = {provider})")
    print("  Press Ctrl+C here to stop.")
    print("=" * 56)
    try:
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
