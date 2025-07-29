# server.py 

import socket
import errno
from argon2 import PasswordHasher       # pip install argon2-cffi
from argon2.exceptions import VerifyMismatchError
from message import Message
from datetime import datetime
from connection import Connection
from db import Database, DbHelper

class Server:
    start_time = 0
    SERVER_VERSION = '1.2.0'

    def __init__(self):
        self.start_time = datetime.now()
        self.db_helper = DbHelper()

    def start_server(self):
        connection = Connection()
        with connection.create_server_connection() as s:
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
                    recv_message = Message()
                    recv_message.decode_message(rec_mess)

                    try:
                        sending_msg = self.process_message(recv_message, connection)
                        json_answer = sending_msg.encode_message()
                        conn.send(json_answer)

                    except IOError as e:
                        if e.errno == errno.EPIPE:
                            pass
    

    def process_message(self, message, connection):
        if message.header == "Command":
            match message.text.lower():
                case "help":
                    comm_dict = {
                        "!help": "Displays list of all server commands",
                        "!uptime": "Returns server lifetime",
                        "!info": "Returns server version and start date",
                        "!inbox":"Gets first unread message from your inbox",
                        "!message": "Sends message to other user",
                        "stop": "Stops server and client simultaneously"
                    }

                    message = Message("Command", comm_dict, connection.host, message.sender)
                    return message

                case "uptime":
                    days, hours, minutes, seconds = self.calc_uptime()
                    uptime_dict = {
                        "Server uptime": f"Server is active for {days} days. {hours} hours, {minutes} minutes and {seconds} seconds"
                    }
                    message = Message("Command", uptime_dict, connection.host, message.sender)
                    return message

                case "info":
                    info_dict = {
                        "Server version": self.SERVER_VERSION,
                        "Server start date": f"{self.start_time}"
                    }

                    message = Message("Command", info_dict, connection.host, message.sender)
                    return message

                case "inbox":
                    message_sender, message_text = self.db_helper.get_msg_from_inbox(message.sender)

                    if message_text == "EMPTY":
                        message = Message("Error", "Inbox empty", connection.host, message.sender)
                        return message
                    else:
                        inbox = {
                            "Sender": message_sender,
                            "Message": message_text, 
                        }
                        message = Message("Inbox_message", inbox, connection.host, message.sender)
                        return message

                case "stop":
                    message = Message("Stop", "Stop", connection.host, message.sender)
                    return message

        elif message.header == "Authentication":
            authenticator = UserAuthenticator(message.text)
            auth_dict = authenticator.verify_login()

            message = Message("Authentication_answer", auth_dict, connection.host, message.sender)
            return message
        elif message.header == "Acc_type":
            update_status = self.db_helper.add_account_type(message.text)
            acc_update_dict = {
                "update_status": update_status,
            }

            message = Message("Account_type_update", acc_update_dict, connection.host, message.sender)
            return message

        elif message.header == "Message":
            if self.db_helper.check_if_registered(message.receiver):
                if self.db_helper.check_recv_inbox(message.receiver):
                    status = self.db_helper.add_msg_to_db(message.receiver, message.sender, message.text)

                    message = Message("Status", status, connection.host, message.sender)
                    return message
                else:
                    status = "Receiver inbox is full"

                    message = Message("Error", status, connection.host, message.sender)
                    return message
            else:
                status = "Receiver not existing in database"

                message = Message("Error", status, connection.host, message.sender)
                return message
        else:
            message = Message("Error", "Invalid message header", connection.host, message.sender)
            return message
   

    def calc_uptime(self) -> tuple[int, int, int, int]:
        now_time = datetime.now()
        uptime_delta = now_time - self.start_time
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        seconds = uptime_delta.seconds

        return days, hours, minutes, seconds
        
        

class UserAuthenticator():
    def __init__(self, message):
        self.text = message
        self.db_helper = DbHelper()
        
    
    def verify_login(self):
        if self.db_helper.check_if_registered(self.text["login"]):
            stored_password = self.db_helper.get_stored_password(self.text["login"])
            if self.verify_password(self.text["password"], stored_password):
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
            hashed_password = self.hash_password(self.text["password"])
            self.db_helper.register_new_user(self.text["login"], hashed_password)
            answer = {
                "is_registered": False,
                "login_successfull": True,
            }

        return answer
    
        
    def verify_password(self, input_pass, stored_pass):
        ph = PasswordHasher()
        try:
           ph.verify(stored_pass, input_pass)
           return True
        except VerifyMismatchError:
           return False
        # if stored_pass == input_pass:
        #     return True
        # return False
    
    
    def hash_password(self, password):
        ph = PasswordHasher()        ## removing argon2 for iPad
        return ph.hash(password)     ## removing argon2 for iPad
        # return password
        
        
        
        
    