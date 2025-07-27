# client.py

import sys
#import maskpass
from message import Message
from connection import Connection
#from collections import namedtuple


class Client:
    def __init__(self):
        self.name = ""
        self.login = False


    def start_client(self):
        connection = Connection()

        with connection.create_client_connection() as s:
            s.connect((connection.host, connection.port))
            
            while not self.login:
                self.user_auth(s)

            print("Choose what you want to do: \nSend a message: Type !message \nCheck your inbox: Type !inbox\nAccess server information: Type !info \nCheck uptime: Type !uptime \nStop server: Type !stop \nNeed help? Type !help")

            while True:
                command = input(f"{self.name}>: ")

                #header, text, sender, receiver = self.check_input_command(command, connection)
                header, text, sender, receiver = self.check_input_command(command, connection)
                if not header:
                    continue

                message = Message(text, header, sender, receiver)
                json_message = message.encode_message()
                s.send(json_message)

                mess_received = s.recv(1024).decode("utf-8")
                decoded_header, decoded_answer, decoded_sender, decoded_receiver = message.decode_message(mess_received)

                self.check_return_msg(decoded_header, decoded_answer, decoded_sender, decoded_receiver)


    def check_input_command(self, command, connection):   
        match command.lower():
            case "!message":
                header = "Message"
                sender = self.name
                receiver = input(f"{self.name}>: Please add receiver username: ")
                text = input(f"{self.name}>: Please type your message: ")

                return header, text, sender, receiver
            case "!info":          
                return "Command", "info", self.name, connection.host
            case "!uptime":
                return "Command", "uptime", self.name, connection.host
            case "!help":
                return "Command", "help", self.name, connection.host
            case "!stop":
                return "Command", "stop", self.name, connection.host
            case "!inbox":
                return "Command", "inbox", self.name, connection.host
            case _:
                print("Wrong command, try again")
                return None, None, None, None


    def check_return_msg(self, header, message, sender, receiver):
        match header:
            case "Command":
                for key, value in message.items():
                    print(f"{key}: {value}")
                
            case "Status":
                if message:
                    print("Operation finished successfully")
                else:
                    print("Operation failed")
                
            case "Stop":
                sys.exit()

            case "Inbox_message":
                print(f"Receiver message from {message['Sender']}: \n{message['Message']}")

            case "Error":
                print(f"[ERROR] {message}")

            case _:
                print("Empty server answer")
                
 
    def user_auth(self, connection):
        print("Welcome on our server. Please sign in or create new account.")

        while True:
            self.name = input("Username: ")
            #password = maskpass.askpass("Password: ") 
            password = input("Password: ")
            if not self.name or not isinstance(self.name, str):
                print("Empty login, try again.")
                continue
            if not password or not isinstance(password, str):
                print("Empty password, try again.")
                continue

            text = {
                "login": self.name,
                "password": password,
            }
            message = Message(text, "Authentication")
            json_message = message.encode_message()

            connection.send(json_message)

            auth_answer = connection.recv(1024).decode("utf-8")
            decoded_header, decoded_answer, decoded_sender, decoder_receiver = message.decode_message(auth_answer)

            if decoded_answer["is_registered"]:
                if decoded_answer["login_successfull"]:
                    print("Sign in successfull, welcome back!")
                    self.login = True
                    return
                else:
                    print("Wrong password, try again!")
            else:
                while True:
                    if self.set_account_type(password, connection):
                        self.login = True
                        return
                
                    
                    
                
                
    def set_account_type(self, password, connection):
        acc_type = input("New user registered, please add account type: admin/user: ")
        if acc_type not in ['admin', 'user']:
            print("[ERROR] Wrong account type")
            return False
            
        text = {
            "login": self.name,
            "password": password,
            "acc_type": acc_type,
            }

        message = Message(text, "Acc_type")
        json_message  = message.encode_message()
        connection.send(json_message)
        
        acc_type_answer = connection.recv(1024).decode("utf-8")
        decoded_header, decoded_answer, decoded_sender, decoded_receiver = message.decode_message(acc_type_answer)

        if decoded_answer["update_status"]:
            print("Account type updated successfully")
            return True
        else:
            print("Account type update failed")
            return False
        



if __name__ == "__main__":
    client = Client()
    client.start_client()