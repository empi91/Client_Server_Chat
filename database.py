# database.py

import pathlib
import os
import json
import psycopg2

from psycopg2 import sql
from configparser import ConfigParser

PATH = pathlib.Path.cwd() / "data.json"


class Database:
    def __init__(self):
        self.database = {}
        # self.load_database()
        self.init_file = "database/database.ini"
        self.config = {}
        self.load_config()

    def load_config(self):
        section = "postgresql"
        parser = ConfigParser()
        parser.read(self.init_file)

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.config[param[0]] = param[1]
        else:
            raise Exception(f"Section {section} not found in the {self.init_file} file")

    def load_database(self):
        # try:
        #     if os.path.getsize(PATH) == 0:
        #         self.database = {}
        #     else:
        #         with PATH.open(mode="r", encoding="utf-8") as file:
        #             self.database = json.load(file)
        # except FileNotFoundError:
        #     self.database = {}
        # except json.decoder.JSONDecodeError as e:
        #     print(f"Error decoding JSON: {e}")
        #     print("Problematic JSON text:")
        #     print(e.doc)
        try:
            print(self.config)
            connection = psycopg2.connect(**self.config)
            connection.autocommit = True
            cursor = connection.cursor()

            query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier("client_server_db"))
            cursor.execute(query)

        except psycopg2.errors.DuplicateDatabase as e:
            print(e)
        except (psycopg2.DatabaseError, Exception) as e:
            print(e)



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

    # if __name__ == '__main__':

db = Database()
# db.load_config()
db.load_database()