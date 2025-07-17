# 📋 Guia de Integração - Omie MCP & Nibo MCP

## 🚀 Visão Geral

Este guia fornece instruções completas para integrar os servidores **Omie MCP** e **Nibo MCP** com:
- N8N (Automação de workflows)
- Zapier (Integração SaaS)
- Microsoft Copilot (Assistente IA)
- Outras aplicações via API REST

## 📊 Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     N8N         │    │     Zapier      │    │  MS Copilot     │
│   Workflows     │    │   Integrations  │    │   Assistant     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────┴─────────────────┐
                │         FastAPI Servers          │
                └─────────────────┬─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼───────┐        ┌───────▼───────┐        ┌───────▼───────┐
│  Omie MCP     │        │  Nibo MCP     │        │  Claude MCP   │
│  Port: 3001   │        │  Port: 3002   │        │  STDIO Mode   │
└───────────────┘        └───────────────┘        └───────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│   Omie API    │        │   Nibo API    │        │   Both APIs   │
│   ERP System  │        │   ERP System  │        │   Combined    │
└───────────────┘        └───────────────┘        └───────────────┘
```

## 🔧 Configuração Inicial

### 1. Instalação de Dependências

```bash
pip install fastapi uvicorn requests pydantic
```

### 2. Inicialização dos Servidores

```bash
# Servidor Omie MCP (porta 3001)
python omie_http_server_fastapi.py --port 3001

# Servidor Nibo MCP (porta 3002)
python nibo-mcp/nibo_http_server_fastapi.py --port 3002
```

### 3. Verificação de Status

```bash
# Verificar Omie MCP
curl http://localhost:3001/

# Verificar Nibo MCP
curl http://localhost:3002/

# Verificar documentação
open http://localhost:3001/docs
open http://localhost:3002/docs
```

## 📋 Endpoints Disponíveis

### Omie MCP (Port 3001)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações do servidor |
| `/tools` | GET | Lista de ferramentas disponíveis |
| `/tools/{tool_name}` | POST | Executar ferramenta específica |
| `/docs` | GET | Documentação Swagger |
| `/health` | GET | Health check |

### Nibo MCP (Port 3002)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações do servidor |
| `/tools` | GET | Lista de ferramentas disponíveis |
| `/tools/{tool_name}` | POST | Executar ferramenta específica |
| `/docs` | GET | Documentação Swagger |
| `/health` | GET | Health check |

## 🔗 Integração com N8N

### 1. Configuração do Nó HTTP Request

```json
{
  "method": "POST",
  "url": "http://localhost:3001/tools/consultar_clientes",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "arguments": {
      "pagina": 1,
      "registros_por_pagina": 50
    }
  }
}
```

### 2. Exemplo de Workflow N8N

```json
{
  "nodes": [
    {
      "name": "Consultar Clientes Omie",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:3001/tools/consultar_clientes",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "{\n  \"arguments\": {\n    \"pagina\": 1,\n    \"registros_por_pagina\": 10\n  }\n}"
      }
    },
    {
      "name": "Processar Dados",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "string": [
            {
              "name": "total_clientes",
              "value": "={{$json.data.total_de_registros}}"
            }
          ]
        }
      }
    }
  ],
  "connections": {
    "Consultar Clientes Omie": {
      "main": [
        [
          {
            "node": "Processar Dados",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 🔗 Integração com Zapier

### 1. Webhook Configuration

```javascript
// Zapier Code Action Example
const response = await fetch('http://localhost:3001/tools/consultar_clientes', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    arguments: {
      pagina: 1,
      registros_por_pagina: 50
    }
  })
});

const data = await response.json();
return data.data; // Retorna dados dos clientes
```

### 2. Trigger Setup

```json
{
  "trigger": {
    "type": "webhook",
    "url": "http://localhost:3001/tools/consultar_clientes",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

## 🔗 Integração com Microsoft Copilot

### 1. Plugin Manifest

```json
{
  "schema_version": "v1",
  "name_for_human": "Omie & Nibo ERP Integration",
  "name_for_model": "omie_nibo_erp",
  "description_for_human": "Integração com sistemas ERP Omie e Nibo",
  "description_for_model": "Permite consultas e operações nos sistemas ERP Omie e Nibo",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "http://localhost:3001/docs"
  },
  "logo_url": "https://your-domain.com/logo.png",
  "contact_email": "your-email@domain.com",
  "legal_info_url": "https://your-domain.com/legal"
}
```

### 2. OpenAPI Integration

```yaml
openapi: 3.0.0
info:
  title: Omie & Nibo MCP API
  version: 2.0.0
servers:
  - url: http://localhost:3001
    description: Omie MCP Server
  - url: http://localhost:3002
    description: Nibo MCP Server
paths:
  /tools/consultar_clientes:
    post:
      summary: Consultar clientes
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                arguments:
                  type: object
                  properties:
                    pagina:
                      type: integer
                    registros_por_pagina:
                      type: integer
      responses:
        '200':
          description: Lista de clientes
          content:
            application/json:
              schema:
                type: object
```

## 🛠️ Ferramentas Disponíveis

### Omie MCP (11 ferramentas)
- `testar_conexao`
- `consultar_categorias`
- `consultar_departamentos`
- `consultar_contas_pagar`
- `consultar_contas_receber`
- `consultar_clientes`
- `consultar_fornecedores`
- `cadastrar_cliente_fornecedor`
- `criar_conta_pagar`
- `criar_conta_receber`

### Nibo MCP (16 ferramentas)
- `testar_conexao`
- `consultar_categorias`
- `consultar_centros_custo`
- `consultar_socios`
- `consultar_clientes`
- `consultar_fornecedores`
- `consultar_contas_pagar`
- `consultar_contas_receber`
- `incluir_socio`
- `incluir_cliente`
- `incluir_fornecedor`
- `incluir_conta_pagar`
- `incluir_conta_receber`
- `alterar_cliente`
- `alterar_fornecedor`
- `excluir_cliente`

## 🔐 Segurança

### 1. Autenticação

```python
# Exemplo de middleware de autenticação
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Implementar validação de token
    token = request.headers.get("Authorization")
    if not validate_token(token):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    return await call_next(request)
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/tools/{tool_name}")
@limiter.limit("10/minute")
async def call_tool(request: Request, tool_name: str, payload: ToolArguments):
    # Implementação da ferramenta
    pass
```

## 📊 Monitoramento

### 1. Health Checks

```bash
# Verificar saúde dos servidores
curl http://localhost:3001/health
curl http://localhost:3002/health
```

### 2. Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omie_mcp.log'),
        logging.StreamHandler()
    ]
)
```

## 📚 Exemplos de Uso

### Consultar Clientes (Omie)

```bash
curl -X POST http://localhost:3001/tools/consultar_clientes \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "pagina": 1,
      "registros_por_pagina": 10
    }
  }'
```

### Incluir Cliente (Nibo)

```bash
curl -X POST http://localhost:3002/tools/incluir_cliente \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "nome": "João Silva",
      "documento": "123.456.789-00",
      "email": "joao@email.com"
    }
  }'
```

## 🚀 Deploy em Produção

### 1. Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3001 3002

CMD ["python", "omie_http_server_fastapi.py", "--host", "0.0.0.0", "--port", "3001"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  omie-mcp:
    build: .
    ports:
      - "3001:3001"
    environment:
      - OMIE_API_KEY=your_api_key
      - OMIE_API_SECRET=your_api_secret
    restart: unless-stopped

  nibo-mcp:
    build: ./nibo-mcp
    ports:
      - "3002:3002"
    environment:
      - NIBO_API_TOKEN=your_api_token
    restart: unless-stopped
```

## 🔄 Troubleshooting

### Problemas Comuns

1. **Erro de conexão**: Verificar se os servidores estão rodando
2. **Erro de autenticação**: Verificar credenciais nos arquivos de configuração
3. **Timeout**: Aumentar timeout nas requisições
4. **Erro de CORS**: Configurar CORS adequadamente

### Logs Úteis

```bash
# Logs em tempo real
tail -f /tmp/omie_fastapi.log
tail -f /tmp/nibo_fastapi.log

# Verificar processos
ps aux | grep fastapi
```

## 📞 Suporte

Para suporte técnico, entre em contato:
- Email: suporte@empresa.com
- Issues: GitHub Issues
- Documentação: /docs endpoint

---

**Nota**: Esta documentação assume que você já tem as credenciais configuradas nos respectivos sistemas ERP.