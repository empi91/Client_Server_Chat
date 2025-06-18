import socket
import sys

from message import Message

HOST = '127.0.0.1'
PORT = 65432

class Client:

    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

    def start_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        while True:
            text = input(f"{self.name}>: ")
            message = Message(1, text, self.name)
            json_message = message.encode_message()
            s.send(json_message)

            mess_received = s.recv(1024).decode("utf-8")
            decoded_header, decoded_answer, author = message.decode_message(mess_received)

            if decoded_header == "Command":
                for key, value in decoded_answer.items():
                    print(f"{key}: {value}")
            elif decoded_header == "Stop":
                    s.close()
                    sys.exit()


client_name = input("Enter client name: ")
client = Client(HOST, PORT, client_name)
client.start_client()