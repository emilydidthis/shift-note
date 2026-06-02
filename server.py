#!/usr/bin/env python3
import http.server
import webbrowser
import os

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

print(f"Shift Note running at: http://localhost:{PORT}")
print("Press Ctrl+C to stop")
webbrowser.open(f'http://localhost:{PORT}')
http.server.HTTPServer(('', PORT), Handler).serve_forever()
