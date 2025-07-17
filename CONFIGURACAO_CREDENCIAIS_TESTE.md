# 🔐 CONFIGURAÇÃO DE CREDENCIAIS - VERSÃO DE TESTE

## 📋 **STATUS ATUAL DAS CREDENCIAIS**

---

## 🔧 **OMIE MCP - CREDENCIAIS CONFIGURADAS**

### **Arquivo**: `/Users/kleberdossantosribeiro/omie-mcp/credentials.json`

```json
{
  "app_key": "2687508979155",
  "app_secret": "23ae858794e1cd879232c81105604b1f"
}
```

### **Detalhes**:
- ✅ **App Key**: `2687508979155` (13 dígitos - formato válido)
- ✅ **App Secret**: `23ae858794e1cd879232c81105604b1f` (32 caracteres hex - formato válido)
- ✅ **Formato**: JSON simples padrão Omie
- ✅ **Localização**: Raiz do projeto

---

## 🔧 **NIBO MCP - CREDENCIAIS AVANÇADAS**

### **Arquivo**: `/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/credentials.json`

```json
{
  "companies": {
    "empresa_exemplo": {
      "name": "I9 MARKETING E TECNOLOGIA LTDA",
      "nibo_api_token": "2264E2C5B5464BFABC3D6E6820EBE47F",
      "company_id": "50404226-615e-48d2-9701-0e765f64e0b9",
      "base_url": "https://api.nibo.com.br",
      "token_expires_at": null,
      "token_timeout_minutes": 60,
      "active": true
    }
  },
  "default_company": "empresa_exemplo",
  "security": {
    "require_company_selection": true,
    "auto_refresh_tokens": true,
    "log_access_attempts": true
  }
}
```

### **Detalhes**:
- ✅ **Token**: `2264E2C5B5464BFABC3D6E6820EBE47F` (32 caracteres hex)
- ✅ **Company ID**: `50404226-615e-48d2-9701-0e765f64e0b9` (UUID válido)
- ✅ **Empresa**: `I9 MARKETING E TECNOLOGIA LTDA`
- ✅ **Base URL**: `https://api.nibo.com.br`
- ✅ **Multi-empresa**: Suporte configurado
- ✅ **Segurança**: Configurações avançadas ativas

---

## ⚠️ **MODO DE OPERAÇÃO ATUAL**

### **IMPORTANTE**: 
Os servidores HTTP puros atualmente estão em **MODO SIMULAÇÃO**

### **Como funciona**:
1. **Credenciais configuradas** ✅ (arquivos existem)
2. **Servidores HTTP** ✅ (não leem credenciais ainda)
3. **Respostas simuladas** ⚠️ (dados fictícios)

### **Exemplo de resposta simulada**:
```json
{
  "status": "conectado",
  "servidor": "Omie ERP",
  "modo": "simulação",
  "nota": "Dados simulados - Configure credenciais para dados reais"
}
```

---

## 🔄 **COMO ATIVAR CREDENCIAIS REAIS**

### **Opção 1: Modificar servidores HTTP para ler credenciais**

**Para Omie** (`omie_http_server_pure.py`):
```python
# Adicionar no início do arquivo
import json

def load_credentials():
    with open('/Users/kleberdossantosribeiro/omie-mcp/credentials.json', 'r') as f:
        return json.load(f)

# Usar nas ferramentas
credentials = load_credentials()
app_key = credentials['app_key']
app_secret = credentials['app_secret']
```

**Para Nibo** (`nibo_http_server_pure.py`):
```python
# Adicionar no início do arquivo
import json

def load_credentials():
    with open('/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/credentials.json', 'r') as f:
        return json.load(f)

# Usar nas ferramentas
credentials = load_credentials()
default_company = credentials['default_company']
company_data = credentials['companies'][default_company]
token = company_data['nibo_api_token']
company_id = company_data['company_id']
```

### **Opção 2: Usar servidores híbridos originais**

Os servidores híbridos já têm suporte completo a credenciais:
- `omie_mcp_server_hybrid.py` - Lê `credentials.json`
- `nibo_mcp_server_hybrid.py` - Lê `credentials.json` com multi-empresa

---

## 📊 **COMPARAÇÃO DE VERSÕES**

| Aspecto | Servidores HTTP Puros | Servidores Híbridos |
|---------|----------------------|---------------------|
| **Credenciais** | ❌ Não leem (simulação) | ✅ Leem e usam |
| **Dependências** | ✅ Apenas stdlib | ❌ Requer FastAPI |
| **Funcionalidade** | ⚠️ Simulada | ✅ Real |
| **Estabilidade** | ✅ Máxima | ⚠️ Dependente |
| **Desenvolvimento** | ✅ Rápido | ⚠️ Mais complexo |

---

## 🎯 **RECOMENDAÇÃO ATUAL**

### **Para Testes de Integração**:
✅ **Use servidores HTTP puros** (atual)
- Sem dependências externas
- Funciona imediatamente no Claude Desktop
- Dados simulados mas estrutura real

### **Para Produção**:
✅ **Migrar para servidores híbridos**
- Credenciais reais
- Funcionalidade completa
- Instalar dependências (FastAPI)

---

## 🚀 **PRÓXIMOS PASSOS**

### **Imediato (Teste)**:
1. **Continue com servidores HTTP puros**
2. **Teste estrutura das ferramentas**
3. **Valide integração Claude Desktop**

### **Produção (Futuro)**:
1. **Instalar dependências**: `pip install fastapi uvicorn requests`
2. **Configurar servidores híbridos**
3. **Testar com APIs reais**
4. **Deploy em produção**

---

## 💡 **RESUMO**

**✅ CREDENCIAIS**: Configuradas e válidas nos arquivos
**⚠️ UTILIZAÇÃO**: Servidores atuais em modo simulação
**🎯 OBJETIVO**: Testar integração antes de produção
**🚀 RESULTADO**: Sistema funcional para desenvolvimento

**As credenciais estão prontas, mas os servidores HTTP puros não as utilizam ainda - isso permite testar a integração sem afetar dados reais!**