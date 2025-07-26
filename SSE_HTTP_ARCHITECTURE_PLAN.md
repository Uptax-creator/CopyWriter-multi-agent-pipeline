# 🌐 PLANO ARQUITETURA SSE/HTTP PARA MÚLTIPLAS PLATAFORMAS

## 🎯 OBJETIVO
Criar versão SSE/HTTP do servidor MCP Omie para integração com:
- VS Code (MCP Extension)
- N8N (Custom Nodes)
- Microsoft Copilot (Plugins)
- Outras plataformas que suportam HTTP/WebSockets

## 🏗️ ARQUITETURA PROPOSTA

### **STACK TECNOLÓGICA**
```
┌─ Frontend Interfaces ─┐    ┌─ MCP Transport Layer ─┐    ┌─ Omie Integration ─┐
│ • VS Code Extension   │────│ • SSE (Server-Sent)    │────│ • FastMCP Core      │
│ • N8N Custom Nodes    │────│ • HTTP REST API        │────│ • Omie Client       │
│ • Copilot Plugins     │────│ • WebSocket Support    │────│ • Database Manager  │
│ • Web Dashboard       │────│ • CORS Configuration   │────│ • Tool Classifier   │
└───────────────────────┘    └────────────────────────┘    └─────────────────────┘
```

### **COMPONENTES PRINCIPAIS**

#### **1. SERVIDOR SSE/HTTP (TypeScript)**
```typescript
// Baseado no src/mcpserver/server.ts existente
class OmieSSEServer {
  - Express HTTP Server
  - SSE Transport Layer
  - MCP Protocol Handler
  - Tool Registry
  - Authentication Layer
}
```

#### **2. ADAPTADOR PYTHON ↔ TYPESCRIPT**
```python
# Ponte entre FastMCP (Python) e SSE Server (TypeScript)
class MCPBridge {
  - HTTP Client para TypeScript
  - Tool Discovery
  - Request/Response Translation
  - Error Handling
}
```

#### **3. CONFIGURAÇÕES MULTI-PLATAFORMA**
```yaml
# Config para diferentes plataformas
platforms:
  vscode:
    transport: "sse"
    port: 3001
    auth: "bearer"
  n8n:
    transport: "http"
    port: 3002
    auth: "api-key"
  copilot:
    transport: "https"
    port: 3003
    auth: "oauth2"
```

---

## 📋 ROADMAP DE IMPLEMENTAÇÃO

### **FASE 1: INFRAESTRUTURA BASE (2-3 dias)**

#### **Dia 1: Setup Base**
- ✅ Análise do server.ts existente
- 🔄 Configuração Express + SSE
- 🔄 Integração com FastMCP Python
- 🔄 Teste básico de comunicação

#### **Dia 2: MCP Protocol**
- 🔄 Implementar MCP Server completo
- 🔄 Tool discovery automático
- 🔄 Request/Response handling
- 🔄 Error management

#### **Dia 3: Validação**
- 🔄 Testes de conectividade
- 🔄 Performance benchmarks
- 🔄 Documentação básica

### **FASE 2: INTEGRAÇÕES ESPECÍFICAS (4-5 dias)**

#### **VS Code Integration**
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "omie": {
      "transport": "sse",
      "url": "http://localhost:3001/sse"
    }
  }
}
```

#### **N8N Custom Nodes**
```javascript
// N8N Node Registration
class OmieNode extends N8NNode {
  description = {
    name: 'Omie ERP',
    group: ['input'],
    version: 1,
    description: 'Integração Omie via MCP'
  }
}
```

#### **Microsoft Copilot Plugin**
```yaml
# Plugin Manifest
apiVersion: v1
kind: Plugin
metadata:
  name: omie-mcp
spec:
  runtime: http
  endpoint: https://your-domain.com/mcp
```

### **FASE 3: FEATURES AVANÇADAS (3-4 dias)**

#### **Dashboard Web**
- Interface para monitoramento
- Logs em tempo real
- Métricas de performance
- Gestão de conexões

#### **Sistema de Cache**
- Redis para cache distribuído
- Cache de autenticação
- Cache de respostas frequentes

#### **Autenticação Multi-Tenant**
- JWT para VS Code
- API Keys para N8N
- OAuth2 para Copilot

---

## 🔧 ESTRUTURA DE ARQUIVOS PROPOSTA

```
src/
├── mcpserver/
│   ├── server.ts           # ✅ Já existe (base)
│   ├── omie-server.ts      # 🔄 Servidor Omie específico
│   ├── bridge.py           # 🔄 Python ↔ TypeScript bridge
│   ├── package.json        # ✅ Já existe
│   ├── tsconfig.json       # ✅ Já existe
│   └── config/
│       ├── vscode.json     # Config VS Code
│       ├── n8n.json        # Config N8N
│       └── copilot.json    # Config Copilot
├── integrations/
│   ├── vscode/
│   │   ├── extension.json  # Extension manifest
│   │   └── settings.json   # MCP settings
│   ├── n8n/
│   │   ├── OmieNode.js     # Custom N8N node
│   │   └── package.json    # Node package
│   └── copilot/
│       ├── plugin.yaml     # Plugin manifest
│       └── api.json        # API specification
└── web/
    ├── dashboard.html      # Web dashboard
    ├── monitor.js          # Real-time monitoring
    └── api.js              # REST API client
```

---

## 🎮 ENDPOINTS E INTERFACES

### **MCP SSE ENDPOINTS**
```
GET  /sse               # Server-Sent Events stream
POST /mcp/initialize    # MCP initialization
POST /mcp/tools         # List available tools
POST /mcp/tools/{name}  # Execute specific tool
GET  /health            # Health check
GET  /metrics           # Prometheus metrics
```

### **PLATFORM-SPECIFIC ENDPOINTS**
```
# VS Code
GET  /vscode/config     # Extension configuration
POST /vscode/auth       # Authentication

# N8N  
GET  /n8n/nodes         # Available nodes
POST /n8n/execute       # Execute workflow step

# Copilot
GET  /copilot/manifest  # Plugin manifest
POST /copilot/chat      # Chat completion
```

---

## 🔍 FERRAMENTAS OMIE DISPONÍVEIS VIA SSE/HTTP

### **CONJUNTO COMPLETO (11 + 2 novas)**
```typescript
interface OmieTools {
  // Básicas (3)
  consultar_categorias: ToolDefinition;
  listar_clientes: ToolDefinition;
  consultar_contas_pagar: ToolDefinition;
  
  // Contas a Receber (2) - ✅ NOVA
  consultar_contas_receber: ToolDefinition;
  status_contas_receber: ToolDefinition;
  
  // Projetos (3)
  incluir_projeto: ToolDefinition;
  listar_projetos: ToolDefinition;
  excluir_projeto: ToolDefinition;
  
  // Lançamentos (2)
  incluir_lancamento: ToolDefinition;
  listar_lancamentos: ToolDefinition;
  
  // Contas Correntes (3)
  incluir_conta_corrente: ToolDefinition;
  listar_contas_correntes: ToolDefinition;
  listar_resumo_contas_correntes: ToolDefinition;
}
```

---

## 📊 CASOS DE USO POR PLATAFORMA

### **VS CODE - Desenvolvimento**
```typescript
// Exemplo de uso no VS Code
await mcp.callTool('consultar_contas_pagar', {
  status: 'vencido',
  pagina: 1
});
```

### **N8N - Automação**
```yaml
# Workflow N8N
workflow:
  - node: OmieNode
    operation: consultar_contas_receber
    parameters:
      status: a_vencer
      dias_antecedencia: 7
```

### **COPILOT - Assistente**
```
User: "Show me overdue invoices from Omie"
Copilot: *calls consultar_contas_pagar with status='vencido'*
```

---

## ⚡ PERFORMANCE E ESCALABILIDADE

### **MÉTRICAS ESPERADAS**
- **Latência**: < 500ms por request
- **Throughput**: > 100 requests/segundo
- **Concurrent Connections**: > 50 SSE clients
- **Memory Usage**: < 512MB

### **OTIMIZAÇÕES**
- Connection pooling para Omie API
- Response caching (Redis)
- Request batching
- Async/await em toda pipeline

---

## 🔒 SEGURANÇA

### **AUTHENTICATION**
```typescript
interface AuthConfig {
  vscode: "bearer" | "api-key";
  n8n: "api-key" | "webhook-signature";
  copilot: "oauth2" | "jwt";
}
```

### **RATE LIMITING**
```typescript
const rateLimits = {
  vscode: "100/hour",
  n8n: "1000/hour", 
  copilot: "500/hour"
};
```

---

## 📅 CRONOGRAMA DETALHADO

| Semana | Fase | Entregáveis | Status |
|--------|------|-------------|--------|
| **Semana 1** | Setup & Base | SSE Server + MCP Bridge | 📋 PLANEJADO |
| **Semana 2** | VS Code | Extension + Config | 📋 PLANEJADO |
| **Semana 3** | N8N | Custom Nodes + Tests | 📋 PLANEJADO |
| **Semana 4** | Copilot | Plugin + Integration | 📋 PLANEJADO |
| **Semana 5** | Web Dashboard | Monitoring + Deploy | 📋 PLANEJADO |

---

## 🎯 RESULTADO ESPERADO

### **DELIVERABLES FINAIS**
1. ✅ Servidor SSE/HTTP funcional (TypeScript)
2. ✅ VS Code Extension configurada
3. ✅ N8N Custom Nodes prontos
4. ✅ Microsoft Copilot Plugin
5. ✅ Web Dashboard para monitoramento
6. ✅ Documentação completa de integração

### **BENEFITS**
- 🔄 **Interoperabilidade**: Uma API, múltiplas plataformas
- ⚡ **Performance**: Cache e otimizações
- 🛡️ **Security**: Auth por plataforma
- 📊 **Monitoring**: Dashboard em tempo real

---

**Data**: 21/07/2025  
**Status**: 📋 PLANEJADO  
**ETA**: 22-28/07/2025 (5-7 dias úteis)  
**Responsável**: Claude + Kleber