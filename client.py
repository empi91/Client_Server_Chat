import socket
import sys
import pathlib
import json

from message import Message

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"

class Client:
    database = []
    is_signed_in = False
    username = ''

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def load_database(self):
        with PATH.open(mode="r", encoding="utf-8") as file:
            self.database = json.load(file)
            # print(self.database["users"]["Agata"]["password"])

    def add_to_database(self, user_data):
        user_data_json = json.dumps(user_data)
        with PATH.open(mode="w", encoding="utf-8") as database:
            database.write(user_data_json)

    def login(self):
        uname = input("Enter username: ")
        password = input("Enter password: ")
        registered = False

        # for user in self.registered_clients.items():
        for user in self.database:
            # print(user)
            if uname == user["username"]:
                registered = True

        if registered:
            if self.check_password(uname, password):
                self.username = uname
                self.is_signed_in = True
                return 0
        else:
            self.is_signed_in = self.register_new_user(uname, password)
            return 0

    def check_password(self, uname, password):
        if self.database["users"][uname]["password"] == password:
            return True
        print("Wrong password, try again!")
        return False

    def register_new_user(self, uname, password):
        acc_type = input("Enter account type (admin/user): ")
        user = {
            "username": uname,
            "password": password,
            "type": acc_type
        }
        self.add_to_database(user)
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
# client.load_database()

while not client.is_signed_in:
    client.login()

client.start_client()

#     # TODO If NOT then save password and right to file

