# Este arquivo contém a lógica principal do agente de QA, incluindo a inicialização, monitoramento e processamento de histórias de usuário.

# Importações necessárias para o funcionamento do agente
import os
import time
import schedule
from datetime import datetime, timedelta
import argparse
import traceback  # Para exibir rastreamentos detalhados de erros
from dotenv import load_dotenv  # Para carregar variáveis de ambiente de um arquivo .env
import unicodedata  # Para normalizar caracteres Unicode

# Importa os componentes do agente, como clientes para Jira e OpenAI, e o gerenciador de banco de dados
from jira_client import JiraClient
from openai_client import OpenAIClient
from db_manager import DBManager

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class QAAgent:
    """
    Classe principal do agente de QA. Gerencia a conexão com serviços externos (Jira, OpenAI),
    interage com o banco de dados e executa o monitoramento de histórias de usuário.
    """

    def __init__(self):
        """
        Inicializa o agente de QA, configurando conexões e parâmetros padrão.
        """
        # Inicializa os clientes para Jira e OpenAI, além do gerenciador de banco de dados
        self.jira_client = JiraClient()
        self.openai_client = OpenAIClient()
        self.db_manager = DBManager()

        # Configurações padrão do agente, como chave do projeto e status das histórias
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "KCA")
        self.status = os.getenv("JIRA_STATUS", "To Do")
        self.check_interval = 0.05  # Intervalo de monitoramento reduzido para ~3 segundos

        # Armazena o timestamp da última verificação
        self.last_checked_time = None

        print(f"QA Agent inicializado para o projeto {self.project_key}")

    def format_jira_datetime(self, dt):
        """
        Formata um objeto datetime para o formato aceito pelo Jira.

        Args:
            dt (datetime): Objeto datetime a ser formatado.

        Returns:
            str: String formatada para uso em consultas JQL.
        """
        return dt.strftime("%Y-%m-%d %H:%M")

    def process_user_story(self, story):
        """
        Processa uma história de usuário, gerando casos de teste e salvando no banco de dados.

        Args:
            story: Objeto Issue do Jira representando a história de usuário.

        Returns:
            bool: True se o processamento foi bem-sucedido, False caso contrário.
        """
        try:
            # Normaliza os caracteres Unicode para evitar problemas de codificação
            jira_key = unicodedata.normalize("NFKD", story["key"]).encode("ascii", "ignore").decode("ascii")
            title = unicodedata.normalize("NFKD", story["title"]).encode("ascii", "ignore").decode("ascii")
            description = unicodedata.normalize("NFKD", story["description"]).encode("ascii", "ignore").decode("ascii")
            status = unicodedata.normalize("NFKD", story["status"]).encode("ascii", "ignore").decode("ascii")

            print(f"Processando história: {jira_key} - {title}")

            # Salva a história no banco de dados e obtém o ID
            story_id = self.db_manager.save_user_story(
                jira_key=jira_key,
                title=title,
                description=description,
                status=status
            )
            print(f"História {jira_key} salva/atualizada no DB com ID: {story_id}")

            # Prepara o texto da história para enviar ao modelo de IA
            story_text = f"""
            Título: {title}

            Descrição:
            {description}
            """

            # Gera os casos de teste usando o OpenAI
            raw_test_cases = self.openai_client.generate_test_cases(story_text)

            # Formata os casos de teste para Markdown
            formatted_test_cases = self.format_test_cases_to_markdown(raw_test_cases)

            # Salva os casos de teste no banco de dados (pode salvar o raw ou o formatado, dependendo da necessidade)
            test_case_db_id = self.db_manager.save_test_cases(story_id, raw_test_cases)
            print(f"Casos de teste gerados e salvos no DB para {jira_key} com ID: {test_case_db_id}")

            # Adicionar os casos de teste formatados como comentário no Jira
            self.jira_client.add_comment_to_issue(issue_key=jira_key, comment_body=formatted_test_cases)

            return True

        except Exception as e:
            print(f"Erro ao processar história {story.key if hasattr(story, 'key') else 'desconhecida'}: {e}")
            traceback.print_exc()  # Exibe o rastreamento completo do erro
            return False

    def check_for_new_stories(self):
        """
        Verifica se há novas histórias de usuário no Jira e as processa.
        """
        try:
            print(f"Verificando novas histórias em {self.project_key} com status '{self.status}'...")

            # Define o período de busca para as últimas 24 horas
            last_checked = datetime.now() - timedelta(days=1)
            print(f"Buscando histórias criadas após {self.format_jira_datetime(last_checked)}")

            # Busca histórias no Jira
            stories = self.jira_client.get_user_stories(
                project_key=self.project_key,
                status=self.status,
                days_ago=1
            )

            # Atualiza o timestamp da última verificação para o momento atual
            self.last_checked_time = datetime.now()
            self.db_manager.log_sync_time()  # Registra o horário da sincronização

            if not stories:
                print("Nenhuma nova história encontrada.")
                return

            print(f"Encontradas {len(stories)} novas histórias.")

            # Processa cada história encontrada
            for story in stories:
                self.process_user_story(story)

        except Exception as e:
            print(f"Erro ao verificar novas histórias: {e}")
            traceback.print_exc()  # Exibe o rastreamento completo do erro

    def start_monitoring(self):
        """
        Inicia o monitoramento periódico de novas histórias.
        """
        print(f"Iniciando monitoramento a cada {self.check_interval} minutos...")

        # Executa imediatamente na primeira vez
        self.check_for_new_stories()

        # Agenda execuções periódicas
        schedule.every(self.check_interval).minutes.do(self.check_for_new_stories)

        # Loop principal para executar as tarefas agendadas
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Monitoramento interrompido pelo usuário.")

    def run_once(self):
        """
        Executa uma única verificação de novas histórias.
        """
        self.check_for_new_stories()
        print("Verificação única concluída.")

    def format_test_cases_to_markdown(self, test_cases_text):
        """
        Formata o texto dos casos de teste para Markdown, destacando títulos e cenários.
        Args:
            test_cases_text (str): O texto dos casos de teste gerados.
        Returns:
            str: O texto formatado em Markdown.
        """
        lines = test_cases_text.splitlines()
        formatted_lines = []
        for line in lines:
            if line.startswith("Título:"):
                formatted_lines.append(f"h2. {line.replace('Título:', '').strip()}\n")
            elif line.startswith("Cenário:"):
                formatted_lines.append(f"h3. {line.strip()}\n")
            elif line.strip().startswith("Dado que") or \
                 line.strip().startswith("Quando") or \
                 line.strip().startswith("Então") or \
                 line.strip().startswith("E") or \
                 line.strip().startswith("Mas"):
                formatted_lines.append(f"* {line.strip()}\n")
            elif line.strip(): # Adiciona linhas não vazias que não são títulos ou cenários
                formatted_lines.append(f"{{code}}{line.strip()}{{code}}\n")
        return "".join(formatted_lines)

def main():
    """
    Função principal que inicia o agente de QA.
    """
    # Configura o parser de argumentos para permitir execução única ou contínua
    parser = argparse.ArgumentParser(description='QA Agent - Gerador automático de casos de teste')
    parser.add_argument('--once', action='store_true', help='Executa uma única verificação e encerra')
    args = parser.parse_args()

    # Inicializa o agente de QA
    agent = QAAgent()

    # Decide entre execução única ou monitoramento contínuo
    if args.once:
        agent.run_once()
    else:
        agent.start_monitoring()

if __name__ == "__main__":
    main()


