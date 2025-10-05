"""Connection Pool module for concurrent connections to database

This module provides a connection pool, which:
- allocated 5 open connections to databaseat the start;
- if necessary, opens and closes additional ones, as per demand (limited to 100 active connections at once);
- regularly checking if there are unused connections which can be closed;
"""

import psycopg2
from config import config

class ConnectionPool:

    open_connections = []
    used_connection = []
    DB_FILE = config.database.DB_FILE
    DB_USER = config.database.DB_USER
    DB_PASSWORD = config.database.DB_PASSWORD
    DB_PORT = config.database.DB_PORT


    def __init__(self):
        """Create connection pool and prepare for operations"""
        self.allocate_db_connections(10)


    def allocate_db_connections(self, no_of_connections):
        """Allocate 10 database connections at the start"""
        for _ in range(no_of_connections):
            db_connection, db_cursor = self.create_new_connection()
            self.open_connections.append((db_connection, db_cursor))


    def create_new_connection(self):
        """Creating new connection if required"""
        db_connection = psycopg2.connect(host="localhost", dbname = self.DB_FILE, user=self.DB_USER, password=self.DB_PASSWORD, port=self.DB_PORT)
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor


    def share_connection(self):
        """Sharing allocated connections with database peration methods"""
        if len(self.open_connections) > 0:
            connection_tuple = self.open_connections[0]
            self.open_connections.pop(0)
            self.used_connection.append(connection_tuple)
            print(f"Connections remaining in pool: {len(self.open_connections)}")
            return connection_tuple[0], connection_tuple[1]
        else:
            raise Exception("0 remaining connections in connection pool!")



    def check_connections_number(self):
        """Checking if conections limit is reached"""
        


    def close_extra_connections(self):
        """Close all unused extra connections over the starting 10"""


    def close_failing_connection(self):
        """Close connection in case of error/exception and create new one"""



