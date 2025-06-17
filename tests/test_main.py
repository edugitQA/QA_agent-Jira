import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import QAAgent
import unittest
from unittest.mock import MagicMock

class TestQAAgent(unittest.TestCase):

    def setUp(self):
        self.agent = QAAgent()
        self.agent.db_manager = MagicMock()
        self.agent.openai_client = MagicMock()

    def test_prevent_duplicate_test_case_generation(self):
        # Mock a user story
        story = {
            'key': 'STORY-123',
            'title': 'Test Story',
            'description': 'This is a test story description.',
            'status': 'To Do'
        }

        # Mock the database manager to return existing test cases
        self.agent.db_manager.get_test_cases_for_story.return_value = [{'id': 1, 'content': 'Existing test case'}]

        # Call process_user_story
        result = self.agent.process_user_story(story)

        # Assert that no new test cases are generated
        self.agent.openai_client.generate_test_cases.assert_not_called()
        self.agent.db_manager.save_test_cases.assert_not_called()
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
