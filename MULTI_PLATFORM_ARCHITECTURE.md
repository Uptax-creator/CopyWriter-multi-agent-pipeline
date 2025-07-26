# 🚀 OMIE MCP - ARQUITETURA MULTI-PLATAFORMA

## 📋 Objetivo
Implementar servidor MCP compatível com **SSE (Server-Sent Events)** e **Streamable HTTP** para integração com:
- ✅ Claude Desktop (atual - STDIO)
- 🔧 VS Code Extensions
- 🔧 N8N Workflows  
- 🔧 Microsoft Copilot
- 🔧 Custom Applications

---

## 🏗️ ARQUITETURA PROPOSTA

### 1. **Servidor Unificado Híbrido**
```python
# omie_mcp_universal_server.py
class OmieMCPUniversalServer:
    """Servidor MCP com suporte STDIO + HTTP + SSE"""
    
    def __init__(self):
        self.stdio_server = FastMCP()      # Claude Desktop
        self.http_server = FastAPI()       # REST APIs
        self.sse_handler = SSEManager()    # Real-time updates
```

### 2. **Protocolos Suportados**
| Protocolo | Uso Principal | Status | Referência |
|-----------|---------------|--------|------------|
| **STDIO** | Claude Desktop | ✅ Ativo | `/omie_fastmcp_extended.py` |
| **HTTP REST** | N8N, APIs | 🔧 Planejado | `/backup/20250715/omie_mcp_http.py` |
| **Server-Sent Events** | VS Code, Real-time | 🔧 Novo | Implementação necessária |
| **WebSocket** | Streaming | 📋 Futuro | Opcional |

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### **Fase 1: HTTP REST Server**
```python
# Baseado no trabalho anterior validado
@app.post("/mcp/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    """Endpoint HTTP para todas as 17 ferramentas"""
    tools_map = {
        "consultar_categorias": consultar_categorias,
        "listar_clientes": listar_clientes,
        "consultar_contas_pagar": consultar_contas_pagar,
        "consultar_contas_receber": consultar_contas_receber,
        # ... todas as 17 tools
    }
    return await tools_map[tool_name](**params)

@app.get("/mcp/resources/{resource_name}")
async def get_resource(resource_name: str):
    """Recursos MCP via HTTP"""
    return await resource_handlers[resource_name]()

@app.get("/mcp/prompts/{prompt_name}")
async def get_prompt(prompt_name: str):
    """Prompts MCP via HTTP"""
    return await prompt_handlers[prompt_name]()
```

### **Fase 2: Server-Sent Events**
```python
# Novo: SSE para atualizações em tempo real
@app.get("/mcp/events")
async def event_stream(request: Request):
    """Stream de eventos para VS Code/Copilot"""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            
            # Enviar status das ferramentas
            event_data = {
                "type": "tool_status", 
                "tools_count": 17,
                "last_execution": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(30)  # Heartbeat 30s
    
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream"
    )
```

### **Fase 3: VS Code Extension**
```typescript
// vscode-omie-mcp/src/extension.ts
import { EventSource } from 'eventsource';

class OmieMCPProvider {
    private eventSource: EventSource;
    
    constructor() {
        this.eventSource = new EventSource('http://localhost:8000/mcp/events');
        this.setupEventHandlers();
    }
    
    private setupEventHandlers() {
        this.eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateUI(data);
        };
    }
    
    async executeOmieTool(toolName: string, params: any) {
        const response = await fetch(`http://localhost:8000/mcp/tools/${toolName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        return response.json();
    }
}
```

### **Fase 4: N8N Custom Node**
```javascript
// n8n-nodes-omie-mcp/nodes/OmieMCP/OmieMCP.node.ts
import { INodeType, INodeTypeDescription } from 'n8n-workflow';

export class OmieMCP implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Omie MCP',
        name: 'omieMcp',
        group: ['integration'],
        version: 1,
        description: 'Execute Omie ERP operations via MCP',
        defaults: { name: 'Omie MCP' },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                options: [
                    { name: 'Consultar Categorias', value: 'consultar_categorias' },
                    { name: 'Listar Clientes', value: 'listar_clientes' },
                    { name: 'Consultar Contas Pagar', value: 'consultar_contas_pagar' },
                    // ... todas as 17 operações
                ]
            }
        ]
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const operation = this.getNodeParameter('operation', 0) as string;
        const params = this.getNodeParameter('params', 0, {}) as object;
        
        const response = await this.helpers.httpRequest({
            method: 'POST',
            url: `http://localhost:8000/mcp/tools/${operation}`,
            body: params,
            json: true
        });
        
        return [this.helpers.returnJsonArray([response])];
    }
}
```

---

## 📊 CRONOGRAMA DE IMPLEMENTAÇÃO

### **Sprint 1 (1-2 dias)**
- ✅ HTTP Server baseado em `/backup/20250715/omie_mcp_http.py`  
- ✅ Adaptar 17 ferramentas para HTTP endpoints
- ✅ Testes de integração N8N

### **Sprint 2 (2-3 dias)**  
- 🔧 Implementar Server-Sent Events
- 🔧 Criar VS Code Extension base
- 🔧 Documentação de APIs

### **Sprint 3 (3-4 dias)**
- 🔧 N8N Custom Node completo
- 🔧 Microsoft Copilot Plugin
- 🔧 Testes multi-plataforma

---

## 🎯 CRITÉRIOS DE SUCESSO

### **Compatibilidade**
- ✅ Claude Desktop (STDIO) - **Funcionando**
- 🔧 VS Code (HTTP + SSE) - **Planejado**  
- 🔧 N8N (HTTP REST) - **Planejado**
- 🔧 Copilot (HTTP + Events) - **Futuro**

### **Performance**
- 📊 Response time < 1s (HTTP)
- 📊 Event latency < 100ms (SSE)  
- 📊 Concurrent connections: 100+

### **Funcionalidades**
- 🎯 **17 ferramentas** disponíveis em todas as plataformas
- 🎯 **Real-time updates** via SSE
- 🎯 **Unified monitoring** dashboard
- 🎯 **Auto-discovery** de ferramentas

---

## 📦 ESTRUTURA DE ARQUIVOS

```
/omie-mcp/
├── src/
│   ├── servers/
│   │   ├── omie_mcp_universal.py      # Servidor principal
│   │   ├── stdio_handler.py           # Claude Desktop
│   │   ├── http_handler.py            # REST APIs
│   │   └── sse_handler.py             # Server-Sent Events
│   ├── integrations/
│   │   ├── vscode/                    # VS Code Extension
│   │   ├── n8n/                      # N8N Custom Node  
│   │   └── copilot/                  # Microsoft Copilot
│   └── shared/
│       ├── tools/                    # 17 ferramentas compartilhadas
│       └── client/                   # OmieClient unificado
├── docs/
│   ├── API_REFERENCE.md              # Documentação APIs
│   ├── VSCODE_SETUP.md              # Setup VS Code
│   └── N8N_INTEGRATION.md           # Guia N8N
└── tests/
    ├── integration/                  # Testes multi-plataforma
    └── performance/                  # Benchmarks
```

---

## 🚀 PRÓXIMOS PASSOS

1. **Finalizar T014** - Servidor estendido STDIO
2. **Implementar HTTP Server** - Baseado no trabalho validado anterior  
3. **Criar VS Code Extension** - Com SSE support
4. **Desenvolver N8N Node** - Custom integration
5. **Testes Multi-Plataforma** - Validação completa

**ETA: 1-2 semanas para versão multi-plataforma completa**

---

**Referências:**
- Servidor HTTP validado: `/backup/20250715/omie_mcp_http.py`
- Cliente HTTP: `/backup/20250715/claude_http_client.py`  
- Servidor STDIO atual: `/omie_fastmcp_extended.py`
- Documentação: `/CLAUDE.md`, `/TASK_CONTROL.md`