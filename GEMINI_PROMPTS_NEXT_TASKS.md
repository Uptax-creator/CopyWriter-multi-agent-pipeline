# 🎯 PROMPTS PARA GEMINI 2.5 - PRÓXIMAS TAREFAS

## 💰 **CONTROLE DE CUSTOS**
- **Investido hoje**: $22 + $1.35 = $23.35
- **Saldo restante**: $1.30
- **Meta**: Máxima eficiência com Gemini (gratuito/barato)

---

## 📋 **PROMPT 1: DOCUMENTAÇÃO TÉCNICA COMPLETA**

### **Para Gemini 2.5:**

```
# TASK: Criar documentação técnica completa do projeto Omie-MCP

## CONTEXTO DO PROJETO:
- Projeto: Sistema MCP (Model Context Protocol) para integração Omie + Nibo + N8N
- Localização: /Users/kleberdossantosribeiro/omie-mcp/
- Status: Integração N8N funcionando, workflows corrigidos, 3 MCP servers ativos

## ARQUIVOS DE REFERÊNCIA:
1. /Users/kleberdossantosribeiro/omie-mcp/CLAUDE.md (instruções principais)
2. /Users/kleberdossantosribeiro/omie-mcp/PLANO_OTIMIZACAO_MULTI_LLM.md (estratégia)
3. /Users/kleberdossantosribeiro/omie-mcp/ERRO_CORRIGIDO_SUCESSO.md (última correção)
4. /Users/kleberdossantosribeiro/omie-mcp/claude_desktop_config.json (configuração)
5. /Users/kleberdossantosribeiro/omie-mcp/credentials.json (credenciais)

## ESTRUTURA TÉCNICA ATUAL:
- **MCP Servers**: omie-mcp, nibo-mcp, n8n-mcp
- **Ferramentas**: 11 Omie + 7 Nibo + 7 N8N = 25 total
- **N8N Workflow**: "Omie MCP Integration - Corrigido" (ID: TwD2MG879s0iknBG)
- **Python**: /Users/kleberdossantosribeiro/omie-mcp/venv/bin/python3

## TAREFAS A EXECUTAR:

### 1. **DOCUMENTATION.md** - Documentação principal
- Visão geral do projeto
- Arquitetura de integração
- Guia de instalação step-by-step
- Lista completa de ferramentas disponíveis
- Troubleshooting common issues

### 2. **API_REFERENCE.md** - Referência das APIs
- Documentação de todas as 25 ferramentas MCP
- Parâmetros, retornos, exemplos
- Códigos de erro e soluções
- Performance benchmarks

### 3. **DEPLOYMENT_GUIDE.md** - Guia de deploy
- Deploy local vs produção
- Configuração Docker
- Deploy em VPS
- Monitoramento e logs

### 4. **INTEGRATION_EXAMPLES.md** - Exemplos práticos
- Casos de uso Omie ↔ Nibo
- Workflows N8N prontos para usar
- Scripts de automação
- Best practices

## FORMATO REQUERIDO:
- Markdown com syntax highlighting
- Diagramas mermaid quando necessário
- Exemplos de código funcional
- Links internos entre documentos
- Índice navegável

## ENTREGÁVEIS:
Criar 4 arquivos de documentação completos e profissionais
```

---

## 📋 **PROMPT 2: SCRIPTS DE MONITORAMENTO**

### **Para Gemini 2.5:**

```
# TASK: Criar sistema de monitoramento automático

## CONTEXTO:
Sistema MCP funcionando com 3 servers (Omie, Nibo, N8N)
Necessidade de monitoramento contínuo sem consumir tokens LLM

## ARQUIVOS BASE:
- /Users/kleberdossantosribeiro/omie-mcp/n8n-mcp/n8n_mcp_server.py
- /Users/kleberdossantosribeiro/omie-mcp/omie_fastmcp_unified.py
- /Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py

## SCRIPTS A CRIAR:

### 1. **monitor_mcp_health.py**
- Verifica status dos 3 MCP servers
- Testa conectividade APIs (Omie, Nibo, N8N)
- Log de performance e uptime
- Alertas automáticos via webhook

### 2. **performance_dashboard.py**
- Dashboard web em tempo real
- Métricas de resposta das APIs
- Gráficos de uso por ferramenta
- Status visual dos serviços

### 3. **automated_tests.py**
- Testes automáticos de todas as 25 ferramentas
- Validação de integridade dos dados
- Relatórios de teste automáticos
- CI/CD health checks

### 4. **backup_automation.py**
- Backup automático de configurações
- Versionamento de credentials.json
- Backup de workflows N8N
- Restore automático em caso de falha

## REQUISITOS TÉCNICOS:
- Python 3.12+
- Async/await para performance
- Logging estruturado (JSON)
- Configuração via environment variables
- Zero dependência de LLMs
- Execução independente via cron

## ENTREGÁVEIS:
4 scripts Python prontos para produção + configuração cron
```

---

## 📋 **PROMPT 3: DASHBOARD DE PERFORMANCE**

### **Para Gemini 2.5:**

```
# TASK: Dashboard web de performance em tempo real

## OBJETIVO:
Interface web para monitorar sistema MCP sem gastar tokens

## TECNOLOGIAS SUGERIDAS:
- FastAPI + HTML/CSS/JS (ou Flask simples)
- Charts.js para gráficos
- WebSockets para tempo real
- SQLite para métricas

## COMPONENTES DO DASHBOARD:

### 1. **Status Overview**
- Cards de status: Omie (🟢/🔴), Nibo (🟢/🔴), N8N (🟢/🔴)
- Uptime percentage últimas 24h
- Total de requisições hoje
- Latência média por serviço

### 2. **Performance Metrics**
- Gráfico de resposta time por hora
- Top 10 ferramentas mais usadas
- Taxa de erro por serviço
- Throughput requests/minute

### 3. **Real-time Logs**
- Stream de logs em tempo real
- Filtros por serviço/nível
- Search e highlight
- Export de logs

### 4. **Health Checks**
- Status de conectividade APIs
- Teste manual de ferramentas
- Restart de serviços
- Configuração de alertas

## ARQUIVOS A CRIAR:
- dashboard_server.py (FastAPI backend)
- templates/dashboard.html (frontend)
- static/dashboard.js (interatividade)
- static/dashboard.css (styling)
- config/dashboard_config.yaml

## URL DE ACESSO:
http://localhost:8080/dashboard

## ENTREGÁVEIS:
Dashboard web completo e funcional
```

---

## 💰 **ECONOMIA PROJETADA COM GEMINI:**

| Tarefa | Claude Cost | Gemini Cost | Economia |
|--------|-------------|-------------|----------|
| Documentação | $8 | $0-1 | $7-8 |
| Scripts | $6 | $0-1 | $5-6 |
| Dashboard | $5 | $0-1 | $4-5 |
| **TOTAL** | **$19** | **$0-3** | **$16-19** |

---

## 🎯 **ESTRATÉGIA DE EXECUÇÃO:**

### **HOJE (Gemini):**
1. Executar prompts de documentação
2. Criar scripts de monitoramento  
3. Desenvolver dashboard básico

### **AMANHÃ (Claude $1.30):**
1. Retomar testes N8N integration
2. Resolver issues críticos identificados
3. Validação final do sistema

---

## 📂 **ESTRUTURA DE ARQUIVOS ESPERADA:**

```
/Users/kleberdossantosribeiro/omie-mcp/
├── docs/
│   ├── DOCUMENTATION.md
│   ├── API_REFERENCE.md  
│   ├── DEPLOYMENT_GUIDE.md
│   └── INTEGRATION_EXAMPLES.md
├── monitoring/
│   ├── monitor_mcp_health.py
│   ├── performance_dashboard.py
│   ├── automated_tests.py
│   └── backup_automation.py
└── dashboard/
    ├── dashboard_server.py
    ├── templates/dashboard.html
    ├── static/dashboard.js
    └── static/dashboard.css
```

---

## ✅ **EXECUÇÃO RECOMENDADA:**

**Copie cada prompt individualmente para Gemini 2.5 e execute sequencialmente.**

**Objetivo**: Documentação completa + Monitoramento automático + Dashboard funcional

**Custo**: ~$0-3 vs $19 no Claude = **84-100% de economia!**