import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        try:
            self.client = OpenAI(api_key=self.openai_api_key)
            print("Conexão com OpenAI estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar com OpenAI: {e}")
            raise

    def generate_test_cases(self, user_story_description: str) -> str: 
        
        prompt = f"""
Você é um especialista em QA. Dada a seguinte história de usuário, gere casos de teste detalhados.
Inclua cenários de sucesso, cenários de falha e casos de borda, se aplicável.
Formate a saída de forma clara e estruturada, por exemplo, usando Markdown.
História do usuário:
{user_story_description} 
casos de teste:
    """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",  #
                temperature=0.7,
                max_tokens=1000,  # Ajuste conforme necessário
            )
            test_cases = chat_completion.choices[0].message.content
            print("Casos de teste gerados com sucesso.")
            return test_cases

        except Exception as e:
            print(f"Erro ao gerar casos de teste com OpenAI: {e}")
            return f"Erro ao gerar casos de teste: {e}"


if __name__ == "__main__":
    # Inicializa o cliente OpenAI
    openai_client = OpenAIClient()

    # Exemplo de história de usuário
    user_story = """
    Como usuário, quero poder redefinir minha senha através de um link enviado por email,
    para que eu possa recuperar o acesso à minha conta caso esqueça minha senha.
    Critérios de Aceitação:
    - O usuário deve poder solicitar a redefinição de senha na tela de login
    - Um email com um link de redefinição deve ser enviado para o endereço cadastrado
    - O link deve expirar após 24 horas
    - Após clicar no link, o usuário deve poder definir uma nova senha
    - A nova senha deve seguir os critérios de segurança (mínimo 8 caracteres, incluindo letras e números)
    """

    # Gera casos de teste para a história de usuário
    test_cases = openai_client.generate_test_cases(user_story)

    # Exibe os casos de teste gerados
    print("\nCasos de Teste Gerados:")
    print(test_cases)
