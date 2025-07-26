# 🌐 ROTEIRO DE IMPLANTAÇÃO MULTI-PLATAFORMAS

## 📋 OVERVIEW
Guia completo para implantar Omie MCP em diferentes plataformas usando HTTP/SSE

---

## 🚀 1. SERVIDOR HTTP/SSE

### **Inicialização**
```bash
# Instalar dependências
pip install fastapi uvicorn

# Iniciar servidor
python mcp_http_sse_server.py

# Verificar status
curl http://localhost:8000/
```

### **Endpoints Disponíveis**
- **MCP Protocol**: `http://localhost:8000/mcp/`
- **HTTP API**: `http://localhost:8000/api/`  
- **SSE Events**: `http://localhost:8000/events`
- **Documentation**: `http://localhost:8000/docs`

---

## 💻 2. INTEGRAÇÃO VS CODE

### **Setup MCP Extension**
```json
// settings.json
{
    "mcp.servers": {
        "omie": {
            "transport": "http",
            "endpoint": "http://localhost:8000/mcp/"
        }
    }
}
```

### **Teste de Conexão**
```bash
# Verificar inicialização
curl http://localhost:8000/mcp/initialize

# Listar ferramentas
curl http://localhost:8000/mcp/tools/list

# Chamar ferramenta
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "consultar_categorias", "arguments": {"pagina": 1}}'
```

### **Comandos VS Code**
- `Ctrl+Shift+P > MCP: Connect to Server`
- `Ctrl+Shift+P > MCP: List Tools`
- `Ctrl+Shift+P > MCP: Call Tool`

---

## 🔗 3. INTEGRAÇÃO N8N

### **HTTP Request Node**
```json
{
    "method": "POST",
    "url": "http://localhost:8000/api/tools/{{$parameter.toolName}}",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "pagina": 1,
        "registros_por_pagina": 50
    }
}
```

### **Workflow N8N Exemplo**
```json
{
    "nodes": [
        {
            "name": "HTTP Request - Omie Categories",
            "type": "n8n-nodes-base.httpRequest",
            "parameters": {
                "url": "http://localhost:8000/api/tools/consultar_categorias",
                "method": "POST",
                "jsonParameters": true,
                "options": {},
                "bodyParametersJson": "{\"pagina\": 1}"
            }
        },
        {
            "name": "Process Response",
            "type": "n8n-nodes-base.function",
            "parameters": {
                "functionCode": "return items.map(item => {\n  const data = item.json.result.data;\n  return { json: data };\n});"
            }
        }
    ]
}
```

### **Ferramentas Disponíveis N8N**
- `consultar_categorias`
- `listar_clientes`
- `consultar_contas_pagar`
- `consultar_contas_receber`

---

## 🤖 4. INTEGRAÇÃO MICROSOFT COPILOT

### **Plugin Manifest**
```json
{
    "schema_version": "v2",
    "name_for_human": "Omie ERP Integration",
    "name_for_model": "omie_erp",
    "description_for_human": "Access Omie ERP data",
    "description_for_model": "Integration with Omie ERP system for categories, clients, and financial data",
    "api": {
        "type": "openapi",
        "url": "http://localhost:8000/docs",
        "is_user_authenticated": false
    }
}
```

### **Copilot Commands**
```
@omie_erp list categories
@omie_erp show clients with filter "test"
@omie_erp check overdue accounts payable
@omie_erp get accounts receivable status
```

---

## 🐳 5. DEPLOY DOCKER

### **Dockerfile HTTP**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements-http.txt .
RUN pip install -r requirements-http.txt

COPY mcp_http_sse_server.py .
COPY src/ src/
COPY config/ config/

EXPOSE 8000

CMD ["python", "mcp_http_sse_server.py"]
```

### **Docker Compose Multi-Platform**
```yaml
version: '3.8'
services:
  omie-mcp-http:
    build:
      context: .
      dockerfile: Dockerfile.http
    ports:
      - "8000:8000"
    environment:
      - OMIE_APP_KEY=${OMIE_APP_KEY}
      - OMIE_APP_SECRET=${OMIE_APP_SECRET}
    volumes:
      - ./config:/app/config
    restart: unless-stopped
    
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - omie-mcp-http
```

---

## 📊 6. MONITORAMENTO E MÉTRICAS

### **Health Checks**
```bash
# Status geral
curl http://localhost:8000/

# Health MCP
curl http://localhost:8000/mcp/initialize

# Lista de ferramentas
curl http://localhost:8000/api/tools

# SSE connection test
curl -H "Accept: text/event-stream" http://localhost:8000/events
```

### **Métricas de Performance**
```bash
# Teste de carga
ab -n 100 -c 10 http://localhost:8000/api/tools/consultar_categorias

# Monitor SSE
curl -H "Accept: text/event-stream" http://localhost:8000/events | head -20
```

---

## 🧪 7. TESTES AUTOMATIZADOS

### **Script de Teste Multi-Platform**
```bash
#!/bin/bash

echo "🧪 Testando Multi-Platform Deployment"

# Teste MCP Protocol
echo "Testing MCP..."
curl -s http://localhost:8000/mcp/initialize | jq .

# Teste HTTP API
echo "Testing HTTP API..."
curl -s http://localhost:8000/api/tools | jq .

# Teste SSE
echo "Testing SSE..."
timeout 5 curl -H "Accept: text/event-stream" http://localhost:8000/events

# Teste ferramentas
echo "Testing tools..."
curl -X POST http://localhost:8000/api/tools/consultar_categorias \
  -H "Content-Type: application/json" \
  -d '{"pagina": 1}' | jq .

echo "✅ Multi-platform tests completed"
```

---

## 🔧 8. CONFIGURAÇÕES ESPECÍFICAS

### **VS Code Extension Settings**
```json
{
    "mcp.omie": {
        "endpoint": "http://localhost:8000/mcp/",
        "timeout": 30000,
        "retries": 3,
        "tools": ["consultar_categorias", "listar_clientes"]
    }
}
```

### **N8N Environment Variables**
```bash
export N8N_OMIE_ENDPOINT="http://localhost:8000/api/tools"
export N8N_OMIE_TIMEOUT=30000
```

### **Nginx Proxy Configuration**
```nginx
upstream omie_mcp {
    server localhost:8000;
}

server {
    listen 80;
    server_name omie-mcp.local;
    
    location /api/ {
        proxy_pass http://omie_mcp/api/;
        proxy_set_header Host $host;
    }
    
    location /events {
        proxy_pass http://omie_mcp/events;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        proxy_buffering off;
    }
}
```

---

## 📋 9. CHECKLIST DE DEPLOY

### **Pré-Deploy**
- [ ] Servidor HTTP/SSE funcionando na porta 8000
- [ ] Credenciais Omie configuradas
- [ ] Dependencies instaladas (`fastapi`, `uvicorn`)
- [ ] Firewall liberado para porta 8000

### **VS Code Integration**
- [ ] MCP extension instalada
- [ ] Settings.json configurado
- [ ] Conexão testada
- [ ] Ferramentas listadas corretamente

### **N8N Integration**  
- [ ] N8N server rodando
- [ ] HTTP Request nodes configurados
- [ ] Workflow de teste criado
- [ ] Dados sendo processados

### **Microsoft Copilot**
- [ ] Plugin manifest criado
- [ ] API endpoint configurado  
- [ ] OpenAPI spec importado
- [ ] Commands funcionando

### **Docker Deployment**
- [ ] Dockerfile criado
- [ ] Docker compose configurado
- [ ] Container healthcheck OK
- [ ] Nginx proxy funcionando

---

## 🎯 RESUMO DE COMANDOS

```bash
# Iniciar servidor multi-platform
python mcp_http_sse_server.py

# Teste rápido
curl http://localhost:8000/api/tools/consultar_categorias -X POST -d '{}'

# Deploy Docker
docker-compose up -d

# Monitor SSE
curl -H "Accept: text/event-stream" http://localhost:8000/events
```

---

**Status**: ✅ PRONTO PARA IMPLANTAÇÃO MULTI-PLATAFORMAS  
**Última atualização**: 21/07/2025