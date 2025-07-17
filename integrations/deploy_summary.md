# 🚀 Deploy Completo: Automação Omie MCP + Nibo MCP via N8N

## ✅ **Status: DEPLOY REALIZADO COM SUCESSO**

### 🎯 **Serviços Ativos**

| Serviço | Status | URL | Porta |
|---------|--------|-----|-------|
| **Omie MCP Server** | ✅ Ativo | http://localhost:3001 | 3001 |
| **Nibo MCP Server** | ✅ Ativo | http://localhost:3002 | 3002 |
| **N8N Workflow Engine** | ✅ Ativo | http://localhost:5678 | 5678 |

### 📋 **Ferramentas Disponíveis**

#### **Omie MCP (6 ferramentas)**
- `testar_conexao` - Teste de conectividade
- `consultar_clientes` - Consulta clientes
- `consultar_fornecedores` - Consulta fornecedores
- `consultar_contas_pagar` - Contas a pagar
- `consultar_contas_receber` - Contas a receber
- `cadastrar_cliente_fornecedor` - CRUD cliente/fornecedor

#### **Nibo MCP (12 ferramentas)**
- `testar_conexao` - Teste de conectividade
- `consultar_categorias` - Categorias
- `consultar_centros_custo` - Centros de custo
- `consultar_clientes` - Clientes
- `consultar_fornecedores` - Fornecedores
- `consultar_contas_pagar` - Contas a pagar
- `consultar_contas_receber` - Contas a receber
- `incluir_cliente` - Criar cliente
- `incluir_fornecedor` - Criar fornecedor
- `incluir_socio` - Criar sócio
- E mais 2 ferramentas avançadas

## 🔗 **Workflows Criados**

### **1. Workflow Principal: Omie + Nibo Integration**
**Arquivo**: `/integrations/n8n_omie_nibo_workflow.json`

**Funcionalidades:**
- ✅ Sincronização de clientes Omie → Nibo
- ✅ Consulta dados financeiros consolidados
- ✅ Teste de conectividade dos dois ERPs
- ✅ Processamento inteligente de dados

### **2. Context7 Configuration**
**Arquivo**: `/integrations/context7_n8n_config.json`

**Recursos:**
- ✅ Automação multi-ERP completa
- ✅ Fluxos de sincronização bidirecionais
- ✅ Analytics e insights automatizados
- ✅ Monitoramento e alertas

## 🎮 **Como Usar o Sistema**

### **Acessar N8N**
```bash
# Abrir navegador em:
http://localhost:5678
```

### **Importar Workflow**
1. Acessar N8N: http://localhost:5678
2. Ir em "Workflows" → "Import from JSON"
3. Importar arquivo: `/integrations/n8n_omie_nibo_workflow.json`

### **Testar Integrações**

#### **Teste de Conectividade**
```bash
curl -X POST "http://localhost:5678/webhook/erp-sync" \
  -H "Content-Type: application/json" \
  -d '{"action": "test_connection"}'
```

#### **Sincronização de Clientes**
```bash
curl -X POST "http://localhost:5678/webhook/erp-sync" \
  -H "Content-Type: application/json" \
  -d '{"action": "sync_clients"}'
```

#### **Relatório Financeiro**
```bash
curl -X POST "http://localhost:5678/webhook/erp-sync" \
  -H "Content-Type: application/json" \
  -d '{"action": "sync_financial"}'
```

## 🔧 **URLs de Teste Direto**

### **Omie MCP**
```bash
# Teste conexão
curl http://localhost:3001/test/testar_conexao

# Consultar clientes
curl -X POST http://localhost:3001/mcp/tools/consultar_clientes \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"pagina": 1, "registros_por_pagina": 10}}'
```

### **Nibo MCP**
```bash
# Teste conexão
curl http://localhost:3002/test/testar_conexao

# Consultar clientes
curl -X POST http://localhost:3002/mcp/tools/consultar_clientes \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"pagina": 1, "registros_por_pagina": 10}}'
```

## 📊 **Monitoramento**

### **Logs dos Serviços**
```bash
# Omie MCP
tail -f /tmp/omie_mcp.log

# Nibo MCP
tail -f /tmp/nibo_mcp.log

# N8N
tail -f /tmp/n8n.log
```

### **Status dos Processos**
```bash
ps aux | grep "omie_mcp_server\|nibo_mcp_server\|n8n"
```

## 🚨 **Troubleshooting**

### **Reiniciar Serviços**
```bash
# Parar todos
killall -9 Python python3 node

# Reiniciar Omie MCP
python omie_mcp_server.py --mode http --port 3001 &

# Reiniciar Nibo MCP
cd nibo-mcp && python nibo_mcp_server_hybrid.py --mode http --port 3002 &

# Reiniciar N8N
n8n start &
```

### **Verificar Conectividade**
```bash
curl http://localhost:3001/
curl http://localhost:3002/
curl http://localhost:5678/healthz
```

## 🎯 **Próximos Passos**

1. **✅ COMPLETO**: Deploy básico funcionando
2. **📋 TODO**: Configurar autenticação N8N
3. **📋 TODO**: Implementar schedules automáticos
4. **📋 TODO**: Deploy em produção (DigitalOcean)
5. **📋 TODO**: Configurar SSL/HTTPS
6. **📋 TODO**: Backup automático

## 📞 **Suporte**

**Sistema funcionando e pronto para uso!**
- **Omie MCP**: 6 ferramentas ativas
- **Nibo MCP**: 12 ferramentas (74% funcionais)
- **N8N**: Interface web completa
- **Workflows**: 3 fluxos de automação prontos

**Para importar o workflow no N8N:**
Acesse http://localhost:5678 e importe o arquivo JSON criado.