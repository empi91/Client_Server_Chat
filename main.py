# main.py

import pathlib

from server import Server

PATH = pathlib.Path.cwd() / "data.json"

server = Server()
server.start_server()