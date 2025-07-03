# message.py
import json
import typing


class Message:
    def __init__(self, text, header=None, sender=None, receiver=None):
        self.header = header
        self.text = text
        self.sender = sender
        self.receiver = receiver


    def encode_message(self) -> bytes:
        text_message = {
            "Header": self.header,
            "Message": self.text,
            "Sender": self.sender,
            "Receiver": self.receiver,
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, json_text) -> tuple[str, str, str, str] | str:
        try:
            text_message = json.loads(json_text)
            self.header = text_message["Header"]
            self.text = text_message["Message"]
            self.sender = text_message["Sender"]
            self.receiver = text_message["Receiver"]

            # return self.header, self.text
            return self.header, self.text, self.sender, self.receiver
        except json.JSONDecodeError:
            return "[Invalid JSON]: " + self.text