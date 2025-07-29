# client.py

import sys
import maskpass     # pip install maskpass
from message import Message, ErrorMessage
from connection import Connection


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

                sender_message = self.check_input_command(command, connection)
                if isinstance(sender_message, ErrorMessage):
                    print("[Error] " + sender_message.text)
                    continue

                sender_message_json = sender_message.encode_message()
                s.send(sender_message_json)

                received_bytes = s.recv(1024).decode("utf-8")
                received_message = Message()
                received_message.decode_message(received_bytes)

                self.check_return_msg(received_message)


    def check_input_command(self, command, connection):
        match command.lower():
            case "!message":
                header = "Message"
                sender = self.name
                receiver = input(f"{self.name}>: Please add receiver username: ")
                text = input(f"{self.name}>: Please type your message: ")

                message = Message(header, text, sender, receiver)

                return message
            case "!info":   
                message = Message("Command", "info", self.name, connection.host)       
                return message
            case "!uptime":
                message = Message("Command", "uptime", self.name, connection.host)       
                return message
            case "!help":
                message = Message("Command", "help", self.name, connection.host)       
                return message
            case "!stop":
                message = Message("Command", "stop", self.name, connection.host)       
                return message
            case "!inbox":
                message = Message("Command", "inbox", self.name, connection.host)       
                return message
            case _:
                message = ErrorMessage("Wrong command, try again!", "Server")
                return message


    def check_return_msg(self, rec_message):
        match rec_message.header:
            case "Command":
                for key, value in rec_message.text.items():
                    print(f"{key}: {value}")
                
            case "Status":
                if rec_message.text:
                    print("Operation finished successfully")
                else:
                    print("Operation failed")
                
            case "Stop":
                sys.exit()

            case "Inbox_message":
                print(f"Receiver message from {rec_message.text['Sender']}: \n{rec_message.text['Message']}")

            case "Error":
                print(f"[ERROR] {rec_message.text}")

            case _:
                print("Empty server answer")
                
 
    def user_auth(self, connection):
        print("Welcome on our server. Please sign in or create new account.")

        while True:
            self.name = input("Username: ")
            password = maskpass.askpass("Password: ") 
            # password = input("Password: ")
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
            message = Message("Authentication", text, "Authenticator", "Server")
            json_message = message.encode_message()

            connection.send(json_message)

            auth_answer = connection.recv(1024).decode("utf-8")
            auth_message = Message()
            auth_message.decode_message(auth_answer)

            if auth_message.text["is_registered"]:
                if auth_message.text["login_successfull"]:
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

        message = Message("Acc_type", text, "Client", "Server")
        json_message  = message.encode_message()
        connection.send(json_message)
        
        acc_type_answer = connection.recv(1024).decode("utf-8")
        decoded_message = Message()
        decoded_message.decode_message(acc_type_answer)

        if decoded_message.text["update_status"]:
            print("Account type updated successfully")
            return True
        else:
            print("Account type update failed")
            return False
        



if __name__ == "__main__":
    client = Client()
    client.start_client()