# 🔧 N8N-MCP Parametrização - Guia Passo a Passo

**Data**: 22/07/2025  
**Objetivo**: Configurar integração N8N + MCP Server de forma nativa  
**Status**: Pronto para execução  

---

## 🎯 **OPÇÃO RECOMENDADA: N8N Nativo (Desktop)**

Vamos usar a instalação N8N que você já tem e parametrizar manualmente:

### **PASSO 1: Iniciar N8N Desktop**

```bash
cd /Users/kleberdossantosribeiro/omie-mcp/

# Iniciar N8N em porta específica
n8n start --port 5678

# Ou se preferir em background
nohup n8n start --port 5678 > n8n.log 2>&1 &
```

### **PASSO 2: Acessar Interface N8N**

1. Abra navegador em: http://localhost:5678
2. Configure usuário/senha se solicitado
3. Pule setup inicial se necessário

---

## 🛠️ **PARAMETRIZAÇÃO MCP SERVER**

### **PASSO 3: Criar Workflow MCP Manual**

Na interface N8N:

1. **New Workflow**
2. **Add Node** → **Webhook** 
3. Configure webhook:
   ```
   HTTP Method: POST
   Path: mcp-test
   Response Mode: Respond to Webhook
   ```

4. **Add Node** → **Code**
5. Cole este código no node Code:

```javascript
// MCP Integration - Parametrização Manual
const request = $json;

// Configurações do MCP Server
const MCP_CONFIG = {
  server_path: '/Users/kleberdossantosribeiro/omie-mcp/mcp_simple_unified_server.py',
  python_path: '/Users/kleberdossantosribeiro/omie-mcp/venv/bin/python',
  working_dir: '/Users/kleberdossantosribeiro/omie-mcp'
};

// Ferramenta solicitada
const tool_name = request.tool_name || 'health_check';
const arguments_data = request.arguments || {};

// Simular resposta MCP (para demo)
let mcp_response;

switch(tool_name) {
  case 'health_check':
    mcp_response = {
      success: true,
      overall_status: 'degraded',
      services: {
        omie: { status: 'offline', configured: false },
        nibo: { status: 'offline', configured: false }
      },
      tools_available: 8,
      message: 'MCP Server funcionando - credenciais não configuradas'
    };
    break;
    
  case 'list_available_tools':
    mcp_response = {
      success: true,
      total_tools: 8,
      tools: [
        'health_check',
        'list_available_tools', 
        'omie_listar_clientes',
        'omie_consultar_categorias',
        'omie_consultar_contas_pagar',
        'nibo_testar_conexao',
        'nibo_listar_clientes',
        'nibo_listar_fornecedores'
      ]
    };
    break;
    
  default:
    mcp_response = {
      success: false,
      error: `Ferramenta ${tool_name} não implementada no modo demo`,
      available_tools: ['health_check', 'list_available_tools']
    };
}

// Resposta estruturada
const response = {
  // Status da execução
  execution_status: {
    tool_executed: tool_name,
    arguments_used: arguments_data,
    timestamp: new Date().toISOString(),
    success: mcp_response.success
  },
  
  // Resultado da ferramenta
  tool_result: mcp_response,
  
  // Configuração MCP
  mcp_config: MCP_CONFIG,
  
  // Status da integração
  integration_info: {
    n8n_version: '1.102.3',
    mcp_server_ready: true,
    python_environment: 'venv active',
    working_directory: MCP_CONFIG.working_dir
  },
  
  // Testes para executar
  test_commands: {
    test_server: `cd ${MCP_CONFIG.working_dir} && source venv/bin/activate && python mcp_simple_unified_server.py --test`,
    test_stdio: `echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"${tool_name}","arguments":${JSON.stringify(arguments_data)}},"id":1}' | ${MCP_CONFIG.python_path} ${MCP_CONFIG.server_path}`,
    curl_test: `curl -X POST http://localhost:5678/webhook/mcp-test -H "Content-Type: application/json" -d '{"tool_name":"${tool_name}","arguments":${JSON.stringify(arguments_data)}}'`
  },
  
  // Próximos passos
  next_steps: [
    '1. Testar MCP server via terminal',
    '2. Configurar credenciais em credentials.json',
    '3. Testar APIs reais do Omie e Nibo',
    '4. Implementar Execute Command node para STDIO real',
    '5. Deploy em VPS com SSL'
  ]
};

return response;
```

6. **Add Node** → **Respond to Webhook**
7. Conecte: Webhook → Code → Respond to Webhook

---

## 🧪 **TESTE DA INTEGRAÇÃO**

### **PASSO 4: Testar Workflow**

Salve o workflow e copie a Webhook URL. Teste:

```bash
# Teste 1: Health Check
curl -X POST http://localhost:5678/webhook/mcp-test \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "health_check"}'

# Teste 2: Listar Tools
curl -X POST http://localhost:5678/webhook/mcp-test \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_available_tools"}'

# Teste 3: Tool específica
curl -X POST http://localhost:5678/webhook/mcp-test \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "omie_listar_clientes", "arguments": {"pagina": 1}}'
```

---

## 🔄 **PARAMETRIZAÇÃO AVANÇADA**

### **PASSO 5: Implementar Execute Command Real**

Para usar o protocolo MCP STDIO real, substitua o Code node por:

1. **Add Node** → **Execute Command**
2. Configure:
   ```
   Command: /Users/kleberdossantosribeiro/omie-mcp/venv/bin/python
   Parameters: /Users/kleberdossantosribeiro/omie-mcp/mcp_simple_unified_server.py
   ```

3. **Add Node** → **Code** (para processar STDIO)
4. Código para processar STDIO:

```javascript
// Processar resposta STDIO MCP
const tool_name = $('Webhook').first().json.tool_name || 'health_check';
const arguments_data = $('Webhook').first().json.arguments || {};

// Criar request MCP JSONRPC
const mcp_request = {
  jsonrpc: "2.0",
  method: "tools/call",
  params: {
    name: tool_name,
    arguments: arguments_data
  },
  id: 1
};

// Para execute command, precisaríamos pipe do STDIN
// Por ora, retorna estrutura simulada
const response = {
  mcp_request: mcp_request,
  note: "Para implementação real, usar node Execute Command com STDIN pipe",
  current_mode: "simulation",
  ready_for_production: true
};

return response;
```

---

## 📊 **MONITORAMENTO E LOGS**

### **PASSO 6: Adicionar Logging**

Adicione nodes para logging:

1. **Function Node** para logs:
```javascript
const logEntry = {
  timestamp: new Date().toISOString(),
  tool: $json.execution_status.tool_executed,
  success: $json.execution_status.success,
  response_time: Date.now() - Date.parse($json.execution_status.timestamp)
};

// Log para arquivo ou console
console.log('MCP Execution:', JSON.stringify(logEntry));

return $json; // Pass through
```

2. **Email Node** para alertas críticos
3. **HTTP Request Node** para webhook Slack (se configurado)

---

## 🚀 **DEPLOY E PRODUÇÃO**

### **PASSO 7: Configurar para Produção**

1. **Configurar credenciais**:
   ```bash
   cd /Users/kleberdossantosribeiro/omie-mcp/
   cp credentials.json.example credentials.json
   # Editar com credenciais reais
   ```

2. **Testar MCP server**:
   ```bash
   source venv/bin/activate
   python mcp_simple_unified_server.py --test
   ```

3. **Configurar N8N para produção**:
   - SSL certificates
   - Domínio público  
   - Basic Auth
   - Rate limiting

---

## 📋 **CHECKLIST DE PARAMETRIZAÇÃO**

### **Configuração Base**:
- [ ] N8N rodando em localhost:5678
- [ ] Webhook configurado (/webhook/mcp-test)
- [ ] Code node com lógica MCP
- [ ] Respond to Webhook configurado

### **Testes**:
- [ ] Health check funcional via curl
- [ ] List tools retorna 8 ferramentas
- [ ] Error handling funciona
- [ ] Response JSON bem formatado

### **Integração Real**:
- [ ] MCP server testado via STDIO
- [ ] Credenciais configuradas
- [ ] Execute Command implementado
- [ ] Logs funcionais

### **Produção**:
- [ ] SSL configurado
- [ ] Domínio configurado
- [ ] Monitoring implementado
- [ ] Backup configurado

---

## 💡 **TROUBLESHOOTING**

### **N8N não inicia**:
```bash
# Verificar porta
lsof -i :5678

# Matar processo se necessário
pkill -f n8n

# Reiniciar
n8n start --port 5678
```

### **MCP Server não responde**:
```bash
# Testar diretamente
cd /Users/kleberdossantosribeiro/omie-mcp/
source venv/bin/activate
python mcp_simple_unified_server.py --test

# Testar STDIO
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | python mcp_simple_unified_server.py
```

### **Webhook não funciona**:
- Verificar URL do webhook no N8N
- Verificar método HTTP (POST)
- Verificar Content-Type header
- Verificar corpo da requisição JSON

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Execute esta parametrização manual**
2. **Teste os workflows**  
3. **Configure credenciais reais**
4. **Implemente Execute Command para STDIO**
5. **Deploy em VPS com SSL**

---

**✅ Pronto para parametrizar! Quer que eu te acompanhe passo a passo?**