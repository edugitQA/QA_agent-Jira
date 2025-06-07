import os
from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta
import unicodedata

load_dotenv()

class JiraClient:
    def __init__(self):
        self.jira_server = os.getenv('JIRA_SERVER')
        self.jira_username = os.getenv('JIRA_USERNAME')
        self.jira_api_token = os.getenv('JIRA_API_TOKEN')

        try:
            self.jira = JIRA(
                server=self.jira_server,
                basic_auth=(self.jira_username, self.jira_api_token),
            )
            print(f"Conexão com jira estabelecida com sucesso em {self.jira_server}") 
        except Exception as e:
            print(f"Erro ao conectar ao Jira: {e}")
            raise

    def get_user_stories(self, project_key, status= "To Do", days_ago=None):
        """
        Busca histórias de usuário em um projeto Jira com base no status e na data de criação.
        args:
            project_key (str): Chave do projeto Jira.
            status (str): Status das histórias de usuário a serem buscadas. Padrão é "To Do".
            days_ago (int, optional): Buscar histórias de usuário criadas nos últimos 'n' dias.
                                                            Se None, busca todas as histórias.
        
        returns:
            list: Lista de histórias de usuário encontradas.
        """
        
        try:
            jql_parts = [
                f'project = {project_key}',
                'issuetype = Story',
                f'status = "{status}"'
            ]

            if days_ago is not None:
                date_limit = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                jql_parts.append(f'created >= "{date_limit}"')
                print(f"Buscando histórias com a query JQL: {date_limit}")

            jql_query = " AND ".join(jql_parts)
            print(f"Buscando histórias com a query JQL: {jql_query}")

            issues = self.jira.search_issues(jql_query, maxResults=50)
            print(f"Encontradas {len(issues)} histórias de usuário no projeto.")

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
            print(f"Erro ao buscar histórias no Jira: {e}")
            return []
        


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

        print(f"\n{story['key']} - {title_normalized}")
        print(f"Status: {story['status']}")
        print(f"Descrição: {description_normalized}...")
