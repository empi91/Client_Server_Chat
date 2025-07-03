# main.py

import pathlib

from server import Server

PATH = pathlib.Path.cwd() / "data.json"

def main():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    main()