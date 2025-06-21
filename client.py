import socket
import sys

from message import Message

HOST = '127.0.0.1'
PORT = 65432

class Client:
    keywords = ['help', 'uptime', 'info', 'stop']

    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

    def start_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            while True:
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
         

if __name__ == "__main__":
    client_name = input("Enter client name: ")
    client = Client(HOST, PORT, client_name)
    client.start_client()