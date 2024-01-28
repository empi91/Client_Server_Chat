import unittest
import database
import pathlib
from unittest.mock import patch

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

    # Test load_database() method
    def test_loading_database_from_json_file(self):
        """
        Testing if loading database does not return any unexpected errors
        """
        self.assertIsNone(self.database.load_database())

    # Test add_to_database() method
    def test_adding_new_user_to_database(self):
        """
        Testing adding new user to database
        Testing if adding new user does not return any unexpected errors
        """
        self.database.load_database()
        length_before = len(self.database.database)
        self.database.add_to_database("test_user1", self.user_data)

        self.assertEqual(len(self.database.database), length_before + 1)
        self.assertIsNone(self.database.add_to_database("test_user2", self.user_data))

    # Test remove_from_database() method
    def test_removing_user_from_database(self):
        """
        Testing removing user from database
        Testing if removing user does not return any unexpected errors
        """
        self.database.load_database()
        length_before = len(self.database.database)
        self.database.remove_from_database("test_user1")
        self.assertEqual(len(self.database.database), length_before - 1)
        self.assertIsNone(self.database.remove_from_database("test_user2"))

if __name__ == '__main__':
    unittest.main()