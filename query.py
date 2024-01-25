# query.py
import sys
import time

from user import User
from database import Database

MAX_INBOX_SIZE = 5

class Query:

    def __init__(self):
        self.user = User()
        self.start_time = time.gmtime()
        self.server_version = 0
        pass

    def process_query(self, header, message):
        if header == "login":               # server
            username = message["username"]
            password = message["password"]

            if self.user.check_if_registered(username):
                if self.user.check_password(username, password):
                    return "ack", "User login successfully"
                else:
                    return "error", "Wrong password, try again"
            else:
                return "add_account_type", "Enter account type: "

        elif header == "account_type":      #server
            return self.user.register_user(message)

        elif header == "delete":            # server
            return self.user.delete_user(message["calling_user"], message["deleted_user"])

        elif header == "check_inbox":       # server
            return self.check_inbox(message)

        elif header == "read_message":      # server
            return self.read_inbox(message)

        elif header == "send_message":      # server
            return self.send_message(message)

        elif header == "check_info":        # server
            info_dict = {
                "Server version": self.server_version,
                "Server start date": f"{self.start_time.tm_year}/{self.start_time.tm_mon}/{self.start_time[2]} {self.start_time.tm_hour}:{self.start_time.tm_min}:{self.start_time.tm_sec}",
                "Server uptime": self.calc_uptime()
            }
            return "info", info_dict

        elif header == "stop":              # server
            sys.exit()

        elif header == "ack":               # client
            print(message)

        elif header == "error":             # client
            print(f"Error: {message}")

        elif header == "inbox":             # client
            print(f"You have {message} unread messages")
            if message > 0:
                print(f"To read first one type !read")
        elif header == "message":           # client
            print(f"Message from {message['sender']}:\n"
                  f"{message['message']}")
        elif header == "info":              # client
            print(f"Server version: {message['Server version']}\n"
                  f"Server start date: {message['Server start date']}\n"
                  f"Server uptime: {message['Server uptime']}")

    def check_inbox(self, message):
        database = Database()
        return "inbox", len(database.database[message]["inbox"])

    def read_inbox(self, message):
        database = Database()
        inbox = database.database[message]["inbox"]
        if len(inbox) > 0:
            message = {
                "sender": inbox[0]["sender"],
                "message": inbox[0]["message"],
            }
            inbox.pop(0)
            database.save_database()
            return "message", message
        else:
            return "error", "Inbox is empty"

    def send_message(self, message):
        sender = message["sender"]
        recv = message["receiver"]
        mess = message["message"]

        if not self.user.check_if_registered(recv):
            return "error", "Receiver doesn't exist"
        inbox_size = self.check_inbox(recv)[1]
        if inbox_size >= MAX_INBOX_SIZE:
            return "error", "Receiver inbox full"
        return self.add_to_inbox(sender, recv, mess)

    def add_to_inbox(self, sender, receiver, message):
        database = Database()
        database.database[receiver]["inbox"].append({
            "sender": sender,
            "message": message
        })
        database.save_database()
        return "acc", "message_delivered"

    def calc_uptime(self):
        curr_time = time.gmtime()
        uptime = f"{curr_time[0] - self.start_time[0]} Years {curr_time[1] - self.start_time[1]} Months {curr_time[2] - self.start_time[2]} Days {curr_time[3] - self.start_time[3]} Hours {curr_time[4] - self.start_time[4]} Minutes {curr_time[5] - self.start_time[5]} Seconds"
        return uptime



