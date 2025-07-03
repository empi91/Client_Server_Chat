# server.py 

import socket
import errno
from message import Message
from datetime import datetime
from connection import Connection
from db import Database

class Server:
    start_time = 0
    SERVER_VERSION = '1.2.0'

    def __init__(self):
        self.start_time = datetime.now()

    def start_server(self):
        connection = Connection()
        with connection.create_server_connection() as s:
            # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((connection.host, connection.port))
            s.listen(5)
            print("Server online")
            
            conn, addr = s.accept()
            with conn:
                print(f"Client connected: {addr}")
                while True:
                    rec_mess = conn.recv(1024).decode("utf-8")
                    if not rec_mess:
                        break
                    message = Message(rec_mess)
                    header, text, sender, receiver = message.decode_message(rec_mess)

                    try:
                        message.header, message.text, message.sender, message.receiver = self.process_message(header, text, sender, receiver, connection)
                        json_answer = message.encode_message()
                        conn.send(json_answer)

                    except IOError as e:
                        if e.errno == errno.EPIPE:
                            pass
    

    def process_message(self, head, text, sender, receiver, connection):
        if head == "Command":
            match text.lower():
                case "help":
                    comm_dict = {
                        "help": "Displays list of all server commands",
                        "uptime": "Returns server lifetime",
                        "info": "Returns server version and start date",
                        "stop": "Stops server and client simultaneously"
                    }
                    return "Command", comm_dict, connection.host, sender

                case "uptime":
                    days, hours, minutes, seconds = self.calc_uptime()
                    uptime_dict = {
                        "Server uptime": f"Server is active for {days} days. {hours} hours, {minutes} minutes and {seconds} seconds"
                    }
                    return "Command", uptime_dict, connection.host, sender

                case "info":
                    info_dict = {
                        "Server version": self.SERVER_VERSION,
                        "Server start date": f"{self.start_time}"
                    }
                    return "Command", info_dict, connection.host, sender
                case "inbox":
                    message_sender, message = self.get_msg_from_inbox(sender)

                    if message == "EMPTY":
                        return "Error", "Inbox empty", connection.host, sender
                    else:
                        inbox = {
                            "Sender": message_sender,
                            "Message": message, 
                        }
                        return "Inbox_message", inbox, connection.host, sender
                case "stop":
                    return "Stop", "Stop", connection.host, sender

        elif head == "Authentication":
            auth_dict = self.authenticate_user(text)
            return "Authentication_answer", auth_dict, connection.host, sender
        elif head == "Acc_type":
            update_status = self.add_account_type(text)
            acc_update_dict = {
                "update_status": update_status,
            }
            return "Account_type_update", acc_update_dict, connection.host, sender

        elif head == "Message":
            if self.check_if_registered(receiver):
                if self.check_recv_inbox(receiver):
                    status = self.add_msg_to_db(receiver, sender, text)
                    return "Status", status, connection.host, sender
                else:
                    status = "Receiver inbox is full"
                    return "Error", status, connection.host, sender
            else:
                status = "Receiver not existing in database"
                return "Error", status, connection.host, sender
        else:
            return "Error", "Invalid message header", connection.host, sender

 
    def authenticate_user(self, text):
        if self.check_if_registered(text["login"]):
            if self.check_if_auth_correct(text["login"], text["password"]):
                answer = {
                "is_registered": True,
                "login_successfull": True,
                }
            else:
                answer = {
                "is_registered": True,
                "login_successfull": False,
                }
        else:
            self.register_new_user(text["login"], text["password"])
            answer = {
                "is_registered": False,
                "login_successfull": True,
            }

        return answer

    
    def check_if_registered(self, login):
        db = Database()
        if db.check_user_in_db(login):
            return True
        return False


    def register_new_user(self, login, password):
        db = Database()
        db.add_user_to_db(login, password)


    def check_if_auth_correct(self, login, password):
        db = Database()
        return db.check_login(login, password)


    def add_account_type(self, text):
        db = Database()
        return db.modify_db(text["login"], "Account type", text["acc_type"])

    
    def add_msg_to_db(self, receiver, sender, message):
        db = Database()
        return db.add_msg_to_db(receiver, sender, message)


    def check_recv_inbox(self, login):
        db = Database()
        inbox_size = db.check_user_inbox(login)
        if inbox_size < 5:
            return True
        return False


    def get_msg_from_inbox(self, login):
        db = Database()
        return db.read_msg_from_inbox(login)


    def calc_uptime(self) -> tuple[int, int, int, int]:
        now_time = datetime.now()
        uptime_delta = now_time - self.start_time
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        seconds = uptime_delta.seconds

        return days, hours, minutes, seconds
