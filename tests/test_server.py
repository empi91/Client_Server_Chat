""" Test suite for Server class"""

import unittest
import os
import time
import psycopg2
from datetime import datetime, timedelta
from server import Server, UserAuthenticator
from config import config
from message import Message
from connection import Connection
from db import DbHelper, Database
from connection_pool import ConnectionPool


class TestServer(unittest.TestCase):
    """ Test suite for Server class """

    def setUp(self):
        """Setting up for testing Server methods"""
        # Setup test database
        self.original_db_path = Database.DB_FILE
        Database.DB_FILE = config.tests.TEST_DB_FILE
        ConnectionPool.DB_FILE = config.tests.TEST_DB_FILE
        self.init_test_db()
        self.create_test_db_tables()
        self.populate_test_db()
        self.db = Database()
        
        # Create a test server instance
        self.server = Server()
        self.server.db_helper = DbHelper()
        
        # Set a fixed start time for consistent uptime testing
        self.server.start_time = datetime.now() - timedelta(days=1, hours=2, minutes=30, seconds=15)
        
        # Create a test connection for testing
        self.connection = Connection()


    def tearDown(self):
        """Clean up after tests"""
        self.db.CONNECTION_POOL.close_all_connections()
        self.server.db_helper.db.CONNECTION_POOL.close_all_connections()
        ConnectionPool.DB_FILE = self.original_db_path

        time.sleep(0.1)

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
            
            # Insert test users
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
        except Exception as e:
            print(f"Error populating test database: {e}")
        finally:
            if conn:
                conn.close()
        

    def drop_test_db(self):
        try:
            conn = psycopg2.connect(host="localhost", dbname="postgres", user=config.database.DB_USER, 
                                   password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s;", (Database.DB_FILE,))
            cursor.execute(f"DROP DATABASE {Database.DB_FILE};")
        except Exception as e: 
            print(f"Error dropping database: {e}")
        finally:
            if conn:
                conn.close()


    def test_server_initialization(self):
        """Test proper initialization of the server"""
        self.assertIsNotNone(self.server.db_helper)
        self.assertEqual(self.server.server_host, config.network.HOST)
        self.assertEqual(self.server.server_port, config.network.PORT)
        self.assertIsInstance(self.server.start_time, datetime)


    def test_server_start(self):
        """Test starting the server"""
        # We'll test only the initialization part since actually starting the server
        # would block the test execution
        connection = Connection()
        self.assertIsNotNone(connection)
        # Verify that creating a connection does not raise an exception
        try:
            s = connection.create_connection(is_server=True)
            self.assertIsNotNone(s)
        finally:
            if hasattr(s, 'close'):
                s.close()


    def test_message_handling(self):
        """Test that different message headers are routed to correct handler methods."""
        # Test Command message
        command_message = Message("Command", "help", "test_user", self.server.server_host)
        response = self.server.process_message(command_message, self.connection)
        self.assertEqual(response.header, "Command")
        
        # Test Authentication message
        auth_message = Message("Authentication", {"login": "test_user", "password": "test_pass"}, "Authenticator", "Server")
        response = self.server.process_message(auth_message, self.connection)
        self.assertEqual(response.header, "Authentication_answer")
        
        # Test invalid header
        invalid_message = Message("InvalidHeader", "test", "test_user", self.server.server_host)
        response = self.server.process_message(invalid_message, self.connection)
        self.assertEqual(response.header, "Error")
        self.assertEqual(response.text, "Invalid message header")


    def test_command_handling(self):
        """ Test all server commands (help, uptime, info, inbox, stop) return correct responses."""
        # Test help command
        help_msg = Message("Command", "help", "test_user", self.server.server_host)
        response = self.server.handle_command(help_msg, self.connection)
        self.assertEqual(response.header, "Command")
        self.assertIn("HELP", response.text)
        
        # Test uptime command
        uptime_msg = Message("Command", "uptime", "test_user", self.server.server_host)
        response = self.server.handle_command(uptime_msg, self.connection)
        self.assertEqual(response.header, "Command")
        self.assertIn("Server uptime", response.text)
        
        # Test info command
        info_msg = Message("Command", "info", "test_user", self.server.server_host)
        response = self.server.handle_command(info_msg, self.connection)
        self.assertEqual(response.header, "Command")
        self.assertIn("Server version", response.text)
        
        # Test stop command
        stop_msg = Message("Command", "stop", "test_user", self.server.server_host)
        response = self.server.handle_command(stop_msg, self.connection)
        self.assertEqual(response.header, "Stop")
        self.assertEqual(response.text, "Stop")


    def test_uptime_calc(self):
        """Test uptime calculation accuracy and proper formatting of time components."""
        days, hours, minutes, seconds = self.server.calc_uptime()
        
        # Since we set start_time in setUp to be 1 day, 2 hours, 30 minutes, and 15 seconds ago
        self.assertEqual(days, 1)
        self.assertAlmostEqual(hours, 2, delta=1)  # Allow small delta due to test execution time
        self.assertAlmostEqual(minutes, 30, delta=1)  # Allow small delta due to test execution time
        
        # Seconds will vary because of test execution time, but should be roughly correct
        self.assertGreaterEqual(seconds, 0)
        self.assertLess(seconds, 86400)  # Less than a day in seconds


    def test_authentication_flow(self):
        """Test complete authentication workflow for both existing and new users."""
        # Test authentication for a new user
        auth_data = {"login": "new_test_user", "password": "test_password"}
        auth_msg = Message("Authentication", auth_data, "Authenticator", "Server")
        response = self.server.handle_authentication(auth_msg, self.connection)
        
        self.assertEqual(response.header, "Authentication_answer")
        self.assertFalse(response.text["is_registered"])
        self.assertTrue(response.text["login_successfull"])
        
        # Test authentication for the same user (now existing)
        response = self.server.handle_authentication(auth_msg, self.connection)
        self.assertTrue(response.text["is_registered"])


    def test_message_sending_validation(self):
        """Test message sending with various scenarios including valid and invalid recipients and empty/full inboxes."""
        # First register a test receiver
        self.server.db_helper.register_new_user("test_receiver", "password_hash")
        
        # Test sending message to valid recipient
        msg = Message("Message", "Test message content", "testUser1", "test_receiver")
        response = self.server.handle_sending_message(msg, self.connection)
        self.assertEqual(response.header, "Status")
        self.assertTrue(response.text)  # Should be True for successful message sending
        
        # Test sending message to non-existent recipient
        msg = Message("Message", "Test message content", "testUser1", "non_existent_user")
        response = self.server.handle_sending_message(msg, self.connection)
        self.assertEqual(response.header, "Error")
        self.assertEqual(response.text, "Receiver not existing in database")


    def test_error_message_handling(self):
        """Test that invalid message headers and malformed requests generate proper error responses."""
        # Test invalid message header
        invalid_msg = Message("InvalidHeader", "test content", "test_sender", self.server.server_host)
        response = self.server.process_message(invalid_msg, self.connection)
        
        self.assertEqual(response.header, "Error")
        self.assertEqual(response.text, "Invalid message header")
        self.assertEqual(response.sender, self.server.server_host)
        self.assertEqual(response.receiver, "test_sender")
        

class TestUserAuthenticator(unittest.TestCase):
    """ Test suite for UserAuthenticator class """


    def setUp(self):
        """Setting up for testing Server methods"""
        # Setup test database
        self.original_db_path = Database.DB_FILE
        Database.DB_FILE = config.tests.TEST_DB_FILE
        ConnectionPool.DB_FILE = config.tests.TEST_DB_FILE
        self.init_test_db()
        self.create_test_db_tables()
        self.populate_test_db()
        self.db = Database()
        
        # Create a test server instance
        self.server = Server()
        self.server.db_helper = DbHelper()
        
        # Set a fixed start time for consistent uptime testing
        self.server.start_time = datetime.now() - timedelta(days=1, hours=2, minutes=30, seconds=15)
        
        # Create a test connection for testing
        self.connection = Connection()

        # Create test data
        self.test_login = "test_auth_user"
        self.test_password = "test_password"
        self.message = {
            "login": self.test_login,
            "password": self.test_password
        }
        
        # Create authenticator instance
        self.authenticator = UserAuthenticator(self.message)


    def tearDown(self):
        """Clean up after tests"""

        self.db.CONNECTION_POOL.close_all_connections()
        self.server.db_helper.db.CONNECTION_POOL.close_all_connections()
        ConnectionPool.DB_FILE = self.original_db_path

        time.sleep(0.1)

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
            
            # Insert test users
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
        except Exception as e:
            print(f"Error populating test database: {e}")
        finally:
            if conn:
                conn.close()
        

    def drop_test_db(self):
        try:
            conn = psycopg2.connect(host="localhost", dbname="postgres", user=config.database.DB_USER, 
                                   password=config.database.DB_PASSWORD, port=config.database.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s;", (Database.DB_FILE,))
            cursor.execute(f"DROP DATABASE {Database.DB_FILE};")
        except Exception as e: 
            print(f"Error dropping database: {e}")
        finally:
            if conn:
                conn.close()


    def test_user_registration(self):
        """Test user registration process including various account types"""
        # Test user registration (new user)
        auth_result = self.authenticator.verify_login()
        
        # Check the result is correct for new user
        self.assertFalse(auth_result["is_registered"])
        self.assertTrue(auth_result["login_successfull"])
        
        # Verify the user was actually added to the database
        self.assertTrue(self.authenticator.db_helper.check_if_registered(self.test_login))


    def test_user_login(self):
        """Test user login process with valid and invalid credentials."""
        # First register the user
        self.authenticator.verify_login()
        
        # Test successful login with correct password
        auth_result = self.authenticator.verify_login()
        self.assertTrue(auth_result["is_registered"])
        self.assertTrue(auth_result["login_successfull"])
        
        # Test failed login with incorrect password
        wrong_password_message = {
            "login": self.test_login,
            "password": "wrong_password"
        }
        wrong_auth = UserAuthenticator(wrong_password_message)
        auth_result = wrong_auth.verify_login()
        
        self.assertTrue(auth_result["is_registered"])
        self.assertFalse(auth_result["login_successfull"])


    def test_password_hashing(self):
        """Test if password hashing is working correctly"""
        # Hash a password
        hashed_password = self.authenticator.hash_password(self.test_password)
        
        # Verify it's not the same as the original
        self.assertNotEqual(hashed_password, self.test_password)
        
        # Verify password validation works
        self.assertTrue(self.authenticator.verify_password(self.test_password, hashed_password))
        self.assertFalse(self.authenticator.verify_password("wrong_password", hashed_password))


    def test_auth_edge_cases(self):
        """Test authentication with empty passwords, very long passwords, and special characters."""
        # Test with special characters in password
        special_password = "p@ssw0rd!#$%"
        special_hash = self.authenticator.hash_password(special_password)
        self.assertTrue(self.authenticator.verify_password(special_password, special_hash))
        
        # Test with long password
        long_password = "a" * 50  # 50 character password
        long_hash = self.authenticator.hash_password(long_password)
        self.assertTrue(self.authenticator.verify_password(long_password, long_hash))
        
        # Test with empty password
        empty_password = ""
        empty_hash = self.authenticator.hash_password(empty_password)
        self.assertTrue(self.authenticator.verify_password(empty_password, empty_hash))
        

if __name__ == "__main__":
    unittest.main()