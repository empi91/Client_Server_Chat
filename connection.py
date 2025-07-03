# connection.py

import socket

class Connection:
    #TODO Add reading those parameters from config file
    host = '127.0.0.1'
    port = 65432

    def __init__(self):
        self.socket = None
        print(f"Host: {self.host}, Port: {self.port}")
        

    def create_client_connection(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return self.socket
        except socket.error as s:
            print(f"[SOCKET ERROR]: {s}")


    def create_server_connection(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return self.socket
        except socket.error as s:
            print(f"[SOCKET ERROR]: {s}")





    