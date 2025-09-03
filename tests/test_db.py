""" Test suite for Database and DbHelper classes"""

import unittest
from db import Database, DbHelper
from config import config
import os
import json
import shutil

class TestDatabase(unittest.TestCase):
    """ Test suite for Database class """

    def setUp(self):
        """Setting up for testing Database methods"""      
        self.fixtures_path = config.tests.FIXTURES_PATH

        self.original_db_path = Database.DB_FILE
        self.test_db_file = os.path.join(self.fixtures_path, "test_db.json")
        self.temp_db_file = os.path.join(self.fixtures_path, "temp_test_db.json")

        if os.path.exists(self.test_db_file):
            shutil.copy(self.test_db_file, self.temp_db_file)

        Database.DB_FILE = self.temp_db_file

    
    def tearDown(self):
        Database.DB_FILE = self.original_db_path
        if os.path.exists(self.temp_db_file):
            os.remove(self.temp_db_file)

    
    def test_database_initialization(self):
        """Testing if Database class creates an empty JSON database if it doesn't exist.
        Testing if Database handles connecting to the existing database correctly"""
        
        # Test database creation if file doesn't exist
        if os.path.exists(Database.DB_FILE):
            os.remove(Database.DB_FILE)
            
        self.assertFalse(os.path.exists(Database.DB_FILE))

        db = Database()
        
        # Check that the file was created
        self.assertTrue(os.path.exists(Database.DB_FILE))
        
        with open(Database.DB_FILE, 'r') as file:
            data = json.load(file)
            self.assertIn('users', data)
            self.assertEqual(len(data['users']), 4)


    def test_adding_user_to_db(self):
        """Testing adding new users with different account types to database. """
        # if os.path.exists(Database.DB_FILE):
        #     os.remove(Database.DB_FILE)

        db = Database()
        existing_db = db.open_db()

        self.assertEqual(len(existing_db['users']), 4)

        db.add_user_to_db("TestUser6", "TestPassword1", "admin")
        db.add_user_to_db("TestUser7", "TestPassword2", "user")

        existing_db = db.open_db()
        
        self.assertEqual(len(existing_db['users']), 6)
        self.assertEqual(existing_db['users'][0]["Account type"], "admin")
        self.assertEqual(existing_db['users'][1]["Account type"], "user")

        # os.remove(Database.DB_FILE)
        

    def test_check_user_in_db(self):
        """Test user existence checking with valid usernames, non-existent users, and edge cases like empty strings. """

        db = Database()
        # db.DB_FILE = os.path.join(self.fixtures_path, 'sample_db.json')

        self.assertTrue(db.check_user_in_db("testUser1"))
        self.assertTrue(db.check_user_in_db(""))
        self.assertFalse(db.check_user_in_db("nonExistingUser"))


    def test_get_user_password(self):
        """Testing retrieval of user passwords for existing users and non-existent users. """
        db = Database()
        # db.DB_FILE = os.path.join(self.fixtures_path, 'sample_db.json')

        self.assertEqual(db.get_user_password("testUser1"), "testPassword1")
        self.assertFalse(db.get_user_password("nonExistingUser"), "testPassword1")


    def test_modify_db_valid_operations(self):
        """
        Testing modifying user data with valid operations like changing account types. 
        Testing modifying user data with invalid operations like non-existent users or non-existin fields.
        """
        db = Database()
        # db.DB_FILE = os.path.join(self.fixtures_path, 'sample_db.json')

        # Valid operations
        existing_db = db.open_db()
        self.assertEqual(existing_db["users"][0]["Account type"], "admin")

        self.assertTrue(db.modify_db("testUser1", "Account type", "user"))

        existing_db = db.open_db()
        self.assertEqual(existing_db["users"][0]["Account type"], "user")

        # self.assertTrue(db.modify_db("testUser1", "Account type", "admin"))

        # Invalid operations
        with self.assertRaises(KeyError):
            db.modify_db("testUser1", "Non Existing Field", "admin")

        with self.assertRaises(KeyError):
            db.modify_db("Non Existing User", "Account type", "admin")


    def test_inbox_operations(self):
        """ Test adding messages, reading messages, checking inbox size, and FIFO message ordering. """
        db = Database
        
        pass



    # def test_inbox_size_limit(self):
    #     """Testing inbox size limit enforcement and behavior when limit is reached. """


    #     pass


    # def test_file_corruption_handling(self):
    #     """Testing database behavior when JSON file is corrupted. """


    #     pass


    ## TODO To be implemented in the future
    # def test_concurrent_access(self):
    #     """Testing database behavior under simulated concurrent access scenarios. """
    #     pass
    

class TestDbHelper(unittest.TestCase):
    """ Test suite for DbHelper class """

    def setUp(self):
        """Setting up for testing DbHelper methods"""


        pass


    # def test_check_if_registered(self):
    #     """Testing user registration checking through DbHelper facade with existing and non-existing users."""


    #     pass


    # def test_register_new_user(self):
    #     """Testing new user registration workflow through DbHelper interface."""


    #     pass


    # def test_get_stored_password(self):
    #     """Testing password retrieval for existing users through DbHelper facade."""


    #     pass


    # def test_add_account_type(self):
    #     """Testing account type addition and modification for users with valid account types."""


    #     pass


    # def test_add_account_type_invalid(self):
    #     """Testing account type modification with invalid data and non-existent users."""


    #     pass


    # def test_add_msg_to_db(self):
    #     """Testing message addition to user inbox through DbHelper interface."""


    #     pass


    # def test_get_msg_from_inbox(self):
    #     """Testing message retrieval from user inbox with FIFO ordering through DbHelper."""


    #     pass


    # def test_check_recv_inbox_capacity(self):
    #     """Testing inbox capacity checking with empty, partial, and full inboxes."""


    #     pass


    # def test_dbhelper_database_integration(self):
    #     """Testing that DbHelper properly delegates operations to Database instance."""


    #     pass


if __name__ == '__main__':
    unittest.main()