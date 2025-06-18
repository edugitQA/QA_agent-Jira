# Guia de Formatação Markdown para Comentários no Jira

Este guia detalha a sintaxe Markdown utilizada para formatar os casos de teste gerados automaticamente no Jira, permitindo que você personalize a saída conforme suas necessidades.

## Títulos

Para destacar títulos e subtítulos, utilize os cabeçalhos do Jira Markdown, que são equivalentes aos cabeçalhos HTML. Quanto mais `#` você usar, menor será o título.

*   **Título Principal (h1):** Não utilizado neste script para evitar conflitos com o título da issue, mas seria `h1. Seu Título Aqui`.
*   **Título de Seção (h2):** Utilizado para o título geral dos casos de teste (ex: "Casos de Teste para a História do Usuário").
    ```
h2. Seu Título de Seção Aqui
    ```
*   **Título de Cenário (h3):** Utilizado para cada cenário de teste (ex: "Cenário 1: Sucesso na Criação do Formulário").
    ```
h3. Seu Título de Cenário Aqui
    ```

## Listas

Para criar listas de itens, como os passos de um teste ou pré-condições, você pode usar listas não ordenadas ou ordenadas.

*   **Listas Não Ordenadas:** Utilize `*` ou `-` seguido de um espaço.
    ```
* Item 1
* Item 2
    ```
    No script, utilizamos `*` para formatar as linhas que começam com "Dado que", "Quando", "Então", "E" e "Mas", transformando-as em itens de lista.

*   **Listas Ordenadas:** Utilize números seguidos de um ponto e um espaço.
    ```
1. Primeiro item
2. Segundo item
    ```

## Blocos de Código

Para incluir trechos de texto que devem ser exibidos como código ou para manter o alinhamento de texto que não se encaixa em outras formatações (como os detalhes de um passo de teste), utilize blocos de código.

*   **Bloco de Código Inline:** Utilize `{{code}}seu texto aqui{{code}}`.
    ```
Isso é um texto normal com um `{{code}}trecho de código inline{{code}}`.
    ```
    No script, usamos `{{code}}` para envolver linhas que não são títulos nem itens de lista, garantindo que o texto seja exibido exatamente como está, sem quebras de linha ou formatações indesejadas que o Jira possa aplicar.

## Exemplo de Saída Formatada (simplificado)

```
h2. Casos de Teste para a História do Usuário: US-XXX - Nome da História

h3. Cenário: Sucesso na Criação do Formulário
* Dado que o usuário está na página do formulário
* Quando o usuário preenche todos os campos obrigatórios
* Então o formulário é enviado com sucesso

h3. Cenário: Falha na Validação do Formulário
* Dado que o usuário está na página do formulário
* Quando o usuário deixa um campo obrigatório em branco
* Então o formulário não é enviado e uma mensagem de erro é exibida
```

Ao entender e manipular essas sintaxes, você pode controlar a apresentação dos casos de teste no Jira de forma eficaz.

