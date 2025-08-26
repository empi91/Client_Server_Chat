"""Test suite for Message and ErrorMessage classes."""

import unittest
import json
import os
import sys

# Add parent directory to path to import message module
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from message import Message, ErrorMessage
from config import config


class TestMessage(unittest.TestCase):
    """Test cases for the Message class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Load sample data from fixtures
        fixtures_path = config.tests.FIXTURES_PATH
        sample_message = os.path.join(fixtures_path, 'sample_messages.json')
        with open(sample_message, 'r') as f:
            self.sample_data = json.load(f)
    
    def test_message_encoding_and_decoding(self):
        """Test basic message encoding and decoding functionality."""
        # Create a message with all fields
        original_message = Message(
            header="Message",
            text="Hello, how are you?",
            sender="TestUser1",
            receiver="TestUser2"
        )
        
        # Encode the message
        encoded_bytes = original_message.encode_message()
        
        # Verify it's valid JSON bytes
        self.assertIsInstance(encoded_bytes, bytes)
        decoded_json = json.loads(encoded_bytes.decode('utf-8'))
        
        # Verify JSON structure
        expected_keys = {"Header", "Message", "Sender", "Receiver"}
        self.assertEqual(set(decoded_json.keys()), expected_keys)
        
        # Create new message and decode
        new_message = Message()
        result = new_message.decode_message(encoded_bytes.decode('utf-8'))
        
        # Verify decoding success
        self.assertTrue(result)
        
        # Verify all attributes match
        self.assertEqual(new_message.header, "Message")
        self.assertEqual(new_message.text, "Hello, how are you?")
        self.assertEqual(new_message.sender, "TestUser1")
        self.assertEqual(new_message.receiver, "TestUser2")
    
    def test_error_message_creation(self):
        """Test ErrorMessage class specialized behavior."""
        error_msg = ErrorMessage("User not found", "server")
        
        # Verify ErrorMessage attributes
        self.assertEqual(error_msg.header, "Error")
        self.assertEqual(error_msg.text, "User not found")
        self.assertEqual(error_msg.sender, "server")
        self.assertIsNone(error_msg.receiver)
        
        # Test encoding
        encoded_bytes = error_msg.encode_message()
        decoded_json = json.loads(encoded_bytes.decode('utf-8'))
        
        # Verify error message structure
        self.assertEqual(decoded_json["Header"], "Error")
        self.assertEqual(decoded_json["Message"], "User not found")
        self.assertEqual(decoded_json["Sender"], "server")
        self.assertIsNone(decoded_json["Receiver"])
    
    def test_json_decode_error_handling(self):
        """Test message decoding with invalid JSON input."""
        message = Message()
        
        # Test with invalid JSON
        invalid_json = self.sample_data["invalid_json"]
        result = message.decode_message(invalid_json)
        
        # Verify decode failure
        self.assertFalse(result)
        
        # Test with completely malformed input
        result = message.decode_message("not json at all")
        self.assertFalse(result)
        
        # Test with valid JSON but missing required fields
        incomplete_json = json.dumps({"Header": "test"})
        with self.assertRaises(KeyError):
            message.decode_message(incomplete_json)


if __name__ == '__main__':
    unittest.main()

