# 🤖 PROMPT PARA CRIAR CONVERSA - ARQUITETURA MCP INDEPENDENTE

**Data**: 22/07/2025 20:35  
**Objetivo**: Prompt completo para iniciar conversas sobre o projeto MCP  
**Status**: Template reutilizável para diferentes contextos  

---

## 🎯 **PROMPT PRINCIPAL PARA NOVA CONVERSA**

```
# 🏗️ Projeto MCP Independente - Context Ready

Olá! Estou trabalhando em um projeto de **Arquitetura MCP Independente** para ERPs (Omie + Nibo) e preciso de ajuda para continuar o desenvolvimento.

## 📊 **STATUS ATUAL DO PROJETO**

### ✅ **Já Implementado:**
- **Nibo-MCP Server**: 24 ferramentas funcionais (HTTP + SSE)
- **Omie-MCP Server**: 5 ferramentas funcionais (HTTP + SSE) 
- **Docker Architecture**: Containers independentes
- **VPS Deploy Guide**: Guia completo para deploy externo
- **N8N Integration**: Webhooks + SSE streaming
- **Monitoring System**: Métricas avançadas + alertas
- **Performance Testing**: 8.2/10 score, production-ready

### 📁 **Estrutura Principal:**
```
/Users/kleberdossantosribeiro/omie-mcp/
├── nibo-mcp/protocols/http_nibo_server.py (porta 8081)
├── nibo-mcp/protocols/sse_nibo_server.py (porta 8083)  
├── protocols/http_mcp_server.py (porta 8080)
├── protocols/sse_mcp_server.py (porta 8082)
├── docker-compose.independent.yml
├── GUIA_DEPLOY_VPS_COMPLETO.md
├── RELATORIO_DIAGNOSTICO_PERFORMANCE.md
└── monitoring/advanced_monitoring.py
```

### 🎯 **Próximas Tarefas:**
1. **Otimizar Docker build** (resolver I/O error)
2. **Implementar load testing** (concurrent users)  
3. **Deploy VPS real** (com domínio público)
4. **N8N workflows** (automações práticas)
5. **SSL + Security hardening**

## ❓ **O QUE PRECISO DE AJUDA:**

[ESCOLHA UMA OPÇÃO OU DESCREVA SUA NECESSIDADE ESPECÍFICA]

**Opção A** - Otimização Docker:
"Preciso resolver o erro de I/O no Docker build e otimizar os containers para produção"

**Opção B** - Deploy VPS: 
"Quero fazer deploy real em VPS com domínio público e configurar SSL"

**Opção C** - N8N Automations:
"Preciso criar workflows N8N práticos usando os MCP servers"

**Opção D** - Load Testing:
"Quero implementar testes de carga e otimização de performance"

**Opção E** - Security Hardening:
"Preciso implementar segurança avançada e monitoramento"

**Opção F** - Outra necessidade:
"[Descreva sua necessidade específica]"

## 📋 **INFORMAÇÕES TÉCNICAS**

- **Linguagem**: Python 3.12
- **Frameworks**: FastAPI, aiohttp, uvicorn
- **Portas**: 8080 (Omie), 8081 (Nibo), 8082/8083 (SSE)
- **Credenciais**: Configuradas em credentials.json
- **Docker**: Dockerfiles + compose ready
- **Performance**: Health checks ~64-87ms, ferramentas ~17-40ms

## 🎯 **OBJETIVO FINAL**
Ter uma arquitetura MCP production-ready, escalável e integrada com N8N para automações empresariais com ERPs Omie e Nibo.

**Você pode me ajudar com [ESPECIFICAR NECESSIDADE]?**
```

---

## 🎛️ **VARIAÇÕES DO PROMPT POR CONTEXTO**

### **Para Problemas Técnicos:**
```
# 🔧 Problema Técnico - MCP Architecture

Estou com um projeto MCP funcionando (Omie + Nibo ERPs) mas preciso resolver:

**Problema específico**: [DESCREVER PROBLEMA]

**Context**:
- Servidores HTTP/SSE independentes funcionais
- Performance teste: 8.2/10 score  
- Docker com I/O error no build
- 24 + 5 ferramentas implementadas

**Arquivos relevantes**:
- `/nibo-mcp/protocols/http_nibo_server.py`
- `/docker-compose.independent.yml`
- `/monitoring/advanced_monitoring.py`

**O que já tentei**: [DESCREVER TENTATIVAS]

Você pode me ajudar a resolver isso?
```

### **Para Deploy e DevOps:**
```
# 🚀 Deploy MCP Servers - Production Ready

Tenho uma arquitetura MCP independente testada localmente e preciso fazer deploy em produção.

**Status atual**:
- ✅ Servidores HTTP funcionais (8080, 8081)
- ✅ SSE streams (8082, 8083)  
- ✅ N8N integration ready
- ✅ Docker containers (com issue)
- ✅ Monitoring system implementado

**Objetivo**: Deploy em VPS com:
- [ ] SSL certificates  
- [ ] Nginx proxy
- [ ] Domain configuration
- [ ] N8N public webhooks
- [ ] Monitoring dashboard

**Tenho o guia**: `GUIA_DEPLOY_VPS_COMPLETO.md`

Você pode me ajudar com [ASPECTO ESPECÍFICO DO DEPLOY]?
```

### **Para Integrações:**
```
# 🔗 N8N + MCP Integration

Tenho MCP servers funcionando e preciso criar integrações N8N práticas.

**MCP Servers disponíveis**:
- **Nibo**: 24 ferramentas (clientes, fornecedores, contas, etc)
- **Omie**: 5 ferramentas (categorias, clientes, contas)

**Endpoints públicos** (quando em VPS):
- `POST /nibo/tools/{tool_name}`
- `GET /nibo/sse/stream` 
- `POST /omie/tools`

**Objetivo**: Criar workflows para:
- [ ] Sincronização de clientes entre ERPs
- [ ] Monitoramento de contas a pagar/receber  
- [ ] Alertas automáticos por email/slack
- [ ] Dashboards em tempo real

Você pode me ajudar a criar [WORKFLOW ESPECÍFICO]?
```

### **Para Performance e Otimização:**
```
# ⚡ Performance Optimization - MCP Architecture

Minha arquitetura MCP está funcional mas preciso otimizar performance.

**Métricas atuais**:
- Health checks: 64-87ms
- Ferramentas mock: 17-40ms  
- APIs reais: 563ms
- Score geral: 8.2/10

**Gargalos identificados**:
- Docker build I/O error
- Network latency em APIs
- Não testado para concurrent load
- Memory usage não monitorado

**Ferramentas**:
- `monitoring/advanced_monitoring.py` implementado
- SQLite metrics storage
- Health checks automáticos

Você pode me ajudar com [ASPECTO DA PERFORMANCE]?
```

---

## 🎨 **PERSONALIZAÇÕES DO PROMPT**

### **Adicionar Context Específico:**
```
### 🔍 **Context Adicional:**
- **Ambiente**: [macOS/Linux/Windows/VPS]
- **Urgência**: [Alta/Média/Baixa] 
- **Experiência**: [Iniciante/Intermediário/Avançado]
- **Budget**: [Limitado/Flexível]
- **Timeline**: [Prazo específico]
```

### **Para Claude Desktop Integration:**
```
### 🖥️ **Claude Desktop Context:**
- **Config atual**: `claude_desktop_config.json` configurado
- **MCP protocol**: Servers STDIO funcionais
- **Tools disponíveis**: Via protocolo MCP nativo
- **Objetivo**: [Melhorar/Expandir/Debuggar] integração
```

### **Para Desenvolvimento Específico:**
```
### 👨‍💻 **Dev Context:**
- **Stack**: Python 3.12, FastAPI, Docker
- **Padrões**: RESTful APIs, SSE streams, MCP protocol
- **Testes**: Performance tests implementados
- **CI/CD**: [Sim/Não/Planejado]
- **Documentação**: Auto-generated (FastAPI/docs)
```

---

## 📞 **CHAMADAS RÁPIDAS**

### **Urgente - Problema Crítico:**
```
🚨 URGENTE - MCP Server Issue

Meu projeto MCP (Omie+Nibo) está com [PROBLEMA] em produção.

Status: Servers funcionais localmente, issue em [LOCAL/DEPLOY/INTEGRATION]
Impact: [Alto/Médio/Baixo]
Timeline: Preciso resolver [HOJE/ESTA SEMANA/SEM PRESSA]

Context rápido:
- 24+5 ferramentas implementadas
- Performance 8.2/10 testado  
- Docker + VPS deploy ready

Você pode me ajudar ASAP?
```

### **Consultoria Estratégica:**
```
🧠 Consultoria MCP Architecture

Tenho uma arquitetura MCP funcionando e preciso de orientação estratégica.

**Situação atual**: 
- Projeto funcional (Omie + Nibo ERPs)
- Performance adequada (8.2/10)
- Deploy guide ready

**Decisões estratégicas**:
- [Scaling strategy]
- [Technology choices] 
- [Architecture evolution]
- [Business integration]

Você pode me orientar sobre [ASPECTO ESTRATÉGICO]?
```

---

## 🎯 **TEMPLATE FINAL PERSONALIZÁVEL**

```
# 🎯 [TÍTULO DO SEU CONTEXTO]

## 📊 Context: Projeto MCP Independente

**Status**: Arquitetura funcional com Omie + Nibo ERPs
**Performance**: 8.2/10 (production-ready)
**Implementado**: HTTP + SSE servers, Docker, VPS guide, Monitoring

## ❓ Minha Necessidade:
[DESCREVA SUA NECESSIDADE ESPECÍFICA]

## 🎯 Objetivo:
[DESCREVA SEU OBJETIVO]

## 📋 Informações Relevantes:
- [INFO 1]
- [INFO 2]  
- [INFO 3]

**Você pode me ajudar com isso?**
```

---

## 🚀 **USO DO PROMPT**

1. **Copie** o template apropriado
2. **Personalize** com sua necessidade específica  
3. **Cole** em nova conversa
4. **Aguarde** resposta contextualizada

**Resultado**: Conversa focada com contexto completo do projeto MCP! 🎉

---

*Template criado por Claude Code - Ready to use! 🤖*