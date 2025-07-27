# 🧪 N8N + MCP Integration - Plano de Testes

**Data**: 22/07/2025  
**Objetivo**: Testar integração completa MCP Server Unificado + N8N Native Client  
**Status**: Ready para execução  

---

## 🏗️ **AMBIENTE ATUAL DETECTADO**

### ✅ **Software Instalado**:
```
✅ N8N: v1.102.3 (/Users/kleberdossantosribeiro/.nvm/versions/node/v22.17.0/bin/n8n)
✅ Python 3.12.11 (venv ativo)
✅ MCP Servers: Implementados e funcionais
✅ Credenciais: credentials.json configurado
```

### 🎯 **Arquivos Criados**:
```
✅ mcp_unified_tools_server.py - Servidor MCP unificado
✅ workflow_6_mcp_client_native.json - Workflow N8N nativo
✅ Workflows 1-5: HTTP-based integration workflows
```

---

## 📋 **PLANO DE TESTE PASSO A PASSO**

### **FASE 1: Preparação do Ambiente**

#### **1.1 - Validar Servidor MCP Unificado**
```bash
cd /Users/kleberdossantosribeiro/omie-mcp/
source venv/bin/activate

# Testar servidor MCP via STDIO
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | python mcp_unified_tools_server.py

# Testar ferramentas específicas
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"health_check","arguments":{}},"id":2}' | python mcp_unified_tools_server.py
```

#### **1.2 - Instalar Dependências N8N-MCP**
```bash
# Se necessário, instalar node MCP client
npm install -g @modelcontextprotocol/client

# Verificar se N8N tem o node mcpClient disponível
n8n --help | grep mcp
```

#### **1.3 - Configurar Instância N8N Local**
```bash
# Opção A: N8N Desktop (existente)
n8n start

# Opção B: N8N Docker (para testes isolados)
docker run -d \
  --name n8n-mcp-test \
  -p 5678:5678 \
  -v ~/omie-mcp/n8n_workflows:/home/node/.n8n/workflows \
  -v ~/omie-mcp/credentials.json:/home/node/.n8n/credentials.json \
  n8nio/n8n

# Opção C: N8N com volume de projeto
docker run -d \
  --name n8n-mcp-integration \
  -p 5679:5678 \
  -v $(pwd):/workspace \
  -w /workspace \
  n8nio/n8n
```

---

### **FASE 2: Testes de Integração**

#### **2.1 - Teste Manual MCP Server**
```bash
# Navegar para diretório
cd /Users/kleberdossantosribeiro/omie-mcp/

# Ativar ambiente virtual
source venv/bin/activate

# Testar health check
python -c "
import asyncio
import sys
sys.path.append('.')
from mcp_unified_tools_server import *

async def test():
    result = health_check()
    print(f'Health Check: {result}')
    
    tools = list_available_tools()
    print(f'Tools Available: {tools[\"total_tools\"]}')

asyncio.run(test())
"
```

#### **2.2 - Importar Workflow no N8N**
1. **Acessar N8N**: http://localhost:5678
2. **Import Workflow**: 
   - Go to **Workflows** → **Import from File**
   - Select `workflow_6_mcp_client_native.json`
3. **Configurar Credenciais**:
   - Configurar paths do Python e script
   - Testar conexão MCP

#### **2.3 - Testes de Ferramentas via N8N**

##### **Teste 1: Health Check**
```bash
curl -X POST http://localhost:5678/webhook/mcp-unified-tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "health_check",
    "arguments": {}
  }'
```

##### **Teste 2: Listar Clientes Omie**
```bash
curl -X POST http://localhost:5678/webhook/mcp-unified-tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "omie_listar_clientes",
    "arguments": {
      "pagina": 1,
      "registros_por_pagina": 5
    }
  }'
```

##### **Teste 3: Listar Ferramentas**
```bash
curl -X POST http://localhost:5678/webhook/mcp-unified-tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_available_tools",
    "arguments": {}
  }'
```

##### **Teste 4: Sync Simulado**
```bash
curl -X POST http://localhost:5678/webhook/mcp-unified-tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "sync_clientes_between_erps",
    "arguments": {
      "dry_run": true
    }
  }'
```

---

### **FASE 3: Testes Avançados**

#### **3.1 - Chat + AI Agent Integration**

Criar workflow adicional para integração com AI:

```json
{
  "name": "MCP + AI Chat Integration",
  "nodes": [
    {
      "name": "Chat Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "AI Agent (OpenAI/Claude)",
      "type": "n8n-nodes-base.openAi"
    },
    {
      "name": "MCP Tool Executor",
      "type": "n8n-nodes-base.mcpClient"
    },
    {
      "name": "Response Formatter",
      "type": "n8n-nodes-base.code"
    }
  ]
}
```

#### **3.2 - SSE Streaming Integration**

Testar integração SSE com N8N:

```bash
# Test SSE endpoint
curl -N -H "Accept: text/event-stream" \
  http://localhost:8082/sse/stream

# N8N SSE Consumer node configuration
```

#### **3.3 - Performance e Load Testing**

```bash
# Teste de carga básico
for i in {1..10}; do
  curl -X POST http://localhost:5678/webhook/mcp-unified-tools \
    -H "Content-Type: application/json" \
    -d '{"tool_name": "health_check"}' &
done
wait

# Monitorar performance
```

---

### **FASE 4: Validação e Documentação**

#### **4.1 - Checklist de Validação**
- [ ] Servidor MCP responde via STDIO
- [ ] N8N conecta ao servidor MCP
- [ ] Todas as ferramentas são listadas
- [ ] Ferramentas Omie funcionam
- [ ] Ferramentas Nibo funcionam
- [ ] Error handling funciona
- [ ] Performance é adequada (<2s)

#### **4.2 - Resultados Esperados**

**Health Check Response:**
```json
{
  "execution": {
    "tool_executed": "health_check",
    "success": true
  },
  "tool_result": {
    "success": true,
    "overall_status": "healthy",
    "services": {
      "omie": {"status": "online"},
      "nibo": {"status": "online"}
    }
  },
  "available_tools": {
    "total": 12,
    "omie_tools": 6,
    "nibo_tools": 4,
    "utility_tools": 2
  }
}
```

---

## 🐳 **OPÇÕES DE AMBIENTE**

### **Opção A: Desktop Nativo**
✅ **Prós**: Rápido, direto  
⚠️ **Contras**: Pode interferir com setup atual  

**Setup**:
```bash
cd /Users/kleberdossantosribeiro/omie-mcp/
source venv/bin/activate
n8n start --port 5678
```

### **Opção B: Docker Isolado** ⭐ **RECOMENDADO**
✅ **Prós**: Isolado, limpo, reproduzível  
✅ **Contras**: Setup inicial maior  

**Setup**:
```bash
# Criar docker-compose para teste
cat > docker-compose.n8n-test.yml << 'EOF'
version: '3.8'
services:
  n8n-test:
    image: n8nio/n8n
    container_name: n8n-mcp-test
    ports:
      - "5679:5678"
    volumes:
      - ./n8n_workflows:/home/node/.n8n/workflows
      - ./credentials.json:/workspace/credentials.json
      - .:/workspace
    working_dir: /workspace
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
    command: n8n start
EOF

docker-compose -f docker-compose.n8n-test.yml up -d
```

### **Opção C: Hybrid** 
N8N Desktop + MCP Docker  

---

## 🎯 **NEXT STEPS**

1. **Escolher ambiente** (recomendo Opção B - Docker)
2. **Executar FASE 1** - Preparação
3. **Executar testes** das FASES 2-3
4. **Validar resultados**
5. **Criar documentação final**

---

## 💡 **TROUBLESHOOTING**

### **MCP Server não conecta**:
```bash
# Verificar paths
which python
ls -la mcp_unified_tools_server.py

# Verificar dependências
pip list | grep fastmcp
pip list | grep httpx
```

### **N8N MCP Client não disponível**:
```bash
# Verificar versão N8N
n8n --version

# Instalar MCP client se necessário  
npm install -g @modelcontextprotocol/client
```

### **Credenciais não funcionam**:
```bash
# Validar credentials.json
cat credentials.json | jq '.'

# Testar APIs diretamente
python -c "
import json
with open('credentials.json') as f:
    creds = json.load(f)
    print('Omie:', bool(creds.get('omie', {}).get('app_key')))
    print('Nibo:', bool(creds.get('nibo', {}).get('api_key')))
"
```

---

**🚀 Pronto para iniciar os testes integrados!**

**Qual opção de ambiente você prefere começar?**
- **A**: Desktop nativo (rápido)
- **B**: Docker isolado (recomendado)
- **C**: Hybrid setup