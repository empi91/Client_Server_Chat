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
        json_message = message.encode_message(text)
        print(f"JSON message before sent: {json_message}")
        s.send(json_message)
        print("Message sent successfully")

        while True:
            server_answer = s.recv(1024).decode("utf-8")
            print(f"Received answer before decoding: {server_answer}")
            print(message.decode_message(server_answer))
            break