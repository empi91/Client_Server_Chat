import os
import sys
import unittest

import user

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

from query import Query
from user import User

class TestQuery(unittest.TestCase):
    #setUp()
    def setUp(self):
        self.query = Query()
        self.user = User()
        self.query.database.create_database("test_db")
        self.query.database.load_config("test_db")
        self.query.database.create_tables()
        self.query.database.execute_query(self.query.database.QUERY_DICT["REGISTER_USER"], ("test_user_1", "test_password_1", "admin"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["REGISTER_USER"], ("test_user_2", "test_password_2", "user"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["ADD_MESSAGE_TO_INBOX"], ("test_msg_1", "test_user_2", "test_user_1"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["ADD_MESSAGE_TO_INBOX"], ("test_msg_2", "test_user_2", "test_user_1"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["ADD_MESSAGE_TO_INBOX"], ("test_msg_3", "test_user_2", "test_user_1"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["ADD_MESSAGE_TO_INBOX"], ("test_msg_4", "test_user_2", "test_user_1"))
        self.query.database.execute_query(self.query.database.QUERY_DICT["ADD_MESSAGE_TO_INBOX"], ("test_msg_5", "test_user_2", "test_user_1"))

    def tearDown(self):
        self.query.database.load_config("postgresql")
        self.query.database.drop_database("test_db")

    # Test check_inbox() method
    def test_checking_number_of_messages_in_user_inbox(self):
        """
        Testing if check_inbox() methods returns correct number of messages in user's inbox
        :return:
        """
        self.assertEqual(self.query.check_inbox("test_user_2"), ("inbox", 5))

    # Test read_inbox() method
    def test_reading_message_from_inbox(self):
        """
        Test if reading message from inbox works as expected
        :return:
        """
        self.assertEqual(self.query.read_inbox("test_user_2"), ("message", {"message": "test_msg_1", "sender": "test_user_1"}))
    def test_removing_read_message_from_inbox(self):
        """
        Testing if unread message is removed from inbox after read
        :return:
        """
        length_before = self.query.check_inbox("test_user_2")
        self.query.read_inbox("test_user_2")
        self.assertEqual(self.query.check_inbox("test_user_2")[1], length_before[1] - 1)
    def test_reading_message_from_empty_inbox(self):
        """
        Testing if inbox is empty a correct error message is returned to user
        :return:
        """
        self.assertEqual(self.query.read_inbox("test_user_1"), ("error", "Inbox is empty"))

    # Test send_message() method
    @patch("user.User.check_if_registered", return_value=True)
    def test_sending_message_to_existing_user(self, mock_user_check):
        """
        Testing sending message to an existing user with not-full inbox
        :return:
        """
        message = {
            "sender": 'test_user_2',
            "receiver": 'test_user_1',
            "message": "test_message"
        }
        self.assertEqual(self.query.send_message(message), ("ack", "Message delivered"))
    def test_sending_message_to_non_existing_user(self):
        """
        Testing sending message to a non-existing user
        :return:
        """
        message = {
            "sender": "test_user_2",
            "receiver": "test_user_3",
            "message": "How are you?"
        }
        self.assertEqual(self.query.send_message(message), ("error", "Receiver doesn't exist"))
    @patch("user.User.check_if_registered", return_value=True)
    def test_sending_message_to__existing_user_with_full_inbox(self, mock_user_check):
        """
        Testing sending message to an existing user with full inbox
        :param mock_user_check:
        :return:
        """
        message = {
            "sender": "test_user_1",
            "receiver": "test_user_2",
            "message": "Hello!"
        }
        self.assertEqual(self.query.send_message(message), ("error", "Receiver inbox full"))

    # Test add_to_inbox() method
    def test_adding_message_to_inbox(self):
        """
        Testing if adding a new message to inbox works
        :return:
        """
        length_before = self.query.check_inbox("test_user_2")[1]
        self.assertEqual(self.query.add_to_inbox("test_user_1", "test_user_2", "test_message"), ("ack", "Message delivered"))
        self.assertEqual(self.query.check_inbox("test_user_2")[1], length_before + 1)

if __name__ == '__main__':
    unittest.main()