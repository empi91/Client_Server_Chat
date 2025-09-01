""" Test suite for Connection.py class"""

import unittest
from connection import Connection
from config import config


class TestConnection(unittest.TestCase):
    """ Test suite for Connection class """

    def setUp(self):
        """Setting up for testing Connection methods"""


        pass


    def test_sockeet_creation(self):
        """Test successful socket creation for both client and server modes with proper socket options."""


        pass


    def test_socket_creation_failure(self):
        """ Test error handling when socket creation fails due to system limitations or permissions."""


        pass


    def test_server_socket_reuse(self):
        """Test that SO_REUSEADDR is properly set for server sockets to allow quick restart."""


        pass


    def test_connection_context_management(self):
        """Test that sockets are properly closed when using the connection as a context manager."""


        pass


if __name__ == '__main__':
    unittest.main()