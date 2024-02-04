# database.py

import pathlib
from configparser import ConfigParser

import psycopg2
from psycopg2 import sql

PATH = pathlib.Path.cwd() / "data.json"


class Database:
    def __init__(self):
        self.init_file = "database/database.ini"
        self.config = {}

        self.load_config("postgresql")
        self.create_database("cs_db")
        self.load_config("client_server_db")
        self.create_tables()

    def load_config(self, section):
        parser = ConfigParser()
        parser.read(self.init_file)

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.config[param[0]] = param[1]
        else:
            raise Exception(f"Section {section} not found in the {self.init_file} file")

    def create_database(self, db_name):
        try:
            connection = psycopg2.connect(**self.config)
            connection.autocommit = True
            cursor = connection.cursor()

            query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            cursor.execute(query)

            cursor.close()
            connection.close()
        except psycopg2.errors.DuplicateDatabase as e:
            pass
        except (psycopg2.DatabaseError, Exception) as e:
            print(e)

    def create_tables(self):
        try:
            with psycopg2.connect(**self.config) as connection:
                with connection.cursor() as cursor:
                    queries = (
                               """
                               CREATE TABLE users (
                               user_id SERIAL PRIMARY KEY,
                               username VARCHAR(50) UNIQUE NOT NULL,
                               password VARCHAR(50) NOT NULL,
                               account_type VARCHAR(10) NOT NULL
                               )
                               """,
                               """
                               CREATE TABLE messages (
                               message_id SERIAL PRIMARY KEY,
                               receiver_id INT NOT NULL REFERENCES users(user_id),
                               sender INT NOT NULL REFERENCES users(user_id),
                               message VARCHAR(255)
                               )
                               """)

                    for query in queries:
                        cursor.execute(query)

        except psycopg2.errors.DuplicateTable:
            pass
        except (psycopg2.DatabaseError, Exception) as e:
            print(e)

    def execute_query(self, query, parameters):
        try:
            with psycopg2.connect(**self.config) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, parameters)
                    rows = cursor.fetchall()
                    if rows:
                        return rows
                    else:
                        return False
        except (psycopg2.DatabaseError, Exception) as e:
            print(e)
            return False

db = Database()
credentials = {
        "username": "Kaja",
        "password": "kajak",
        "acc_type": "user"
            }
# db.add_to_database(credentials)
# db.check_user_registered("Kaja")
# db.check_user_password("Kaja", "kajak")
# db.load_config()
# db.load_database()
# db.create_database()
# db.remove_from_database("Agata")
