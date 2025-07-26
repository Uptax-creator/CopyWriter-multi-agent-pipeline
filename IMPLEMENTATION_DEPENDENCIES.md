# 🔧 DEPENDÊNCIAS DE IMPLEMENTAÇÃO - UPTAX PLATFORM

## 📋 **CHECKLIST PARA CONFIGURAÇÃO MANUAL**

### **🔑 API KEYS & TOKENS NECESSÁRIOS**

#### **1. Supabase Configuration**
```bash
# Criar conta em: https://supabase.com
# Após criação, obter:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Adicionar ao .env:
echo "SUPABASE_URL=your_url_here" >> .env
echo "SUPABASE_ANON_KEY=your_key_here" >> .env
echo "SUPABASE_SERVICE_KEY=your_service_key_here" >> .env
```

#### **2. GitHub Personal Access Token**
```bash
# Criar em: https://github.com/settings/tokens
# Permissions necessárias:
# - repo (full control)
# - issues (read/write)
# - workflow (if using actions)

GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Adicionar ao .env:
echo "GITHUB_TOKEN=your_token_here" >> .env
```

#### **3. Multi-LLM API Keys**
```bash
# Google Gemini
# Obter em: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI (opcional)
# Obter em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Adicionar ao .env:
echo "GEMINI_API_KEY=your_gemini_key" >> .env
echo "OPENAI_API_KEY=your_openai_key" >> .env
```

---

## 🐍 **DEPENDÊNCIAS PYTHON DETECTADAS**

### **Instalação Automática Preparada**
```bash
# O script irá instalar automaticamente:
pip install supabase-py
pip install pygithub
pip install google-generativeai
pip install openai
pip install fastmcp
pip install psutil
pip install httpx
pip install asyncio-mqtt
```

### **Dependências Já Instaladas**
```bash
✅ sqlite3 (built-in)
✅ json (built-in) 
✅ datetime (built-in)
✅ typing (built-in)
✅ pathlib (built-in)
✅ dataclasses (built-in)
```

---

## 📦 **SETUP SUPABASE SCHEMA**

### **Tabelas Necessárias (Auto-criação)**
```sql
-- Será criado automaticamente pelo script
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'pending',
  priority INTEGER DEFAULT 3,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE budget_tracking (
  id SERIAL PRIMARY KEY,
  llm_provider TEXT NOT NULL,
  cost DECIMAL(10,4),
  tokens_used INTEGER,
  task_id INTEGER REFERENCES tasks(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_metrics (
  id SERIAL PRIMARY KEY,
  agent_name TEXT NOT NULL,
  task_count INTEGER DEFAULT 0,
  success_rate DECIMAL(5,2),
  avg_response_time DECIMAL(8,2),
  last_heartbeat TIMESTAMP DEFAULT NOW()
);
```

---

## 🔍 **VERIFICAÇÃO DE DEPENDÊNCIAS**

### **Script de Verificação (Será Executado)**
```python
# check_dependencies.py - Criado automaticamente
import subprocess
import sys

def check_dependency(package):
    try:
        __import__(package)
        return True
    except ImportError:
        return False

dependencies = [
    'supabase', 'github', 'google.generativeai', 
    'openai', 'fastmcp', 'psutil', 'httpx'
]

missing = [dep for dep in dependencies if not check_dependency(dep)]
if missing:
    print(f"⚠️  Instalar: pip install {' '.join(missing)}")
else:
    print("✅ Todas as dependências OK")
```

---

## 🚀 **COMANDOS DE ATIVAÇÃO (QUANDO RETORNAR)**

### **1. Ativar Platform**
```bash
cd ~/uptaxdev
./start_uptax_platform.sh
```

### **2. Verificar Status**
```bash
python check_platform_status.py
```

### **3. Configurar Pendências**
```bash
python setup_missing_dependencies.py
```

### **4. Testar Integração**
```bash
python test_platform_integration.py
```

---

## ⚠️ **KNOWN ISSUES & SOLUÇÕES**

### **Issue 1: Supabase Connection**
```bash
# Erro: "Invalid API key"
# Solução: Verificar se SUPABASE_ANON_KEY está correto
python -c "from supabase import create_client; print('OK')"
```

### **Issue 2: GitHub Rate Limits**
```bash
# Erro: "API rate limit exceeded"
# Solução: Usar GitHub token com higher limits
# Rate limit: 5000 requests/hour com token
```

### **Issue 3: Multi-LLM Conflicts**
```bash
# Erro: "Multiple API clients conflict"
# Solução: Usar singleton pattern (já implementado)
```

---

## 📊 **STATUS DE IMPLEMENTAÇÃO**

### **Componentes Implementados (Auto)**
- ✅ Budget Tracker Core
- ✅ MCP Optimizer Integration  
- ✅ Monitoring Dashboard Unified
- ✅ Setup Scripts
- ✅ Dependency Checker

### **Configuração Manual Necessária**
- 🔑 Supabase Account + Keys
- 🔑 GitHub Token
- 🔑 Multi-LLM API Keys
- 🔑 Schema Creation (auto se keys OK)

---

## 📞 **NEXT STEPS (QUANDO RETORNAR)**

1. **Executar**: `python check_dependencies.py`
2. **Configurar**: APIs keys conforme lista acima
3. **Testar**: `python test_platform_integration.py`
4. **Ativar**: `./start_uptax_platform.sh`

**🎯 Tempo estimado para setup manual: 15-20 minutos**