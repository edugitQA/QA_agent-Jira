import os
import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/qa_agent.db'))
        else:
            self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = None
        self.cursor = None

        self._init_db()

    def connect(self):
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                self.cursor = self.conn.cursor()
                print(f"Conexão com o banco de dados estabelecida: {self.db_path}")
            except sqlite3.Error as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                raise

    def _disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Conexão com o banco de dados fechada.")

    def _init_db(self):
        print(f"Inicializando o banco de dados em {self.db_path}...")
        try:
            self.connect()
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jira_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(jira_key)
                )
                """
            )
            print("Tabela user_stories verificada/criada.")

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_story_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_story_id) REFERENCES user_stories(id)
                )
                """
            )
            print("Tabela test_cases verificada/criada.")

            self.conn.commit()
            print("Banco de dados inicializado com sucesso.")
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            raise
        finally:
            self._disconnect()

    def save_user_story(self, jira_key, title, description, status):
        self.connect()
        try:
            self.cursor.execute(
                "SELECT id FROM user_stories WHERE jira_key = ?",
                (jira_key,)
            )
            result = self.cursor.fetchone()

            if result:
                self.cursor.execute(
                    """
                    UPDATE user_stories 
                    SET title = ?, description = ?, status = ? 
                    WHERE jira_key = ?
                    """,
                    (title, description, status, jira_key)
                )
                story_id = result['id']
            else:
                self.cursor.execute(
                    """
                    INSERT INTO user_stories (jira_key, title, description, status) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (jira_key, title, description, status)
                )
                story_id = self.cursor.lastrowid

            self.conn.commit()
            return story_id
        finally:
            self._disconnect()

    def save_test_cases(self, user_story_id, content):
        self.connect()
        try:
            self.cursor.execute(
                "INSERT INTO test_cases (user_story_id, content) VALUES (?, ?)",
                (user_story_id, content)
            )
            test_case_id = self.cursor.lastrowid
            self.conn.commit()
            return test_case_id
        finally:
            self._disconnect()
    
    def get_all_user_stories(self):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM user_stories ORDER BY created_at DESC")
            stories = [dict(row) for row in self.cursor.fetchall()]
            print("Histórias recuperadas do banco de dados:", stories)
            return stories
        finally:
            self._disconnect()

    def get_user_story(self, story_id):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM user_stories WHERE id = ?", (story_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        finally:
            self._disconnect() 

    def get_test_cases_for_story(self, user_story_id):
       
        self.connect()
        try:
            self.cursor.execute(
                "SELECT * FROM test_cases WHERE user_story_id = ? ORDER BY generated_at DESC",
                (user_story_id,)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        finally:
            self._disconnect()

    def get_latest_test_case_for_story(self, user_story_id):
        
        self.connect()
        try:
            self.cursor.execute(
                """
                SELECT * FROM test_cases 
                WHERE user_story_id = ? 
                ORDER BY generated_at DESC 
                LIMIT 1
                """,
                (user_story_id,)
            )
            row = self.cursor.fetchone()
            return dict(row) if row else None
        finally:
            self._disconnect()


##TESTES BD
from db_manager import DBManager

# Inicializa o gerenciador de banco de dados
db_manager = DBManager()

# Salva uma história de usuário de exemplo
story_id = db_manager.save_user_story(
    jira_key="TEST-123",
    title="Exemplo de História",
    description="Esta é uma história de usuário de exemplo para testar o banco de dados.",
    status="To Do"
)
print(f"História salva com ID: {story_id}")

# Salva casos de teste para a história
test_case_id = db_manager.save_test_cases(
    user_story_id=story_id,
    content="# Casos de Teste\n\n## Cenário 1\n- Passo 1\n- Passo 2\n\n## Cenário 2\n- Passo 1\n- Passo 2"
)
print(f"Casos de teste salvos com ID: {test_case_id}")

# Recupera todas as histórias
stories = db_manager.get_all_user_stories()
print(f"Número de histórias no banco: {len(stories)}")

# Recupera os casos de teste para a história
test_cases = db_manager.get_test_cases_for_story(story_id)
print(f"Número de casos de teste para a história {story_id}: {len(test_cases)}")
print(f"Conteúdo do primeiro caso de teste: {test_cases[0]['content'][:50]}...")
