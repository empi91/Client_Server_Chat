import socket
from message import Message

HOST = "127.0.0.1"
PORT = 65432
HEADER_LENGTH = 2

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        text = input("Message: ")
        message = Message(text)
        print(message.encode_message())


        # mes_len = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        # mes = message.encode("utf-8")
        # s.send(mes_len)
        # s.send(mes)
