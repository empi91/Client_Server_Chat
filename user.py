# user.py

from connection import Connection
from database import Database

class User:

    def __init__(self):
        self.username = ""
        self.password = ""
        self.type = None
        self.is_user_login = False
        self.database = Database()
        pass

    def check_if_registered(self, username):
        if self.database.execute_query(self.database.QUERY_DICT["CHECK_IF_REGISTERED"], (username,)):
            return True
        return False

    def check_password(self, username, password):
        if self.database.execute_query(self.database.QUERY_DICT["CHECK_PASSWORD"], (username, password)):
            return True
        return False

    def register_user(self, user_data):
        try:
            user_data["inbox"] = []

            if self.database.execute_query(self.database.QUERY_DICT["REGISTER_USER"], (user_data["username"], user_data["password"], user_data["acc_type"])):
                print(f"User {user_data['username']} registered")
                return "ack", "Registration successful"
            else:
                return "error", "User with this username already exists"
        except TypeError as e:
            print(f"Error: {e}")

    def login_user(self, socket):
        connection = Connection(socket)
        while not self.is_user_login:
            self.username = input("Enter username: ")
            self.password = input("Enter password: ")

            credentials = {
                "username": self.username,
                "password": self.password
            }

            connection.send_data("login", credentials)
            query_header, query_message = connection.receive_data()
            if query_header == "ack":
                self.is_user_login = True
                print(query_message)
                return True
            elif query_header == "add_account_type":
                while not self.type:
                    acc_type = input("Enter account type (admin/user): ")
                    if acc_type == "admin" or acc_type == "user":
                        self.type = acc_type
                        credentials["acc_type"] = self.type
                    else:
                        print("Each user can be either admin or user, try again")
                connection.send_data("account_type", credentials)
                self.is_user_login = True
            else:
                print(query_message)
        return 0

    def check_acc_type(self, username):
        return self.database.execute_query(self.database.QUERY_DICT["CHECK_ACCOUNT_TYPE"], (username, "admin"))

    def delete_user(self, calling_user, removed_user):
        if self.check_if_registered(removed_user):
            if self.check_acc_type(calling_user):
                if self.database.execute_query(self.database.QUERY_DICT["DELETE_USER"], (removed_user,)):
                    return "ack", "user_deleted"
                return "error", "Error while deleting user"
            return "error", f"User {calling_user} cannot delete other users"
        return "error", f"User {removed_user} is not registered in database"
