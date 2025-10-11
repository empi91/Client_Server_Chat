"""Connection module for socket communication setup.

This module provides the Connection class that manages socket creation
and configuration for both client and server connections.
"""

import socket


class Connection:
    """Manages socket connections for client-server communication.

    Provides methods to create and configure socket connections
    with appropriate settings for both client and server modes.
    """

    def __init__(self):
        self.socket = None

    def create_connection(self, is_server=False):
        """Create and configure a socket connection.

        Args:
            is_server: Whether this connection is for server mode.
                      If True, enables socket reuse for server binding.

        Returns:
            Configured socket object ready for use.

        Raises:
            Prints socket error message if connection creation fails.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if is_server:
                self.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return self.socket
        except socket.error as s:
            print(f"[SOCKET ERROR]: {s}")
            return None

    def close(self):
        """Close the socket connection if it exists."""
        if self.socket:
            self.socket.close()
            self.socket = None

    def __enter__(self):
        """Enter context manager method for use with 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager method that ensures socket is closed."""
        self.close()
