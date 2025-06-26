import socket
import sys

from message import Message

HOST = '127.0.0.1'
PORT = 65432

class Client:
    keywords = ['help', 'uptime', 'info', 'stop']

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.name = ""
        self.login = False

    def start_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            print("Welcome on our server. Please sign in or create new account.")

            while not self.login:
                self.user_auth()

            while True:
                print("Let's talk")
                text = input(f"{self.name}>: ")
                header = self.check_msg_header(text)
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



    def check_msg_header(self, text) -> str:
        if text.lower() in self.keywords: 
            header = "Command"
        else: 
            header = "Message"

        return header
    


    def user_auth(self):
        self.name = input("Username: ")
        password = input("Password: ")

        if self.check_if_registered(self.name, password):
            if self.verify_login(self.name, password):
                print("Sign in successfull, welcome back!")
                self.login = True
            else:
                print("Wrong password, try again!")
        else:
            print("New user registered.")
            self.login = True



    def verify_login(self, login, password):
        # Connect to database
        # Check is user with given username has given password assigned to his account
        # Return accordingly

        return True



    def check_if_registered(self, login, password):
        # Connect to database
        # Check if useer with this username exists
        # If YES, continue
        # If NOT, create new user with given username and password

        return True
         


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.start_client()