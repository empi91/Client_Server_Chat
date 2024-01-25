#client.py

import socket
import sys

from connection import Connection
from query import Query
from user import User

HOST = '127.0.0.1'
PORT = 65432
MAX_MESSAGE_SIZE = 512
MANUAL = "If you want to write new message, type '!message'\n\
If you want to check your inbox, type '!inbox'\n\
If you want to delete an account (admin only), type '!delete'\n\
If you want to get info about this server, type '!info'\n\
If you need to see this manual again, type '!help'\n\
If you want to exit, type '!stop'"

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = Connection(self.socket)
        self.user = User()
        self.query = Query()
        self.start_client(HOST, PORT)
        pass

    def start_client(self, host, port):
        self.socket.connect((host, port))

        self.user.login_user(self.socket)

        while True:
            command = input(f"{self.user.username} >:")
            header, message = self.process_user_command(command)

            if header == "error_msg":
                if isinstance(message, str):
                    print(message)
                else:
                    pass
            else:
                header, data = self.connection.receive_data()
                self.query.process_query(header, data)


    def process_user_command(self, command):
        match command:
            case "!message":
                self.send_message()
                return "ack", 1

            case "!inbox":
                self.connection.send_data("check_inbox", self.user.username)
                return "ack", 1

            case "!read":
                self.connection.send_data("read_message", self.user.username)
                return "ack", 1

            case "!delete":
                uname_to_delete = input("Enter name of the user to be removed from database: ")
                remove_user = {
                    "calling_user": self.user.username,
                    "deleted_user": uname_to_delete
                }
                self.connection.send_data("delete", remove_user)
                return "ack", 1

            case "!help":
                print(MANUAL)
                return "error_msg", 1

            case "!info":
                self.connection.send_data("check_info", "")
                return "ack", 1

            case "!stop":
                self.connection.send_data("stop", "")
                self.socket.close()
                sys.exit()

            case _:
                error_msg = "Wrong command, try again"
                return "error_msg", error_msg

    def send_message(self):
        receiver = input("Enter received name: ")
        message = input("Enter message (up to 255 characters): ")
        while len(message) > 255:
            print("Message too long, try again")
            message = input("Enter message (up to 255 characters): ")
        message_dict = {
            "sender": self.user.username,
            "receiver": receiver,
            "message": message,
        }
        self.connection.send_data("send_message", message_dict)



client = Client()
client.start_client(HOST, PORT)