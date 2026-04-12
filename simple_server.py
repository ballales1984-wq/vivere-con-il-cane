#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body><h1>Vivere con il Cane</h1><p>Server running!</p></body></html>"
        )

    def log_message(self, format, *args):
        pass


port = int(__import__("os").environ.get("PORT", "10000"))
print(f"Starting simple server on port {port}", flush=True)
server = HTTPServer(("0.0.0.0", port), Handler)
server.serve_forever()
