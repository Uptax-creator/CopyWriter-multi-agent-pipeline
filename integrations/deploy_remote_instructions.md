# 🚀 Deploy no N8N Remoto: Manual de Instruções

## 🎯 **Objetivo**
Fazer deploy do workflow **Omie MCP + Nibo MCP** no N8N remoto em:
**https://applications-n8nt.jg26hn.easypanel.host**

## 📋 **Pré-requisitos**

### ✅ **Status Atual**
- [x] N8N local instalado e funcionando
- [x] n8n-mcp package instalado globalmente
- [x] Omie MCP Server rodando (porta 3001)
- [x] Nibo MCP Server rodando (porta 3002)
- [x] Workflow JSON criado

### ❌ **Pendente**
- [ ] Acesso/credenciais do N8N remoto
- [ ] URLs públicas dos MCP servers
- [ ] Configuração de autenticação

## 🔧 **Métodos de Deploy**

### **Método 1: Manual via Interface Web** ⭐ **RECOMENDADO**

#### **Passo 1: Acessar N8N Remoto**
```
URL: https://applications-n8nt.jg26hn.easypanel.host
```

#### **Passo 2: Importar Workflow**
1. Fazer login no N8N remoto
2. Ir em **Workflows** → **Import from JSON**
3. Selecionar arquivo: `/integrations/n8n_omie_nibo_workflow.json`
4. Clicar em **Import**

#### **Passo 3: Configurar URLs dos MCP Servers**
**IMPORTANTE**: Alterar URLs nos nós HTTP Request de:
```
❌ ATUAL (localhost):
http://localhost:3001/mcp/tools/...
http://localhost:3002/mcp/tools/...

✅ PRODUÇÃO (necessário):
https://your-domain.com/omie-mcp/mcp/tools/...
https://your-domain.com/nibo-mcp/mcp/tools/...
```

#### **Passo 4: Ativar Workflow**
1. Salvar workflow
2. Ativar toggle "Active"
3. Testar webhook

### **Método 2: Via n8n-mcp CLI**

#### **Configurar Credenciais**
```bash
# Exportar variáveis de ambiente
export N8N_API_URL="https://applications-n8nt.jg26hn.easypanel.host/api/v1"
export N8N_API_KEY="YOUR_API_KEY_HERE"
```

#### **Comandos n8n-mcp**
```bash
# Verificar conexão
n8n-mcp status

# Importar workflow (se suportado)
n8n-mcp import /Users/kleberdossantosribeiro/omie-mcp/integrations/n8n_omie_nibo_workflow.json
```

### **Método 3: Via API REST**

#### **Importar via cURL**
```bash
curl -X POST "https://applications-n8nt.jg26hn.easypanel.host/api/v1/workflows" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/Users/kleberdossantosribeiro/omie-mcp/integrations/n8n_omie_nibo_workflow.json
```

## 🌐 **URLs de Produção Necessárias**

### **MCP Servers Públicos**
Para o workflow funcionar no N8N remoto, você precisa:

#### **Opção A: Deploy em DigitalOcean/VPS**
```
https://omie-mcp.your-domain.com      # Omie MCP Server
https://nibo-mcp.your-domain.com      # Nibo MCP Server
```

#### **Opção B: Túneis Temporários (Teste)**
```bash
# Usando ngrok (temporário)
ngrok http 3001  # Para Omie MCP
ngrok http 3002  # Para Nibo MCP
```

#### **Opção C: Modificar para uso local**
Se o N8N remoto pode acessar sua rede local:
```
http://YOUR_PUBLIC_IP:3001/mcp/tools/...
http://YOUR_PUBLIC_IP:3002/mcp/tools/...
```

## 🧪 **Testes Após Deploy**

### **Webhook de Teste**
```bash
# Testar conectividade
curl -X POST "https://applications-n8nt.jg26hn.easypanel.host/webhook/erp-sync" \
  -H "Content-Type: application/json" \
  -d '{"action": "test_connection"}'

# Sincronizar clientes
curl -X POST "https://applications-n8nt.jg26hn.easypanel.host/webhook/erp-sync" \
  -H "Content-Type: application/json" \
  -d '{"action": "sync_clients"}'
```

## 🔒 **Configuração de Credenciais**

### **No N8N Remoto**
1. Ir em **Credentials**
2. Criar credenciais para:
   - **Omie API**: App Key + App Secret
   - **Nibo API**: Token de acesso
   - **Webhooks**: Tokens de autenticação

### **No Claude Desktop (n8n-mcp)**
```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "n8n-mcp",
      "args": [],
      "env": {
        "N8N_API_URL": "https://applications-n8nt.jg26hn.easypanel.host/api/v1",
        "N8N_API_KEY": "YOUR_N8N_API_KEY_HERE"
      }
    }
  }
}
```

## 📊 **Monitoramento**

### **Verificar Status**
```bash
# Verificar execuções
curl "https://applications-n8nt.jg26hn.easypanel.host/api/v1/executions" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Verificar workflows ativos
curl "https://applications-n8nt.jg26hn.easypanel.host/api/v1/workflows" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 🚨 **Limitações Atuais**

### **Problema Principal**
❌ **MCP Servers estão rodando em localhost**
- Omie MCP: `http://localhost:3001`
- Nibo MCP: `http://localhost:3002`

### **Soluções**
1. **Deploy MCP Servers em produção** (recomendado)
2. **Usar túnels temporários** (teste)
3. **Modificar workflow para usar APIs diretas** (alternativa)

## 🎯 **Próximos Passos**

### **Imediato**
1. Acessar: https://applications-n8nt.jg26hn.easypanel.host
2. Fazer login/obter credenciais
3. Importar workflow manualmente

### **Produção**
1. Deploy MCP Servers em VPS
2. Configurar domínios públicos
3. Atualizar URLs no workflow
4. Configurar SSL/HTTPS

## 📞 **Status Atual**

✅ **Workflow criado e testado localmente**
✅ **n8n-mcp instalado e configurado**
❌ **Aguardando credenciais N8N remoto**
❌ **Aguardando URLs públicas MCP Servers**

**O workflow está pronto para deploy assim que tivermos:**
1. Acesso ao N8N remoto
2. URLs públicas dos MCP servers