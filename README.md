# QA-Agent
O QA Agent é um exemplo de como a IA pode ser aplicada para automatizar tarefas repetitivas e aumentar a produtividade das equipes de QA.
Ao gerar casos de teste automaticamente a partir de histórias de usuário, o sistema permite que os testadores foquem em atividades de maior
valor agregado, como a execução e análise dos testes.

## Visão Geral
O QA Agent é um sistema automatizado projetado para equipes de Garantia de Qualidade (QA) que desejam automatizar a criação de casos de teste. Ele monitora novas histórias de usuário no Jira e utiliza a API da OpenAI (GPT) para gerar casos de teste detalhados, economizando tempo e mantendo consistência.

## Funcionalidades
- **Monitoramento de histórias de usuário no Jira**: Integração com o Jira para identificar novas histórias.
- **Geração de casos de teste**: Utiliza modelos de linguagem avançados da OpenAI para criar casos de teste detalhados.
- **Automatização**: Reduz o esforço manual e melhora a eficiência do processo de QA.

## Estrutura do Projeto
```
qa_agent/
├── requirements.txt
├── start_agent.sh
├── start_webapp.sh
├── config/
├── data/
│   └── qa_agent.db
├── src/
│   ├── db_manager.py
│   ├── jira_client.py
│   ├── main.py
│   ├── openai_client.py
│   └── web_app.py
├── static/
│   └── styles.css
├── templates/
│   ├── base.html
│   ├── index.html
│   └── story.html
└── README.md
```

## Configuração do Ambiente

### Pré-requisitos
- Python 3.9 ou superior
- Git
- Ambiente virtual configurado

### Passos
1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```
2. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Execução

### Iniciar o Agente QA
Execute o script para iniciar o agente:
```bash
./start_agent.sh
```

### Iniciar a Aplicação Web
Execute o script para iniciar a aplicação web:
```bash
./start_webapp.sh
```

## Componentes Principais

### `src/db_manager.py`
Gerencia a interação com o banco de dados.

### `src/jira_client.py`
Realiza a integração com o Jira para monitorar histórias de usuário.

### `src/openai_client.py`
Comunica-se com a API da OpenAI para gerar casos de teste.

### `src/web_app.py`
Configura e executa a aplicação web usando Flask.

## Tecnologias Utilizadas
- **Python 3.9+**: Linguagem principal para desenvolvimento.
- **Flask**: Framework web para a aplicação front-end.
- **Jira API**: Integração para monitoramento de histórias de usuário.
- **OpenAI API**: Geração de casos de teste automatizados.
- **SQLite**: Banco de dados local para armazenamento de histórias e casos de teste.
- **python-dotenv**: Gerenciamento de variáveis de ambiente.
- **markdown**: Renderização de conteúdo Markdown para HTML.
- **bleach**: Sanitização de HTML para segurança contra XSS.
- **pytz**: Biblioteca para manipulação de fusos horários e ajuste para o fuso de São Paulo nas datas exibidas no front-end.

## Variáveis de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
JIRA_URL=https://<seu-dominio>.atlassian.net
JIRA_USER=<seu-email>
JIRA_API_TOKEN=<seu-token>
JIRA_PROJECT_KEY=<chave-do-projeto>
OPENAI_API_KEY=<sua-chave-openai>
CHECK_INTERVAL_MINUTES=60
```

## Execução Manual

### Iniciar o Agente QA (modo único)
```bash
python3 src/main.py --once
```

### Iniciar o Agente QA (modo monitoramento contínuo)
```bash
python3 src/main.py
```

### Iniciar a Aplicação Web
```bash
python3 src/web_app.py
```

Acesse a aplicação em [http://127.0.0.1:5003](http://127.0.0.1:5003).

## Observações
- O banco de dados será criado automaticamente em `data/qa_agent.db`.
- O projeto não utiliza mais `test_cases.db`.
- O front-end exibe histórias e casos de teste gerados automaticamente.
- O código está preparado para rodar em Linux.

## Dependências
Instale todas as dependências com:
```bash
pip install -r requirements.txt
```

## Segurança
- O arquivo `.env` **NÃO** deve ser versionado. Adicione ao `.gitignore`.

## Contribuição
Contribuições são bem-vindas! Siga os passos abaixo:
1. Faça um fork do repositório.
2. Crie uma branch para sua funcionalidade:
   ```bash
   git checkout -b minha-funcionalidade
   ```
3. Envie um pull request após testar suas alterações.

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).

---

Com este guia, você pode configurar, executar e contribuir para o QA Agent com facilidade. Caso tenha dúvidas, entre em contato comigo.
