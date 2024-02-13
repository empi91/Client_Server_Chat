import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

from query import Query

class TestQuery(unittest.TestCase):
    #setUp()
    def setUp(self):
        self.query = Query()

    # Test check_inbox() method
    @patch("query.Database")
    def test_checking_number_of_messages_in_user_inbox(self, mock_database):
        """
        Testing if check_inbox() methods returns correct number of messages in user's inbox
        :param mock_database:
        :return:
        """
        mock_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                    "inbox": [
                      {
                        "sender": "test_user_2",
                        "message": "Hello"
                      },
                      {
                        "sender": "test_user_3",
                        "message": "Hi"
                      }
                    ]
            }
        }
        self.assertEqual(self.query.check_inbox("test_user"), ("inbox", 2))

    # Test read_inbox() method
    @patch("database.Database")
    def test_reading_message_from_inbox(self, mock_database):
        """
        Test if reading message from inbox works as expected
        :param mock_database:
        :return:
        """
        mock_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [
                    {
                        "sender": "test_user_2",
                        "message": "Hello"
                    }
                ]
            }
        }
        self.assertEqual(self.query.read_inbox("test_user"), ("message", {"message": "Hello", "sender": "test_user_2"}))
    @patch("query.Database")
    def test_removing_read_message_from_inbox(self, mock_database):
        """
        Testing if unread message is removed from inbox after read
        :param mock_database:
        :return:
        """
        mock_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [
                    {
                        "sender": "test_user_2",
                        "message": "Hello"
                    }
                ]
            }
        }
        length_before = self.query.check_inbox("test_user")
        self.query.read_inbox("test_user")
        self.assertEqual(self.query.check_inbox("test_user")[1], length_before[1] - 1)
    @patch("query.Database")
    def test_reading_message_from_empty_inbox(self, mock_database):
        """
        Testing if if inbox is empty a correct error message is returned to user
        :param mock_database:
        :return:
        """
        mock_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": []
            }
        }
        self.assertEqual(self.query.read_inbox("test_user"), ("error", "Inbox is empty"))

    # Test send_message() method
    @patch("user.Database")
    @patch("query.Database")
    def test_sending_message_to_existing_user(self, mock_query_database, mock_user_database):
        """
        Testing sending message to an existing user with not-full inbox
        :param mock_query_database:
        :param mock_user_database:
        :return:
        """
        mock_query_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [{}]
            },
            "test_user_2": {
                "username": "test_user_2",
                "inbox": []
            }
        }
        mock_user_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [{}]
            },
            "test_user_2": {
                "username": "test_user_2",
                "inbox": []
            }
        }
        message = {
            "sender": "test_user_2",
            "receiver": "test_user",
            "message": "Hello!"
        }
        self.assertEqual(self.query.send_message(message), ("ack", "message_delivered"))
    @patch("user.Database")
    def test_sending_message_to_non_existing_user(self, mock_user_database):
        """
        Testing sending message to a non-existing user
        :param mock_user_database:
        :return:
        """
        mock_user_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [{}]
            }
        }
        message = {
            "sender": "test_user",
            "receiver": "test_user_2",
            "message": "Hello!"
        }
        self.assertEqual(self.query.send_message(message), ("error", "Receiver doesn't exist"))
    @patch("user.Database")
    @patch("query.Database")
    def test_sending_message_to__existing_user_with_full_inbox(self, mock_query_database, mock_user_database):
        """
        Testing sending message to an existing user with full inbox
        :param mock_user_database:
        :param mock_query_database:
        :return:
        """
        mock_user_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [{}]
            },
            "test_user_2": {
                "username": "test_user_2",
                "inbox": [{}]
            }
        }
        mock_query_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": [
                    {"message": "Hello"},
                    {"message": "Hello"},
                    {"message": "Hello"},
                    {"message": "Hello"},
                    {"message": "Hello"},
                ]
            }
        }
        message = {
            "sender": "test_user_2",
            "receiver": "test_user",
            "message": "Hello!"
        }
        self.assertEqual(self.query.send_message(message), ("error", "Receiver inbox full"))

    # Test add_to_inbox() method
    @patch("query.Database")
    def test_adding_message_to_inbox(self, mock_query_database):
        """
        Testing if adding a new message to inbox works
        :param mock_query_database:
        :return:
        """
        mock_query_database.return_value.database = {
            "test_user": {
                "username": "test_user",
                "inbox": []
            }
        }
        length_before = self.query.check_inbox("test_user")[1]
        self.assertEqual(self.query.add_to_inbox("test_user_2", "test_user", "test_message"), ("ack", "Message delivered"))
        self.assertEqual(self.query.check_inbox("test_user")[1], length_before + 1)

if __name__ == '__main__':
    unittest.main()