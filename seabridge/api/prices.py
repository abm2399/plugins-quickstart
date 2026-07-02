"""Vercel serverless entry point — GET/POST /api/prices.

Vercel's Python runtime invokes a `handler` subclass of BaseHTTPRequestHandler.
This file stays thin: it defers all logic to price_service.service.serve().

Deploy: `vercel deploy` from the seabridge/ dir (see vercel.json + README).
Set the PRICE_PROVIDER env var in the Vercel project settings.
"""
from __future__ import annotations

import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

# Make the sibling price_service package importable when Vercel runs this file.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from price_service.service import serve  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _dispatch(self, method: str) -> None:
        parts = urlsplit(self.path)
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None

        status, payload = serve(method, parts.query, body)

        self.send_response(status)
        self._cors()
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
