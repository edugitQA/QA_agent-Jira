# qa_agent/src/main.py

import os
import time
import schedule
from datetime import datetime, timedelta
import argparse
import traceback # Importa o módulo traceback
from dotenv import load_dotenv
import unicodedata # Importa o módulo unicodedata para normalização de Unicode

# Importa os componentes do nosso agente
from jira_client import JiraClient
from openai_client import OpenAIClient
from db_manager import DBManager

# Carrega as variáveis de ambiente
load_dotenv()

class QAAgent:
    def __init__(self):
        """
        Inicializa o agente de QA, conectando-se aos serviços necessários.
        """
        # Inicializa os clientes e o gerenciador de banco de dados
        self.jira_client = JiraClient()
        self.openai_client = OpenAIClient()
        self.db_manager = DBManager()
        
        # Configurações padrão
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "KCA")
        self.status = os.getenv("JIRA_STATUS", "To Do")
        self.check_interval = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))
        
        # Data da última verificação 
        self.last_checked_time = None
        
        print(f"QA Agent inicializado para o projeto {self.project_key}")
    
    def format_jira_datetime(self, dt):
        """
        Formata um objeto datetime para o formato de data/hora aceito pelo Jira.
        
        Args:
            dt (datetime): Objeto datetime a ser formatado.
            
        Returns:
            str: String formatada para uso em consultas JQL.
        """
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def process_user_story(self, story):
        """
        Processa uma história de usuário, gerando casos de teste e salvando no banco.

        Args:
            story: Objeto Issue do Jira representando a história de usuário.
            
        Returns:
            bool: True se o processamento foi bem-sucedido, False caso contrário.
        """
        try:
            # Extrai informações da história
            # Normaliza os caracteres Unicode
            jira_key = unicodedata.normalize('NFKD', story['key']).encode('ascii', 'ignore').decode('ascii')
            title = unicodedata.normalize('NFKD', story['title']).encode('ascii', 'ignore').decode('ascii')
            description = unicodedata.normalize('NFKD', story['description']).encode('ascii', 'ignore').decode('ascii')
            status = unicodedata.normalize('NFKD', story['status']).encode('ascii', 'ignore').decode('ascii')
            
            print(f"Processando história: {jira_key} - {title}")
            
            # Salva a história no banco de dados
            story_id = self.db_manager.save_user_story(
                jira_key=jira_key,
                title=title,
                description=description,
                status=status
            )
            print(f"História {jira_key} salva/atualizada no DB com ID: {story_id}")
            
            # Prepara o texto da história para enviar ao LLM
            story_text = f"""
            Título: {title}
            
            Descrição:
            {description}
            """
            
            # Gera os casos de teste usando o OpenAI
            test_cases = self.openai_client.generate_test_cases(story_text)
            
            # Salva os casos de teste no banco de dados
            test_case_db_id = self.db_manager.save_test_cases(story_id, test_cases)
            print(f"Casos de teste gerados e salvos no DB para {jira_key} com ID: {test_case_db_id}")
            return True
            
        except Exception as e:
            print(f"Erro ao processar história {story.key if hasattr(story, 'key') else 'desconhecida'}: {e}")
            traceback.print_exc() # Imprime o traceback completo
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
            
            if not stories:
                print("Nenhuma nova história encontrada.")
                return
            
            print(f"Encontradas {len(stories)} novas histórias.")
            
            # Processa cada história
            for story in stories:
                self.process_user_story(story)
                
        except Exception as e:
            print(f"Erro ao verificar novas histórias: {e}")
            traceback.print_exc() # Imprime o traceback completo
    
    def start_monitoring(self):
        """
        Inicia o monitoramento periódico de novas histórias.
        """
        print(f"Iniciando monitoramento a cada {self.check_interval} minutos...")
        
        # Executa imediatamente na primeira vez
        self.check_for_new_stories()
        
        # Agenda execuções periódicas
        schedule.every(self.check_interval).minutes.do(self.check_for_new_stories)
        
        # Loop principal
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

def main():
    """
    Função principal que inicia o agente de QA.
    """
    parser = argparse.ArgumentParser(description='QA Agent - Gerador automático de casos de teste')
    parser.add_argument('--once', action='store_true', help='Executa uma única verificação e encerra')
    args = parser.parse_args()
    
    agent = QAAgent()
    
    if args.once:
        agent.run_once()
    else:
        agent.start_monitoring()

if __name__ == "__main__":
    main()


