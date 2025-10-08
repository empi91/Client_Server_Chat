"""Database module for user management and message storage.

This module provides classes for managing user data and messages in a JSON file-based
database system. It handles user authentication, message storage, and data persistence.
"""

import json 
import os 
import psycopg2
from config import config
from connection_pool import ConnectionPool

class Database:
    """Low-level database operations for JSON file storage.
    
    Handles direct file operations, user management, and message storage
    in a JSON-based database system.
    """
    
    DB_FILE = config.database.DB_FILE
    DB_USER = config.database.DB_USER
    DB_PASSWORD = config.database.DB_PASSWORD
    DB_PORT = config.database.DB_PORT
    CONNECTION_POOL = None
    _instance = None

    @classmethod
    def get_instance(cls):
        """Utilizing Singelton pattern, to ensure a single databse is used across entire project"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    

    def __init__(self):
        """Connect to exisitng PostgreSQL database or create new one"""

        self.initialize_db()
        self.CONNECTION_POOL = ConnectionPool()
        self.create_db_tables()


    def initialize_db(self):
        try:
            conn = psycopg2.connect(host="localhost", dbname = "postgres", user=self.DB_USER, password=self.DB_PASSWORD, port=self.DB_PORT)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (self.DB_FILE,))
            db_exists = cursor.fetchone()

            if not db_exists:
                cursor.execute(f"CREATE DATABASE {self.DB_FILE}")
                print(f"New database {self.DB_FILE} created")
        except Exception as e: 
            print(f"Error initializing databse: {e}")
        finally:
            if conn:
                conn.close


    def create_db_tables(self):
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(config.database.CREATE_USER_TABLE_QUERY)
            db_connection.commit()
            db_cursor.execute(config.database.CREATE_MESSAGE_TABLE_QUERY)
            db_connection.commit()
        except Exception as e: 
            print(f"Error initializing databse: {e}")
        finally:
            self.close_db(db_connection, db_cursor)
      

    def check_user_in_db(self, username: str) -> bool:
        """Check if a user exists in the database.
        
        Args:
            username: The username to check for existence.
            
        Returns:
            True if user exists, False otherwise.
        """
        try:
            check_user_query = '''SELECT username FROM users WHERE username = %s;'''
            check_user_values = (username,)
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(check_user_query, (check_user_values,))
            db_connection.commit()
            exisitng_username = db_cursor.fetchone()
            if exisitng_username:
                if exisitng_username[0] == username:
                    self.close_db(db_connection, db_cursor)
                    return True
            self.close_db(db_connection, db_cursor)
            return False
        except Exception as e: 
            print(f"Error initializing databse: {e}")
        finally:
            self.close_db(db_connection, db_cursor)
 
 
    def get_user_password(self, username: str) -> str:
        """Retrieve the stored password for a given username.
        
        Args:
            username: The username to get the password for.
            
        Returns:
            The stored password hash for the user.
        """
        get_password_query = """SELECT password FROM users WHERE username = %s;"""
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(get_password_query, (username,))
            db_connection.commit()
            return db_cursor.fetchone()[0]
        except:
            return False
        finally:
            self.close_db(db_connection, db_cursor)
   
    
    def add_user_to_db(self, login, password, type=None):
        """Add a new user to the database.
        
        Args:
            login: The username for the new user.
            password: The password (should be hashed) for the new user.
            type: Optional account type (admin/user).
            
        Returns:
            True if user was successfully added.
        """
        add_user_query = '''INSERT INTO users (username, password, account_type) VALUES (%s,%s,%s);'''
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(add_user_query, (login, password, "user",))
            db_connection.commit()
            return True
        except:
            return False
        finally:
            self.close_db(db_connection, db_cursor)


    def remove_user_from_db(self):


        pass


    def modify_db(self, username: str, field: str, value: str) -> bool:
        """Modify a specific field for a user in the database.
        
        Args:
            username: The username of the user to modify.
            field: The field name to update.
            value: The new value for the field.
            
        Returns:
            True if modification was successful, False otherwise.
        """
        allowed_fields = ['password', 'account_type', 'email']  # Add your valid fields
        if field not in allowed_fields:
            raise ValueError(f"Invalid field name: {field}")
        
        update_data_query = f"UPDATE users SET {field} = %s WHERE username = %s;"

        
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(update_data_query, (value, username))
            
            rows_affected = db_cursor.rowcount
            
            if rows_affected == 0:
                db_connection.rollback()
                raise ValueError(f"User '{username}' not found in database")
            
            db_connection.commit()
            return True
                        
        except Exception as e:
            if db_connection:
                db_connection.rollback()
            raise Exception(f"Unexpected error during database modification: {e}")
            
        finally:
            self.close_db(db_connection, db_cursor)
            

    def add_msg_to_db(self, username, sender, message) -> bool:
        """Add a message to a user's inbox.
        
        Args:
            username: The recipient's username.
            sender: The sender's username.
            message: The message content.
            
        Returns:
            True if message was successfully added, False otherwise.
        """
        add_msg_query = """INSERT INTO messages (sender_id, receiver_id, content) 
                            VALUES (
                            (SELECT id from USERS WHERE username = %s),
                            (SELECT id from USERS WHERE username = %s),
                            %s
                            );"""
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(add_msg_query, (sender, username, message,))
            db_connection.commit()
            return True
        except Exception as e:
            if db_connection:
                db_connection.rollback()
            raise Exception(f"Unexpected error during database modification: {e}")
            
        finally:
            self.close_db(db_connection, db_cursor)


    def read_msg_from_inbox(self, username) -> list[str, str]:
        """Read and remove the first message from a user's inbox.
        
        Args:
            username: The username whose inbox to read from.
            
        Returns:
            A list containing al messages from inbox (sender, message) or (username, "EMPTY") if no messages.
        """
        read_msg_query = """SELECT sender_id, content, timestamp FROM messages WHERE receiver_id = (SELECT id from users WHERE username = %s);"""
        get_username_query = """SELECT username FROM users WHERE id = %s"""
        delete_read_msg_query = """DELETE FROM messages WHERE receiver_id = (SELECT id from users WHERE username = %s);"""
        messages = []
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(read_msg_query, (username,))
            db_connection.commit()
            raw_messages = db_cursor.fetchall()
            if self.check_user_inbox(username) != 0:
                for msg in raw_messages:
                    db_cursor.execute(get_username_query, (msg[0],))
                    sender = db_cursor.fetchone()
                    message = {
                        "Sender": sender[0],
                        "Text": msg[1],
                        "Datetime": msg[2],
                    }
                    messages.append(message)

                db_cursor.execute(delete_read_msg_query, (username,))
                db_connection.commit()
                return messages
            message = {
                "Sender": username,
                "Text": "EMPTY",
            }
            messages.append(message)
            return messages
        except Exception as e: 
            print(f"Error initializing databse: {e}")
        finally:
            self.close_db(db_connection, db_cursor)
    
 
    def check_user_inbox(self, username) -> int:
        """Check the number of messages in a user's inbox.
        
        Args:
            username: The username to check.
            
        Returns:
            The number of messages in the user's inbox.
        """
        check_user_inbox_query = """SELECT * FROM messages WHERE receiver_id = (SELECT id from users WHERE username = %s);"""
        try:
            db_connection, db_cursor = self.open_db()
            db_cursor.execute(check_user_inbox_query, (username,))
            db_connection.commit()
            no_of_messages = db_cursor.fetchall()
            return len(no_of_messages)
        except:
            raise KeyError(f"User {username} does not exist")
        finally:
            self.close_db(db_connection, db_cursor)


    def check_value(self, query, params=None):
        try:
            db_connection, db_cursor = self.open_db()
            if params:
                db_cursor.execute(query, params)
            else:
                db_cursor.execute(query)
            db_connection.commit()
            value = db_cursor.fetchall()
            return value
        except:
            raise KeyError(f"Invalid query")
        finally:
            self.close_db(db_connection, db_cursor)


    def open_db(self):
        """Open and load the database from the JSON file.
        
        Returns:
            The loaded database dictionary.
        """
        # db_connection = psycopg2.connect(host="localhost", dbname = self.DB_FILE, user=self.DB_USER, password=self.DB_PASSWORD, port=self.DB_PORT)
        # db_cursor = db_connection.cursor()
        # return db_connection, db_cursor

        return self.CONNECTION_POOL.get_connection()


    def close_db(self, connection, cursor):
        # if connection:
        #     cursor.close()
        #     connection.close()
        self.CONNECTION_POOL.return_connection(connection, cursor)
                       
            
class DbHelper:
    """High-level database helper providing simplified database operations.
    
    Acts as a facade for the Database class, providing more convenient
    methods for common database operations.
    """
    
    def __init__(self):
        self.db = Database.get_instance()
        
        
    def get_msg_from_inbox(self, login):
        """Get the next message from a user's inbox.
        
        Args:
            login: The username to get messages for.
            
        Returns:
            A tuple containing the sender and message content.
        """
        return self.db.read_msg_from_inbox(login)
        
        
    def check_if_registered(self, login):
        """Check if a user is registered in the system.
        
        Args:
            login: The username to check.
            
        Returns:
            True if user is registered, False otherwise.
        """
        if self.db.check_user_in_db(login):
            return True
        return False


    def register_new_user(self, login, password):
        """Register a new user in the system.
        
        Args:
            login: The username for the new user.
            password: The password for the new user (should be hashed).
        """
        self.db.add_user_to_db(login, password)


    def get_stored_password(self, login):
        """Get the stored password for a user.
        
        Args:
            login: The username to get the password for.
            
        Returns:
            The stored password hash or 'False' if user doesn't exist
        """
        return self.db.get_user_password(login)


    def add_account_type(self, text):
        """Add or update the account type for a user.
        
        Args:
            text: Dictionary containing login and acc_type fields.
            
        Returns:
            True if account type was successfully updated.
        """
        return self.db.modify_db(text["login"], "account_type", text["acc_type"])

    
    def add_msg_to_db(self, receiver, sender, message):
        """Add a message to a receiver's inbox.
        
        Args:
            receiver: The username of the message recipient.
            sender: The username of the message sender.
            message: The message content.
            
        Returns:
            True if message was successfully added.
        """
        return self.db.add_msg_to_db(receiver, sender, message)


    def check_recv_inbox(self, login):
        """Check if a user's inbox has space for new messages.
        
        Args:
            login: The username to check.
            
        Returns:
            True if inbox has less than 5 messages, False otherwise.
        """
        inbox_size = self.db.check_user_inbox(login)
        if inbox_size < config.database.MAX_INBOX_SIZE:
            return True
        return False