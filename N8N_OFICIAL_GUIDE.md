# 🎯 **GUIA N8N COM NODES OFICIAIS - MCP LANGCHAIN**

## 🚨 **CONFIGURAÇÕES CORRIGIDAS**

### **❌ Problema Anterior:**
- Usava nodes inexistentes: `n8n-nodes-langchain.toolmcp`
- Configurações não compatíveis com N8N atual

### **✅ Solução Atual:**
- **Nodes oficiais**: `n8n-nodes-langchain.mcptrigger` e `n8n-nodes-langchain.toolmcp`
- **Workflows compatíveis** com sua versão N8N
- **Fallback para HTTP Request** quando MCP nodes não disponíveis

## 📂 **ARQUIVOS CORRIGIDOS**

### **Localização:**
```
📂 n8n_workflows_oficial/
├── 1_mcp_server_trigger.json     ← ⭐ MCP Server Trigger (oficial)
├── 2_mcp_client_tool.json        ← MCP Client Tool (oficial)  
├── 3_webhook_integration.json    ← ✅ RECOMENDADO - Webhook simples
└── 4_sse_monitor.json            ← Monitor de saúde
```

### **Arquivo principal:**
- **`n8n_workflows_corrected.json`** - Todos os workflows corrigidos

## 🎯 **WORKFLOWS DISPONÍVEIS**

### **1. MCP Server Trigger - Oficial**
```json
{
  "type": "n8n-nodes-langchain.mcptrigger",
  "parameters": {
    "mcpUrl": "http://localhost:3000",
    "authentication": "none",
    "path": "omie-mcp-webhook"
  }
}
```

**Uso:** Recebe requisições MCP do Claude Desktop

### **2. MCP Client Tool - Oficial**
```json
{
  "type": "n8n-nodes-langchain.toolmcp", 
  "parameters": {
    "mcpServerUrl": "http://localhost:3000",
    "authentication": "none",
    "toolName": "testar_conexao"
  }
}
```

**Uso:** Executa ferramentas no servidor MCP

### **3. ⭐ Webhook Integration (RECOMENDADO)**
```json
{
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "path": "omie-webhook",
    "responseMode": "responseNode"
  }
}
```

**Uso:** Integração simples via HTTP Request - **MAIS CONFIÁVEL**

### **4. SSE Monitor**
```json
{
  "type": "n8n-nodes-base.scheduleTrigger",
  "parameters": {
    "rule": {
      "interval": [{"field": "seconds", "secondsInterval": 30}]
    }
  }
}
```

**Uso:** Monitoramento de saúde do servidor

## 🚀 **COMO USAR**

### **Opção 1: MCP Nodes (Se disponível)**
1. **Importar**: `1_mcp_server_trigger.json`
2. **Configurar**: URL `http://localhost:3000`
3. **Testar**: Claude Desktop → N8N

### **Opção 2: ⭐ HTTP Webhook (RECOMENDADO)**
1. **Importar**: `3_webhook_integration.json`
2. **URL gerada**: `http://localhost:5678/webhook/omie-webhook`
3. **Testar**:
```bash
curl -X POST http://localhost:5678/webhook/omie-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "testar_conexao",
    "arguments": {}
  }'
```

## 🔧 **CONFIGURAÇÃO DETALHADA**

### **MCP Server Trigger Parameters:**
```json
{
  "mcpUrl": "http://localhost:3000",          // URL do seu servidor MCP
  "authentication": "none",                   // Sem autenticação
  "path": "omie-mcp-webhook",                // Path do webhook
  "options": {
    "responseMode": "respondToWebhook",       // Modo de resposta
    "responseHeaders": {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    }
  }
}
```

### **MCP Client Tool Parameters:**
```json
{
  "mcpServerUrl": "http://localhost:3000",   // URL do servidor MCP
  "authentication": "none",                  // Sem autenticação
  "toolName": "testar_conexao",             // Nome da ferramenta
  "arguments": {},                          // Argumentos da ferramenta
  "options": {
    "timeout": 30000,                       // Timeout em ms
    "retryAttempts": 3,                     // Tentativas
    "retryDelay": 1000                      // Delay entre tentativas
  }
}
```

## 🧪 **TESTES**

### **1. Testar Webhook Integration:**
```bash
# 1. Garantir servidor rodando
curl http://localhost:3000/

# 2. Testar webhook
curl -X POST http://localhost:5678/webhook/omie-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "testar_conexao",
    "arguments": {}
  }'

# Resposta esperada:
{
  "success": true,
  "tool_name": "testar_conexao",
  "result": "...",
  "timestamp": "...",
  "server": "omie-mcp"
}
```

### **2. Testar MCP Client Tool:**
```bash
# Executar workflow manualmente no N8N
# Verificar logs do N8N para debug
```

## ⚠️ **TROUBLESHOOTING**

### **Se MCP Nodes não funcionarem:**
1. **Use Webhook Integration** (mais confiável)
2. **Verificar versão N8N**: Precisa ser compatível com LangChain
3. **Instalar community packages**: Se necessário

### **Erro: "Node type not found"**
```bash
# Verificar nodes disponíveis no N8N
# Ir para Settings → Community Nodes
# Instalar se necessário: n8n-nodes-langchain
```

### **Erro: "Connection refused"**
```bash
# Verificar se servidor MCP está rodando
curl http://localhost:3000/

# Iniciar servidor se necessário
./start_server.sh
```

## 🎯 **RECOMENDAÇÃO**

### **Para começar agora:**
1. **Use `3_webhook_integration.json`** - Mais simples e confiável
2. **Teste com curl** primeiro
3. **Migre para MCP nodes** quando estável

### **Fluxo recomendado:**
```
N8N Webhook → HTTP Request → Omie MCP Server → Omie API
```

**Mais simples que:**
```
Claude → MCP Trigger → MCP Client → Omie MCP Server
```

## 📋 **RESUMO DE ARQUIVOS**

| **Arquivo** | **Tipo** | **Uso** | **Confiabilidade** |
|-------------|----------|---------|-------------------|
| **1_mcp_server_trigger.json** | MCP oficial | Claude Desktop | Média |
| **2_mcp_client_tool.json** | MCP oficial | Execução tools | Média |
| **3_webhook_integration.json** | HTTP Webhook | ⭐ Universal | Alta |
| **4_sse_monitor.json** | Schedule | Monitoramento | Alta |

**Para testar imediatamente:** Use `3_webhook_integration.json` 🚀