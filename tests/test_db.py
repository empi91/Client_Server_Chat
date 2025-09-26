""" Test suite for Database and DbHelper classes"""

import unittest
from db import Database, DbHelper
from config import config
import os
import json
import shutil
import psycopg2


class TestDatabase(unittest.TestCase):
    """ Test suite for Database class """

    def setUp(self):
        """Setting up for testing Database methods"""      
        self.original_db_path = Database.DB_FILE
        Database.DB_FILE = config.tests.TEST_DB_FILE
        self.init_test_db()
        self.create_test_db_tables()
        self.populate_test_db()
        self.db = Database()


    def tearDown(self):
        self.drop_test_db()
        Database.DB_FILE = self.original_db_path



    def init_test_db(self):
        # Create test database
        try:
            conn = psycopg2.connect(host="localhost", dbname="postgres", user=config.database.DB_USER, 
                                   password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (Database.DB_FILE,))
            db_exists = cursor.fetchone()
            if not db_exists:
                cursor.execute(f"CREATE DATABASE {Database.DB_FILE};")
                print(f"New database {Database.DB_FILE} created")
        except Exception as e: 
            print(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()


    def create_test_db_tables(self):
        # Create tables in database
        try:
            conn = psycopg2.connect(host="localhost", dbname=Database.DB_FILE, user=config.database.DB_USER, 
                                    password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Create the tables using the queries defined in the config
            cursor.execute(config.database.CREATE_USER_TABLE_QUERY)
            cursor.execute(config.database.CREATE_MESSAGE_TABLE_QUERY)
            
            conn.commit()
            print("Test database tables created successfully")
        except Exception as e: 
            print(f"Error creating test database tables: {e}")
        finally:
            if conn:
                conn.close()
    
    def populate_test_db(self):
        """Populate the test database with test users and data required for tests"""
        try:
            conn = psycopg2.connect(host="localhost", dbname=Database.DB_FILE, user=config.database.DB_USER, 
                                    password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Insert test users from test_db.json
            users = [
                ("testUser1", "testPassword1", "admin"),
                ("testUser2", "testPassword2", "user"),
                ("", "testPassword3", "user")
            ]
            
            for username, password, account_type in users:
                cursor.execute(
                    "INSERT INTO users (username, password, account_type) VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING",
                    (username, password, account_type)
                )
            
            conn.commit()
            print("Test database populated successfully")
        except Exception as e:
            print(f"Error populating test database: {e}")
        finally:
            if conn:
                conn.close()
        


    def drop_test_db(self):
        try:
            conn = psycopg2.connect(host="localhost", dbname = "postgres", user=config.database.DB_USER, password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE {Database.DB_FILE};")
            print(f"Database {Database.DB_FILE} removed.")
        except Exception as e: 
            print(f"Error initializing databse: {e}")
        finally:
            if conn:
                conn.close

    
    def test_database_initialization(self):
        """Testing if Database class creates an empty PostgreSQL database if it doesn't exist.
        Testing if Database handles connecting to the existing database correctly"""
        #TODO Modify code to assert if SQL DB does or does not exist
        #TODO Assert if tables are created correctly
        
        # Test database creation if file doesn't exist
        # if os.path.exists(Database.DB_FILE):
        #     os.remove(Database.DB_FILE)
            
        self.assertFalse(os.path.exists(Database.DB_FILE))

        db = Database()
        
        # Check that the file was created
        self.assertTrue(os.path.exists(Database.DB_FILE))
        
        # with open(Database.DB_FILE, 'r') as file:
        #     data = json.load(file)
        #     self.assertIn('users', data)
        #     self.assertEqual(len(data['users']), 0)

        



    def test_adding_user_to_db(self):
        """Testing adding new users with different account types to database. """
        #TODO Add adding default messages to test database
        #TODO Modify number of testUsers created by default

        check_no_of_users_query = """SELECT username FROM users;"""
        check_user_acc_type = """SELECT account_type FROM users WHERE username=%s"""
        db = Database()
        existing_db = db.open_db()

        # self.assertEqual(len(db.check_value(check_no_of_users_query)), 0)
        print(db.check_value(check_no_of_users_query))

        db.add_user_to_db("TestUser4", "TestPassword4", "admin")
        db.add_user_to_db("TestUser5", "TestPassword5", "user")

        existing_db = db.open_db()
        
        self.assertEqual(db.check_value(check_no_of_users_query), 2)
        # self.assertEqual(existing_db['users'][0]["Account type"], "admin")
        # self.assertEqual(existing_db['users'][1]["Account type"], "user")
        self.assertEqual(db.check_value((check_no_of_users_query,"TestUser6")), "admin")
        self.assertEqual(db.check_value((check_no_of_users_query,"TestUser7")), "user")


    def test_check_user_in_db(self):
        """Test user existence checking with valid usernames, non-existent users, and edge cases like empty strings. """

        db = Database()

        self.assertTrue(db.check_user_in_db("testUser1"))
        self.assertTrue(db.check_user_in_db(""))
        self.assertFalse(db.check_user_in_db("nonExistingUser"))


    def test_get_user_password(self):
        """Testing retrieval of user passwords for existing users and non-existent users. """
        db = Database()

        self.assertEqual(db.get_user_password("testUser1"), "testPassword1")
        self.assertFalse(db.get_user_password("nonExistingUser"), "testPassword1")


    def test_modify_db_valid_operations(self):
        """
        Testing modifying user data with valid operations like changing account types. 
        Testing modifying user data with invalid operations like non-existent users or non-existin fields.
        """
        #TODO Modify to properly access existing data from DB
        db = Database()

        # Valid operations
        existing_db = db.open_db()
        self.assertEqual(existing_db["users"][0]["Account type"], "admin")  # !!!!

        self.assertTrue(db.modify_db("testUser1", "Account type", "user"))

        existing_db = db.open_db()
        self.assertEqual(existing_db["users"][0]["Account type"], "user")   # !!!!

        # Invalid operations
        with self.assertRaises(KeyError):
            db.modify_db("testUser1", "Non Existing Field", "admin")

        with self.assertRaises(KeyError):
            db.modify_db("Non Existing User", "Account type", "admin")


    def test_inbox_operations(self):
        """ Test adding messages, reading messages, checking inbox size, and overflowing user inbox. """
        #TODO Modify test to comply with new rules of retreiving all messages from inbox at once
        db = Database()
        
        # Clear inbox first to ensure a clean state
        while db.check_user_inbox("testUser1") > 0:
            db.read_msg_from_inbox("testUser1")

        # Add multiple messages in a specific order
        db.add_msg_to_db("testUser1", "sender1", "First Message")
        db.add_msg_to_db("testUser1", "sender2", "Second Message")
        db.add_msg_to_db("testUser1", "sender3", "Third Message")

        # Verify the inbox size
        self.assertEqual(db.check_user_inbox("testUser1"), 3)

        # Verify messages are retrieved in the same order they were added (FIFO)
        sender1, message1 = db.read_msg_from_inbox("testUser1")
        self.assertEqual(sender1, "sender1")
        self.assertEqual(message1, "First Message")

        sender2, message2 = db.read_msg_from_inbox("testUser1")
        self.assertEqual(sender2, "sender2")
        self.assertEqual(message2, "Second Message")

        sender3, message3 = db.read_msg_from_inbox("testUser1")
        self.assertEqual(sender3, "sender3")
        self.assertEqual(message3, "Third Message")

        # Verify inbox is empty after all messages are retrieved
        self.assertEqual(db.check_user_inbox("testUser1"), 0)
        

    def test_inbox_size_limit(self):
        """Testing inbox size limit enforcement and behavior when limit is reached. """
        db = Database()
        for i in range(6):
            if i < 5:
                self.assertEqual(db.check_user_inbox("testUser1"), i)
                db.add_msg_to_db("testUser1", "testUser2", f"Test Message{i}")
                self.assertEqual(db.check_user_inbox("testUser1"), i + 1)
            else:
                self.assertRaises(OverflowError)
  

# class TestDbHelper(unittest.TestCase):
#     """ Test suite for DbHelper class """

#     def setUp(self):
#         """Setting up for testing DbHelper methods"""
#         self.fixtures_path = config.tests.FIXTURES_PATH
#         self.original_db_path = Database.DB_FILE
        
#         self.test_db_file = os.path.join(self.fixtures_path, "test_db.json")
#         self.temp_db_file = os.path.join(self.fixtures_path, f"temp_test_db.json")
        
#         if os.path.exists(self.test_db_file):
#             shutil.copy(self.test_db_file, self.temp_db_file)
            
#         Database.DB_FILE = self.temp_db_file
#         self.db_helper = DbHelper()


#     def tearDown(self):
#         Database.DB_FILE = self.original_db_path
#         if os.path.exists(self.temp_db_file):
#             os.remove(self.temp_db_file)


#     def test_check_if_registered(self):
#         """Testing user registration checking through DbHelper facade with existing and non-existing users."""
#         # Test with existing user
#         self.assertTrue(self.db_helper.check_if_registered("testUser1"))
        
#         # Test with non-existing user
#         self.assertFalse(self.db_helper.check_if_registered("nonExistingUser"))
        

#     def test_register_new_user(self):
#         """Testing new user registration workflow through DbHelper interface."""
#         # Register a new user through DbHelper
#         self.db_helper.register_new_user("newTestUser", "newTestPassword")
        
#         # Verify user was added correctly
#         self.assertTrue(self.db_helper.check_if_registered("newTestUser"))
#         self.assertEqual(self.db_helper.get_stored_password("newTestUser"), "newTestPassword")


#     def test_get_stored_password(self):
#         """Testing password retrieval for existing users through DbHelper facade."""
#         # Test password retrieval for existing user
#         self.assertEqual(self.db_helper.get_stored_password("testUser1"), "testPassword1")
        
#         # Test password retrieval for non-existing user
#         self.assertFalse(self.db_helper.get_stored_password("nonExistingUser"))


#     def test_add_account_type(self):
#         """Testing account type addition and modification for users with valid account types."""
#         # Test modifying account type for existing user
#         result = self.db_helper.add_account_type({"login": "testUser1", "acc_type": "admin"})
#         self.assertTrue(result)
        
#         # Verify that account type was updated
#         db = Database()
#         existing_db = db.open_db()
        
#         # Find the user and check their account type
#         user_found = False
#         for user in existing_db["users"]:
#             if user["Username"] == "testUser1":
#                 user_found = True
#                 self.assertEqual(user["Account type"], "admin")
        
#         self.assertTrue(user_found)


#     def test_add_account_type_invalid(self):
#         """Testing account type modification with invalid data and non-existent users."""
#         # Test with non-existent user
#         with self.assertRaises(KeyError):
#             self.db_helper.add_account_type({"login": "nonExistingUser", "acc_type": "admin"})


#     def test_add_msg_to_db(self):
#         """Testing message addition to user inbox through DbHelper interface."""
            
#         # Add a test message
#         result = self.db_helper.add_msg_to_db("testUser1", "sender", "Test message content")
#         self.assertTrue(result)
        
#         # Verify message was added correctly
#         sender, message = self.db_helper.get_msg_from_inbox("testUser1")
#         self.assertEqual(sender, "sender")
#         self.assertEqual(message, "Test message content")
        
#         # Test adding to non-existent user
#         result = self.db_helper.add_msg_to_db("nonExistingUser", "sender", "Test message")
#         self.assertFalse(result)


#     def test_get_msg_from_inbox(self):
#         """Testing message retrieval from user inbox with FIFO ordering through DbHelper."""
            
#         # Add multiple messages in a specific order
#         self.db_helper.add_msg_to_db("testUser1", "sender1", "First Message")
#         self.db_helper.add_msg_to_db("testUser1", "sender2", "Second Message")
        
#         # Test FIFO order retrieval
#         sender1, message1 = self.db_helper.get_msg_from_inbox("testUser1")
#         self.assertEqual(sender1, "sender1")
#         self.assertEqual(message1, "First Message")
        
#         sender2, message2 = self.db_helper.get_msg_from_inbox("testUser1")
#         self.assertEqual(sender2, "sender2")
#         self.assertEqual(message2, "Second Message")
        
#         # Test empty inbox returns EMPTY
#         empty_sender, empty_message = self.db_helper.get_msg_from_inbox("testUser1")
#         self.assertEqual(empty_sender, "testUser1")
#         self.assertEqual(empty_message, "EMPTY")


#     def test_check_recv_inbox_capacity(self):
#         """Testing inbox capacity checking with empty, partial, and full inboxes."""
            
#         # Empty inbox should have capacity
#         self.assertTrue(self.db_helper.check_recv_inbox("testUser1"))
        
#         # Add 4 messages (below the limit of 5)
#         for i in range(4):
#             self.db_helper.add_msg_to_db("testUser1", "sender", f"Message {i}")
            
#         # Inbox with 4 messages should still have capacity
#         self.assertTrue(self.db_helper.check_recv_inbox("testUser1"))
        
#         # Add 5th message (reaching the limit)
#         self.db_helper.add_msg_to_db("testUser1", "sender", "Message 5")
        
#         # Full inbox should report no capacity
#         self.assertFalse(self.db_helper.check_recv_inbox("testUser1"))


#     def test_dbhelper_database_integration(self):
#         """Testing that DbHelper properly integrates with Database methods."""
#         # Test that DbHelper methods return the same values as direct Database calls
        
#         # Test check_if_registered method
#         username = "testUser1"
#         db_result = self.db_helper.db.check_user_in_db(username)
#         helper_result = self.db_helper.check_if_registered(username)
#         self.assertEqual(db_result, helper_result)
        
#         # Test get_stored_password method
#         db_password = self.db_helper.db.get_user_password(username)
#         helper_password = self.db_helper.get_stored_password(username)
#         self.assertEqual(db_password, helper_password)
        
#         # Test add_msg_to_db method
#         # First, let's create a unique test message
#         test_message = f"Integration test message {os.urandom(4).hex()}"
        
#         # Add message directly using Database and through DbHelper to different users
#         direct_recipient = "testUser2"
#         helper_recipient = "testUser3"
        
#         self.db_helper.db.add_msg_to_db(direct_recipient, "sender", test_message)
#         self.db_helper.add_msg_to_db(helper_recipient, "sender", test_message)

#         # Verify both messages were added correctly
#         db_sender, db_message = self.db_helper.db.read_msg_from_inbox(direct_recipient)
#         helper_sender, helper_message = self.db_helper.get_msg_from_inbox(helper_recipient)
        
#         self.assertEqual(db_sender, helper_sender)
#         self.assertEqual(db_message, helper_message)


if __name__ == '__main__':
    unittest.main()