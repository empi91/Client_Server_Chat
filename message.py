# message.py
import json
import typing


class Message:
    def __init__(self, text, header=None):
        self.header = header
        self.text = text


    def encode_message(self) -> bytes:
        text_message = {
            "Header": self.header,
            "Message": self.text,
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, json_text) -> tuple[str, str] | str:
        try:
            text_message = json.loads(json_text)
            self.header = text_message["Header"]
            self.text = text_message["Message"]

            return self.header, self.text
        except json.JSONDecodeError:
            return "[Invalid JSON]: " + self.text