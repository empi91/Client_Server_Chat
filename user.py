# user.py

from connection import Connection
from database import Database

class User:

    def __init__(self):
        self.username = ""
        self.password = ""
        self.type = None
        self.user_login = False
        pass

    def check_if_registered(self, username):
        database = Database()
        for user in database.database:
          if username == user:
                return True
        return False

    def check_password(self, username, password):
        database = Database()
        if database.database[username]["password"] == password:
            return True
        return False

    def register_user(self, user_data):
        try:
            user_data["inbox"] = []
            database = Database()
            database.add_to_database(user_data["username"], user_data)
            print(f"User {user_data['username']} registered")
            return "ack", "Registration successful"
        except TypeError as e:
            print(f"Error: {e}")

    def login_user(self, socket):
        connection = Connection(socket)
        while not self.user_login:
            self.username = input("Enter username: ")
            self.password = input("Enter password: ")

            credentials = {
                "username": self.username,
                "password": self.password
            }

            connection.send_data("login", credentials)
            query_header, query_message = connection.receive_data()
            if query_header == "ack":
                self.user_login = True
                print(query_message)
            elif query_header == "add_account_type":
                self.type = input("Enter account type (admin/user): ")
                credentials["acc_type"] = self.type
                connection.send_data("account_type", credentials)
                self.user_login = True
            else:
                print(query_message)
        return 0

    def delete_user(self, calling_user, removed_user):
        database = Database()
        if self.check_if_registered(removed_user):
            if database.database[calling_user]["acc_type"] == "admin":
                database.remove_from_database(removed_user)
                return "ack", "user_deleted"
            return "error", f"User {calling_user} cannot delete other users"
        return "error", f"User {removed_user} is not registered in database"