"""Test suite for testing application performance"""

import unittest
import time
import sqlite3
import random
import threading
import string
import socket
import os
import resource
from asciichartpy import plot
from db import Database, DbHelper
from server import Server
from client import Client
from connection import Connection
from config import config
from connection_pool import ConnectionPool
from message import Message


class TestPerformance(unittest.TestCase):
    """Test cases for performance testing."""

    def setUp(self):
        """Setting up for testing Database methods"""
        self.drop_test_db()
        self.original_db_path = Database.DB_FILE
        Database.DB_FILE = config.tests.TEST_DB_FILE
        ConnectionPool.DB_FILE = config.tests.TEST_DB_FILE
        self.create_test_db_tables()
        self.populate_test_db()
        self.db = Database()
        # Initialize client and server instances
        self.server = Server()
        self.client = Client()

        # Create connection for tests
        self.connection = Connection()

    def tearDown(self):
        self.db.CONNECTION_POOL.close_all_connections()
        self.server.db_helper.db.CONNECTION_POOL.close_all_connections()
        ConnectionPool.DB_FILE = self.original_db_path

        time.sleep(0.1)

        self.drop_test_db()
        Database.DB_FILE = self.original_db_path

    def create_test_db_tables(self):
        # Create tables in database
        try:
            db_connection = sqlite3.connect(Database.DB_FILE)
            db_cursor = db_connection.cursor()

            # Create the tables using the queries defined in the config
            db_cursor.execute(config.database.CREATE_USER_TABLE_QUERY)
            db_connection.commit()
            db_cursor.execute(config.database.CREATE_USER_INDEX_QUERY)
            db_connection.commit()
            db_cursor.execute(config.database.CREATE_MESSAGE_TABLE_QUERY)
            db_connection.commit()
            db_cursor.execute(config.database.CREATE_MESSAGE_INDEX_QUERY)
            db_connection.commit()

        except Exception as e:
            print(f"Error creating test database tables: {e}")
        finally:
            if db_connection:
                db_cursor.close()
                db_connection.close()

    def populate_test_db(self):
        """Populate the test database with test users and data required for tests"""
        try:
            conn = sqlite3.connect(Database.DB_FILE)
            cursor = conn.cursor()

            # Insert test users
            users = [
                ("testUser1", "testPassword1", "admin"),
                ("testUser2", "testPassword2", "user"),
                ("", "testPassword3", "user"),
            ]

            for username, password, account_type in users:
                cursor.execute(
                    "INSERT INTO users (username, password, account_type) VALUES (?, ?, ?) ON CONFLICT (username) DO NOTHING",
                    (username, password, account_type),
                )

            conn.commit()
        except Exception as e:
            print(f"Error populating test database: {e}")
        finally:
            if conn:
                conn.close()

    def drop_test_db(self):
        try:
            os.remove(Database.DB_FILE)
        except OSError:
            pass

    def _print_connection_chart(self, data):
        """Print a simple ASCII chart showing connection count over time using asciichartpy."""
        if not data:
            print("No connection data to display")
            return
        
        print("Connection Pool Usage Over Time:")
        print("=" * 50)
        
        # Create the chart using asciichartpy
        chart = plot(data, {'height': 15, 'format': '{:8.0f}'})
        print(chart)
        
        # Print additional information
        print(f"Time: 0s -> {len(data)}s (1 sample per second)")
        print(f"Range: {min(data)} - {max(data)} connections")
        print(f"Average: {sum(data)/len(data):.1f} connections")
        print()


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
        self.assertLess(message_add_time/num_messages, 0.02, f"Adding messages is too slow: {message_add_time/num_messages:.6f} seconds per message")


    def test_perform_concurrent_operations(self):
        """Test for stress testing the connection pool class with few minutes of high intense, concurrent operations from various users,
        checking program behavious under pressure"""
        start_time = time.time()
        test_duration = 120
        num_threads = 200
        stop_event = threading.Event()

        db = Database()
        user_pool = [f"stressTestUser{i}" for i in range(30)]
        threads = []
        self.current_no_of_connections = []
        self.max_no_of_connections = 0
        self.sending_requests = 0
        self.reading_requests = 0

        check_no_of_users_query = """SELECT username FROM users;"""


        def logging():
            """Logging the behaviour and state of connection pool and other modules"""
            while not stop_event.is_set():
                print(f"Time since test start: {int(time.time() - start_time)}")
                available_connections = len(db.CONNECTION_POOL.open_connections)
                used_connections = db.CONNECTION_POOL.used_connection

                self.current_no_of_connections.append(available_connections + used_connections)
                
                if self.max_no_of_connections < available_connections + used_connections: 
                    self.max_no_of_connections = available_connections + used_connections

                time.sleep(1)

        def connection_cleanup():
            while not stop_event.is_set():
                db.CONNECTION_POOL.check_for_cleanup()
                time.sleep(10)


        def sim_user_behaviour():
            username = random.choice(user_pool)
            while not stop_event.is_set():
                operation = random.choice(
                    [
                        "send",
                        "send",
                        "send",
                        "send",
                        "send",
                        "send",
                        "check",
                        "check",
                        "check",
                        "check",
                    ]
                )
                if operation == "send":
                    self.sending_requests += 1
                    db.add_msg_to_db(
                        random.choice(user_pool),
                        username,
                        "".join(
                            random.choices(
                                string.ascii_uppercase + string.digits, k=100
                            )
                        ),
                    )
                else:
                    self.reading_requests += 1
                    db.read_msg_from_inbox(username)
                time.sleep(random.uniform(0.1, 1))

        print(f"[DEBUG] Number of users in DB before adding: {len(db.check_value(check_no_of_users_query))}")
        for user in user_pool:
            print(user)
            db.add_user_to_db(user, user)
        print(f"[DEBUG] Number of users in DB after adding: {len(db.check_value(check_no_of_users_query))}")

        logging_thread = threading.Thread(target=logging)
        logging_thread.start()

        cleaning_thread = threading.Thread(target=connection_cleanup)
        cleaning_thread.start()

        for _ in range(num_threads):
            t = threading.Thread(target=sim_user_behaviour)
            threads.append(t)
            t.start()

        time.sleep(test_duration)
        stop_event.set()
        
        active_threads = [t for t in threads if t.is_alive()]
        print(f"Active threads before join: {len(active_threads)}")

        # Enhanced join with monitoring
        for i, thread in enumerate(threads):
            if thread.is_alive():
                print(f"Waiting for thread {i}...")
                thread.join(timeout=10)
                if thread.is_alive():
                    print(f"⚠️  Thread {i} is stuck!")
                else:
                    print(f"✅ Thread {i} completed")

        for thread in threads:
            thread.join(timeout=10)

        print("###\n# LOGGING\n###")
        print(f"Maximum number of connections at one time: {self.max_no_of_connections}")
        print(f"Number of 'send message' requests: {self.sending_requests}")
        print(f"Number of 'read message' requests: {self.reading_requests}")
        print()
        self._print_connection_chart(self.current_no_of_connections)


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
            self.assertLess(avg_response_time, 0.5, f"Average server response time is too slow: {avg_response_time:.6f} seconds")

        except (socket.timeout, ConnectionRefusedError) as e:
            # Handle connection errors gracefully
            self.skipTest(f"Server connection error: {e}. Ensure server is running.")
        finally:
            s.close()


    def test_resource_usage(self):
        """Test the resource usage (CPU, memory) of the client and server during operation."""
        # Get baseline memory usage
        baseline_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss /1024  # KB to MB

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
        self.assertLess(memory_increase, 350.0, f"Memory increase is too high: {memory_increase:.2f} MB")
        self.assertLess(operation_time, 15.0, f"Operations took too long: {operation_time:.6f} seconds")


if __name__ == "__main__":
    unittest.main()
