import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

from user import User

class TestUser(unittest.TestCase):
    #setUp()
    def setUp(self):
        self.user = User()
        self.user_data = {
            "username": "test_user",
            "password": "test_password",
            "acc_type": "user",
        }

    # Testing check_if_registered() method
    @patch("user.Database")
    def test_checking_if_registered_user_is_registered(self, mock_database):
        """
        Test if registered user is recognised correctly
        """
        mock_database.return_value.database = {
            "Filip": {},
            "Jan": {}
        }
        self.assertTrue(self.user.check_if_registered("Filip"))

    @patch("user.Database")
    def test_checking_if_not_registered_user_is_registered(self, mock_database):
        """
        Test if non-registered user is recognised correctly
        """
        mock_database.return_value.database = {
            "Filip": {},
            "Jan": {}
        }
        self.assertFalse(self.user.check_if_registered("Agata"))

    # Testing check_password()
    @patch("user.Database")
    def test_checking_correct_password(self, mock_database):
        """
        Test if the right password is recognised correctly
        """
        mock_database.return_value.database = {
            "user": {"password": "password123"}
        }
        self.assertTrue(self.user.check_password("user", "password123"))

    @patch("user.Database")
    def test_checking_wrong_password(self, mock_database):
        """
        Test if the wrong password recognised correctly
        """
        mock_database.return_value.database = {
            "user": {"password": "password12345"}
        }
        self.assertFalse(self.user.check_password("user", "password123"))

    # Testing register_user() method

    @patch("user.Database")
    def test_registering_new_user_without_providing_user_data(self, mock_database):
        """
        Test if registering user without providing required data throws expected error
        """
        with (self.assertRaises(TypeError)):
            self.user.register_user()

    # Testing login_user() method
    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["Filip", "password"])
    def test_sending_user_login_data(self, mock_input, mock_socket, mock_connection):
        mock_connection.return_value.receive_data.side_effect = [("ack", "")]
        self.user.login_user(mock_socket)
        mock_connection.send_data_assert_called_once_with("login", {"username": "Filip", "password": "password"})

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["Filip", "password"])
    def test_processing_ack_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("ack", "")]

        self.assertEqual(self.user.login_user(mock_socket), 0)
        self.assertIsNone(self.user.type)
        self.assertTrue(self.user.user_login)

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["Filip", "password", "admin"])
    def test_processing_add_account_type_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("add_account_type", "")]

        self.user.login_user(mock_socket)

        self.assertEqual(self.user.login_user(mock_socket), 0)
        self.assertIsNotNone(self.user.type)
        self.assertTrue(self.user.user_login)
        mock_connection_instance.send_data.assert_called_with("account_type", {"username": "Filip", "password": "password", "acc_type": "admin"})

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["Filip", "password", "Filip", "password"])
    def test_processing_error_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("error", ""), ("ack", "")]

        self.assertEqual(self.user.login_user(mock_socket), 0)
        self.assertEqual(mock_connection_instance.receive_data.call_count, 2)


    # Testing delete_user() method
    @patch("user.Database")
    def test_removing_registered_user(self, mock_database):
        mock_database.return_value.database = {
            "calling_user": {
                "username": "",
                "password": "password12345",
                "acc_type": "admin"
            },
            "removed_user": {
                "username": "",
                "password": "password12345",
                "acc_type": "user"
            }
        }
        self.assertEqual(self.user.delete_user("calling_user", "removed_user"), ("ack", "user_deleted"))

    @patch("user.Database")
    def test_removing_not_registered_user(self, mock_database):
        mock_database.return_value.database = {
            "calling_user": {
                "username": "",
                "password": "password12345",
                "acc_type": "admin"
            }
        }
        self.assertEqual(self.user.delete_user("calling_user", "test_user"), ("error", "User test_user is not registered in database"))

    @patch("user.Database")
    def test_removing__user_by_not_admin(self, mock_database):
        mock_database.return_value.database = {
            "calling_user": {
                "username": "",
                "password": "password12345",
                "acc_type": "user"
            },
            "removed_user": {
                "username": "",
                "password": "password12345",
                "acc_type": "user"
            }
        }
        self.assertEqual(self.user.delete_user("calling_user", "removed_user"), ("error", "User calling_user cannot delete other users"))


if __name__ == '__main__':
    unittest.main()