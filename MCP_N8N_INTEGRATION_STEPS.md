# 🚀 MCP + N8N Integration - Passos Práticos

**N8N Status**: ✅ Online em http://localhost:5678  
**MCP Server**: ✅ mcp_simple_unified_server.py funcional  
**Objetivo**: Configurar integração completa agora  

---

## 📋 **PASSO A PASSO IMEDIATO**

### **1. Acessar N8N** 
🌐 Abrir: http://localhost:5678

### **2. Criar Workflow MCP**

#### **2.1 - Adicionar Webhook Node**
1. Click **"+ Add first step"**
2. Search: **"Webhook"**
3. Configure:
   - **HTTP Method**: `POST`
   - **Path**: `mcp-integration`
   - **Response Mode**: `Respond to Webhook`

#### **2.2 - Adicionar Code Node**
1. Click **"+"** após Webhook
2. Search: **"Code"** 
3. Select: **"Code (Run custom JavaScript)"**
4. **Cole este código**:

```javascript
// MCP Integration - Live Test
const request = $json;
const tool_name = request.tool_name || 'health_check';
const arguments_data = request.arguments || {};

// Configuração MCP
const MCP_CONFIG = {
  server_path: '/Users/kleberdossantosribeiro/omie-mcp/mcp_simple_unified_server.py',
  python_path: '/Users/kleberdossantosribeiro/omie-mcp/venv/bin/python',
  working_dir: '/Users/kleberdossantosribeiro/omie-mcp'
};

// Simulação de resposta MCP (modo demo)
let tool_result;

switch(tool_name) {
  case 'health_check':
    tool_result = {
      success: true,
      overall_status: 'ready_for_testing',
      services: {
        omie: { status: 'configured', ready: true },
        nibo: { status: 'configured', ready: true }
      },
      tools_available: 8,
      integration_status: 'n8n_connected',
      timestamp: new Date().toISOString()
    };
    break;
    
  case 'list_available_tools':
    tool_result = {
      success: true,
      total_tools: 8,
      omie_tools: [
        'omie_listar_clientes',
        'omie_consultar_categorias', 
        'omie_consultar_contas_pagar',
        'omie_consultar_contas_receber'
      ],
      nibo_tools: [
        'nibo_testar_conexao',
        'nibo_listar_clientes',
        'nibo_listar_fornecedores',
        'nibo_listar_contas_pagar'
      ],
      utility_tools: [
        'health_check',
        'list_available_tools'
      ]
    };
    break;
    
  case 'omie_listar_clientes':
    tool_result = {
      success: true,
      message: 'Demo: Listaria clientes do Omie ERP',
      sample_data: [
        { id: 1, nome: 'Cliente Demo 1', email: 'demo1@test.com' },
        { id: 2, nome: 'Cliente Demo 2', email: 'demo2@test.com' }
      ],
      pagination: { pagina: arguments_data.pagina || 1, total: 50 }
    };
    break;
    
  case 'nibo_testar_conexao':
    tool_result = {
      success: true,
      message: 'Demo: Conexão com Nibo testada',
      api_status: 'simulated_online',
      response_time: 156
    };
    break;
    
  default:
    tool_result = {
      success: false,
      error: `Ferramenta '${tool_name}' não encontrada`,
      available_tools: [
        'health_check', 'list_available_tools', 
        'omie_listar_clientes', 'nibo_testar_conexao'
      ]
    };
}

// Resposta completa
const response = {
  // Status da execução  
  execution: {
    tool_name: tool_name,
    arguments: arguments_data,
    timestamp: new Date().toISOString(),
    success: tool_result.success,
    mode: 'n8n_demo_integration'
  },
  
  // Resultado da ferramenta
  result: tool_result,
  
  // Status da integração
  integration: {
    n8n_version: '1.102.3',
    mcp_server_ready: true,
    docker_container: true,
    webhook_url: 'http://localhost:5678/webhook/mcp-integration'
  },
  
  // Comandos para teste real
  test_commands: {
    curl_example: `curl -X POST http://localhost:5678/webhook/mcp-integration \\
  -H "Content-Type: application/json" \\
  -d '{"tool_name":"${tool_name}","arguments":${JSON.stringify(arguments_data)}}'`,
    
    mcp_direct: `cd ${MCP_CONFIG.working_dir} && source venv/bin/activate && \\
python mcp_simple_unified_server.py --test`,
    
    mcp_stdio: `echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"${tool_name}","arguments":${JSON.stringify(arguments_data)}},"id":1}' | \\
${MCP_CONFIG.python_path} ${MCP_CONFIG.server_path}`
  },
  
  // Próximos passos
  next_steps: [
    'Testar este workflow via webhook',
    'Implementar Execute Command para STDIO real',
    'Configurar credenciais para APIs reais',
    'Adicionar error handling e logs',
    'Deploy em produção com SSL'
  ]
};

return response;
```

#### **2.3 - Adicionar Respond to Webhook**
1. Click **"+"** após Code
2. Search: **"Respond to Webhook"**
3. Configure:
   - **Respond With**: `JSON`
   - **Response Body**: `{{ JSON.stringify($json, null, 2) }}`

#### **2.4 - Conectar Nodes**
Drag arrows: **Webhook** → **Code** → **Respond to Webhook**

#### **2.5 - Salvar Workflow**
1. Click **"Save"** (canto superior direito)
2. Nome: `MCP Integration Test`
3. Click **"Save"**

---

## 🧪 **TESTAR INTEGRAÇÃO**

### **3. Obter Webhook URL**
1. Click no **Webhook node**
2. Copy **"Production URL"** 
3. Deve ser: `http://localhost:5678/webhook/mcp-integration`

### **4. Executar Testes**

Abrir terminal e executar:

```bash
# Teste 1: Health Check
curl -X POST http://localhost:5678/webhook/mcp-integration \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "health_check"}'

# Teste 2: Listar Tools
curl -X POST http://localhost:5678/webhook/mcp-integration \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_available_tools"}'

# Teste 3: Omie Clientes
curl -X POST http://localhost:5678/webhook/mcp-integration \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "omie_listar_clientes", "arguments": {"pagina": 1}}'

# Teste 4: Nibo Conexão
curl -X POST http://localhost:5678/webhook/mcp-integration \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "nibo_testar_conexao"}'
```

---

## 🔄 **UPGRADE PARA MCP REAL**

### **5. Implementar Execute Command (Opcional)**

Para usar protocolo MCP STDIO real:

1. **Add Node**: **Execute Command**
2. Configure:
   - **Command**: `/Users/kleberdossantosribeiro/omie-mcp/venv/bin/python`
   - **Parameters**: `/Users/kleberdossantosribeiro/omie-mcp/mcp_simple_unified_server.py`

3. **Add Node**: **Code** (para processar STDIO output)

---

## 📊 **RESULTADOS ESPERADOS**

### **Teste Health Check**:
```json
{
  "execution": {
    "tool_name": "health_check",
    "success": true,
    "mode": "n8n_demo_integration"
  },
  "result": {
    "overall_status": "ready_for_testing",
    "services": {
      "omie": { "status": "configured" },
      "nibo": { "status": "configured" }
    }
  }
}
```

### **Teste List Tools**:
```json
{
  "result": {
    "total_tools": 8,
    "omie_tools": ["omie_listar_clientes", "..."],
    "nibo_tools": ["nibo_testar_conexao", "..."]
  }
}
```

---

## ✅ **CHECKLIST DE EXECUÇÃO**

- [ ] N8N acessível em http://localhost:5678
- [ ] Webhook node configurado
- [ ] Code node com script MCP  
- [ ] Respond to Webhook conectado
- [ ] Workflow salvo como "MCP Integration Test"
- [ ] Webhook URL copiada
- [ ] Teste health_check executado via curl
- [ ] Teste list_available_tools executado
- [ ] Resultados JSON recebidos corretamente

---

## 🎯 **PRÓXIMOS PASSOS APÓS TESTE**

1. **Validar funcionamento** dos 4 testes
2. **Implementar Execute Command** para MCP STDIO
3. **Configurar credenciais reais** 
4. **Testar APIs Omie/Nibo** reais
5. **Adicionar monitoring e logs**
6. **Deploy em VPS** com SSL

---

**🚀 Pronto! Execute estes passos e me diga os resultados dos testes!**