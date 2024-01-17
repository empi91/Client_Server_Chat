import socket
import sys
import pathlib
import json
import os

from message import Message

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"

class Client:
    database = {}
    socket = None
    is_signed_in = False
    username = ''

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def receive_data(self):
        while True:
            received_data = self.socket.recv(255).decode("utf-8")
            if not received_data:
                break
            message = Message(received_data)
            decoded_header, decoded_message = message.decode_message(received_data)
            return decoded_header, decoded_message

    def send_data(self, header, data):
        message = Message(data)
        json_message = message.encode_message(header, data)
        self.socket.send(json_message)
        return 0

    def login(self):
        self.username = input("Enter username: ")
        password = input("Enter password: ")
        credentials = {
            "username": self.username,
            "password": password
        }
        self.send_data("credentials", credentials)

    def send_acc_type(self):
        acc_type = input("Enter account type (admin/user): ")
        self.send_data("type", acc_type)
        return True

    def start_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket = s

        self.login()
        while not self.is_signed_in:
            header, data = self.receive_data()
            if header == "type":
                self.send_acc_type()
            elif header == "password":
                print("Wrong password, try again!")
                self.login()
            elif header == "acc" and data == "login":
                self.is_signed_in = True

        print(f"User {self.username} logged successfully")

        while True:
            pass

            # self.send_data(text)
            #
            # message = Message(text)
            # json_message = message.encode_message(text)
            # s.send(json_message)

            # json_answer = s.recv(1024).decode("utf-8")
            # decoded_answer = message.decode_message(json_answer)
            # if type(decoded_answer) == dict:
            #     for key, value in decoded_answer.items():
            #         print(f"{key}: {value}")
            # elif type(decoded_answer) == bool:
            #     if decoded_answer:
            #         s.close()
            #         sys.exit()


client = Client(HOST, PORT, PATH)
client.start_client()






