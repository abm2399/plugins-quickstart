"""Local dev server for the price service — stdlib only, no extra deps.

    cd seabridge
    PRICE_PROVIDER=sample python server.py            # offline, deterministic
    PRICE_PROVIDER=yfinance python server.py          # live (needs `pip install yfinance`)

Then:
    curl 'http://localhost:8787/api/prices?tickers=NVDA,MSFT,AAPL'
    curl -X POST http://localhost:8787/api/prices -d '{"tickers":["NVDA","MSFT"]}'

This mirrors the deployed contract exactly, so the Retool REST query you build
against localhost works unchanged against the Vercel deployment.
"""
from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from price_service.service import serve

PORT = int(os.environ.get("PORT", "8787"))


def _cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class Handler(BaseHTTPRequestHandler):
    def _dispatch(self, method: str) -> None:
        parts = urlsplit(self.path)
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
    print(f"SeaBridge price service on http://localhost:{PORT}  (provider={provider})")
    print(f"  try: curl 'http://localhost:{PORT}/api/prices?tickers=NVDA,MSFT,AAPL'")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
