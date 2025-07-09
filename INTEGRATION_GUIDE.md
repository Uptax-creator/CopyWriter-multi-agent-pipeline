# 🚀 Guia de Integração - Omie MCP Server

Este guia mostra como integrar o Omie MCP Server com diferentes plataformas de IA.

## 🤖 **Claude (Anthropic)**

### Opção 1: Claude Desktop App (Recomendado)

1. **Localizar arquivo de configuração:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Configurar o servidor MCP:**
```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
```

> **Nota**: As credenciais são carregadas automaticamente do arquivo `credentials.json`!

3. **Reiniciar Claude Desktop**

4. **Testar integração:**
```
Olá! Consulte as categorias do Omie ERP para mim.
```

### Opção 2: Claude via API HTTP

1. **Iniciar servidor:**
```bash
export OMIE_APP_KEY="sua_app_key"
export OMIE_APP_SECRET="seu_app_secret"
python omie_http_server.py
```

2. **Exemplo de uso via API:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "consultar_categorias",
      "arguments": {"pagina": 1}
    }
  }'
```

## 🔷 **Microsoft Copilot Studio**

### Passo 1: Configurar Plugin

1. **Abrir Copilot Studio**
2. **Ir para Actions > Create Action**
3. **Selecionar "From OpenAPI"**
4. **Usar URL:** `http://localhost:8000/openapi.json`

### Passo 2: Configurar Manifest

Use o arquivo `integrations/copilot_studio_manifest.json`:

```json
{
  "schema_version": "v1",
  "name_for_human": "Omie ERP Integration",
  "name_for_model": "omie_erp",
  "description_for_human": "Integração completa com Omie ERP",
  "api": {
    "type": "openapi",
    "url": "http://localhost:8000/openapi.json"
  }
}
```

### Passo 3: Configurar Actions

1. **Criar Action "Consultar Categorias":**
   - **Endpoint:** `POST /mcp`
   - **Body Template:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "consultar_categorias",
    "arguments": {}
  }
}
```

2. **Criar Action "Criar Conta a Pagar":**
   - **Endpoint:** `POST /mcp`
   - **Parâmetros:** cnpj_fornecedor, valor, data_vencimento, etc.

### Passo 4: Testar no Copilot

```
Consulte as categorias do Omie ERP e crie uma conta a pagar no valor de R$ 1.000,00 para o fornecedor 16.726.230/0001-78 com vencimento em 31/12/2024.
```

## 🔄 **N8N Workflow**

### Passo 1: Importar Workflow

1. **Abrir N8N**
2. **Criar New Workflow**
3. **Importar JSON** do arquivo `integrations/n8n_workflow.json`

### Passo 2: Configurar Variáveis

1. **Configurar URL do servidor:**
   - **URL:** `http://localhost:8000/mcp`
   
2. **Configurar credenciais Omie:**
   - Definir nas variáveis de ambiente do N8N

### Passo 3: Configurar Webhook

1. **Nó Webhook:** Configure o endpoint que receberá dados
2. **URL gerada:** `http://n8n-url/webhook/omie-integration`

### Passo 4: Testar Workflow

**Exemplo de POST para o webhook:**
```json
{
  "action": "criar_conta_pagar",
  "cnpj_fornecedor": "16.726.230/0001-78",
  "razao_social": "Fornecedor Teste",
  "numero_documento": "NF-001",
  "data_vencimento": "31/12/2024",
  "valor_documento": 1000.00,
  "codigo_categoria": "0.01"
}
```

## 🌐 **Zapier Integration**

### Criar App Zapier

1. **Configurar REST Hook:**
```javascript
const options = {
  url: 'http://localhost:8000/mcp',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name: 'criar_conta_pagar',
      arguments: {
        cnpj_cpf_fornecedor: inputData.cnpj,
        razao_social_fornecedor: inputData.razao_social,
        numero_documento: inputData.numero_doc,
        data_vencimento: inputData.vencimento,
        valor_documento: inputData.valor,
        codigo_categoria: inputData.categoria
      }
    }
  })
};
```

## 📱 **Power Platform (Power Automate)**

### Criar Flow

1. **Trigger:** HTTP Request
2. **Action:** HTTP Request para Omie MCP
3. **Response:** Processar resposta JSON

**Exemplo de configuração:**
```json
{
  "method": "POST",
  "uri": "http://localhost:8000/mcp",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "@{triggerBody()['tool_name']}",
      "arguments": "@{triggerBody()['arguments']}"
    }
  }
}
```

## 🔧 **Configuração Avançada**

### Autenticação (Opcional)

Para ambientes de produção, adicione autenticação:

```python
# Adicionar ao servidor FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "seu_token_secreto":
        raise HTTPException(status_code=401, detail="Token inválido")
    return credentials.credentials
```

### HTTPS (Recomendado)

```python
# Configurar SSL
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')

uvicorn.run(app, host="0.0.0.0", port=8000, ssl_context=ssl_context)
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OMIE_APP_KEY=""
ENV OMIE_APP_SECRET=""

EXPOSE 8000

CMD ["python", "omie_http_server.py"]
```

## 🧪 **Testes de Integração**

### Teste com Claude

```bash
# Iniciar servidor
python omie_http_server.py

# Testar no Claude Desktop
"Consulte as categorias do Omie ERP"
```

### Teste com Copilot Studio

```bash
# Testar endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"consultar_categorias","arguments":{}}}'
```

### Teste com N8N

```bash
# Webhook de teste
curl -X POST http://n8n-url/webhook/omie-integration \
  -H "Content-Type: application/json" \
  -d '{"action":"criar_conta_pagar","cnpj_fornecedor":"16.726.230/0001-78","valor_documento":1000}'
```

## 📋 **Resumo de Endpoints**

| Plataforma | Método | Endpoint |
|------------|---------|----------|
| Claude Desktop | MCP | Configuração local |
| Claude API | HTTP | `POST /mcp` |
| Copilot Studio | OpenAPI | `GET /openapi.json` |
| N8N | Webhook | `POST /webhook/omie` |
| Zapier | REST | `POST /mcp` |
| Power Automate | HTTP | `POST /mcp` |

## 🚀 **Próximos Passos**

1. **Configurar sua plataforma preferida**
2. **Definir credenciais Omie**
3. **Testar integração básica**
4. **Implementar casos de uso específicos**
5. **Monitorar e otimizar performance**

---

**Todas as integrações estão prontas para uso!** 🎉