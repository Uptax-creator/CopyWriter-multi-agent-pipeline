# 📦 T011 - PLANO DE MIGRAÇÃO PARA ~/omie-fastmcp/

## 🎯 OBJETIVO
Organizar estrutura de arquivos para ~/omie-fastmcp/ limpando arquivos obsoletos e mantendo apenas o essencial.

## 📋 ARQUIVOS DE PRODUÇÃO IDENTIFICADOS

### ✅ **SERVIDORES FASTMCP PRINCIPAIS (9 arquivos)**
```
omie_fastmcp_conjunto_1_enhanced.py      # 3 tools básicas
omie_fastmcp_conjunto_2_complete.py      # 8 tools CRUD  
omie_fastmcp_contas_receber_enhanced.py  # 2 tools contas receber
omie_fastmcp_empresas_conexao.py         # 3 tools empresas/conexão
omie_fastmcp_example.py                  # Exemplo/template
omie_fastmcp_expanded.py                 # Versão expandida
omie_fastmcp_extended.py                 # Versão extendida
omie_fastmcp_unified.py                  # Servidor unificado (em desenvolvimento)
omie_fastmcp_conjunto_1.py               # Versão original
```

### ✅ **ESTRUTURA CORE NECESSÁRIA**
```
src/
├── client/
│   ├── omie_client.py                   # Cliente HTTP principal
│   └── __init__.py
├── config.py                            # Configurações
├── database/
│   ├── database_manager.py              # Sistema opcional
│   └── schema.sql
├── tools/
│   └── tool_classifier_enhanced.py      # Classificação tools
└── utils/
    ├── logger.py
    ├── validators.py  
    └── __init__.py
```

### ✅ **ARQUIVOS DE CONFIGURAÇÃO**
```
requirements.txt                         # Dependências
credentials.json                         # Credenciais (produção)
CLAUDE.md                               # Instruções projeto
TASK_CONTROL.md                         # Controle de tarefas
```

### ✅ **DOCUMENTAÇÃO ESSENCIAL**
```
README.md                               # Documentação principal
TOOLS_RESEARCH_PREVIOUS_PROJECT.md     # Pesquisa projeto anterior
FRAMEWORK_COMPLIANCE_REVIEW.md         # Review compliance
SSE_HTTP_ARCHITECTURE_PLAN.md          # Plano arquitetura multi-plataforma
```

## 🗂️ **ESTRUTURA ALVO ~/omie-fastmcp/**

```
~/omie-fastmcp/
├── servers/                            # Servidores MCP
│   ├── omie_fastmcp_unified.py         # Servidor unificado (16 tools)
│   ├── omie_fastmcp_conjunto_1_enhanced.py
│   ├── omie_fastmcp_conjunto_2_complete.py
│   ├── omie_fastmcp_contas_receber_enhanced.py
│   └── omie_fastmcp_empresas_conexao.py
├── src/                                # Código fonte
│   ├── client/
│   ├── config.py
│   ├── database/
│   ├── tools/
│   └── utils/
├── config/                             # Configurações
│   ├── requirements.txt
│   ├── credentials.json
│   └── claude_desktop_config.json
├── docs/                               # Documentação
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── API_REFERENCE.md
├── tests/                              # Testes automatizados
│   └── test_all_tools.py
└── scripts/                            # Scripts utilitários
    ├── setup.py
    ├── validate.py
    └── deploy.py
```

## 🧹 **ARQUIVOS PARA LIMPEZA/BACKUP (70+ arquivos)**

### **CATEGORIA: BACKUP**
- All backup/ directory contents
- Arquivos *_backup_*.py
- Arquivos *_old.py, *_deprecated.py
- Test files temporários

### **CATEGORIA: DESENVOLVIMENTO/DEBUG** 
- omie_mcp_server_*.py (múltiplas versões)
- test_*.py files de desenvolvimento
- Arquivos de configuração duplicados
- Logs temporários

### **CATEGORIA: DOCUMENTAÇÃO REDUNDANTE**
- *.md files com informações duplicadas
- Guides específicos já consolidados
- Reports de testes antigos

## ⚡ **PLANO DE EXECUÇÃO**

### **FASE 1: BACKUP SEGURANÇA**
1. Criar backup completo em ~/omie-mcp-backup-$(date)
2. Verificar integridade dos arquivos essenciais

### **FASE 2: ESTRUTURA NOVA** 
1. Criar diretórios ~/omie-fastmcp/
2. Migrar arquivos essenciais
3. Atualizar imports e paths

### **FASE 3: VALIDAÇÃO**
1. Testar servidores na nova estrutura
2. Validar Claude Desktop config
3. Confirmar funcionalidade completa

### **FASE 4: LIMPEZA**
1. Remover arquivos obsoletos do original
2. Manter apenas links/referências necessárias

## 📊 **MÉTRICAS ESPERADAS**

- **Antes**: 172 arquivos (~70 MB)
- **Depois**: ~25 arquivos essenciais (~5 MB)
- **Redução**: 85% de arquivos, 93% de espaço
- **Manutenibilidade**: Muito melhor

## 🎯 **CRITÉRIOS DE SUCESSO**

✅ Todos os 16 tools funcionais na nova estrutura  
✅ Claude Desktop conecta sem erros  
✅ Performance igual ou melhor  
✅ Documentação atualizada e limpa  
✅ Scripts de deploy funcionais  

---

**Status**: 📋 PLANEJADO  
**Início**: 21/07/2025 11:15  
**ETA**: 21/07/2025 12:00 (45 min)  