# Personal Chief

Assistente de cozinha construído com LangChain e LangGraph. O agente pesquisa receitas e informações nutricionais usando Tavily e extrai conteúdo de páginas com TinyFish. A aplicação oferece uma API HTTP com FastAPI e um script de exemplo que executa uma pesquisa pelo terminal.

## Requisitos

- Python 3.10 ou superior
- Chaves de API da [Groq](https://console.groq.com/keys) e da [Tavily](https://app.tavily.com/home)
- Acesso ao TinyFish MCP com autenticação OAuth

As dependências Python estão listadas em `requirements.txt`. O projeto usa os modelos Groq configurados em `app/agent/personal_chief.py`.

## Configuração

No PowerShell, na raiz do repositório, crie e ative um ambiente virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crie o arquivo local de variáveis de ambiente a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite `.env` e informe as chaves:

```dotenv
TAVILY_API_KEY=sua-chave-tavily
GROQ_API_KEY=sua-chave-groq

# Opcionais: tracing e observabilidade com LangSmith
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=sua-chave-langsmith
LANGSMITH_PROJECT=personal-chief
```

`.env` é um arquivo local e não deve ser commitado. O exemplo versionado não contém credenciais reais.

## Executar a API

Com o ambiente virtual ativado e `.env` preenchido, inicie o servidor:

```powershell
uvicorn app.api.main:app --reload
```

Por padrão, a API estará em `http://127.0.0.1:8000`.

- Documentação interativa: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Endpoint de conversa: `POST http://127.0.0.1:8000/chat`

Exemplo de requisição:

```powershell
$body = @{
  message = "Sugira uma receita de lasanha à bolonhesa e informe os ingredientes."
  thread_id = "cozinha-1"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Formato da requisição:

```json
{
  "message": "Sugira uma receita de lasanha à bolonhesa.",
  "thread_id": "cozinha-1"
}
```

`message` e `thread_id` são obrigatórios e devem ser strings não vazias. `thread_id` aceita até 128 caracteres. A resposta contém o texto produzido pelo agente e o mesmo identificador:

```json
{
  "response": "...",
  "thread_id": "cozinha-1"
}
```

Chamadas com o mesmo `thread_id` compartilham o identificador da conversa. O checkpoint atual é `InMemorySaver`: o histórico fica apenas na memória do processo e se perde quando a API reinicia.

## Executar o exemplo de terminal

O script `scripts/run_agent.py` conecta-se aos servidores MCP, lista as ferramentas encontradas e executa uma solicitação de exemplo sobre lasanha:

```powershell
python -m scripts.run_agent
```

## Ferramentas e fluxo do agente

- **Tavily** pesquisa na web e encontra páginas relevantes. O wrapper limita cada execução a cinco pesquisas.
- **TinyFish** visita páginas e extrai o conteúdo solicitado. A conexão é feita pelo servidor MCP com OAuth.
- **Groq** fornece o modelo principal, o sumarizador e o seletor de ferramentas.

O prompt do agente instrui o fluxo de pesquisa a localizar páginas com Tavily e usar TinyFish para extrair seu conteúdo. Os modelos configurados atualmente são `openai/gpt-oss-120b`, `openai/gpt-oss-20b` e `qwen/qwen3.8-27b`.

## Estrutura do projeto

```text
.
├── app/
│   ├── agent/       # Construção e configuração do agente
│   ├── api/         # Aplicação FastAPI, rotas, schemas e ciclo de vida
│   ├── mcp/         # Conexões com servidores MCP
│   ├── prompts/     # Prompts do sistema, seleção de ferramentas e resumo
│   └── tools/       # Wrappers e controles das ferramentas
├── scripts/
│   └── run_agent.py # Execução de exemplo pelo terminal
├── .env.example     # Modelo de variáveis de ambiente
├── langgraph.json   # Configuração do LangGraph CLI
└── requirements.txt
```

## LangGraph CLI

`langgraph.json` contém uma referência a `STUDIO_AGENT`, mas esse objeto não está definido atualmente em `app/agent/personal_chief.py`. Por isso, a configuração ainda não pode ser iniciada pelo LangGraph CLI. A API FastAPI e o script de terminal são os caminhos de execução disponíveis no código atual.

## Solução de problemas

- **Variável de ambiente ausente:** confirme que `.env` existe na raiz e contém `TAVILY_API_KEY` e `GROQ_API_KEY` válidas.
- **Falha na inicialização ou ferramenta MCP indisponível:** verifique a conectividade com os servidores Tavily e TinyFish e a autenticação OAuth do TinyFish.
- **Erro 502 em `/chat`:** a API não conseguiu completar a chamada ao agente. Confira os logs do servidor, as chaves e a disponibilidade dos serviços externos.
- **PowerShell bloqueia a ativação do ambiente virtual:** se a política local impedir `Activate.ps1`, execute os comandos usando o interpretador do ambiente diretamente, por exemplo `\.venv\Scripts\python.exe -m pip install -r requirements.txt` e `\.venv\Scripts\python.exe -m uvicorn app.api.main:app --reload`.
