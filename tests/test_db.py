""" Test suite for Database and DbHelper classes"""

import unittest
from db import Database, DbHelper
from config import config

class TestDatabase(unittest.TestCase):
    """ Test suite for Database class """

    def SetUp(self):
        """Setting up for testing Database methods"""
        

        pass

    
    def test_database_initialization(self):
        """Testing if Database class creates an empty JSON database if it doesn't exist.
        Testing if Database handles connecting to the existing database correctly"""


        pass


    def test_adding_user_to_db(self):
        """Testing adding new users with different account types to database. """


        pass


    def test_check_user_in_db(self):
        """Test user existence checking with valid usernames, non-existent users, and edge cases like empty strings. """


        pass


    def test_get_user_password(self):
        """Testing retrieval of user passwords for existing users and handling non-existent users. """


        pass


    def test_modify_db_valid_operations(self):
        """Testing modifying user data with valid operations like changing passwords and account types. """


        pass


    def test_modify_db_invalid_operations(self):
        """Testing modifying user data with invalid operations like non-existent users or non-existin fields. """


        pass


    def test_inbox_operations(self):
        """ Test adding messages, reading messages, checking inbox size, and FIFO message ordering. """


        pass


    def test_inbox_size_limit(self):
        """Testing inbox size limit enforcement and behavior when limit is reached. """


        pass


    def test_file_corruption_handling(self):
        """Testing database behavior when JSON file is corrupted. """


        pass


    ## TODO To be implemented in the future
    # def test_concurrent_access(self):
    #     """Testing database behavior under simulated concurrent access scenarios. """
    #     pass
    

class TestDbHelper(unittest.TestCase):
    """ Test suite for DbHelper class """

    def setUp(self):
        """Setting up for testing DbHelper methods"""


        pass


    def test_check_if_registered(self):
        """Testing user registration checking through DbHelper facade with existing and non-existing users."""


        pass


    def test_register_new_user(self):
        """Testing new user registration workflow through DbHelper interface."""


        pass


    def test_get_stored_password(self):
        """Testing password retrieval for existing users through DbHelper facade."""


        pass


    def test_add_account_type(self):
        """Testing account type addition and modification for users with valid account types."""


        pass


    def test_add_account_type_invalid(self):
        """Testing account type modification with invalid data and non-existent users."""


        pass


    def test_add_msg_to_db(self):
        """Testing message addition to user inbox through DbHelper interface."""


        pass


    def test_get_msg_from_inbox(self):
        """Testing message retrieval from user inbox with FIFO ordering through DbHelper."""


        pass


    def test_check_recv_inbox_capacity(self):
        """Testing inbox capacity checking with empty, partial, and full inboxes."""


        pass


    def test_dbhelper_database_integration(self):
        """Testing that DbHelper properly delegates operations to Database instance."""


        pass


if __name__ == '__main__':
    unittest.main()