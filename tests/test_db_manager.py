import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from db_manager import DBManager
import unittest

class TestDBManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DBManager()
        self.db_manager.connect()
        self.db_manager.cursor.execute("DELETE FROM test_cases")
        self.db_manager.conn.commit()

    def tearDown(self):
        self.db_manager.connect()
        self.db_manager.cursor.execute("DELETE FROM test_cases")
        self.db_manager.conn.commit()
        self.db_manager._disconnect()

    def test_save_test_cases_no_duplicates(self):
        user_story_id = 1
        content = "Test case content"

        # Save the first test case
        test_case_id_1 = self.db_manager.save_test_cases(user_story_id, content)
        self.assertIsNotNone(test_case_id_1)

        # Attempt to save a duplicate test case
        test_case_id_2 = self.db_manager.save_test_cases(user_story_id, content)
        self.assertEqual(test_case_id_1, test_case_id_2)

    def test_save_test_cases_new_content(self):
        user_story_id = 1
        content_1 = "Test case content 1"
        content_2 = "Test case content 2"

        # Save the first test case
        test_case_id_1 = self.db_manager.save_test_cases(user_story_id, content_1)
        self.assertIsNotNone(test_case_id_1)

        # Save a new test case with different content
        test_case_id_2 = self.db_manager.save_test_cases(user_story_id, content_2)
        self.assertNotEqual(test_case_id_1, test_case_id_2)

if __name__ == "__main__":
    unittest.main()
