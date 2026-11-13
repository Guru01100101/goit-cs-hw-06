import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse

# HTTP server
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000

# Socket server (UDP)
SOCKET_HOST = "0.0.0.0"
SOCKET_PORT = 5000

# Folder with html pages and static assets
BASE_DIR = Path(__file__).parent / "front-init"

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(processName)s] %(levelname)s: %(message)s",
)


class HttpHandler(BaseHTTPRequestHandler):
    def send_html(self, filename, status=200):
        file_path = BASE_DIR / filename
        content = file_path.read_bytes()

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_static(self, path):
        base_dir = BASE_DIR.resolve()
        file_path = (base_dir / unquote(path.lstrip("/"))).resolve()

        if not file_path.is_file() or base_dir not in file_path.parents:
            self.send_html("error.html", 404)
            return

        content = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.send_html("index.html")
        elif path in ("/message", "/message.html"):
            self.send_html("message.html")
        elif path != "/":
            self.send_static(path)
        else:
            self.send_html("error.html", 404)


def run_http_server():
    server = HTTPServer((HTTP_HOST, HTTP_PORT), HttpHandler)
    logging.info("HTTP server listening on %s:%s", HTTP_HOST, HTTP_PORT)
    server.serve_forever()


def main():
    run_http_server()


if __name__ == "__main__":
    main()
