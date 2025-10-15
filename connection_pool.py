"""Connection Pool module for concurrent connections to database

This module provides a connection pool, which:
- allocated 5 open connections to databaseat the start;
- if necessary, opens and closes additional ones, as per demand (limited to 100 active connections at once);
- regularly checking if there are unused connections which can be closed;
"""

import sqlite3
import time
from config import config
import threading


class ConnectionPool:

    DB_FILE = config.database.DB_FILE
    DB_USER = config.database.DB_USER
    DB_PASSWORD = config.database.DB_PASSWORD
    DB_PORT = config.database.DB_PORT

    def __init__(self):
        """Create connection pool and prepare for operations"""
        self.lock = threading.Lock()
        self.min_connections = 5
        self.max_connections = 100
        self.semaphore = threading.Semaphore(value=self.max_connections)
        self.cleanup_interval = 10
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

        db_connection = sqlite3.connect(self.DB_FILE, check_same_thread=False)
        db_cursor = db_connection.cursor()

        db_cursor.execute("PRAGMA foreign_keys = ON;")

        return db_connection, db_cursor

    def get_connection(self):
        """Sharing allocated connections with database peration methods"""
        # If pool is empty, create a new connection directly
        self.semaphore.acquire()
        try:
            with self.lock:
                available_slots = self.max_connections - self.used_connection
                if len(self.open_connections) == 0:
                    if available_slots > 0:
                        connections_to_create = min(5, available_slots)
                        self.allocate_db_connections(connections_to_create)
                    else:
                        self.semaphore.release()
                        raise Exception("Maximum number of database connections reached")

                connection_tuple = self.open_connections[0]
                self.open_connections.pop(0)
                self.used_connection += 1
                return connection_tuple[0], connection_tuple[1]
        except Exception as e:
            self.semaphore.release()
            print(f"[ERROR] Exception: {e}")
            raise e

    def return_connection(self, db_conn, db_cursor):
        with self.lock:
            if (db_conn, db_cursor) not in self.open_connections:
                self.open_connections.append((db_conn, db_cursor))
                self.used_connection -= 1
            self.semaphore.release()

    def close_all_connections(self):
        """Closing all connections inside the pool"""
        for conn, cursor in self.open_connections:
            cursor.close()
            conn.close()
        self.open_connections.clear()

    def check_for_cleanup(self):
        """Checking if it's time for connection cleanup"""
        current_time = time.time()
        if current_time - self.last_cleanup_time > self.cleanup_interval:
            # print("Connections cleanup")
            self.close_extra_connections()
            self.last_cleanup_time = time.time()

    def close_extra_connections(self):
        """Close all unused extra connections over the starting 5"""
        print(f"Number of available connections BEFORE cleanup: {len(self.open_connections)}")
        with self.lock:
            while len(self.open_connections) > self.min_connections:
                conn, cursor = self.open_connections.pop()
                cursor.close()
                conn.close()
        print(f"Number of available connections AFTER cleanup: {len(self.open_connections)}")

    def close_failing_connection(self, db_conn, db_cursor):
        """Close connection in case of error/exception and create new one"""
        try:
            if db_cursor:
                db_cursor.close()
        except:
            pass

        try:
            if db_conn:
                db_conn.close()
        except:
            pass

        with self.lock:
            self.used_connection -= 1
            self.semaphore.release()
