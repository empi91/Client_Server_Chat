# db.py

import json 
import os 

class Database:
    DB_FILE = "db.json"

    def __init__(self):
        if not os.path.exists("db.json"):
            print("DB not exsiting, creating new")
            empty_data = {"users": []}
            with open(self.DB_FILE, "w") as db:
                json.dump(empty_data, db, indent=4)
       

    def check_user_in_db(self, username):
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return True
        return False
 
 
    def check_login(self, username, password):
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                if user["Password"] == password:
                    return True
                else:
                    return False
       
    
    def add_user_to_db(self, login, password, type=None):
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


    def modify_db(self, username, field, value):
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


    def add_msg_to_db(self, username, sender, message):
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


    def read_msg_from_inbox(self, username):
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


    def check_user_inbox(self, username):
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return len(user["Inbox"])
        

    def open_db(self):
        with open(self.DB_FILE, "r") as db:
            opened_db = json.load(db)
        return opened_db


    def dump_db(self, existing_db):
        with open(self.DB_FILE, "w") as db:
            json.dump(existing_db, db, indent=4)