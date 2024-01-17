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
    is_signed_in = False
    username = ''

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def send_data(self, header, data, s):
        message = Message(data)
        json_message = message.encode_message(header, data)
        s.send(json_message)
        return 0

    def login(self, socket):
        uname = input("Enter username: ")
        registered = False

        self.send_data("username", uname, socket)

        # for user in self.database:
        #     if uname == user:
        #         registered = True

        password = input("Enter password: ")

        self.send_data("password", password, socket)

        # if registered:
        #     if self.check_password(uname, password):
        #         self.username = uname
        #         self.is_signed_in = True
        #         return 0
        # else:
        #     self.is_signed_in = self.register_new_user(uname, password)
        #     return 0

    def check_password(self, uname, password):
        if self.database[uname]["password"] == password:
            print("Password correct, welcome back!")
            return True
        print("Wrong password, try again!")
        return False

    def register_new_user(self, uname, password):
        acc_type = input("Enter account type (admin/user): ")
        user_data = {
            "username": uname,
            "password": password,
            "type": acc_type
        }
        self.add_to_database(uname, user_data)
        return True

    def start_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        return s
        # while True:
        #     self.login()
        #
        #     text = input(f"{self.username}>: ")
        #     # self.send_data(text)
        #
        #     message = Message(text)
        #     json_message = message.encode_message(text)
        #     s.send(json_message)
        #
        #     json_answer = s.recv(1024).decode("utf-8")
        #     decoded_answer = message.decode_message(json_answer)
        #     if type(decoded_answer) == dict:
        #         for key, value in decoded_answer.items():
        #             print(f"{key}: {value}")
        #     elif type(decoded_answer) == bool:
        #         if decoded_answer:
        #             s.close()
        #             sys.exit()


client = Client(HOST, PORT, PATH)
connection = client.start_client()

while not client.is_signed_in:
    client.login(connection)




