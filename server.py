# server.py

import socket
import time

from connection import Connection
from query import Query

class Server:

    def __init__(self, host, port, server_version):
        self.host = host
        self.port = port
        self.query = Query()
        self.query.start_time = time.gmtime()
        self.query.server_version = server_version

        # Starting the server socket connection
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print("Server online")

    def start_server(self):
        # Accepting connection from client
        client_socket, addr = self.socket.accept()
        connection = Connection(client_socket)

        print(f"Client connected: {addr}")

        while True:
            query_header, query_message = connection.receive_data()
            ans_header, ans_message = self.query.process_query(query_header, query_message)
            connection.send_data(ans_header, ans_message)





