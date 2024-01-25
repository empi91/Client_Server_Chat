# database.py

import pathlib
import os
import json

PATH = pathlib.Path.cwd() / "data.json"

class Database:

    def __init__(self):
        self.database = {}
        self.load_database()
        pass

    def load_database(self):
        try:
            if os.path.getsize(PATH) == 0:
                self.database = {}
            else:
                with PATH.open(mode="r", encoding="utf-8") as file:
                    self.database = json.load(file)
        except FileNotFoundError:
            self.database = {}
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Problematic JSON text:")
            print(e.doc)

    def add_to_database(self, username, user_data):
        self.database[username] = user_data
        self.save_database()

    def save_database(self):
        with PATH.open(mode="w", encoding="utf-8") as file:
            json.dump(self.database, file, indent=2)
        self.load_database()

    def remove_from_database(self, removed_user):
        del self.database[removed_user]
        self.save_database()
        pass