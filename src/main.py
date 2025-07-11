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
        Agora, cada cenário de teste é registrado como subtarefa no Jira.
        """
        print(f"[DEBUG] Iniciando processamento da história: {story.get('key', story)}")
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
            print(f"[DEBUG] História salva no banco: {jira_key}")

            # Verificar se já existem casos de teste para a história (pelo story_id)
            existing_test_cases = self.db_manager.get_test_cases_for_story(story_id)
            if existing_test_cases:
                print(f"Já existem casos de teste para a história {jira_key} (ID: {story_id}). Pulando geração.")
                return True

            # Prepara o texto da história para enviar ao modelo de IA
            story_text = f"""
            Título: {title}

            Descrição:
            {description}
            """

            # Gera os casos de teste usando o OpenAI
            raw_test_cases = self.openai_client.generate_test_cases(story_text)
            print(f"[DEBUG] Casos de teste gerados para {jira_key}:\n{raw_test_cases}")

            # Salva os casos de teste no banco de dados
            test_case_db_id = self.db_manager.save_test_cases(story_id, raw_test_cases)
            print(f"Casos de teste gerados e salvos no DB para {jira_key} com ID: {test_case_db_id}")

            # Divide os cenários de teste por "Cenário:" (padrão do prompt)
            cenarios = []
            current = []
            for line in raw_test_cases.splitlines():
                if line.strip().lower().startswith("cenário") or line.strip().lower().startswith("cenario"):
                    if current:
                        cenarios.append("\n".join(current))
                        current = []
                current.append(line)
            if current:
                cenarios.append("\n".join(current))

            # Cria uma subtarefa para cada cenário
            for idx, cenario in enumerate(cenarios, 1):
                resumo = cenario.splitlines()[0].replace("Cenário:", "").replace("Cenario:", "").strip() or f"Cenário {idx}"
                descricao_bruta = "\n".join(cenario.splitlines()[1:]).strip()
                # Formata a descrição para Markdown antes de criar a subtarefa
                descricao_formatada = self.format_test_cases_to_markdown(descricao_bruta)
                self.jira_client.create_subtask(
                    parent_issue_key=jira_key,
                    summary=resumo,
                    description=descricao_formatada
                )

            print(f"[DEBUG] Subtarefas criadas para {jira_key} (total: {len(cenarios)})")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao processar história {story.get('key', story)}: {e}")
            traceback.print_exc()
            return False

    def check_for_new_stories(self):
        """
        Verifica se há novas histórias de usuário no Jira e as processa.
        """
        print(f"[DEBUG] Iniciando verificação de novas histórias no Jira...")
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

            print(f"[DEBUG] {len(stories)} histórias encontradas para processar.")
            print(f"Encontradas {len(stories)} novas histórias.")

            # Processa cada história encontrada
            for story in stories:
                print(f"[DEBUG] Processando história: {story.get('key', story)}")
                self.process_user_story(story)

        except Exception as e:
            print(f"[ERRO] Falha ao verificar novas histórias: {e}")
            traceback.print_exc()

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


