# main.py

import pathlib

from server import Server

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"
SERVER_VERSION = "1.0.1"

server = Server(HOST, PORT, SERVER_VERSION)
server.start_server()