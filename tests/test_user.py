import unittest
import user

from unittest.mock import patch

from user import User


class TestUser(unittest.TestCase):

    #setUp()
    def setUp(self):
        self.user = User()

    # Testing check_if_registered() method
    @patch("user.Database")
    def test_check_if_registered_user_is_registered(self, mock_database):
        mock_database.return_value.database = {
            "Filip": {},
            "Jan": {}
        }
        self.assertTrue(self.user.check_if_registered("Filip"))

    @patch("user.Database")
    def test_check_if_not_registered_user_is_registered(self, mock_database):
        mock_database.return_value.database = {
            "Filip": {},
            "Jan": {}
        }
        self.assertFalse(self.user.check_if_registered("Agata"))

    # Testing check_password()
    @patch("user.Database")
    def test_check_correct_password(self, mock_database):
        mock_database.return_value.database = {
            "user": {"password": "password123"}
        }
        self.assertTrue(self.user.check_password("user", "password123"))

    @patch("user.Database")
    def test_check_wrong_password(self, mock_database):
        mock_database.return_value.database = {
            "user": {"password": "password12345"}
        }
        self.assertFalse(self.user.check_password("user", "password123"))

    # Testing register_user() method

    # Testing login_user() method

    # Testing delete_user() method
