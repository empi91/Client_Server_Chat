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


    def open_db(self):
        with open(self.DB_FILE, "r") as db:
            opened_db = json.load(db)
        return opened_db


    def dump_db(self, existing_db):
        with open(self.DB_FILE, "w") as db:
            json.dump(existing_db, db, indent=4)
        


    def check_in_db(self, username, password):
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
       
    
    def add_to_db(self, login, password, type=None):
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



    def remove_from_db(self):


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

        
