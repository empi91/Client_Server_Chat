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
        self.user.database.create_database("test_db")
        self.user.database.load_config("test_db")
        self.user.database.create_tables()
        self.user.database.execute_query(self.user.database.QUERY_DICT["REGISTER_USER"], ("test_user_1", "test_password_1", "admin"))
        self.user.database.execute_query(self.user.database.QUERY_DICT["REGISTER_USER"], ("test_user_2", "test_password_2", "user"))

    def tearDown(self):
        self.user.database.load_config("postgresql")
        self.user.database.drop_database("test_db")


    # Testing check_if_registered() method
    def test_checking_if_registered_user_is_registered(self):
        """
        Test if registered user is recognised correctly
        """
        self.assertTrue(self.user.check_if_registered("test_user_1"))

    def test_checking_if_not_registered_user_is_registered(self):
        """
        Test if non-registered user is recognised correctly
        """
        self.assertFalse(self.user.check_if_registered("test_user_3"))

    # Testing check_password()
    def test_checking_correct_password(self):
        """
        Test if the right password is recognised correctly
        """
        self.assertTrue(self.user.check_password("test_user_1", "test_password_1"))

    def test_checking_wrong_password(self):
        """
        Test if the wrong password recognised correctly
        """
        self.assertFalse(self.user.check_password("test_user_2", "password123"))

    # Testing register_user() method
    def test_registering_new_user_without_providing_user_data(self):
        """
        Test if registering user without providing required data throws expected error
        """
        with (self.assertRaises(TypeError)):
            self.user.register_user()

    # Testing login_user() method
    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["test_user_1", "test_password_1"])
    def test_sending_user_login_data(self, mock_input, mock_socket, mock_connection):
        mock_connection.return_value.receive_data.side_effect = [("ack", "")]
        self.user.login_user(mock_socket)
        mock_connection.send_data_assert_called_once_with("login", {"username": "test_user_1", "password": "test_password_1"})

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["test_user_1", "test_password_1"])
    def test_processing_ack_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("ack", "")]

        self.assertTrue(self.user.login_user(mock_socket))
        self.assertIsNone(self.user.type)
        self.assertTrue(self.user.is_user_login)

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["test_user_3", "test_password_3", "user"])
    def test_processing_add_account_type_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("add_account_type", "")]

        self.user.login_user(mock_socket)

        self.assertEqual(self.user.login_user(mock_socket), 0)
        self.assertIsNotNone(self.user.type)
        self.assertTrue(self.user.is_user_login)
        mock_connection_instance.send_data.assert_called_with("account_type", {"username": "test_user_3", "password": "test_password_3", "acc_type": "user"})

    @patch("user.Connection")
    @patch("socket.socket")
    @patch("builtins.input", side_effect=["test_user_1", "test_password_1", "test_user_1", "test_password_1"])
    def test_processing_error_login_answers(self, mock_input, mock_socket, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.receive_data.side_effect = [("error", ""), ("ack", "")]

        self.assertTrue(self.user.login_user(mock_socket))
        self.assertEqual(mock_connection_instance.receive_data.call_count, 2)


    # Testing delete_user() method
    def test_removing_registered_user(self):
        self.assertEqual(self.user.delete_user("test_user_1", "test_user_2"), ("ack", "user_deleted"))

    def test_removing_not_registered_user(self):
        self.assertEqual(self.user.delete_user("test_user_1", "test_user_3"), ("error", "User test_user_3 is not registered in database"))

    def test_removing__user_by_not_admin(self):
        self.assertEqual(self.user.delete_user("test_user_2", "test_user_1"), ("error", "User test_user_2 cannot delete other users"))


if __name__ == '__main__':
    unittest.main()