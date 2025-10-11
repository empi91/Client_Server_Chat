"""Message handling module for client-server communication.

This module provides Message and ErrorMessage classes for encoding,
decoding, and managing messages exchanged between client and server.
"""

import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects.

    Converts datetime objects to ISO format strings during JSON serialization.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Message:
    """Represents a message for client-server communication.

    Handles encoding and decoding of messages to/from JSON format
    for transmission over socket connections.
    """

    def __init__(self, header=None, text=None, sender=None, receiver=None):
        """Initialize a message with optional parameters.

        Args:
            header: The message type/category.
            text: The message content.
            sender: The ID/username of the message sender.
            receiver: The ID/username of the message recipient.
        """
        self.header = header
        self.text = text
        self.sender = sender
        self.receiver = receiver

    def encode_message(self) -> bytes:
        """Encode the message to JSON bytes for transmission.

        Returns:
            UTF-8 encoded JSON bytes representing the message.
        """
        text_message = {
            "Header": self.header,
            "Message": self.text,
            "Sender": self.sender,
            "Receiver": self.receiver,
        }
        json_message = json.dumps(
            text_message, cls=DateTimeEncoder).encode("utf-8")
        return json_message

    def decode_message(self, json_text) -> bool:
        """Decode a JSON message and populate message attributes.

        Args:
            json_text: JSON string to decode into message components.

        Returns:
            1 for successful decoding, or error tuple for JSON decode errors.
        """
        try:
            text_message = json.loads(json_text)
            self.header = text_message["Header"]
            self.text = text_message["Message"]
            self.sender = text_message["Sender"]
            self.receiver = text_message["Receiver"]

            return True
        except json.JSONDecodeError:
            print("[JSON ERROR]: Invalid JSON format.")
            return False


class ErrorMessage(Message):
    """Specialized message class for error messages.

    Inherits from Message but specifically designed for error scenarios
    with predefined header and no receiver.
    """

    def __init__(self, text: str, sender: str):
        super().__init__(header="Error", text=text, sender=sender, receiver=None)

    def encode_message(self) -> bytes:
        return super().encode_message()

    def decode_message(self, json_text) -> tuple[str, str, str, str]:
        return super().decode_message(json_text)
