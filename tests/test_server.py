""" Test suite for Server class"""

import unittest
from server import Server, UserAuthenticator
from config import config


class TestServer(unittest.TestCase):
    """ Test suite for Server class """

    def setUp(self):
        """Setting up for testing Server methods"""
        
        pass

    # def test_server_initialization(self):
    #     """Test proper initialization of the server"""
        
    #     pass

    # def test_server_start(self):
    #     """Test starting the server"""
        
    #     pass

    # def test_message_handling(self):
    #     """Test that different message headers are routed to correct handler methods."""

    #     pass

    # def test_command_handling(self):
    #     """ Test all server commands (help, uptime, info, inbox, stop) return correct responses."""

    #     pass

    # def test_uptime_calc(self):
    #     """Test uptime calculation accuracy and proper formatting of time components."""

    #     pass

    # def test_authentication_flow(self):
    #     """Test complete authentication workflow for both existing and new users."""

    #     pass

    # def test_message_sending_validation(self):
    #     """Test message sending with various scenarios including valid and invalid recipients and empty/full inboxes."""

    #     pass

    # def test_error_message_handling(self):
    #     """Test that invalid message headers and malformed requests generate proper error responses."""

    #     pass


class TestUserAuthenticator(unittest.TestCase):
    """ Test suite for UserAuthenticator class """

    def setUp(self):
        """Setting up for testing UserAuthenticator methods"""

        pass

    # def test_user_registration(self):
    #     """Test user registration process including various account types"""

    #     pass

    # def test_user_login(self):
    #     """Test user login process with valid and invalid credentials."""

    #     pass

    # def test_password_hashing(self):
    #     """Test if password hashing is working correctly"""

    #     pass

    # def test_auth_edge_cases(self):
    #     """Test authentication with empty passwords, very long passwords, and special characters."""

    #     pass



if __name__ == "__main__":
    unittest.main()