import socket
import sys
import pathlib

from message import Message

HOST = '127.0.0.1'
PORT = 65432
PATH = pathlib.Path.cwd() / "data.json"
MANUAL = "If you want to write new message, type '!message'\n\
If you want to check your inbox, type '!inbox'\n\
If you want to delete an account (admin only), type '!delete'\n\
If you want to get info about this server, type '!info'\n\
If you need to see this manual again, type '!help'\n\
If you want to exit, type '!stop'"

class Client:
    database = {}
    socket = None
    is_signed_in = False
    removing_itself = False
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
            # print(f"Receiving data: {decoded_header}: {decoded_message}")
            return decoded_header, decoded_message

    def send_data(self, header, data):
        message = Message(data)
        json_message = message.encode_message(header, data)
        self.socket.send(json_message)
        return 0

    def login(self):
        self.username = input("Enter username: ")
        password = input("Enter password: ")
        # TODO hardcoded for testing purposes
        # self.username = "Filip"
        # password = "password"
        credentials = {
            "username": self.username,
            "password": password
        }
        self.send_data("credentials", credentials)

    def send_account_type(self):
        acc_type = input("Enter account type (admin/user): ")
        self.send_data("type", acc_type)
        return True

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
        self.send_data("message", message_dict)

    def check_inbox(self):
        self.send_data("check_inbox", self.username)

    def read_inbox(self):
        self.send_data("read_inbox", self.username)
        pass

    def process_query(self, command):
        match command:
            case "!message":
                self.send_message()
            case "!inbox":
                self.check_inbox()
            case "!read":
                self.read_inbox()
            case "!delete":
                uname_to_delete = input("Enter name of the user to be removed from database: ")
                if self.username == uname_to_delete:
                    self.removing_itself = True
                remove_user = {
                    "calling_user": self.username,
                    "deleted_user": uname_to_delete
                }
                self.send_data("delete", remove_user)
            case "!help":
                print(MANUAL)
                return 1
            case "!info":
                self.send_data("info", "")
                return 0
            case "!stop":
                self.send_data("stop", "")
                self.socket.close()
                sys.exit()
            case _:
                error_msg = "Wrong command, try again"
                return error_msg

    def process_answer(self, header, message):
        if header == "type":
            self.send_account_type()
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

        pass

    def start_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket = s

        self.login()
        while not self.is_signed_in:
            header, data = self.receive_data()
            self.process_answer(header, data)

        print(f"User {self.username} logged successfully")
        print(MANUAL)

        while self.is_signed_in:
            command = input(f"{self.username} >:")
            error_msg = self.process_query(command)
            if error_msg:
                if isinstance(error_msg, str):
                    print(error_msg)
                else:
                    pass
            else:
                header, data = self.receive_data()
                self.process_answer(header, data)

client = Client(HOST, PORT, PATH)
client.start_client()






