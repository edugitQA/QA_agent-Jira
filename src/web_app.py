from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os
import time


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_manager import DBManager
import os 
import markdown
import bleach
from datetime import datetime

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

# chave secreta para sessões e flash messages
app.secret_key = 'qa_agent_secret'

# Inicializa o gerenciador de banco de dados
db_manager = DBManager(db_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'qa_agent.db'))

@app.route('/')
def index():
    """Página inicial - lista todas as histórias de usuário."""
    user_stories = db_manager.get_all_user_stories()
    print(f"Histórias de usuário recuperadas: {user_stories}")
    print(f"Histórias enviadas para o template: {user_stories}")
    return render_template('index.html', user_stories=user_stories)

@app.route('/story/<int:story_id>')
def view_story(story_id):
    """Visualiza uma história específica e seus casos de teste."""
    story = db_manager.get_user_story(story_id)
    if not story:
        flash('História não encontrada', 'error')
        return redirect(url_for('index'))

    start_time = time.time()
    test_cases = db_manager.get_test_cases_for_story(story_id)
    end_time = time.time()
    print(f"Recuperação dos casos de teste executada em {end_time - start_time:.2f} segundos.")

    # Converte o conteúdo Markdown dos casos de teste para HTML
    for test_case in test_cases:
        # Sanitiza o HTML para evitar XSS
        test_case['content_html'] = bleach.clean(
            markdown.markdown(test_case['content']),
            tags=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 
                  'strong', 'em', 'a', 'code', 'pre', 'blockquote', 'table', 
                  'thead', 'tbody', 'tr', 'th', 'td'],
            attributes={'a': ['href', 'title']}
        )

    render_start_time = time.time()
    response = render_template('story.html', story=story, test_cases=test_cases)
    render_end_time = time.time()
    print(f"Renderização do template executada em {render_end_time - render_start_time:.2f} segundos.")

    return response

@app.route('/delete_story/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    """
    Exclui uma história de usuário do banco de dados.
    """
    try:
        db_manager.delete_user_story(story_id)
        return '', 204  # Retorna sucesso sem conteúdo
    except Exception as e:
        print(f"Erro ao excluir história: {e}")
        return str(e), 500

@app.template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    """Filtro para formatar timestamps no template."""
    if value:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime(format)
    return ''

if __name__ == '__main__':
    # Cria as pastas de templates e static se não existirem
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'), exist_ok=True)

    
    app.run(debug=True, host='0.0.0.0', port=5003)
