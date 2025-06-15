# message.py
import json
import typing


class Message:
    def __init__(self, text):
        self.text = text

    def encode_message(self) -> bytes:
        text_message = {
            "Message": self.text
        }
        json_message = json.dumps(text_message).encode("utf-8")
        print(type(json_message))
        return json_message

    def decode_message(self) -> str:
        try:
            text_message = json.loads(self.text)
            return text_message["Message"]
        except json.JSONDecodeError:
            return "[Invalid JSON]: " + self.text