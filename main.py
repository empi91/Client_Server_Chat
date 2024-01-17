import pathlib
from server import Server

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"


server = Server(HOST, PORT, PATH)
server.start_server()


