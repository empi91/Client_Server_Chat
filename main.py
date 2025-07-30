"""Main entry point for the socket-based client-server application.

This module starts the server and handles the main application flow.
"""

import pathlib

from server import Server
from config import config

PATH = pathlib.Path.cwd() / config.database.DB_FILE

def main():
    """Start the server application."""
    server = Server()
    server.start_server()


if __name__ == "__main__":
    main()