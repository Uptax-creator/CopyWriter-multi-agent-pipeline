# 📋 Guia de Scripts - Nibo MCP v2.0

Este documento descreve todos os scripts utilitários disponíveis para gerenciar o Nibo MCP Server.

## 🚀 **Scripts Disponíveis**

### **1. start_nibo_service.py** - Ativação do Serviço
**Localização:** `scripts/start_nibo_service.py`

**Funcionalidade:**
- Verifica pré-requisitos completos
- Valida credenciais e conectividade
- Inicia o servidor MCP com verificações

**Uso:**
```bash
cd nibo-mcp
python scripts/start_nibo_service.py
```

**Verificações Executadas:**
- ✅ Versão do Python (3.8+)
- ✅ Dependências instaladas
- ✅ Arquivo `credentials.json` válido
- ✅ Conectividade com API do Nibo
- ✅ Estrutura do projeto

**Output:**
- Logs coloridos em tempo real
- Arquivo `service_status.json` criado
- Servidor executado em modo stdio

---

### **2. diagnose_nibo_service.py** - Diagnóstico Completo
**Localização:** `scripts/diagnose_nibo_service.py`

**Funcionalidade:**
- Diagnóstico abrangente do sistema
- Testes de todas as funcionalidades
- Relatório detalhado de saúde

**Uso:**
```bash
cd nibo-mcp
python scripts/diagnose_nibo_service.py
```

**Verificações Executadas:**
- 🔍 **Sistema:** OS, Python, recursos
- 📦 **Dependências:** Pacotes instalados
- 📁 **Estrutura:** Arquivos obrigatórios
- 🔐 **Credenciais:** Validade e expiração
- 🌐 **API:** Conectividade e resposta
- 🛠️ **Ferramentas:** Funcionalidades básicas
- ⚡ **Performance:** Tempo de resposta

**Output:**
- Relatório JSON: `diagnostic_report_YYYYMMDD_HHMMSS.json`
- Resumo com estatísticas
- Códigos de saída: 0=OK, 1=Erro, 2=Aviso

---

### **3. test_all_tools_v2.py** - Teste Completo de Ferramentas
**Localização:** `scripts/test_all_tools_v2.py`

**Funcionalidade:**
- Testa todas as 31 ferramentas implementadas
- Validação de funcionalidades CRUD
- Relatório detalhado por categoria

**Uso:**
```bash
cd nibo-mcp
python scripts/test_all_tools_v2.py
```

**Categorias Testadas:**
- 📋 **Consulta (7 tools):** endpoints de leitura
- 🔧 **CRUD (18 tools):** operações simuladas
- 🔄 **Compatibilidade (2 tools):** aliases Omie
- ⚙️ **Gerenciamento (4 tools):** multi-empresa

**Output:**
- Relatório JSON: `tools_test_report_YYYYMMDD_HHMMSS.json`
- Estatísticas por categoria
- Taxa de sucesso geral

---

### **4. health_monitor.py** - Monitor de Saúde
**Localização:** `scripts/health_monitor.py`

**Funcionalidade:**
- Monitoramento contínuo de saúde
- Detecção de problemas em tempo real
- Histórico de uptime

**Uso:**
```bash
# Monitoramento contínuo (padrão: 30s)
cd nibo-mcp
python scripts/health_monitor.py

# Verificação única
python scripts/health_monitor.py --once

# Intervalo personalizado
python scripts/health_monitor.py --interval 60
```

**Parâmetros:**
- `--interval, -i`: Intervalo em segundos (padrão: 30)
- `--once`: Executa apenas uma verificação

**Monitoramento:**
- 🌐 **API:** Conectividade e tempo de resposta
- 🛠️ **Ferramentas:** Amostra de funcionalidades
- 💻 **Sistema:** CPU, memória, disco
- 🔐 **Credenciais:** Expiração de tokens

**Output:**
- Log contínuo: `health_monitor.log`
- Histórico de 24 horas em memória
- Estatísticas de uptime

---

### **5. test_connection.py** - Teste Básico de Conectividade
**Localização:** `scripts/test_connection.py`

**Funcionalidade:**
- Teste rápido de conectividade
- Validação básica de credenciais

**Uso:**
```bash
cd nibo-mcp
python scripts/test_connection.py
```

---

## 🎯 **Fluxo Recomendado de Uso**

### **Primeira Execução:**
```bash
# 1. Configurar credenciais
cp credentials.json.example credentials.json
# Editar credentials.json com suas credenciais

# 2. Testar conectividade básica
python scripts/test_connection.py

# 3. Diagnóstico completo
python scripts/diagnose_nibo_service.py

# 4. Teste de todas as ferramentas
python scripts/test_all_tools_v2.py

# 5. Iniciar serviço
python scripts/start_nibo_service.py
```

### **Uso em Produção:**
```bash
# Monitor contínuo (em background)
python scripts/health_monitor.py --interval 60 &

# Diagnóstico diário
python scripts/diagnose_nibo_service.py

# Teste semanal das ferramentas
python scripts/test_all_tools_v2.py
```

### **Resolução de Problemas:**
```bash
# 1. Diagnóstico para identificar problema
python scripts/diagnose_nibo_service.py

# 2. Teste específico se necessário
python scripts/test_connection.py

# 3. Monitor para acompanhar correção
python scripts/health_monitor.py --once
```

---

## 🔧 **Códigos de Saída**

Todos os scripts seguem o padrão Unix:

| **Código** | **Significado** | **Ação** |
|------------|-----------------|----------|
| **0** | Sucesso total | Continuar operação |
| **1** | Erro crítico | Investigar e corrigir |
| **2** | Aviso/Parcial | Monitorar situação |
| **130** | Interrompido (Ctrl+C) | Normal |

---

## 📊 **Interpretação de Relatórios**

### **Diagnostic Report:**
```json
{
  "summary": {
    "overall_status": "success|warning|error",
    "success_rate": 95.5,
    "total_tests": 20
  },
  "results": [...]
}
```

### **Tools Test Report:**
```json
{
  "summary": {
    "tools_tested": 31,
    "tools_passed": 29,
    "success_rate": 93.5
  },
  "category_stats": {...}
}
```

### **Health Monitor Log:**
```json
{
  "timestamp": "2025-01-11T22:00:00",
  "status": "healthy",
  "checks": {
    "api": {"status": "healthy"},
    "tools": {"status": "healthy"},
    "system": {"status": "healthy"},
    "credentials": {"status": "healthy"}
  }
}
```

---

## 🚨 **Alertas e Notificações**

### **Status Críticos (Erro):**
- ❌ API não responde
- ❌ Credenciais inválidas
- ❌ Token expirado
- ❌ Dependências faltantes

### **Status de Atenção (Aviso):**
- ⚠️ Latência alta (>2000ms)
- ⚠️ Token expira em 1 hora
- ⚠️ Recursos do sistema altos
- ⚠️ Algumas ferramentas falhando

### **Status Normal (Sucesso):**
- ✅ Todos os sistemas operacionais
- ✅ API respondendo rapidamente
- ✅ Todas as ferramentas funcionando
- ✅ Recursos normais

---

## 🛡️ **Segurança e Logs**

### **Dados Sensíveis:**
- Tokens de API são mascarados nos logs
- Credenciais não são exibidas em texto plano
- Logs não contêm informações confidenciais

### **Arquivos de Log:**
- `service_status.json` - Status atual do serviço
- `health_monitor.log` - Histórico de saúde
- `diagnostic_report_*.json` - Relatórios de diagnóstico
- `tools_test_report_*.json` - Relatórios de teste

### **Rotação de Logs:**
```bash
# Limpar logs antigos (exemplo)
find . -name "*_report_*.json" -mtime +30 -delete
```

---

## 🔄 **Automação e CI/CD**

### **Scripts para CI/CD:**
```yaml
# GitHub Actions example
- name: Test Nibo MCP
  run: |
    python scripts/diagnose_nibo_service.py
    python scripts/test_all_tools_v2.py
```

### **Cron Jobs:**
```bash
# Diagnóstico diário às 2h
0 2 * * * cd /path/to/nibo-mcp && python scripts/diagnose_nibo_service.py

# Monitor de saúde contínuo
@reboot cd /path/to/nibo-mcp && python scripts/health_monitor.py &
```

---

## 📞 **Troubleshooting**

### **Problemas Comuns:**

**1. "Módulos não encontrados"**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/nibo-mcp"

# Instalar dependências
pip install -r requirements.txt
```

**2. "Credenciais não configuradas"**
```bash
# Verificar arquivo
cat credentials.json

# Validar estrutura
python -c "import json; print(json.load(open('credentials.json')))"
```

**3. "API não responde"**
```bash
# Teste manual
curl -H "ApiToken: YOUR_TOKEN" https://api.nibo.com.br/empresas/v1/categories

# Verificar conectividade
ping api.nibo.com.br
```

**4. "Dependências com conflito"**
```bash
# Criar ambiente virtual limpo
python -m venv venv_clean
source venv_clean/bin/activate
pip install -r requirements.txt
```

---

*Documentação atualizada para Nibo MCP v2.0 - Janeiro 2025*