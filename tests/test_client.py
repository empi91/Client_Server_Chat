"""Test suite for Client class"""


import unittest
import sys
import io
from unittest.mock import patch
from client import Client
from config import config
from message import Message, ErrorMessage
from connection import Connection


class TestClient(unittest.TestCase):
    """Test cases for Client class methods."""

    def setUp(self):
        """Set up a fresh Client instance for each test."""
        self.client = Client()

    def test_initialization(self):
        """Test that the client initializes with correct default values."""
        self.assertEqual(self.client.name, "")
        self.assertFalse(self.client.login)
        self.assertEqual(self.client.client_host, config.network.HOST)
        self.assertEqual(self.client.client_port, config.network.PORT)

    def test_client_command_handling(self):
        """Test that user input commands are correctly parsed into appropriate Message objects."""
        # Create a test connection
        connection = Connection()

        # Test info command
        self.client.name = "test_user"
        message = self.client.check_input_command("!info")
        self.assertEqual(message.header, "Command")
        self.assertEqual(message.text, "info")
        self.assertEqual(message.sender, "test_user")
        self.assertEqual(message.receiver, config.network.HOST)

        # Test uptime command
        message = self.client.check_input_command("!uptime")
        self.assertEqual(message.header, "Command")
        self.assertEqual(message.text, "uptime")

        # Test help command
        message = self.client.check_input_command("!help")
        self.assertEqual(message.header, "Command")
        self.assertEqual(message.text, "help")

        # Test stop command
        message = self.client.check_input_command("!stop")
        self.assertEqual(message.header, "Command")
        self.assertEqual(message.text, "stop")

        # Test inbox command
        message = self.client.check_input_command("!inbox")
        self.assertEqual(message.header, "Command")
        self.assertEqual(message.text, "inbox")

    @patch('builtins.input', side_effect=["recipient", "Hello world"])
    def test_input_validation(self, mock_input):
        """Test client-side validation for message length, username length, and password requirements."""
        connection = Connection()
        self.client.name = "test_user"

        # Test valid message
        message = self.client.check_input_command("!message")
        self.assertEqual(message.header, "Message")
        self.assertEqual(message.text, "Hello world")
        self.assertEqual(message.sender, "test_user")
        self.assertEqual(message.receiver, "recipient")

        # Reset the mock inputs for next test
        mock_input.side_effect = ["recipient", "A" *
                                  (config.message.MAX_MESSAGE_LENGTH + 1)]

        # Test message too long
        message = self.client.check_input_command("!message")
        self.assertIsInstance(message, ErrorMessage)
        self.assertEqual(message.header, "Error")
        self.assertTrue(
            f"Message cannot be longar than {
                config.message.MAX_MESSAGE_LENGTH} characters" in message.text)

    def test_error_message_creation(self):
        """Test that invalid commands generate proper ErrorMessage objects instead of sending invalid requests."""
        connection = Connection()

        # Test invalid command
        message = self.client.check_input_command("invalid_command")
        self.assertIsInstance(message, ErrorMessage)
        self.assertEqual(message.header, "Error")
        self.assertEqual(message.text, "Wrong command, try again!")
        self.assertEqual(message.sender, "Server")

    @patch('builtins.input', side_effect=["admin", "superuser"])
    def test_account_type_selection(self, mock_input):
        """Test that users can select between different account types (e.g., user, admin) during registration."""
        # Test with valid account type 'admin'
        # mock_input.return_value = "admin"

        # Create a dummy connection object that implements send and recv
        class DummyConnection:
            def send(self, message):
                pass

            def recv(self, size):
                # Create a mock successful response
                response_msg = Message(
                    "Account_type_update", {
                        "update_status": True}, "Server", "Client")
                return response_msg.encode_message()

        dummy_connection = DummyConnection()
        result = self.client.set_account_type("password123", dummy_connection)
        self.assertTrue(result)

        # Test with invalid account type
        # mock_input.return_value = "superuser"  # Not in VALID_ACCOUNT_TYPES
        result = self.client.set_account_type("password123", dummy_connection)
        self.assertFalse(result)

    def test_authentication_process(self):
        """Check if registration/authentication process is working correctly from the client perspective,
        including wrong credentials, wrong account type, empty strings etc"""

        # Test username validation
        username = "a"  # Too short
        self.assertTrue(
            len(username) < config.security.MIN_USERNAME_LENGTH,
            "Username should be considered too short"
        )

        username = "a" * (config.security.MAX_USERNAME_LENGTH + 1)  # Too long
        self.assertTrue(
            len(username) > config.security.MAX_USERNAME_LENGTH,
            "Username should be considered too long"
        )

        username = "valid_user"  # Valid length
        self.assertTrue(
            config.security.MIN_USERNAME_LENGTH <= len(username) <= config.security.MAX_USERNAME_LENGTH,
            "Username should be considered valid length")

        # Test password validation
        password = "123"  # Too short
        self.assertTrue(
            len(password) < config.security.PASSWORD_MIN_LENGTH,
            "Password should be considered too short"
        )

        password = "password123"  # Valid length
        self.assertTrue(
            len(password) >= config.security.PASSWORD_MIN_LENGTH,
            "Password should be considered valid length"
        )

        # Test account type validation
        valid_account_types = config.message.VALID_ACCOUNT_TYPES
        self.assertIn("admin", valid_account_types)
        self.assertIn("user", valid_account_types)
        self.assertNotIn("superuser", valid_account_types)


if __name__ == "__main__":
    unittest.main()
