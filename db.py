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
       

    def check_user_in_db(self, username: str) -> bool:
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return True
        return False
 
 
    def get_user_password(self, username: str) -> str:
        existing_db = self.open_db()

        for user in existing_db["users"]:
            if user["Username"] == username:
                return user["Password"]
       
    
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


    def modify_db(self, username: str, field: str, value: str) -> bool:
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
            
            
            
class DbHelper:
    def __init__(self):
        self.db = Database()
        
        
    def get_msg_from_inbox(self, login):
        return self.db.read_msg_from_inbox(login)
        
        
    def check_if_registered(self, login):
        if self.db.check_user_in_db(login):
            return True
        return False


    def register_new_user(self, login, password):
        self.db.add_user_to_db(login, password)


    def get_stored_password(self, login):
        return self.db.get_user_password(login)


    def add_account_type(self, text):
        return self.db.modify_db(text["login"], "Account type", text["acc_type"])

    
    def add_msg_to_db(self, receiver, sender, message):
        return self.db.add_msg_to_db(receiver, sender, message)


    def check_recv_inbox(self, login):
        inbox_size = self.db.check_user_inbox(login)
        if inbox_size < 5:
            return True
        return False