"""Message handling module for client-server communication.

This module provides Message and ErrorMessage classes for encoding,
decoding, and managing messages exchanged between client and server.
"""

import json
import typing


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
            sender: The username of the message sender.
            receiver: The username of the message recipient.
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
        json_message = json.dumps(text_message).encode("utf-8")
        return json_message

    def decode_message(self, json_text) -> tuple[str, str, str, str] | str:
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

            # return self.header, self.text, self.sender, self.receiver
            return 1            # Unify return tyopes with error below
        except json.JSONDecodeError:
            return "Error", "[Invalid JSON]: " + self.text, None, None


class ErrorMessage(Message):
    """Specialized message class for error messages.
    
    Inherits from Message but specifically designed for error scenarios
    with predefined header and no receiver.
    """
    
    def __init__(self, text: str, sender: str):
        """Initialize an error message.
        
        Args:
            text: The error message content.
            sender: The sender of the error message.
        """
        super().__init__(header="Error", text=text, sender=sender, receiver=None)

    def encode_message(self) -> bytes:
        """Encode the error message to JSON bytes.
        
        Returns:
            UTF-8 encoded JSON bytes representing the error message.
        """
        return super().encode_message()

    def decode_message(self, json_text) -> tuple[str, str, str, str]:
        """Decode a JSON error message.
        
        Args:
            json_text: JSON string to decode.
            
        Returns:
            Tuple containing decoded message components.
        """
        return super().decode_message(json_text)