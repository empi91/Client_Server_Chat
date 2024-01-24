import socket
import sys
import pathlib

from connection import Connection

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"
MAX_MESSAGE_SIZE = 512
MANUAL = "If you want to write new message, type '!message'\n\
If you want to check your inbox, type '!inbox'\n\
If you want to delete an account (admin only), type '!delete'\n\
If you want to get info about this server, type '!info'\n\
If you need to see this manual again, type '!help'\n\
If you want to exit, type '!stop'"

class Client:
    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path
        self.database = {}
        self.socket = None
        self.is_signed_in = False
        self.removing_itself = False
        self.username = ""

# ----------------------- Connection part -----------------------

    def send_data(self, header, data):
        connection = Connection(self.socket)
        json_message = connection.encode_message(header, data)
        self.socket.send(json_message)
        return 0

# ----------------------- User login/register part -----------------------

    def login(self):
        self.username = input("Enter username: ")
        password = input("Enter password: ")
        credentials = {
            "username": self.username,
            "password": password
        }
        connection = Connection(self.socket)
        connection.send_data("credentials", credentials)
        # self.send_data("credentials", credentials)

# ----------------------- Query part -----------------------

    def send_account_type(self):
        acc_type = input("Enter account type (admin/user): ")
        return "type", acc_type

    def send_message(self):
        receiver = input("Enter received name: ")
        message = input("Enter message (up to 255 characters): ")
        while len(message) > 255:
            print("Message too long, try again")
            message = input("Enter message (up to 255 characters): ")
        message_dict = {
            "sender": self.username,
            "receiver": receiver,
            "message": message,
        }
        return "message", message_dict

    def process_query(self, command):
        match command:
            case "!message":
                header, message = self.send_message()
                return header, message
            case "!inbox":
                return "check_inbox", self.username
            case "!read":
                return "read_inbox", self.username
            case "!delete":
                uname_to_delete = input("Enter name of the user to be removed from database: ")
                if self.username == uname_to_delete:
                    self.removing_itself = True
                remove_user = {
                    "calling_user": self.username,
                    "deleted_user": uname_to_delete
                }
                return "delete", remove_user
            case "!help":
                print(MANUAL)
                return "error_msg", 1
            case "!info":
                return "info", ""
            case "!stop":
                self.send_data("stop", "")
                self.socket.close()
                sys.exit()
            case _:
                error_msg = "Wrong command, try again"
                return "error_msg", error_msg

    def process_answer(self, header, message):
        if header == "type":
            header, message = self.send_account_type()
            self.send_data(header, message)
        elif header == "password":
            print("Wrong password, try again!")
            self.login()
        elif header == "acc":
            if message == "login":
                self.is_signed_in = True
            elif message == "user_deleted":
                if self.removing_itself:
                    print(f"Your account deleted successfully")
                    self.process_query("!stop")
                print(f"User account deleted successfully")
            elif message == "message_delivered":
                print("Message delivered successfully")
        elif header == "server_info":
            print(f"Server version: {message['Server version']}\n"
                  f"Server start date: {message['Server start date']}\n"
                  f"Server uptime: {message['Server uptime']}")
        elif header == "error":
            print(message)
        elif header == "inbox_size":
            print(f"You have {message} unread messages")
            if message > 0:
              print(f"To read first one type !read")
        elif header == "inbox_message":
            print(f"Message from {message['sender']}:\n"
                  f"{message['message']}")

    # ----------------------- Client part -----------------------
    def start_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket = s
        connection = Connection(self.socket)

        self.login()
        while not self.is_signed_in:
            header, data = connection.receive_data()
            self.process_answer(header, data) #TODO Move to query

        print(f"User {self.username} logged successfully")
        print(MANUAL)

        while self.is_signed_in:
            command = input(f"{self.username} >:")
            header, message = self.process_query(command) #TODO Move to query
            if header == "error_msg":
                if isinstance(message, str):
                    print(message)
                else:
                    pass
            else:
                connection.send_data(header, message)
                header, data = connection.receive_data()
                self.process_answer(header, data)

client = Client(HOST, PORT, PATH)
client.start_client()






