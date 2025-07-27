# 🏗️ ARQUITETURA MCP UNIVERSAL - DOCUMENTAÇÃO TÉCNICA

## 📋 **RESUMO EXECUTIVO**

**Data**: 22/07/2025  
**Status**: Implementação iniciada  
**Objetivo**: Arquitetura híbrida para suportar múltiplos protocolos MCP em uma única base de código  

### **Problema Identificado**
- ❌ FastMCP incompatível com clientes MCP padrão (Claude Desktop, VS Code)
- ✅ Solução: Servidor MCP padrão funcional + Wrappers HTTP/SSE

### **Solução Proposta** 
Arquitetura multi-protocolo que atende:
- 🖥️ Claude Desktop (STDIO MCP)
- 🔧 VS Code (STDIO MCP) 
- 🐳 Docker (HTTP REST)
- 🔗 N8N (HTTP + SSE)
- ⚡ Zapier (HTTP REST)
- 👨‍💻 Microsoft Copilot (Plugin API + SSE)
- 🌐 Replit/Replit.dev (Container + HTTP)

---

## 🎯 **FASES DE IMPLEMENTAÇÃO**

### **FASE 1: CONSOLIDAÇÃO STDIO** ✅
- **Status**: Concluída
- **Deliverable**: `omie_mcp_standard_simple.py`
- **Funcionalidade**: 5 ferramentas Omie via protocolo MCP puro
- **Clientes suportados**: Claude Desktop

### **FASE 2: HTTP WRAPPER** 🔧
- **Status**: Planejada
- **Timeline**: 2-3 horas
- **Deliverable**: `http_mcp_server.py` (FastAPI)
- **Funcionalidade**: REST API wrapper sobre core MCP
- **Clientes suportados**: Docker, N8N (webhook), Zapier

### **FASE 3: SSE STREAMING** ⚡ 
- **Status**: Planejada  
- **Timeline**: 1-2 horas
- **Deliverable**: `sse_mcp_server.py`
- **Funcionalidade**: Real-time streaming para N8N + Microsoft Copilot
- **Protocolo**: Server-Sent Events com fallback WebSocket

### **FASE 4: UNIVERSAL LAUNCHER** 🎛️
- **Status**: Planejada
- **Timeline**: 1 hora  
- **Deliverable**: `universal_start.py`
- **Funcionalidade**: Auto-detectar protocolo e iniciar servidor apropriado

### **FASE 5: CLOUD DEPLOYMENT** ☁️
- **Status**: Planejada
- **Timeline**: 2-4 horas
- **Platforms**: Google Cloud Run, Docker Hub, Replit.dev
- **Funcionalidade**: Deploy automatizado multi-ambiente

---

## 🏗️ **ARQUITETURA TÉCNICA**

### **Core Engine**
```python
class UniversalMCPCore:
    """Engine centralizado para todas as 42 ferramentas Omie"""
    
    def __init__(self):
        self.omie_client = SimpleOmieClient()
        self.tools = {
            # 5 ferramentas validadas
            'incluir_cliente': self.incluir_cliente,
            'consultar_clientes': self.consultar_clientes,
            'consultar_categorias': self.consultar_categorias,
            'consultar_contas_pagar': self.consultar_contas_pagar,
            'consultar_contas_receber': self.consultar_contas_receber,
        }
    
    async def execute_tool(self, tool_name: str, arguments: dict):
        """Execução unificada independente de protocolo"""
        if tool_name in self.tools:
            return await self.tools[tool_name](**arguments)
        raise ToolNotFoundError(f"Ferramenta {tool_name} não encontrada")
```

### **Protocol Adapters**

#### **1. STDIO Adapter (Claude Desktop)**
```python
class STDIOMCPServer(UniversalMCPCore):
    """Protocolo MCP padrão via STDIO"""
    
    async def handle_stdio_request(self, request: dict):
        method = request.get("method")
        if method == "tools/call":
            params = request.get("params", {})
            result = await self.execute_tool(
                params.get("name"), 
                params.get("arguments", {})
            )
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"content": [{"type": "text", "text": result}]}
            }
```

#### **2. HTTP Adapter (Docker + N8N + Zapier)**
```python
from fastapi import FastAPI

class HTTPMCPServer(UniversalMCPCore):
    """REST API wrapper"""
    
    def __init__(self):
        super().__init__()
        self.app = FastAPI(title="Omie MCP Universal API")
        
    @app.post("/tools/{tool_name}/call")
    async def call_tool(self, tool_name: str, arguments: dict):
        result = await self.execute_tool(tool_name, arguments)
        return {"success": True, "data": result}
```

#### **3. SSE Adapter (Real-time + Microsoft Copilot)**
```python
class SSEMCPServer(UniversalMCPCore):
    """Server-Sent Events para streaming"""
    
    async def stream_tool_results(self, tool_name: str, arguments: dict):
        # Streaming para N8N workflows real-time
        async for chunk in self.execute_tool_streaming(tool_name, arguments):
            yield f"data: {json.dumps(chunk)}\\n\\n"
```

---

## 📦 **ESTRUTURA DE DEPLOYMENT**

### **Docker Multi-Stage Build**
```dockerfile
# Dockerfile.universal
FROM python:3.12-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# STDIO Stage
FROM base as stdio
COPY core/ ./core/
COPY protocols/stdio_server.py ./
EXPOSE 8000
CMD ["python", "stdio_server.py"]

# HTTP Stage  
FROM base as http
COPY core/ ./core/
COPY protocols/http_server.py ./
EXPOSE 8080
CMD ["python", "http_server.py"]

# Universal Stage
FROM base as universal
COPY . .
EXPOSE 8000 8080 8081
CMD ["python", "universal_start.py"]
```

### **Docker Compose Multi-Protocol**
```yaml
version: '3.8'
services:
  omie-mcp-stdio:
    build: 
      context: .
      target: stdio
    ports: ["8000:8000"]
    
  omie-mcp-http:
    build:
      context: .
      target: http  
    ports: ["8080:8080"]
    
  omie-mcp-sse:
    build:
      context: .
      target: universal
    ports: ["8081:8081"]
    environment:
      - PROTOCOL=sse
```

---

## 🎯 **CRONOGRAMA DE DEPLOY**

### **DOCKER DEPLOY TIMELINE**

| Fase | Timeline | Deliverable |
|------|----------|-------------|
| **Docker Local** | 2-3 horas | Container funcional localhost |
| **Docker Hub** | +1 hora | Imagem pública disponível |
| **Docker Compose** | +30 min | Multi-service setup |

**🚀 Estimativa Docker Ready: 4 horas**

### **CLOUD DEPLOY TIMELINE**  

| Platform | Timeline | Complexity |
|----------|----------|------------|
| **Google Cloud Run** | 2-3 horas | HTTP + Auto-scaling |
| **Replit.dev** | 1-2 horas | Dev environment |
| **Railway** | 1-2 horas | Git-based deploy |

**☁️ Estimativa Cloud Ready: 6 horas**

---

## 🔧 **REPLIT.DEV REQUIREMENTS**

### **Para implementar no Replit.dev precisamos:**

1. **✅ Python Environment**
   - Python 3.12+ 
   - Requirements.txt com httpx, fastapi, uvicorn
   
2. **🔧 Replit Configuration**
   ```toml
   # .replit
   run = "python universal_start.py"
   language = "python3"
   
   [env]
   PYTHONPATH = "."
   PROTOCOL = "auto"
   PORT = "8080"
   ```

3. **🌐 Web Service Setup**
   - HTTP endpoint para interface web
   - Health check endpoint `/health`
   - Auto-detect protocolo via headers

4. **📦 File Structure**
   ```
   replit-omie-mcp/
   ├── main.py              # Entry point
   ├── universal_start.py   # Multi-protocol launcher  
   ├── core/                # Engine + tools
   ├── protocols/           # STDIO + HTTP + SSE
   ├── requirements.txt     # Dependencies
   └── .replit             # Replit config
   ```

5. **🔗 Integration Points**
   - **N8N**: HTTP webhook nodes
   - **Claude Desktop**: STDIO local connection
   - **Web Interface**: Debug console built-in

**Replit.dev é ideal para desenvolvimento e testes, depois migrate para Google Cloud Run para produção.**

---

## ✅ **PRÓXIMOS PASSOS EXECUTIVOS**

1. **Implementar HTTP wrapper** (Fase 2)
2. **Criar SSE endpoint** (Fase 3)  
3. **Build Docker images** (Deploy Phase 1)
4. **Setup Google Cloud Run** (Deploy Phase 2)
5. **Configure Replit.dev** (Dev Environment)

**Timeline Total: 8-12 horas para arquitetura completa funcional**