# 🤖 UPTAX - Matriz de Atribuições dos Agentes MCP

## 🏆 **HIERARQUIA E RESPONSABILIDADES**

### **👨‍💻 SENIOR DEVELOPER AGENT**
- **Arquivo**: `senior_developer_agent_mcp.py`
- **Prioridade**: ⭐⭐⭐⭐⭐ (Crítico)
- **Status**: ✅ Ativo via Claude Desktop MCP

#### **🎯 Responsabilidades:**
- **Arquitetura de Software**: Decisões de design patterns, estrutura de código
- **Code Review**: Análise de qualidade, segurança, performance
- **Technical Leadership**: Orientar decisões técnicas complexas
- **Problem Solving**: Resolver bugs críticos e issues arquiteturais

#### **🛠️ Tools Disponíveis:**
- `senior_developer_consultation` - Consulta especializada
- `architecture_review` - Revisão de arquitetura
- `code_quality_analysis` - Análise de qualidade
- `technical_recommendation` - Recomendações técnicas

#### **📞 Quando Usar:**
- ✅ Implementar nova funcionalidade complexa
- ✅ Resolver erro crítico não documentado
- ✅ Decisões de arquitetura (Database, APIs, Patterns)
- ✅ Otimização de performance crítica
- ❌ Tarefas simples de configuração
- ❌ Documentação básica

---

### **🎭 AGENT ORCHESTRATOR**
- **Arquivo**: `agent_orchestrator_mcp.py`
- **Prioridade**: ⭐⭐⭐⭐⭐ (Crítico)
- **Status**: ✅ Ativo via Claude Desktop MCP

#### **🎯 Responsabilidades:**
- **Coordenação Multi-Agente**: Orquestrar tarefas entre agentes
- **Task Distribution**: Distribuir tarefas para agentes especializados
- **Workflow Management**: Gerenciar fluxos complexos
- **Cost Optimization**: Selecionar agente mais eficiente por tarefa

#### **🛠️ Tools Disponíveis:**
- `orchestrate_task` - Orquestrar tarefa complexa
- `delegate_to_specialist` - Delegar para agente especializado
- `optimize_workflow` - Otimizar fluxo de trabalho
- `cost_analysis` - Análise de custo por agente

#### **📞 Quando Usar:**
- ✅ Projetos que envolvem múltiplos sistemas
- ✅ Tarefas que requerem diferentes especialidades
- ✅ Otimização de custos LLM
- ✅ Workflows complexos (ERP + N8N + Dashboard)
- ❌ Tarefas simples de um só agente
- ❌ Consultas rápidas

---

### **📚 DOCUMENTATION AGENT**
- **Arquivo**: `documentation_agent_mcp.py`
- **Prioridade**: ⭐⭐⭐⭐ (Alto)
- **Status**: ✅ Ativo via Claude Desktop MCP

#### **🎯 Responsabilidades:**
- **Auto-Documentation**: Gerar docs a partir de código
- **API Documentation**: Manter documentação de APIs atualizada
- **User Guides**: Criar guias de usuário executivo
- **Changelog Management**: Gerenciar mudanças e versões

#### **🛠️ Tools Disponíveis:**
- `generate_project_documentation` - Gerar docs do projeto
- `update_api_docs` - Atualizar documentação API
- `create_user_guide` - Criar guia do usuário
- `generate_changelog` - Gerar changelog automático

#### **📞 Quando Usar:**
- ✅ Após implementar nova funcionalidade
- ✅ Preparar documentação para release
- ✅ Criar guias para novos usuários/devs
- ✅ Atualizar docs após mudanças na API
- ❌ Documentação já atualizada
- ❌ Mudanças menores sem impacto

---

### **🏗️ INFRASTRUCTURE AGENT**
- **Arquivo**: `infrastructure_agent_mcp.py`
- **Prioridade**: ⭐⭐⭐⭐ (Alto)
- **Status**: ✅ Ativo via Claude Desktop MCP

#### **🎯 Responsabilidades:**
- **System Monitoring**: Monitorar saúde do sistema 24/7
- **Docker Management**: Gerenciar containers e recovery
- **Performance Optimization**: Otimizar recursos e performance
- **Health Checks**: Validar integridade de todos os serviços

#### **🛠️ Tools Disponíveis:**
- `infrastructure_health_check` - Check de saúde completo
- `docker_status_report` - Relatório status Docker
- `performance_analysis` - Análise de performance
- `system_recovery` - Recovery automático

#### **📞 Quando Usar:**
- ✅ Sistema apresentando lentidão
- ✅ Containers Docker com problemas
- ✅ Monitoramento preventivo regular
- ✅ Preparar deploy em produção
- ❌ Sistema funcionando normalmente
- ❌ Problemas de aplicação (não infra)

---

### **📱 APPLICATION MANAGER**
- **Arquivo**: `application_manager_agent.py`
- **Prioridade**: ⭐⭐⭐ (Médio)
- **Status**: ✅ Ativo via Python direto

#### **🎯 Responsabilidades:**
- **App Lifecycle**: Gerenciar ciclo de vida das 50+ aplicações
- **Version Control**: Controlar versões e dependências
- **Status Monitoring**: Monitorar status individual de cada app
- **Catalog Management**: Manter catálogo atualizado

#### **🛠️ Tools Disponíveis:**
- `list_applications` - Listar todas aplicações
- `check_app_status` - Status de aplicação específica
- `update_app_catalog` - Atualizar catálogo
- `manage_app_lifecycle` - Gerenciar lifecycle

#### **📞 Quando Usar:**
- ✅ Auditoria de aplicações ativas
- ✅ Verificar dependências entre apps
- ✅ Atualizar catálogo após mudanças
- ✅ Planejamento de releases
- ❌ Problemas técnicos específicos
- ❌ Desenvolvimento de nova feature

---

### **🔄 N8N INTEGRATION AGENT**
- **Arquivo**: `n8n_mcp_server_standard.py`
- **Prioridade**: ⭐⭐⭐⭐ (Alto)  
- **Status**: ✅ Ativo via MCP Protocol

#### **🎯 Responsabilidades:**
- **Workflow Management**: Criar, importar, gerenciar workflows N8N
- **Automation Setup**: Configurar automações de negócio
- **Integration Testing**: Testar integrações N8N com ERPs
- **API Orchestration**: Orquestrar chamadas de API via N8N

#### **🛠️ Tools Disponíveis:**
- `import_workflow_dev` - Importar workflow desenvolvimento
- `import_workflow_prod` - Importar workflow produção  
- `test_n8n_dev_connection` - Testar conexão dev
- `test_n8n_prod_connection` - Testar conexão prod
- `list_workflows_dev` - Listar workflows dev
- `list_workflows_prod` - Listar workflows prod

#### **📞 Quando Usar:**
- ✅ Configurar novas automações
- ✅ Importar workflows para projetos
- ✅ Testar integrações N8N
- ✅ Troubleshooting de workflows
- ❌ Problemas não relacionados a N8N
- ❌ Integrações diretas sem workflow

---

## 🎯 **MATRIZ DE DECISÃO - QUAL AGENTE USAR?**

### **🚨 PROBLEMAS CRÍTICOS**
| Problema | Agente Responsável | Prioridade |
|----------|-------------------|------------|  
| Sistema travado/lento | Infrastructure Agent | P0 |
| Bug crítico em produção | Senior Developer | P0 |
| API não responde | N8N Integration Agent | P1 |
| Múltiplos sistemas afetados | Agent Orchestrator | P0 |

### **🚀 DESENVOLVIMENTO**
| Tarefa | Agente Responsável | Quando Usar |
|--------|-------------------|-------------|
| Nova funcionalidade complexa | Senior Developer | Sempre |
| Automação simples | N8N Integration | Workflows |
| Múltiplas integrações | Agent Orchestrator | Coordenação |
| Documentar mudanças | Documentation Agent | Pós-dev |

### **📊 OPERAÇÕES DIÁRIAS**
| Atividade | Agente Responsável | Frequência |
|-----------|-------------------|-------------|
| Health check matinal | Infrastructure Agent | Diário |
| Status das aplicações | Application Manager | Semanal |
| Atualizar documentação | Documentation Agent | Por release |
| Otimizar custos | Agent Orchestrator | Mensal |

---

## 🎪 **FLUXO DE ESCALAÇÃO**

### **Nível 1: Auto-Resolução**
- **Application Manager**: Status e catálogo
- **N8N Integration**: Workflows simples

### **Nível 2: Especialista**  
- **Senior Developer**: Problemas técnicos
- **Infrastructure**: Problemas de sistema
- **Documentation**: Geração de docs

### **Nível 3: Coordenação**
- **Agent Orchestrator**: Problemas complexos multi-agente
- **Senior Developer**: Arquitetura crítica

---

## 💡 **BOAS PRÁTICAS**

### **✅ USAR AGENTES QUANDO:**
- Tarefa alinhada com especialidade do agente
- Problema requer expertise específica  
- Coordenação entre múltiplos sistemas necessária
- Otimização de custos é prioridade

### **❌ NÃO USAR AGENTES QUANDO:**
- Tarefa simples que você pode fazer diretamente
- Consulta rápida de informação
- Problema já tem solução documentada
- Urgência máxima (use ferramentas diretas)

---

## 🎯 **COMANDOS EXECUTIVOS PARA AGENTES**

### **Via Claude Desktop (MCP):**
```
# Consultar especialista sênior
Use tool: senior_developer_consultation

# Orquestrar tarefa complexa  
Use tool: orchestrate_task

# Gerar documentação
Use tool: generate_project_documentation

# Check saúde infraestrutura
Use tool: infrastructure_health_check
```

### **Via Python direto:**
```bash
# Gerenciar aplicações
python3 application_manager_agent.py

# Testar N8N  
python3 n8n_mcp_server_standard.py test
```

---

**🚀 AGENTES OTIMIZADOS PARA MÁXIMA EFICIÊNCIA EXECUTIVA**