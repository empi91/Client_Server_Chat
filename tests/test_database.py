import os
import pathlib
import sys
import unittest

import psycopg2.errors

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

from database import Database

class TestDatabase(unittest.TestCase):

    #setUp()
    def setUp(self):
        path = pathlib.Path.cwd() / "test_db.json"
        database.PATH = path
        self.database = Database()
        self.user_data = {
            "username": "test_user",
            "password": "test_password",
            "acc_type": "user",
            "inbox": []
        }

    # Test create_database() method
    def test_creating_database(self):
        """
        Testing if database is created properly during creation inti
        """
        query = """SELECT datname FROM pg_database WHERE datname = %s"""
        self.assertTrue(self.database.execute_query(query, ("cs_db",)))

    # Test create_table() method
    def test_created_db_tables(self):
        """
        Testing if tables are created properly inside the database
        :return:
        """
        query = """SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'"""
        table_names = ["users", "messages"]
        tables = self.database.execute_query(query, ())
        for table, table_name in zip(tables, table_names):
            self.assertEqual(table[0], table_name)


if __name__ == '__main__':
    unittest.main()