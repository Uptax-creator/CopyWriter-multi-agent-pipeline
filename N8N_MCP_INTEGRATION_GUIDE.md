# 🎯 **GUIA COMPLETO: N8N + MCP SERVER INTEGRATION**

## 🚀 **CONFIGURAÇÕES OTIMIZADAS CRIADAS**

### **1. MCP Server Trigger (Recomendado 2024-2025)**
- **Arquivo**: `mcp_server_trigger_optimized`
- **Protocolo**: SSE (Server-Sent Events) com fallback
- **Uso**: Trigger automático para eventos do servidor MCP
- **Vantagens**: Reconexão automática, baixa latência

### **2. MCP Client Tool - SSE Streamable**
- **Arquivo**: `mcp_client_tool_sse_optimized`
- **Protocolo**: SSE com filtragem de eventos
- **Uso**: Cliente para consumir eventos do servidor MCP
- **Vantagens**: Filtragem inteligente, processamento diferenciado

### **3. HTTP Streamable Workflow (Moderno)**
- **Arquivo**: `mcp_http_streamable_workflow`
- **Protocolo**: HTTP Streamable (recomendado)
- **Uso**: Alternativa moderna ao SSE
- **Vantagens**: Melhor performance, mais estável

### **4. Tool Execution Workflow (Completo)**
- **Arquivo**: `mcp_tool_execution_workflow`
- **Protocolo**: HTTP + SSE híbrido
- **Uso**: Execução completa de ferramentas MCP
- **Vantagens**: Validação, logs, tratamento de erros

## 🔧 **CONFIGURAÇÃO AMBIENTE N8N**

### **Variáveis de Ambiente Necessárias**
```bash
# Docker N8N
N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
N8N_MCP_SERVER_URL=http://localhost:3000
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_SECURE_COOKIE=false
N8N_PROTOCOL=http
N8N_HOST=localhost
N8N_PORT=5678
```

### **docker-compose.yml para N8N + MCP**
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
      - N8N_MCP_SERVER_URL=http://omie-mcp:3000
      - N8N_WEBHOOK_URL=http://localhost:5678/webhook
      - N8N_SECURE_COOKIE=false
      - N8N_PROTOCOL=http
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - omie-mcp
    networks:
      - mcp-network

  omie-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - ENV=production
      - DEBUG=false
    networks:
      - mcp-network

volumes:
  n8n_data:

networks:
  mcp-network:
    driver: bridge
```

## 📊 **COMPARAÇÃO DE PROTOCOLOS**

| **Protocolo** | **Latência** | **Confiabilidade** | **Complexidade** | **Suporte 2025** |
|---------------|--------------|--------------------|------------------|-------------------|
| **SSE** | Baixa | Média | Baixa | ⚠️ Deprecado |
| **HTTP Streamable** | Baixa | Alta | Média | ✅ Recomendado |
| **WebSocket** | Muito Baixa | Alta | Alta | ✅ Futuro |
| **HTTP Request** | Média | Alta | Baixa | ✅ Estável |

## 🎯 **ENDPOINTS PARA N8N**

### **Para seus workflows N8N, use:**

#### **1. SSE Events (Monitoramento)**
```
URL: http://localhost:3000/sse/events
Method: GET
Headers: Accept: text/event-stream
```

#### **2. Tool Execution (Ações)**
```
URL: http://localhost:3000/mcp/tools/{tool_name}
Method: POST
Headers: Content-Type: application/json
Body: {"arguments": {...}}
```

#### **3. Tool Streaming (Tempo Real)**
```
URL: http://localhost:3000/sse/tools/{tool_name}
Method: GET
Headers: Accept: text/event-stream
```

#### **4. Health Check**
```
URL: http://localhost:3000/test/testar_conexao
Method: GET
```

## 🔧 **CONFIGURAÇÃO PASSO A PASSO**

### **Passo 1: Preparar Ambiente**
```bash
# 1. Iniciar seu servidor MCP
python omie_mcp_server_hybrid.py --mode http --port 3000

# 2. Verificar se está respondendo
curl http://localhost:3000/

# 3. Testar SSE
curl -N -H "Accept: text/event-stream" http://localhost:3000/sse/events
```

### **Passo 2: Importar Workflows**
1. Abra N8N em `http://localhost:5678`
2. Vá em **Workflows** → **Import from JSON**
3. Cole o conteúdo de `n8n_mcp_configurations.json`
4. Escolha o workflow desejado

### **Passo 3: Configurar Credenciais**
```json
{
  "name": "MCP Server Auth",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer YOUR_TOKEN_HERE"
  }
}
```

### **Passo 4: Testar Conexão**
1. Execute o workflow **Tool Execution**
2. Envie POST para webhook:
```bash
curl -X POST http://localhost:5678/webhook/omie-tools \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "testar_conexao", "arguments": {}}'
```

## 🐛 **TROUBLESHOOTING**

### **Erro: "Could not connect to MCP server"**
```bash
# Verificar se servidor está rodando
curl http://localhost:3000/

# Verificar logs
docker logs omie-mcp-server

# Reiniciar servidor
docker restart omie-mcp-server
```

### **Erro: "SSE connection failed"**
```bash
# Testar SSE endpoint
curl -N -H "Accept: text/event-stream" http://localhost:3000/sse/events

# Verificar headers CORS
curl -H "Origin: http://localhost:5678" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Accept" \
     -X OPTIONS http://localhost:3000/sse/events
```

### **Erro: "Tool not found"**
```bash
# Listar ferramentas disponíveis
curl http://localhost:3000/mcp/tools | jq '.tools[].name'

# Testar ferramenta específica
curl http://localhost:3000/test/testar_conexao
```

## 🚀 **OTIMIZAÇÕES AVANÇADAS**

### **1. Nginx Proxy para Produção**
```nginx
# /etc/nginx/sites-available/mcp-server
server {
    listen 80;
    server_name your-domain.com;
    
    location /sse/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **2. Monitoramento com Prometheus**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### **3. Alertas Slack/Discord**
```json
{
  "name": "MCP Server Alerts",
  "trigger": "webhook",
  "actions": [
    {
      "type": "slack",
      "webhook_url": "YOUR_SLACK_WEBHOOK",
      "message": "🚨 MCP Server: {{ $json.alert }}"
    }
  ]
}
```

## 📈 **MÉTRICAS DE PERFORMANCE**

| **Métrica** | **Valor Esperado** | **Monitoramento** |
|-------------|-------------------|-------------------|
| **Latência SSE** | < 100ms | Prometheus |
| **Uptime** | > 99.5% | Healthcheck |
| **Throughput** | > 1000 req/min | N8N logs |
| **Erro Rate** | < 1% | Dashboard |

## 🎯 **PRÓXIMOS PASSOS**

1. **Teste imediato**: Use `mcp_tool_execution_workflow`
2. **Produção**: Implemente `mcp_http_streamable_workflow`
3. **Monitoramento**: Configure `mcp_server_trigger_optimized`
4. **Escalabilidade**: Use Docker Compose completo

---

**✅ Todas as configurações estão prontas para uso imediato!**

**Para começar agora:**
1. Importe `mcp_tool_execution_workflow` no N8N
2. Inicie servidor: `python omie_mcp_server_hybrid.py --mode http --port 3000`
3. Teste webhook: `curl -X POST http://localhost:5678/webhook/omie-tools -d '{"tool_name": "testar_conexao"}'`

**Suporte disponível nos arquivos:**
- `n8n_mcp_configurations.json` - Configurações completas
- `DIAGNOSTIC_REPORT.md` - Análise técnica
- `DEPLOYMENT_ANALYSIS.md` - Estratégias de deploy