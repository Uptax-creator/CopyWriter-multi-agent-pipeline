# 🔄 N8N Workflows - Guia de Ativação UPTAX

## 📋 **Status dos Workflows**
**Total**: 8 workflows prontos para importação  
**Localização**: `/Users/kleberdossantosribeiro/uptaxdev/n8n_workflows_ready/`  
**Context7 Integration**: ✅ 7 workflows habilitados  

---

## 🎯 **Workflows Disponíveis**

### **1. Master Orchestrator**
- **Arquivo**: `master_orchestrator.json`
- **Função**: Orquestração principal do sistema
- **Capabilities**: orchestration, workflow_management
- **Context7**: ✅ Enabled

### **2. Agent Orchestrator** 
- **Arquivo**: `mcp_agent_agent_orchestrator.json`
- **Função**: Coordenação entre agentes
- **Capabilities**: agent_coordination, workflow_management, task_distribution
- **Context7**: ✅ Enabled

### **3. Application Manager**
- **Arquivo**: `mcp_agent_application_manager.json` 
- **Função**: Gerenciamento de aplicações
- **Capabilities**: context7_integration, debugging_enabled
- **Context7**: ✅ Enabled

### **4. N8N-MCP Integration**
- **Arquivo**: `mcp_agent_n8n_mcp_integration.json`
- **Função**: Integração core N8N-MCP
- **Capabilities**: workflow_integration, api_connections, automation
- **Context7**: ✅ Enabled

### **5. Infrastructure Agent**
- **Arquivo**: `mcp_agent_infrastructure_agent.json`
- **Função**: Monitoramento e gestão de infraestrutura  
- **Capabilities**: system_monitoring, docker_management, resource_optimization
- **Context7**: ✅ Enabled

### **6. Senior Developer Agent**
- **Arquivo**: `mcp_agent_senior_developer_agent.json`
- **Função**: Análise de código e arquitetura
- **Capabilities**: code_analysis, debugging, architecture_design
- **Context7**: ✅ Enabled

### **7. Documentation Agent**
- **Arquivo**: `mcp_agent_documentation_agent.json`
- **Função**: Geração automática de documentação
- **Capabilities**: doc_generation, api_documentation, wiki_creation
- **Context7**: ✅ Enabled

### **8. Context7 SSE**
- **Arquivo**: `mcp_agent_context7_sse.json`
- **Função**: Server-Sent Events para Context7
- **Capabilities**: Real-time communication
- **Context7**: ⚠️ Special configuration

---

## 🚀 **Instruções de Importação**

### **Opção 1: N8N Development (Recomendado)**
```bash
# 1. Iniciar N8N Dev
docker-compose -f docker-compose.n8n-dev.yml up -d

# 2. Aguardar inicialização (2-3 minutos)
curl http://localhost:5679/healthz

# 3. Acessar interface
open http://localhost:5679
```

### **Opção 2: N8N Production** 
```bash
# Acessar N8N Prod (com novo token)
open https://applications-n8nt.jg26hn.easypanel.host
```

---

## 📥 **Processo de Importação Manual**

### **Passo a Passo**
1. **Acesse a Interface N8N**
   - Dev: `http://localhost:5679`
   - Prod: `https://applications-n8nt.jg26hn.easypanel.host`

2. **Navegue para Importação**
   - Menu: Settings → Import/Export
   - Clique em "Import workflow"

3. **Selecione os Arquivos**
   - Navegue até: `/Users/kleberdossantosribeiro/uptaxdev/n8n_workflows_ready/`
   - Importe na ordem sugerida (Master Orchestrator primeiro)

4. **Configure Credenciais**
   - Cada workflow pode precisar de configuração específica
   - Use as credenciais do `credentials.json`

5. **Ative os Workflows**
   - Toggle "Active" em cada workflow importado
   - Verifique status: Active/Inactive

---

## ⚙️ **Configurações Necessárias**

### **Credenciais por Workflow**

#### **Omie Integration**
```json
{
  "app_key": "2687508979155",
  "app_secret": "23ae858794e1cd879232c81105604b1f",
  "base_url": "https://app.omie.com.br/api/v1/"
}
```

#### **Nibo Integration**
```json
{
  "api_token": "F4F935978D824232A0363F5BDD69CE89",
  "base_url": "https://api.nibo.com.br/empresas/v1/organizations",
  "header_format": "apitoken: {token}"
}
```

#### **Context7 Integration**
```json
{
  "endpoint": "http://localhost:8080/context7",
  "transport": "sse",
  "project_prefix": "uptax-"
}
```

---

## 🔧 **Importação Automatizada**

### **Script de Importação**
```python
# Usar quando Docker estiver estável
python3 import_workflows_automated.py
```

### **Via MCP Tools**
```python
# Através do Claude Desktop
import_all_uptax_workflows_dev()
```

---

## 🔍 **Validação Pós-Importação**

### **Checklist**
- [ ] **8 workflows importados** com sucesso
- [ ] **7 workflows ativos** (Context7 SSE pode precisar config especial)
- [ ] **Credenciais configuradas** em cada workflow
- [ ] **Teste manual** de 1-2 workflows críticos
- [ ] **Logs sem erros** na interface N8N

### **Comandos de Teste**
```bash
# Testar conectividade N8N
curl http://localhost:5679/rest/workflows

# Testar workflow específico  
curl -X POST http://localhost:5679/rest/workflows/{id}/activate
```

---

## 🎯 **Ordem de Ativação Recomendada**

1. 🎭 **Master Orchestrator** (base de tudo)
2. 🔗 **N8N-MCP Integration** (conectividade core)
3. 🏗️ **Infrastructure Agent** (monitoramento)
4. 👨‍💻 **Senior Developer Agent** (análise)
5. 🤖 **Agent Orchestrator** (coordenação)
6. 📱 **Application Manager** (gestão apps)
7. 📚 **Documentation Agent** (docs)
8. 📡 **Context7 SSE** (real-time, por último)

---

## 🚨 **Troubleshooting**

### **Problemas Comuns**

#### **Docker Timeout**
```bash
# Solução: Usar recovery script
./docker-recovery.sh
```

#### **N8N Não Responde**
```bash
# Verificar container
docker ps | grep n8n
docker logs n8n-dev
```

#### **Import Falha**
- Verificar formato JSON dos workflows
- Conferir credenciais no `credentials.json`
- Tentar importação individual por workflow

#### **Context7 Não Conecta**
```bash
# Verificar porta 8080
lsof -i :8080
curl http://localhost:8080/context7
```

---

## 📊 **Monitoramento Pós-Ativação**

### **Métricas a Acompanhar**
- **Workflows ativos**: 8/8
- **Execuções bem-sucedidas**: > 95%
- **Tempo médio de execução**: < 30s
- **Erros de conectividade**: < 1%

### **Dashboard de Monitoramento**
```bash
# Ativar dashboard (opcional)
python3 start_monitoring_dashboard.py
open http://localhost:8080/dashboard
```

---

## ✅ **Conclusão**

Com os **8 workflows prontos**, o sistema UPTAX terá:
- ✅ **Orquestração inteligente** multi-agente
- ✅ **Integração completa** Omie + Nibo + Context7
- ✅ **Monitoramento automatizado** de infraestrutura  
- ✅ **Documentação auto-gerada** 
- ✅ **Debugging avançado** em tempo real

**Próximo passo**: Obter novo token N8N Prod e executar importação!

---
**Documentado em**: 24/07/2025  
**Para**: UPTAX Platform v3.0_unified  
**Status**: ⏳ Aguardando ativação Docker/N8N