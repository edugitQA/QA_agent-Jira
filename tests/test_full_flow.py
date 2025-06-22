import unittest
from unittest.mock import patch, MagicMock
import time
from src.main import QAAgent

class TestQAIntegrationFlow(unittest.TestCase):
    @patch('src.jira_client.JiraClient')
    @patch('src.openai_client.OpenAIClient')
    @patch('src.db_manager.DBManager')
    def test_full_flow(self, MockDBManager, MockOpenAIClient, MockJiraClient):
        # Mock Jira
        mock_jira = MockJiraClient.return_value
        mock_jira.get_user_stories.return_value = [
            {'key': 'KCA-1', 'title': 'US Teste', 'description': 'Desc', 'status': 'To Do'}
        ]
        mock_jira.create_subtask.return_value = MagicMock(key='KCA-2')
        # Mock OpenAI
        mock_openai = MockOpenAIClient.return_value
        mock_openai.generate_test_cases.return_value = """
Cenário: Sucesso\nDado que...\nQuando...\nEntão...\nCenário: Falha\nDado que...\nQuando...\nEntão..."""
        # Mock DB
        mock_db = MockDBManager.return_value
        mock_db.save_user_story.return_value = 1
        mock_db.get_test_cases_for_story.return_value = []
        mock_db.save_test_cases.return_value = 1
        mock_db.log_sync_time.return_value = None
        # Instancia o agente
        agent = QAAgent()
        # Executa o fluxo de verificação (simula 2 ciclos)
        for _ in range(2):
            agent.check_for_new_stories()
            time.sleep(3)
        # Verifica se as integrações foram chamadas corretamente
        self.assertTrue(mock_jira.get_user_stories.called)
        self.assertTrue(mock_openai.generate_test_cases.called)
        self.assertTrue(mock_jira.create_subtask.called)
        self.assertTrue(mock_db.save_user_story.called)
        self.assertTrue(mock_db.save_test_cases.called)

if __name__ == "__main__":
    unittest.main()
