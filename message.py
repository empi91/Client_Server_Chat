# message.py
import json


class Message:
    def __init__(self, text):
        self.text = text

    def encode_message(self, text):
        text_len = len(text)
        text_message = {
            "Message": text
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, text):
        text_message = json.loads(text)
        return text_message["Message"]