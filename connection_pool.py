"""Connection Pool module for concurrent connections to database

This module provides a connection pool, which:
- allocated 5 open connections to databaseat the start;
- if necessary, opens and closes additional ones, as per demand (limited to 100 active connections at once);
- regularly checking if there are unused connections which can be closed;
"""

import psycopg2
import time
from config import config

class ConnectionPool:


    DB_FILE = config.database.DB_FILE
    DB_USER = config.database.DB_USER
    DB_PASSWORD = config.database.DB_PASSWORD
    DB_PORT = config.database.DB_PORT


    def __init__(self):
        """Create connection pool and prepare for operations"""
        self.min_connections = 5
        self.max_connections = 100
        self.clenup_interval = 60
        self.open_connections = []
        self.used_connection = 0
        self.last_cleanup_time = time.time()
        self.allocate_db_connections(self.min_connections)


    def allocate_db_connections(self, no_of_connections):
        """Allocate X database connections at the start"""
        for _ in range(no_of_connections):
            db_connection, db_cursor = self.create_new_connection()
            self.open_connections.append((db_connection, db_cursor))


    def create_new_connection(self):
        """Creating new connection if required"""
        db_connection = psycopg2.connect(host="localhost", dbname = self.DB_FILE, user=self.DB_USER, password=self.DB_PASSWORD, port=self.DB_PORT)
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor


    def get_connection(self):
        """Sharing allocated connections with database peration methods"""      
        # If pool is empty, create a new connection directly
        if len(self.open_connections) == 0:
            if self.used_connection < self.max_connections:
                self.allocate_db_connections(5)
                # return self.create_new_connection()
            else:
                raise Exception("Maximum number of database connections reached")

        connection_tuple = self.open_connections[0]
        self.open_connections.pop(0)
        self.used_connection += 1
        # print(f"Connections remaining in pool: {len(self.open_connections)}")
        return connection_tuple[0], connection_tuple[1]


    def return_connection(self, db_conn, db_cursor):
        if (db_conn, db_cursor) not in self.open_connections:
            self.open_connections.append((db_conn, db_cursor))
            self.used_connection -= 1
        self.close_extra_connections()


    def close_all_connections(self):
        """Closing all connections inside the pool"""
        for conn, cursor in self.open_connections:
            cursor.close()
            conn.close()
        self.open_connections.clear()
       

    def check_for_cleanup(self):
        """Checking if it's time for connection cleanup"""
        current_time = time.time()
        if self.start_time - current_time > self.clenup_interval:
            self.close_extra_connections()
            self.last_cleanup_time = time.time()


    def close_extra_connections(self):
        """Close all unused extra connections over the starting 5"""
        while len(self.open_connections) > self.min_connections:
            conn, cursor = self.open_connections.pop()
            cursor.close()
            conn.close()


    def close_failing_connection(self):
        """Close connection in case of error/exception and create new one"""



