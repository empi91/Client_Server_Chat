"""Test suite for Client class"""


import unittest
from client import Client
from config import config


class TestClient(unittest.TestCase):
    """Test cases for Client class methods."""

    def setUp(self):
        self.client = Client()

    def test_initialization(self):
        """Test that the client initializes with correct default values."""
        
        pass

    # def test_client_command_handling(self):
    #     """Test that user input commands are correctly parsed into appropriate Message objects."""
       
       
    #     pass

    # def test_input_validation(self):
    #     """ Test client-side validation for message length, username length, and password requirements."""
        
        
    #     pass


    # def test_error_message_creation(self):
    #     """Test that invalid commands generate proper ErrorMessage objects instead of sending invalid requests."""

    #     pass


    # def test_account_type_selection(self):
    #     """Test that users can select between different account types (e.g., user, admin) during registration."""
        
    #     pass


    # def test_client_response_handling(self):
    #     """Test that different server response types are properly displayed to the user."""

    #     pass

    
    # def test_authentication_process(self):
    #     """Check if registration/authentication process is working correctly from the client perspective, including wrong credentials, wrong account type, empty strings etc"""


    #     pass


if __name__ == "__main__":
    unittest.main()