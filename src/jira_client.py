import os
from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta
import unicodedata
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

class JiraClient:
    def __init__(self):
        self.jira_server = os.getenv("JIRA_SERVER")
        self.jira_username = os.getenv("JIRA_USERNAME")
        self.jira_api_token = os.getenv("JIRA_API_TOKEN")

        try:
            self.jira = JIRA(
                server=self.jira_server,
                basic_auth=(self.jira_username, self.jira_api_token),
            )
            logger.info(f"Conexão com jira estabelecida com sucesso em {self.jira_server}") 
        except Exception as e:
            logger.error(f"Erro ao conectar ao Jira: {e}")
            raise

    def get_user_stories(self, project_key, status="To Do", days_ago=None, no_date_limit=False):
        """
        Busca histórias de usuário em um projeto Jira com base no status e na data de criação.
        Args:
            project_key (str): Chave do projeto Jira.
            status (str): Status das histórias de usuário a serem buscadas. Padrão é "To Do".
            days_ago (int, optional): Buscar histórias de usuário criadas nos últimos 'n' dias.
            no_date_limit (bool, optional): Ignorar limite de data e buscar todas as histórias.
        Returns:
            list: Lista de histórias de usuário encontradas.
        """
        try:
            jql_parts = [
                f'project = {project_key}',
                'issuetype = Story',
                f'status = "{status}"'
            ]

            if days_ago is not None and not no_date_limit:
                date_limit = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                jql_parts.append(f'created >= "{date_limit}"')

            jql_query = " AND ".join(jql_parts)
            logger.info(f"Buscando histórias com a query JQL: {jql_query}")

            issues = self.jira.search_issues(jql_query, maxResults=50)
            logger.info(f"Encontradas {len(issues)} histórias de usuário no projeto.")

            # Formatando os resultados
            user_stories = []
            for issue in issues:
                user_stories.append({
                    'key': issue.key,
                    'title': issue.fields.summary,
                    'description': issue.fields.description or '',
                    'status': issue.fields.status.name
                })

            return user_stories

        except Exception as e:
            logger.error(f"Erro ao buscar histórias no Jira: {e}")
            return []

    def add_comment_to_issue(self, issue_key, comment_body):
        """
        [REMOVIDO] Função substituída por registro automático de subtarefas.
        """
        pass

    def create_subtask(self, parent_issue_key, summary, description=None):
        """
        Cria uma subtarefa (sub-task) em uma User Story no Jira.
        Args:
            parent_issue_key (str): Chave da User Story (ex: KCA-123).
            summary (str): Título da subtarefa (ex: nome do cenário de teste).
            description (str, opcional): Descrição detalhada do cenário.
        Returns:
            issue: Objeto da issue criada ou None em caso de erro.
        """
        try:
            parent_issue = self.jira.issue(parent_issue_key)
            project_key = parent_issue.fields.project.key
            subtask_issue_type = None
            # Busca o tipo de issue 'Sub-task' para o projeto
            for issue_type in self.jira.project(project_key).issueTypes:
                if issue_type.name.lower() in ["sub-task", "subtarefa", "subtask"]:
                    subtask_issue_type = issue_type
                    break
            if not subtask_issue_type:
                logger.error(f"Tipo de issue 'Sub-task' não encontrado no projeto {project_key}.")
                return None
            issue_dict = {
                'project': {'key': project_key},
                'parent': {'key': parent_issue_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'id': subtask_issue_type.id}
            }
            new_issue = self.jira.create_issue(fields=issue_dict)
            logger.info(f"Subtarefa criada: {new_issue.key} para {parent_issue_key}")
            return new_issue
        except Exception as e:
            logger.error(f"Erro ao criar subtarefa para {parent_issue_key}: {e}")
            return None


##teste isolado
if __name__ == "__main__":
   
    jira_client = JiraClient()

   
    project_key = os.getenv("JIRA_PROJECT_KEY")
    status = os.getenv("JIRA_STATUS", "To Do")
    stories = jira_client.get_user_stories(
        project_key=project_key,
        status=status,
        days_ago=30 
    )

   
    for story in stories:
        title_normalized = unicodedata.normalize('NFKD', story['title']).encode('ascii', 'ignore').decode('ascii')
        description_normalized = unicodedata.normalize('NFKD', story['description'][:100]).encode('ascii', 'ignore').decode('ascii')

        logger.info(f"\n{story['key']} - {title_normalized}")
        logger.info(f"Status: {story['status']}")
        logger.info(f"Descrição: {description_normalized}...")