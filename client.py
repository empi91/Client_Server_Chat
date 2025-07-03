# client.py

import sys

from message import Message
from connection import Connection
from db import Database


class Client:
    def __init__(self):
        self.name = ""
        self.login = False


    def start_client(self):
        connection = Connection()

        with connection.create_server_connection() as s:
            s.connect((connection.host, connection.port))
            
            while not self.login:
                self.user_auth(s)

            print("Choose what you want to do: \nSend a message: Type !message \nAccess server information: Type !info \nCheck uptime: Type !uptime \nStop server: Type !stop \nNeed help? Type !help")

            while True:
                command = input(f"{self.name}>: ")

                header, text = self.check_command(command)
                if not header:
                    continue

                message = Message(text, header)
                json_message = message.encode_message()
                s.send(json_message)

                mess_received = s.recv(1024).decode("utf-8")
                decoded_header, decoded_answer = message.decode_message(mess_received)
                if decoded_header == "Command":
                    if decoded_answer == "Stop":
                        sys.exit()
                    else:
                        for key, value in decoded_answer.items():
                            print(f"{key}: {value}")


    def check_command(self, command):
        match command:
            case "!message":
                header = "Message"
                

                return header
            case "!info":
                header = "Command" 
            
                return header, "info"
            case "!uptime":
                header = "Command"
                
                return header, "uptime"
            case "!help":
                header = "Command"
                
                return header, "help"
            case "!stop":
                header = "Command"
                
                return header, "stop"
            case _:
                print("Wrong command, try again")
                return None, None

    def create_msg(self):



        pass

 
    def user_auth(self, connection):
        print("Welcome on our server. Please sign in or create new account.")

        while True:
            self.name = input("Username: ")
            password = input("Password: ")

            text = {
                "login": self.name,
                "password": password,
            }
            message = Message(text, "Authentication")
            json_message = message.encode_message()

            connection.send(json_message)

            auth_answer = connection.recv(1024).decode("utf-8")
            decoded_header, decoded_answer = message.decode_message(auth_answer)

            if decoded_answer["is_registered"]:
                if decoded_answer["login_successfull"]:
                    print("Sign in successfull, welcome back!")
                    self.login = True
                    return
                else:
                    print("Wrong password, try again!")
            else:
                acc_type = input("New user registered, please add account type: admin/user: ")

                text = {
                "login": self.name,
                "password": password,
                "acc_type": acc_type,
                }

                message = Message(text, "Acc_type")
                json_message  = message.encode_message()
                connection.send(json_message)

                acc_type_answer = connection.recv(1024).decode("utf-8")
                decoded_header, decoded_answer = message.decode_message(acc_type_answer)

                if decoded_answer["update_status"]:
                    print("Account type updated successfully")
                else:
                    print("Account type update failed")

                self.login = True
                return



if __name__ == "__main__":
    client = Client()
    client.start_client()