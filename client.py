import socket
import sys

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
        s.send(json_message)

        json_answer = s.recv(1024).decode("utf-8")
        decoded_answer = message.decode_message(json_answer)
        if type(decoded_answer) == dict:
            for key, value in decoded_answer.items():
                print(f"{key}: {value}")
        elif type(decoded_answer) == bool:
            if decoded_answer:
                s.close()
                sys.exit()