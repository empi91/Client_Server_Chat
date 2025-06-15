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
            message = Message(text)
            json_message = message.encode_message()
            s.send(json_message)

            message.text = s.recv(1024).decode("utf-8")
            decoded_answer = message.decode_message()
            if type(decoded_answer) == dict:
                for key, value in decoded_answer.items():
                    print(f"{key}: {value}")
            elif type(decoded_answer) == bool:
                if decoded_answer:
                    s.close()
                    sys.exit()


client_name = input("Enter client name: ")
client = Client(HOST, PORT, client_name)
client.start_client()