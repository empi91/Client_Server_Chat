import socket
import time
import json
import os
import sys

from message import Message

class Server:
    SERVER_VERSION = '1.0.1'

    database = {}
    start_time = 0
    client_signed_in = False
    socket = None
    username = ""
    password = ""

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def load_database(self):
        try:
            if os.path.getsize(self.database_path) == 0:
                self.database = {}
            else:
                with self.database_path.open(mode="r", encoding="utf-8") as file:
                    self.database = json.load(file)
        except FileNotFoundError:
            self.database = {}
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Problematic JSON text:")
            print(e.doc)

    def add_to_database(self, username, user_data):
        self.database[username] = user_data
        self.save_database()

    def save_database(self):
        with self.database_path.open(mode="w", encoding="utf-8") as file:
            json.dump(self.database, file, indent=2)
        self.load_database()

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
        # print(f"Sending data: {header}: {data}")
        json_message = message.encode_message(header, data)
        self.socket.send(json_message)
        return 0

    def check_if_registered(self, uname):
        for user in self.database:
            if uname == user:
                return True
        return False

    def check_password(self, uname, password):
        if self.database[uname]["password"] == password:
            # print("Password correct, welcome back!")
            self.send_data("acc", "login")
            return True
        # print("Wrong password, try again!")
        self.send_data("password", "wrong")

        return False

    def register_new_user(self, username, password, acc_type):
        user_data = {
            "username": username,
            "password": password,
            "type": acc_type,
            "inbox": []
        }
        self.add_to_database(username, user_data)
        print(f"User {self.username} registered")
        return True

    def login(self, login_data):
        self.username = login_data["username"]
        self.password = login_data["password"]

        client_signed_up = self.check_if_registered(self.username)
        if client_signed_up:
            self.client_signed_in = self.check_password(self.username, self.password)
        else:
            self.send_data("type", "Enter account type: ")

    def calc_uptime(self):
        curr_time = time.gmtime()
        uptime = f"{curr_time[0] - self.start_time[0]} Years {curr_time[1] - self.start_time[1]} Months {curr_time[2] - self.start_time[2]} Days {curr_time[3] - self.start_time[3]} Hours {curr_time[4] - self.start_time[4]} Minutes {curr_time[5] - self.start_time[5]} Seconds"
        return uptime

    def delete_user(self, calling_user, removed_user):
        if self.check_if_registered(removed_user):
            if self.database[calling_user]["type"] == "admin":
                del self.database[removed_user]
                self.save_database()
                return "acc", "user_deleted"
            elif calling_user == removed_user and self.username == removed_user:
                del self.database[removed_user]
                self.username = ""
                self.client_signed_in = False
                self.save_database()
                return "acc", "user_deleted"
            return "error", f"User {calling_user} cannot delete other users"
        return "error", f"User {removed_user} is not registered in database"

    def add_to_inbox(self, sender, receiver, message, size):
        position = str(size + 1)
        self.database[receiver]["inbox"].append({
            "sender": sender,
            "message": message
        })
        self.save_database()
        return "acc", "message_delivered"

    def check_inbox(self, user):
        return len(self.database[user]["inbox"])

    def decode_message(self, message):
        sender = message["sender"]
        recv = message["receiver"]
        mess = message["message"]

        if not self.check_if_registered(recv):
            return "error", "Receiver doesn't exist"
        inbox_size = self.check_inbox(recv)
        if inbox_size >= 5:
            return "error", "Receiver inbox full"
        return self.add_to_inbox(sender, recv, mess, inbox_size)

    def read_inbox(self, message):
        inbox = self.database[message]["inbox"]
        if len(inbox) > 0:
            message = {
                "sender": inbox[0]["sender"],
                "message": inbox[0]["message"],
            }
            inbox.pop(0)
            self.save_database()
            return "inbox_message", message
        else:
            return "error", "Inbox is empty"

    def process_query(self, header, message):
        if header == "credentials":
            self.login(message)
        elif header == "type":
            if self.register_new_user(self.username, self.password, message):
                self.client_signed_in = True
                self.send_data("acc", "login")
        elif header == "stop":
            self.socket.close()
            sys.exit()
        elif header == "info":
            info_dict = {
                "Server version": self.SERVER_VERSION,
                "Server start date": f"{self.start_time.tm_year}/{self.start_time.tm_mon}/{self.start_time[2]} {self.start_time.tm_hour}:{self.start_time.tm_min}:{self.start_time.tm_sec}",
                "Server uptime": self.calc_uptime()
            }
            return "server_info", info_dict
        elif header == "delete":
            header, message = self.delete_user(message["calling_user"], message["deleted_user"])
            return header, message
        elif header == "message":
            header, message = self.decode_message(message)
            return header, message
        elif header == "check_inbox":
            message = self.check_inbox(message)
            return "inbox_size", message
        elif header == "read_inbox":
            header, message = self.read_inbox(message)
            return header, message


    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_time = time.gmtime()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen()
        print("Server online")

        self.load_database()

        conn, addr = s.accept()
        with conn:
            self.socket = conn
            print(f"Client connected: {addr}")

            while not self.client_signed_in:
                header, data = self.receive_data()
                self.process_query(header, data)

            while True:
                header, data = self.receive_data()
                ans_header, ans_message = self.process_query(header, data)
                self.send_data(ans_header, ans_message)

                # except IOError as e:
                #     if e.errno == errno.EPIPE:
                #         pass