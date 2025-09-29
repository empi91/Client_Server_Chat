"""Test suite for testing application performance"""

import unittest
import time
import os
import socket
import resource  # Standard library for resource usage
import shutil
import psycopg2
from db import Database, DbHelper
from server import Server
from client import Client
from message import Message
from connection import Connection
from config import config


class TestPerformance(unittest.TestCase):
    """Test cases for performance testing."""


    def setUp(self):
        """Setting up for testing Database methods"""      
        self.original_db_path = Database.DB_FILE
        Database.DB_FILE = config.tests.TEST_DB_FILE
        self.init_test_db()
        self.create_test_db_tables()
        self.populate_test_db()
        self.db = Database()
        # Initialize client and server instances
        self.server = Server()
        self.client = Client()
        
        # Create connection for tests
        self.connection = Connection()


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
            cursor.execute(f"DROP DATABASE {Database.DB_FILE};")
        except Exception as e: 
            print(f"Error dropping database: {e}")
        finally:
            if conn:
                conn.close()


    def test_large_message_handling(self):
        """Test the performance of sending large messages from client to server (assiming there is no limit implemented)."""
        # Create a large message of varying sizes
        message_sizes = [10_000, 100_000, 500_000]
        encoding_times = []
        
        for size in message_sizes:
            # Create large message text
            large_text = "a" * size
            
            # Create message object
            message = Message(
                header="Message",
                text=large_text,
                sender="testUser1",
                receiver="testUser2"
            )
            
            # Measure encoding time
            start_time = time.time()
            encoded_message = message.encode_message()
            encoding_time = time.time() - start_time
            encoding_times.append(encoding_time)
            
            # Print results
            print(f"Message size: {size} characters")
            print(f"Encoding time: {encoding_time:.6f} seconds")
            print(f"Encoded message size: {len(encoded_message)} bytes")
            
            # Basic assertions to ensure performance is reasonable
            self.assertLess(encoding_time, 1.0, 
                           f"Encoding {size} characters took too long: {encoding_time:.6f} seconds")
        print("-------------------------")


    def test_database_query_performance(self):
        """Test database operations with large numbers of users and messages."""
        # Create a database instance
        db = Database()
        db_helper = DbHelper()
        
        # Test user addition performance
        start_time = time.time()
        num_users = 100  # Adjust based on what's reasonable for your application
        
        for i in range(num_users):
            username = f"perfTestUser{i}"
            password = f"perfTestPassword{i}"
            account_type = "user"
            db.add_user_to_db(username, password, account_type)
        
        user_add_time = time.time() - start_time
        print(f"Time to add {num_users} users: {user_add_time:.6f} seconds")
        print(f"Average time per user: {user_add_time/num_users:.6f} seconds")
        
        # Test message addition performance
        start_time = time.time()
        num_messages = 100  # Adjust based on what's reasonable
        
        for i in range(num_messages):
            sender = "perfTestUser0"
            receiver = f"perfTestUser{i%num_users}"
            message_text = f"Performance test message {i}"
            db_helper.add_msg_to_db(receiver, sender, message_text)
        
        message_add_time = time.time() - start_time
        print(f"Time to add {num_messages} messages: {message_add_time:.6f} seconds")
        print(f"Average time per message: {message_add_time/num_messages:.6f} seconds")
        print("-------------------------")
        
        # Basic assertions
        self.assertLess(user_add_time/num_users, 0.05, 
                       f"Adding users is too slow: {user_add_time/num_users:.6f} seconds per user")
        self.assertLess(message_add_time/num_messages, 0.02, 
                       f"Adding messages is too slow: {message_add_time/num_messages:.6f} seconds per message")


    def test_server_response_time(self):
        """Test the time taken by the server to respond to client requests."""
        # Set up connection for testing
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a timeout for the connection attempts
        
        try:
            # Create a connection to server
            s.connect((config.network.HOST, config.network.PORT))
            
            # Prepare test messages
            test_messages = [
                Message(header="Command", text="info", sender="testUser", receiver=config.network.HOST),
                Message(header="Command", text="uptime", sender="testUser", receiver=config.network.HOST),
                Message(header="Command", text="help", sender="testUser", receiver=config.network.HOST)
            ]
            
            # Measure response times
            response_times = []
            
            for msg in test_messages:
                encoded_msg = msg.encode_message()
                
                start_time = time.time()
                s.sendall(encoded_msg)
                
                # Wait for response (adjust buffer size as needed)
                response = s.recv(config.network.BUFFER_SIZE)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                print(f"Command '{msg.text}' response time: {response_time:.6f} seconds")
            
            # Calculate average response time
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average server response time: {avg_response_time:.6f} seconds")
            
            # Basic assertion
            self.assertLess(avg_response_time, 0.5, 
                           f"Average server response time is too slow: {avg_response_time:.6f} seconds")
                
        except (socket.timeout, ConnectionRefusedError) as e:
            # Handle connection errors gracefully
            self.skipTest(f"Server connection error: {e}. Ensure server is running.")
        finally:
            s.close()


    def test_resource_usage(self):
        """Test the resource usage (CPU, memory) of the client and server during operation."""
        # Get baseline memory usage
        baseline_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
        
        # Create database with test data
        db = Database()
        db_helper = DbHelper()
        
        # Perform operations that might stress resources
        num_operations = 1000
        
        # Measure performance during database operations
        start_time = time.time()
        for i in range(num_operations):
            # Simulate database queries
            db.check_user_in_db(f"testUser{i % 10}")
            
        operation_time = time.time() - start_time
        
        # Measure memory usage after operations
        current_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
        memory_increase = current_memory - baseline_memory
        
        # Get CPU time used (user + system time)
        user_cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        system_cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_stime
        total_cpu_time = user_cpu_time + system_cpu_time
        
        print(f"Baseline memory usage: {baseline_memory:.2f} MB")
        print(f"Current memory usage: {current_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"User CPU time: {user_cpu_time:.6f} seconds")
        print(f"System CPU time: {system_cpu_time:.6f} seconds")
        print(f"Total CPU time: {total_cpu_time:.6f} seconds")
        print(f"Time to perform {num_operations} operations: {operation_time:.6f} seconds")
        print(f"Operations per second: {num_operations/operation_time:.2f}")
        
        # Basic assertions
        self.assertLess(memory_increase, 50.0, 
                       f"Memory increase is too high: {memory_increase:.2f} MB")
        self.assertLess(operation_time, 15.0, 
                       f"Operations took too long: {operation_time:.6f} seconds")


if __name__ == "__main__":
    unittest.main()