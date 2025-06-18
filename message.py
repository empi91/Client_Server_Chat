# message.py
import json
import typing


class Message:
    keywords = ['help', 'uptime', 'info']

    def __init__(self, type, text, author=None):
        if type:
            self.type = 'Request'
        else:
            self.type = 'Answer'

        if text in self.keywords:
            self.header = 'Command'
        elif text == "stop" or text == "Stop":
            self.header = "Stop"
        else:
            self.header = "Message"

        self.text = text
        if author:
            self.author = author
        else:
            self.author = ''

    def encode_message(self) -> bytes:
        text_message = {
            "Type": self.type,
            "Header": self.header,
            "Message": self.text,
            "Author": self.author
        }
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, json_text) -> str:
        try:
            text_message = json.loads(json_text)
            self.type = text_message["Type"]
            self.header = text_message["Header"]
            self.text = text_message["Message"]
            self.author = text_message["Author"]

            return self.header, self.text, self.author
        except json.JSONDecodeError:
            return "[Invalid JSON]: " + self.text