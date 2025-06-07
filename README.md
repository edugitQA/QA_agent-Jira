# QA Agent

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
│   └── test_cases.db
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

## Boas Práticas
- **Segurança**: Certifique-se de que o arquivo `.env` contendo chaves de API esteja no `.gitignore`.
- **Manutenção**: Atualize regularmente as dependências e revise o código para melhorias.

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
