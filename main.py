import logging
import os
from pathlib import Path

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


def main():
    # TODO: run HTTP server and Socket server in separate processes
    pass


if __name__ == "__main__":
    main()
