#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Alessio. All Rights Reserved.
#
# Licensed under the Private Use License.
# This software may only be used for private, non-commercial purposes.
# Redistribution, reproduction, or commercial use is strictly prohibited
# without express written permission from the copyright holder.
#
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
