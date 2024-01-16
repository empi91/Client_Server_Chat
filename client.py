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
    database_exists = False
    database_empty = False
    username = ''

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def check_database_exists(self):
        if not self.database_path.is_file():
            self.database_path.touch()
        return self.database_path.is_file()

    def check_database_empty(self):
        if os.path.getsize(self.database_path) == 0:
            return True
        return False

    def load_database(self):
        self.check_database_exists()
        if self.database_empty:
            return 0

        with self.database_path.open(mode="r", encoding="utf-8") as file:
            for line in file:
                user = json.loads(line)
                for key, value in user.items():
                    self.database[key] = value


    def add_to_database(self, username, user_data):
        new_user = {username: user_data}
        json_database = json.dumps(new_user)

        with self.database_path.open(mode="a", encoding="utf-8") as database:
            if self.check_database_empty():
                database.write(json_database)
                return 0
            database.write("\n")
            database.write(json_database)
            return 0

    def login(self):
        uname = input("Enter username: ")
        registered = False

        for user, user_data in self.database.items():
            if uname == user:
                registered = True

        password = input("Enter password: ")

        if registered:
            if self.check_password(uname, password):
                self.username = uname
                self.is_signed_in = True
                return 0
        else:
            self.is_signed_in = self.register_new_user(uname, password)
            return 0

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
        while True:
            text = input(f"{self.username}>: ")

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


client = Client(HOST, PORT, PATH)
client.load_database()

while not client.is_signed_in:
    client.login()

client.start_client()

#     # TODO If NOT then save password and right to file

