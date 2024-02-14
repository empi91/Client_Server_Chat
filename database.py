# database.py

import pathlib
import sys
import os
from configparser import ConfigParser

import psycopg2
from psycopg2 import sql

PATH = pathlib.Path.cwd() / "data.json"

class Database:
    QUERY_DICT = {
        "CHECK_INBOX": """SELECT count(*) 
                            FROM messages 
                            INNER JOIN users ON messages.receiver_id = users.user_id 
                            WHERE users.username = %s;""",
        "READ_INBOX": """SELECT messages.message, sender.username as sender_username, messages.message_id
                            FROM messages 
                            INNER JOIN users AS receiver ON messages.receiver_id = receiver.user_id 
                            INNER JOIN users AS sender ON messages.sender = sender.user_id 
                            WHERE receiver.username = %s 
                            LIMIT 1;""",
        "DELETE_MESSAGE": """DELETE FROM messages 
                            WHERE message_id = %s 
                            RETURNING message_id;""",
        "ADD_MESSAGE_TO_INBOX": """INSERT INTO messages (receiver_id, sender, message)
                            SELECT receiver.user_id, sender.user_id, %s
                            FROM users AS receiver, users AS sender
                            WHERE receiver.username = %s AND sender.username = %s
                            RETURNING message_id;""",
        "CHECK_IF_REGISTERED": """SELECT user_id 
                            FROM users 
                            WHERE username = %s;""",
        "CHECK_PASSWORD": """SELECT user_id 
                            FROM users 
                            WHERE username = %s AND password = %s;""",
        "REGISTER_USER": """INSERT INTO users(username, password, account_type)
                            VALUES(%s, %s, %s) 
                            RETURNING user_id;""",
        "CHECK_ACCOUNT_TYPE": """SELECT user_id 
                            FROM users 
                            WHERE username = %s AND account_type = %s;""",
        "DELETE_USER": """DELETE FROM users 
                            WHERE username = %s 
                            RETURNING user_id;""",
    }
    def __init__(self):
        self.init_file = os.path.dirname(os.path.abspath(__file__)) + "/database/database.ini"
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

    def drop_database(self, db_name):
        try:
            connection = psycopg2.connect(**self.config)
            connection.autocommit = True
            cursor = connection.cursor()

            query = sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name))
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

if __name__ == '__main__':
    pass

