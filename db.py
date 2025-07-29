"""Database module for user management and message storage.

This module provides classes for managing user data and messages in a JSON file-based
database system. It handles user authentication, message storage, and data persistence.
"""

import json 
import os 

class Database:
    """Low-level database operations for JSON file storage.
    
    Handles direct file operations, user management, and message storage
    in a JSON-based database system.
    """
    
    DB_FILE = "db.json"

    def __init__(self):
        """Initialize database and create empty database file if it doesn't exist."""
        if not os.path.exists("db.json"):
            print("DB not exsiting, creating new")
            empty_data = {"users": []}
            with open(self.DB_FILE, "w") as db:
                json.dump(empty_data, db, indent=4)
      

    def check_user_in_db(self, username: str) -> bool:
        """Check if a user exists in the database.
        
        Args:
            username: The username to check for existence.
            
        Returns:
            True if user exists, False otherwise.
        """
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return True
        return False
 
 
    def get_user_password(self, username: str) -> str:
        """Retrieve the stored password for a given username.
        
        Args:
            username: The username to get the password for.
            
        Returns:
            The stored password hash for the user.
        """
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return user["Password"]
   
    
    def add_user_to_db(self, login, password, type=None):
        """Add a new user to the database.
        
        Args:
            login: The username for the new user.
            password: The password (should be hashed) for the new user.
            type: Optional account type (admin/user).
            
        Returns:
            True if user was successfully added.
        """
        new_user = {
            "Username": login,
            "Password": password,
            "Account type": type,
            "Inbox": [],
        }

        existing_db = self.open_db()
        existing_db["users"].append(new_user)
        self.dump_db(existing_db)

        return True


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
        try:
            existing_db = self.open_db()

            for user in existing_db["users"]:
                if user["Username"] == username:
                    user[field] = value

            self.dump_db(existing_db)
            return True
        except KeyError:
            print(f"KeyError: {field} not found in user data.")
            return False


    def add_msg_to_db(self, username, sender, message) -> bool:
        """Add a message to a user's inbox.
        
        Args:
            username: The recipient's username.
            sender: The sender's username.
            message: The message content.
            
        Returns:
            True if message was successfully added, False otherwise.
        """
        try:
            existing_db = self.open_db()

            message = {
                "Sender": sender,
                "Message": message,
            }

            for user in existing_db["users"]:
                if user["Username"] == username:
                    user["Inbox"].append(message)

            self.dump_db(existing_db)
            return True
        except KeyError:
            print(f"KeyError: {username} not found in user data.")
            return False


    def read_msg_from_inbox(self, username) -> tuple[str, str]:
        """Read and remove the first message from a user's inbox.
        
        Args:
            username: The username whose inbox to read from.
            
        Returns:
            A tuple containing (sender, message) or (username, "EMPTY") if no messages.
        """
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if self.check_user_inbox(username) > 0:
                if user["Username"] == username:
                    message = user["Inbox"][0]
                    user["Inbox"].pop(0)
                    self.dump_db(existing_db)
                    return message["Sender"], message["Message"]
            else:
                return username, "EMPTY"


    def check_user_inbox(self, username) -> int:
        """Check the number of messages in a user's inbox.
        
        Args:
            username: The username to check.
            
        Returns:
            The number of messages in the user's inbox.
        """
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return len(user["Inbox"])
        

    def open_db(self):
        """Open and load the database from the JSON file.
        
        Returns:
            The loaded database dictionary.
        """
        with open(self.DB_FILE, "r") as db:
            opened_db = json.load(db)
        return opened_db


    def dump_db(self, existing_db):
        """Save the database dictionary to the JSON file.
        
        Args:
            existing_db: The database dictionary to save.
        """
        with open(self.DB_FILE, "w") as db:
            json.dump(existing_db, db, indent=4)
            
            
            
class DbHelper:
    """High-level database helper providing simplified database operations.
    
    Acts as a facade for the Database class, providing more convenient
    methods for common database operations.
    """
    
    def __init__(self):
        self.db = Database()
        
        
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
            The stored password hash.
        """
        return self.db.get_user_password(login)


    def add_account_type(self, text):
        """Add or update the account type for a user.
        
        Args:
            text: Dictionary containing login and acc_type fields.
            
        Returns:
            True if account type was successfully updated.
        """
        return self.db.modify_db(text["login"], "Account type", text["acc_type"])

    
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
        if inbox_size < 5:
            return True
        return False