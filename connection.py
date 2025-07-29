# connection.py

import socket

class Connection:
    #TODO Add reading those parameters from config file
    host = '127.0.0.1'
    port = 65432

    def __init__(self):
        self.socket = None
        print(f"Host: {self.host}, Port: {self.port}")
        

    def create_connection(self, is_server=False):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if is_server:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return self.socket
        except socket.error as s:
            print(f"[SOCKET ERROR]: {s}")






    