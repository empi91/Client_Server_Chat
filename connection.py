# connection.py
import socket
import json

from query import Query

MAX_MESSAGE_SIZE = 512

class Connection:
    def __init__(self, socket):
        self.socket = socket
        pass

    def encode_message(self, header, text):
        text_message = {
            "Header": header,
            "Message": text,
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, text):
        try:
            text_message = json.loads(text)
            return text_message["Header"], text_message['Message']
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Problematic JSON text:")
            print(e.doc)

    def send_data(self, header, data):
        json_message = self.encode_message(header, data)
        self.socket.send(json_message)
        return 0

    def receive_data(self):
        while True:
            received_data = self.socket.recv(MAX_MESSAGE_SIZE).decode("utf-8")
            if not received_data:
                break
            decoded_header, decoded_message = self.decode_message(received_data)
            return decoded_header, decoded_message


