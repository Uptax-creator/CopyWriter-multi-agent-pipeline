# Guia N8N Oficial - Integração Omie MCP

## ✅ Status: TOTALMENTE COMPATÍVEL COM N8N OFICIAL

Este guia utiliza **APENAS** nodes oficiais do N8N, sem dependências externas ou LangChain.

## 🔧 Nodes Oficiais Utilizados

- ✅ `n8n-nodes-base.webhook` - Webhook Trigger
- ✅ `n8n-nodes-base.httpRequest` - HTTP Request  
- ✅ `n8n-nodes-base.set` - Set/Extract Data
- ✅ `n8n-nodes-base.if` - Conditional Logic
- ✅ `n8n-nodes-base.respondToWebhook` - Webhook Response
- ✅ `n8n-nodes-base.manualTrigger` - Manual Trigger
- ✅ `n8n-nodes-base.scheduleTrigger` - Schedule Trigger
- ✅ `n8n-nodes-base.splitInBatches` - Split in Batches
- ✅ `n8n-nodes-base.wait` - Wait

## 📁 Workflows Disponíveis

### 1. Webhook Integration (PRINCIPAL)
**Arquivo:** `3_webhook_integration.json`
- ✅ Recebe requisições webhook
- ✅ Valida ferramentas disponíveis
- ✅ Executa tools via HTTP
- ✅ Retorna resposta formatada

### 2. MCP Server Trigger (CORRIGIDO)
**Arquivo:** `1_mcp_server_trigger_oficial.json`
- ✅ Simula protocolo MCP via webhook
- ✅ Suporta `tools/list` e `tools/call`
- ✅ Resposta no formato JSON-RPC 2.0

### 3. MCP Client Tool (CORRIGIDO)
**Arquivo:** `2_mcp_client_tool_oficial.json`
- ✅ Execução manual de tools
- ✅ Configuração de parâmetros
- ✅ Processamento de resultados

### 4. SSE Monitor (JÁ OFICIAL)
**Arquivo:** `4_sse_monitor.json`
- ✅ Monitoramento de saúde
- ✅ Execução agendada (30s)
- ✅ Logging de status

### 5. Test All Tools (NOVO)
**Arquivo:** `5_test_all_tools_oficial.json`
- ✅ Testa todas as 6 ferramentas
- ✅ Execução sequencial com delay
- ✅ Resultados formatados

## 🚀 Setup Rápido

### 1. Iniciar Servidor Omie MCP
```bash
cd /Users/kleberdossantosribeiro/omie-mcp
python3 omie_mcp_server_hybrid.py --mode http --port 3000
```

### 2. Importar Workflows no N8N
1. Abra N8N (http://localhost:5678)
2. Vá em **Workflows**
3. Clique **Import from file**
4. Selecione qualquer arquivo `.json` da pasta `n8n_workflows_oficial/`

### 3. Testar Integração

#### Webhook Test (Recomendado)
```bash
curl -X POST http://localhost:5678/webhook/omie-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "testar_conexao",
    "arguments": {}
  }'
```

#### Test All Tools
1. Importe `5_test_all_tools_oficial.json`
2. Execute manualmente
3. Verifique os resultados

## 📊 URLs de Teste

### Servidor MCP (Direto)
- Health: `http://localhost:3000/`
- Tools List: `http://localhost:3000/mcp/tools`
- Execute Tool: `http://localhost:3000/mcp/tools/testar_conexao`

### N8N Webhooks
- Main Webhook: `http://localhost:5678/webhook/omie-webhook`
- MCP Webhook: `http://localhost:5678/webhook/omie-mcp-webhook`

## 🔍 Troubleshooting

### Erro "Could not find property option"
- ✅ **RESOLVIDO**: Removidos todos os nodes LangChain
- ✅ **SOLUÇÃO**: Use workflows da pasta `n8n_workflows_oficial/`

### Erro "node type not found"
- ❌ **CAUSA**: Usando workflow com nodes LangChain
- ✅ **SOLUÇÃO**: Use workflows com sufixo `_oficial.json`

### Servidor não responde
```bash
# Verificar se está rodando
curl http://localhost:3000/

# Reiniciar se necessário
python3 omie_mcp_server_hybrid.py --mode http --port 3000
```

## 🎯 Ferramentas Disponíveis

1. **testar_conexao** - Teste de conectividade
2. **consultar_categorias** - Lista categorias
3. **consultar_departamentos** - Lista departamentos  
4. **consultar_tipos_documento** - Lista tipos de documento
5. **consultar_contas_pagar** - Lista contas a pagar
6. **consultar_contas_receber** - Lista contas a receber

## 📈 Próximos Passos

1. ✅ Importar workflow principal: `3_webhook_integration.json`
2. ✅ Testar com `curl` ou Postman
3. ✅ Integrar com seus sistemas existentes
4. ✅ Monitorar com `4_sse_monitor.json`

---

**Importante:** Todos os workflows foram testados e são 100% compatíveis com N8N oficial v1.0+