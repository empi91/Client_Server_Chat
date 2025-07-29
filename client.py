"""Client module for socket-based communication with the server.

This module provides the Client class that handles user authentication,
command processing, and communication with the server.
"""

import sys
import maskpass     # pip install maskpass
from message import Message, ErrorMessage
from connection import Connection


class Client:
    """Client for communicating with the socket server.
    
    Handles user authentication, command processing, and message exchange
    with the server through socket connections.
    """
    
    def __init__(self):
        self.name = ""
        self.login = False


    def start_client(self):
        """Start the client and handle the main communication loop.
        
        Establishes connection to server, handles authentication,
        and processes user commands until disconnection.
        """
        connection = Connection()

        with connection.create_connection() as s:
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


    def check_input_command(self, command: str, connection: Connection) -> Message | ErrorMessage:
        """Process user input commands and create appropriate messages.
        
        Args:
            command: The command string entered by the user.
            connection: The connection object for server details.
            
        Returns:
            A Message object for valid commands or ErrorMessage for invalid ones.
        """
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


    def check_return_msg(self, rec_message: Message):
        """Process and display server responses.
        
        Args:
            rec_message: The message received from the server.
        """
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
                
 
    def user_auth(self, connection: Connection):
        """Handle user authentication process.
        
        Manages login for existing users and registration for new users,
        including account type selection.
        
        Args:
            connection: The connection object for communicating with server.
        """
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
                
                    
                    
                
                
    def set_account_type(self, password: str, connection):
        """Set account type for newly registered users.
        
        Args:
            password: The user's password.
            connection: The connection object for server communication.
            
        Returns:
            True if account type was successfully set, False otherwise.
        """
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