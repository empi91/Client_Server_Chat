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
    
    #TODO Add reading those parameters from config file
    host = '127.0.0.1'
    port = 65432

    def __init__(self):
        self.socket = None
        print(f"Host: {self.host}, Port: {self.port}")
        

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
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return self.socket
        except socket.error as s:
            print(f"[SOCKET ERROR]: {s}")






