# db.py

import json 
import os 

class Database:

    def __init__(self):
        if not os.path.exists("db.json"):
            print("DB not exsiting, creating new")
            empty_data = {"users": []}
            with open("db.json", "w") as db:
                json.dump(empty_data, db, indent=4)
        else:
            print("DB already exists")


    def check_in_db(self, username, password):
        with open("db.json", "r") as db:
            existing_db = json.load(db)

        for user in existing_db["users"]:
            if user["Username"] == username:
                return True
        return False


    def check_login(self, username, password):
        with open("db.json", "r") as db:
            existing_db = json.load(db)   

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

        with open("db.json", "r") as db:
            existing_db = json.load(db)
        
        existing_db["users"].append(new_user)

        with open("db.json", "w") as db:
            json.dump(existing_db, db, indent=4)

        return True



    def remove_from_db(self):


        pass


    def modify_db(self):


        pass
