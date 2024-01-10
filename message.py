# message.py
import json


class Message:
    def __init__(self, text):
        self.text = text


    def encode_message(self):
        json_message = json.dumps(self.text)
        print(json_message)

    def decode_message(self):
        text_message = json.loads(self.text)
        print(text_message)
