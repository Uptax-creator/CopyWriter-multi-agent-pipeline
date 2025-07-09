# 🏗️ Plano de Reestruturação - Omie MCP

## 🎯 **Objetivo**
Combinar a **arquitetura HTTP** (nossa inovação) com a **estrutura modular** (proposta inicial) para criar o melhor dos dois mundos.

## 📋 **Estrutura Híbrida Proposta**

```
omie-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # Servidor HTTP MCP principal
│   ├── config.py              # Configurações unificadas
│   ├── client/
│   │   ├── __init__.py
│   │   ├── omie_client.py     # Cliente HTTP para API Omie
│   │   └── mcp_client.py      # Cliente MCP para Claude Desktop
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py            # Classe base para tools
│   │   ├── cliente_tool.py    # Tool de cliente/fornecedor
│   │   ├── contas_pagar.py    # Tool de contas a pagar
│   │   ├── contas_receber.py  # Tool de contas a receber
│   │   ├── consultas.py       # Tools de consulta
│   │   └── tipos_documento.py # Tool de tipos de documento
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py      # Validadores de dados
│   │   ├── sanitizers.py      # Sanitizadores JSON
│   │   └── logger.py          # Configuração de logs
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Modelos Pydantic
├── tests/
│   ├── __init__.py
│   ├── test_tools/
│   │   ├── test_cliente.py
│   │   ├── test_contas_pagar.py
│   │   ├── test_contas_receber.py
│   │   └── test_consultas.py
│   ├── test_integration.py
│   └── test_http_server.py
├── scripts/
│   ├── start_server.py        # Iniciar servidor HTTP
│   ├── configure_claude.py    # Configurar Claude Desktop
│   ├── test_tool.py           # Testar tools individuais
│   └── validate_all.py        # Validação completa
├── docs/
│   ├── TOOLS.md              # Documentação das tools
│   ├── API_MAPPING.md        # Mapeamento API Omie
│   ├── HTTP_ARCHITECTURE.md  # Arquitetura HTTP
│   └── TROUBLESHOOTING.md    # Guia de problemas
├── integrations/
│   ├── claude/
│   │   ├── config.json
│   │   └── client.py
│   ├── copilot/
│   │   └── manifest.json
│   ├── n8n/
│   │   └── workflow.json
│   └── zapier/
│       └── config.js
├── requirements.txt
├── .env.example
├── README.md
├── credentials.json           # Credenciais locais
└── run_server.py             # Entry point principal
```

## 🔄 **Plano de Migração**

### **Fase 1: Reestruturação Base**
1. ✅ Mover arquivos para `src/`
2. ✅ Criar módulos organizados
3. ✅ Implementar classe base para tools
4. ✅ Configuração unificada

### **Fase 2: Implementação de Testes**
1. ✅ Criar estrutura de testes
2. ✅ Testes unitários para cada tool
3. ✅ Testes de integração
4. ✅ Testes do servidor HTTP

### **Fase 3: Documentação Estruturada**
1. ✅ Documentação de cada tool
2. ✅ Mapeamento completo da API Omie
3. ✅ Guias de troubleshooting
4. ✅ Exemplos de uso

### **Fase 4: Integrações Organizadas**
1. ✅ Configurações por plataforma
2. ✅ Templates prontos
3. ✅ Scripts de configuração
4. ✅ Validação automatizada

## 💡 **Vantagens da Estrutura Híbrida**

### **Mantém as Inovações**
- ✅ **Arquitetura HTTP** - Servidor único para múltiplas integrações
- ✅ **Credenciais automáticas** - Carregamento do credentials.json
- ✅ **Logs limpos** - Separação entre logs e protocolo MCP
- ✅ **Estabilidade** - Servidor HTTP mais robusto

### **Adiciona Organização**
- ✅ **Modularidade** - Cada tool em arquivo separado
- ✅ **Testes** - Cobertura completa com pytest
- ✅ **Documentação** - Estruturada e completa
- ✅ **Configuração** - Unificada e flexível

### **Melhora Manutenção**
- ✅ **Código limpo** - Separação clara de responsabilidades
- ✅ **Escalabilidade** - Fácil adicionar novas tools
- ✅ **Debug** - Logs estruturados e testes unitários
- ✅ **Deploy** - Scripts organizados e automatizados

## 🎯 **Decisão Final**

**Implementar a estrutura híbrida** porque:

1. **Mantém as inovações** - Arquitetura HTTP funciona perfeitamente
2. **Melhora a organização** - Código mais limpo e manutenível
3. **Adiciona robustez** - Testes e documentação estruturada
4. **Facilita expansão** - Fácil adicionar novas funcionalidades

## 📋 **Próximos Passos**

### **Imediato:**
1. ✅ Reestruturar arquivos existentes
2. ✅ Criar estrutura de módulos
3. ✅ Implementar classe base para tools
4. ✅ Migrar handlers para tools separadas

### **Curto Prazo:**
1. ✅ Implementar testes unitários
2. ✅ Criar documentação estruturada
3. ✅ Organizar integrações
4. ✅ Scripts de configuração

### **Médio Prazo:**
1. ✅ Testes de integração completos
2. ✅ Documentação da API
3. ✅ Guias de troubleshooting
4. ✅ Validação automatizada

---

**Vamos implementar a estrutura híbrida!** 🚀