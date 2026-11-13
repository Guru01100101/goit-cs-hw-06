import logging
import os
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
from multiprocessing import Process
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from pymongo import MongoClient

# HTTP server
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "3000"))

# Socket server (UDP)
SOCKET_HOST = os.getenv("SOCKET_HOST", "0.0.0.0")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", "5000"))
SOCKET_HOST_CLIENT = os.getenv("SOCKET_HOST_CLIENT", "localhost")

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

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/message":
            self.send_html("error.html", 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        logging.info("Received message form data: %s", body)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(body, (SOCKET_HOST_CLIENT, SOCKET_PORT))

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def parse_message(data):
    decoded_data = unquote(data.decode("utf-8"))
    fields = parse_qs(decoded_data)
    return {
        "username": fields.get("username", [""])[0],
        "message": fields.get("message", [""])[0],
    }


def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((SOCKET_HOST, SOCKET_PORT))
        logging.info("UDP server listening on %s:%s", SOCKET_HOST, SOCKET_PORT)

        mongo_client = MongoClient(MONGO_URI)
        messages_collection = mongo_client["messages_db"]["messages"]

        try:
            while True:
                data, address = server_socket.recvfrom(1024 * 4)

                try:
                    message = parse_message(data)
                    document = {
                        "date": str(datetime.now()),
                        "username": message["username"],
                        "message": message["message"],
                    }
                    messages_collection.insert_one(document)
                    logging.info("Saved message from %s", address)
                except Exception:
                    logging.exception("Failed to process UDP message from %s", address)
        finally:
            mongo_client.close()


def run_http_server():
    server = HTTPServer((HTTP_HOST, HTTP_PORT), HttpHandler)
    logging.info("HTTP server listening on %s:%s", HTTP_HOST, HTTP_PORT)
    server.serve_forever()


def main():
    http_process = Process(target=run_http_server, name="http-server")
    socket_process = Process(target=run_socket_server, name="socket-server")

    http_process.start()
    socket_process.start()

    http_process.join()
    socket_process.join()


if __name__ == "__main__":
    main()
