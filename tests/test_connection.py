"""Test suite for Connection.py class"""

import unittest
import socket
from connection import Connection


class TestConnection(unittest.TestCase):
    """Test suite for Connection class"""

    def setUp(self):
        """Setting up for testing Connection methods"""
        self.connection = Connection()

    def test_sockeet_creation(self):
        """Test successful socket creation for both client and server modes with proper socket options."""
        # Test client socket creation
        client_socket = self.connection.create_connection(is_server=False)
        self.assertIsInstance(client_socket, socket.socket)
        self.assertEqual(client_socket.family, socket.AF_INET)
        self.assertEqual(client_socket.type, socket.SOCK_STREAM)
        client_socket.close()

        # Test server socket creation
        self.connection = Connection()  # Create a new connection object
        server_socket = self.connection.create_connection(is_server=True)
        self.assertIsInstance(server_socket, socket.socket)
        self.assertEqual(server_socket.family, socket.AF_INET)
        self.assertEqual(server_socket.type, socket.SOCK_STREAM)
        server_socket.close()

    def test_socket_creation_failure(self):
        """Test error handling when socket creation fails due to system limitations or permissions."""
        original_socket = socket.socket

        try:
            # Replace socket.socket with a function that raises an error
            def mock_socket(*args, **kwargs):
                raise socket.error("Simulated socket creation failure")

            socket.socket = mock_socket

            # The method should handle the exception and print an error
            result = self.connection.create_connection()
            self.assertIsNone(result)
            self.assertIsNone(self.connection.socket)

        finally:
            # Restore the original socket.socket function
            socket.socket = original_socket

    def test_server_socket_reuse(self):
        """Test that SO_REUSEADDR is properly set for server sockets to allow quick restart."""
        server_socket = self.connection.create_connection(is_server=True)

        # Check that SO_REUSEADDR is set
        option_value = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertEqual(
            option_value, 1, "SO_REUSEADDR should be set for server sockets"
        )

        server_socket.close()

    def test_connection_context_management(self):
        """Test that sockets are properly closed when using the connection as a context manager."""
        # Test that Connection implements context management
        self.assertTrue(
            hasattr(self.connection, "__enter__"),
            "Connection should implement context management (__enter__)",
        )
        self.assertTrue(
            hasattr(self.connection, "__exit__"),
            "Connection should implement context management (__exit__)",
        )

        # Test actual context management behavior
        with Connection() as conn:
            socket_obj = conn.create_connection()
            self.assertIsInstance(socket_obj, socket.socket)
            # Store the socket file descriptor to check it later
            fd = socket_obj.fileno()

        # After exiting the context, the socket should be closed
        # Trying to use the socket should raise an error because it's closed
        with self.assertRaises(OSError):
            socket_obj.getsockname()


if __name__ == "__main__":
    unittest.main()
