"""Test suite for testing application performance"""

import unittest
import time
import os
import socket
import resource  # Standard library for resource usage
import shutil
from db import Database, DbHelper
from server import Server
from client import Client
from message import Message
from connection import Connection
from config import config


class TestPerformance(unittest.TestCase):
    """Test cases for performance testing."""

    def setUp(self):
        """Setup code to initialize server, client instances and test database."""
        # Create a temporary test database file
        self.fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures")
        self.original_db_path = Database.DB_FILE
        self.test_db_file = os.path.join(self.fixtures_path, "test_db.json")
        self.temp_db_file = os.path.join(self.fixtures_path, "temp_performance_test_db.json")
        
        if os.path.exists(self.test_db_file):
            shutil.copy(self.test_db_file, self.temp_db_file)
        
        Database.DB_FILE = self.temp_db_file
        
        # Initialize client and server instances
        self.server = Server()
        self.client = Client()
        
        # Create connection for tests
        self.connection = Connection()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original database path
        Database.DB_FILE = self.original_db_path
        
        # Remove temporary test database if it exists
        if os.path.exists(self.temp_db_file):
            os.remove(self.temp_db_file)

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
        self.assertLess(user_add_time/num_users, 0.01, 
                       f"Adding users is too slow: {user_add_time/num_users:.6f} seconds per user")
        self.assertLess(message_add_time/num_messages, 0.01, 
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
        self.assertLess(operation_time, 5.0, 
                       f"Operations took too long: {operation_time:.6f} seconds")


if __name__ == "__main__":
    unittest.main()