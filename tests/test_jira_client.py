import unittest
from unittest.mock import patch, MagicMock
from jira_client import JiraClient
import os

class TestJiraClientAPI(unittest.TestCase):
    def setUp(self):
        # Mock variáveis de ambiente
        os.environ["JIRA_SERVER"] = "https://fake-jira-server.com"
        os.environ["JIRA_USERNAME"] = "fakeuser"
        os.environ["JIRA_API_TOKEN"] = "faketoken"
        self.jira_client = JiraClient()

    @patch("jira.JIRA")
    def test_conexao_jira(self, mock_jira):
        # Testa se a conexão é estabelecida sem erro
        mock_jira.return_value = MagicMock()
        try:
            client = JiraClient()
            self.assertIsNotNone(client.jira)
        except Exception as e:
            self.fail(f"Falha ao conectar: {e}")

    @patch.object(JiraClient, 'jira')
    def test_get_user_stories(self, mock_jira):
        # Testa busca de user stories
        mock_issue = MagicMock()
        mock_issue.key = 'KCA-1'
        mock_issue.fields.summary = 'Teste'
        mock_issue.fields.description = 'Descrição'
        mock_issue.fields.status.name = 'To Do'
        mock_jira.search_issues.return_value = [mock_issue]
        stories = self.jira_client.get_user_stories('KCA')
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]['key'], 'KCA-1')

    @patch.object(JiraClient, 'jira')
    def test_create_subtask(self, mock_jira):
        # Testa criação de subtarefa
        mock_parent = MagicMock()
        mock_parent.fields.project.key = 'KCA'
        mock_issue_type = MagicMock()
        mock_issue_type.name = 'Sub-task'
        mock_issue_type.id = '10000'
        mock_jira.issue.return_value = mock_parent
        mock_jira.project.return_value.issueTypes = [mock_issue_type]
        mock_jira.create_issue.return_value.key = 'KCA-2'
        result = self.jira_client.create_subtask('KCA-1', 'Cenário Teste', 'Descrição do cenário')
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
