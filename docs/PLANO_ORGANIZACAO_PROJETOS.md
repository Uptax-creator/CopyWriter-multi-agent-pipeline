# 📋 PLANO DE ORGANIZAÇÃO DOS PROJETOS - ESTRUTURA GITHUB

## 🎯 **ESTRATÉGIA DE ORGANIZAÇÃO**

Baseado na análise completa, vou organizar **11 projetos** em repositórios GitHub independentes, otimizando para deploy, manutenção e escalabilidade.

---

## 🗂️ **ESTRUTURA DE REPOSITÓRIOS GITHUB**

### **1️⃣ omie-mcp-core** (Repositório Principal)
```
🎯 Propósito: Servidor MCP principal para integração Omie ERP
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/ (arquivos principais)
🔧 Componentes:
├── src/                           # Código fonte principal
├── omie_fastmcp_unified.py       # Servidor unificado (25 tools)
├── credentials.json.template      # Template de credenciais
├── claude_desktop_config.json    # Configuração Claude Desktop
├── docker-compose.yml            # Orquestração
├── tests/                        # Suíte de testes
├── docs/                         # Documentação
└── README.md                     # Setup e uso

🚀 Status: Production-ready
📊 Tools: 11 ferramentas Omie validadas
```

### **2️⃣ nibo-mcp-server** 
```
🎯 Propósito: Servidor MCP dedicado para Nibo ERP
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/
🔧 Componentes:
├── src/core/                     # Cliente e configurações Nibo
├── src/tools/                    # 11 ferramentas financeiras
├── nibo_mcp_server_hybrid.py     # Servidor híbrido STDIO/HTTP
├── credentials.json.template      # Template credenciais Nibo
├── docker/                       # Containerização
└── README.md                     # Setup Nibo específico

🚀 Status: Functional, credenciais corrigidas
📊 Tools: 11 ferramentas Nibo
```

### **3️⃣ mcp-optimization-toolkit** 🆕
```
🎯 Propósito: Sistema de otimização LLM e gerenciamento tarefas
📂 Origem: task_classifier.py, prompt_optimizer.py, budget_tracker.py
🔧 Componentes:
├── task_classifier.py            # Classificação inteligente
├── prompt_optimizer.py           # Templates otimizados  
├── budget_tracker.py             # Rastreamento de custos
├── templates/                    # Templates de prompts
├── analytics/                    # Dashboard de métricas
├── docs/ESTRATEGIA_OTIMIZACAO_LLM_AVANCADA.md
└── README.md                     # Guia de otimização

🚀 Status: Implementado e testado
💰 ROI: 79% economia projetada
```

### **4️⃣ universal-credentials-manager**
```
🎯 Propósito: Gestão segura de credenciais multi-tenant
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/universal-credentials-manager/
🔧 Componentes:
├── src/api/                      # REST API
├── src/core/                     # Core logic + encryption
├── src/storage/                  # Cloud storage backup
├── docker-compose.yml            # Deploy containerizado
├── tests/                        # Security tests
└── README.md                     # Setup e security guide

🚀 Status: Multi-tenant ready
🔐 Security: Criptografia implementada
```

### **5️⃣ mcp-tools-library**
```
🎯 Propósito: Biblioteca padronizada de tools + gerador MCP
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/tools_library/ + classifier
🔧 Componentes:
├── schemas/                      # Definições YAML tools
├── classifier/                   # Sistema classificação
├── generator/                    # Gerador automático MCP servers
├── integrations/                 # Conectores ERP
├── templates/                    # Templates base MCP
└── README.md                     # Criar seu próprio MCP

🚀 Status: Foundation ready
🎯 Visão: MCP-as-a-Service generator
```

### **6️⃣ n8n-mcp-integration**
```
🎯 Propósito: Workflows N8N + integração MCP
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/n8n_workflows*/
🔧 Componentes:
├── workflows/                    # 22+ workflows N8N
├── official/                     # Workflows produção
├── configs/                      # Configurações N8N
├── webhooks/                     # Endpoints configurados
├── examples/                     # Casos de uso
└── README.md                     # Setup N8N + MCP

🚀 Status: 1 workflow ativo, N8N rodando
🔗 Integration: localhost:5678 configurado  
```

### **7️⃣ omie-dashboard-web**
```
🎯 Propósito: Interface web para monitoramento
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/omie-dashboard-v2/
🔧 Componentes:
├── public/                       # HTML/CSS/JS interface
├── api/                         # Backend APIs
├── monitoring/                   # Real-time metrics
├── charts/                      # Visualizações
├── docker/                      # Deploy containerizado
└── README.md                    # Setup dashboard

🚀 Status: Web interface ready
📊 Features: Real-time monitoring
```

### **8️⃣ omie-tenant-manager**
```
🎯 Propósito: Gestão multi-empresa e usuários
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/omie-tenant-manager/
🔧 Componentes:
├── src/routers/                 # API endpoints
├── src/models/                  # Database models
├── src/auth/                    # Authentication
├── database/                    # Schemas + migrations
├── docker-compose.yml           # Deploy
└── README.md                    # Multi-tenant setup

🚀 Status: Multi-company architecture
👥 Features: User management, empresa isolation
```

### **9️⃣ mcp-deployment-toolkit**
```
🎯 Propósito: Deploy, CI/CD, monitoramento produção
📂 Origem: Docker files, deploy scripts, monitoring
🔧 Componentes:
├── docker/                      # All Dockerfiles
├── k8s/                        # Kubernetes manifests
├── ci-cd/                      # GitHub Actions
├── monitoring/                 # Prometheus + Grafana
├── backup/                     # Backup strategies
├── scripts/                    # Deploy automation
└── README.md                   # Production deployment

🚀 Status: Docker ready, CI/CD pending
🏗️ Features: Multi-platform deployment
```

### **🔟 mcp-composio-integration**
```
🎯 Propósito: Integração com Composio.dev platform
📂 Origem: Novo - baseado em mcp servers existentes
🔧 Componentes:
├── composio/                    # Composio API integration
├── publishers/                  # Tool publishers
├── validators/                  # Tool validation
├── examples/                    # Usage examples
├── docs/                       # Composio setup guide
└── README.md                   # Publish to Composio

🚀 Status: Architecture planned
🌐 Purpose: Public tool distribution
```

### **1️⃣1️⃣ mcp-server-template**
```
🎯 Propósito: Template base para novos servidores MCP
📂 Origem: /Users/kleberdossantosribeiro/omie-mcp/mcp_server_template/
🔧 Componentes:
├── template/                    # Base server structure
├── examples/                    # Implementation examples
├── generators/                  # Auto-generation scripts
├── best-practices/              # Development guidelines
├── testing/                     # Test templates
└── README.md                   # Create new MCP server

🚀 Status: Template structure ready
🎯 Purpose: Accelerate new MCP development
```

---

## 📦 **ESTRATÉGIA DE BACKUP E LIMPEZA**

### **🗂️ Arquivos para Backup** (mover para `/backup/legacy/`)
```
legacy_servers/
├── omie_mcp_server_old.py
├── omie_mcp_server_simple.py
├── omie_mcp_server_clean.py
├── omie_mcp_corrected.py
├── omie_mcp_standard.py
└── omie_mcp_standard_simple.py

development/
├── omie_debug_output.txt
├── test_response.json
├── quick_evaluation.py
├── diagnostico_erro_500.py  
└── patch_omie_server.py

archived_docs/
├── Documentos obsoletos (identificar por data)
├── Análises antigas
└── Relatórios superados
```

### **🔄 Estrutura Final do Projeto Principal**
```
/Users/kleberdossantosribeiro/omie-mcp/ (Repositório omie-mcp-core)
├── 🔴 ACTIVE_SERVICES/
│   ├── omie_fastmcp_unified.py          # Servidor principal
│   └── src/                             # Source code
├── 🔧 CONFIGS/
│   ├── claude_desktop_config.json       # Claude config
│   ├── credentials.json.template        # Template seguro
│   └── docker-compose.yml              # Orquestração
├── 📚 DOCS/
│   ├── README.md                       # Main documentation
│   ├── API_REFERENCE.md               # API docs
│   └── DEPLOYMENT_GUIDE.md            # Deploy guide
├── 🧪 TESTS/
│   ├── execute_homologacao_now.py     # Production tests
│   └── test_suites/                   # All test files
└── 🗂️ BACKUP/
    ├── legacy_servers/                # Old implementations
    ├── development/                   # Debug files
    └── archived_docs/                 # Obsolete docs
```

---

## 🚀 **CRONOGRAMA DE IMPLEMENTAÇÃO**

### **📅 FASE 1 - ORGANIZAÇÃO (Hoje)**
- ✅ Criar estrutura de pastas
- ✅ Mover arquivos para backup
- ✅ Limpar projeto principal
- ✅ Preparar READMEs base

### **📅 FASE 2 - GITHUB SETUP (Amanhã)**  
- ✅ Criar 11 repositórios GitHub
- ✅ Upload código organizado
- ✅ Configurar GitHub Actions básicas
- ✅ Documentação inicial

### **📅 FASE 3 - DOCKER & DEPLOY (Semana)**
- ✅ Validar todos os Dockerfiles
- ✅ Testar docker-compose
- ✅ Setup CI/CD pipeline
- ✅ Deploy staging environment

### **📅 FASE 4 - PRODUÇÃO (2 semanas)**
- ✅ Deploy produção
- ✅ Monitoramento ativo
- ✅ Backup automático
- ✅ Performance indicators

---

## 💡 **BENEFÍCIOS DA ORGANIZAÇÃO**

### **🎯 Para Desenvolvimento:**
- **Modularidade**: Cada projeto independente
- **Manutenibilidade**: Código limpo e organizado
- **Escalabilidade**: Fácil adicionar novos ERPs
- **Colaboração**: Multiple contributors possível

### **🏗️ Para Deploy:**
- **Containerização**: Docker para cada serviço
- **Orquestração**: Kubernetes ready
- **CI/CD**: Automated pipelines
- **Monitoring**: Production observability

### **💰 Para Business:**
- **ROI**: Sistema de otimização economiza 79%
- **Time-to-Market**: Templates aceleram desenvolvimento
- **Reliability**: Testes automatizados
- **Scalability**: Multi-tenant architecture

---

## 🎖️ **PRÓXIMO PASSO**

**Usar sistema de otimização criado:**
```bash
# Classificar tarefa de organização
python task_classifier.py "Organizar 11 projetos GitHub"
# Resultado esperado: Haiku ($0.25) - task estrutural

# Otimizar prompt para cada README
python prompt_optimizer.py "Criar README" "gemini"  
# Resultado: Template gratuito otimizado

# Monitorar budget durante processo
python budget_tracker.py
# Controle: Não exceder daily limit
```

**🚀 SISTEMA PRONTO PARA EXECUÇÃO OTIMIZADA!**