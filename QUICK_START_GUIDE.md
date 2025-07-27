# 🚀 UPTAX - Guia de Início Imediato

> **Para você que precisa começar a usar o sistema UPTAX agora mesmo!**

---

## ⚡ **Em 5 Minutos**

### **1. Dashboard Principal (MAIS IMPORTANTE)**
```bash
cd /Users/kleberdossantosribeiro/uptaxdev
python3 start_uptax_dashboard.py
```
**📱 Acesse**: http://localhost:8081  
**✅ Você verá**: Status de todos os serviços em tempo real

### **2. Testar Integrações**
```bash
python3 unified_credentials_manager.py
```
**✅ Mostra**: Status Omie, Nibo, N8N, Context7

### **3. MCP Claude Desktop (Se você usa Claude)**
```bash
python3 n8n_mcp_server_standard.py test
```
**✅ Resultado**: "Servidor N8N testado com sucesso!"

---

## 🎯 **Top 5 Aplicações - Como Usar**

### **1. 📊 Dashboard Web** - `start_uptax_dashboard.py`
```bash
python3 start_uptax_dashboard.py
# Acesse: http://localhost:8081
```
**O QUE FAZ**: Mostra status de todos os serviços  
**QUANDO USAR**: Sempre! É sua interface principal  
**RESULTADO**: Dashboard web com métricas em tempo real

### **2. 🔐 Credentials Manager** - `unified_credentials_manager.py`
```bash
python3 unified_credentials_manager.py
```
**O QUE FAZ**: Gerencia credenciais de Omie, Nibo, N8N  
**QUANDO USAR**: Quando APIs não estão funcionando  
**RESULTADO**: Relatório de status de todas as credenciais

### **3. 🔄 N8N MCP Server** - `n8n_mcp_server_standard.py`
```bash
# Para testar:
python3 n8n_mcp_server_standard.py test

# Para usar no Claude Desktop (já configurado):
# Use as ferramentas MCP no Claude Desktop
```
**O QUE FAZ**: Integra N8N com Claude Desktop  
**QUANDO USAR**: Para automatizar workflows via Claude  
**RESULTADO**: 5 ferramentas N8N disponíveis no Claude

### **4. 🧪 Integration Tester** - `orchestrated_n8n_integration_test.py`
```bash
python3 orchestrated_n8n_integration_test.py
```
**O QUE FAZ**: Testa todas as integrações de forma otimizada  
**QUANDO USAR**: Para verificar se tudo está funcionando  
**RESULTADO**: Relatório completo + custo otimizado ($0.237)

### **5. 🏗️ Infrastructure Agent** - `infrastructure_agent_mcp.py`
```bash
python3 infrastructure_agent_mcp.py
```
**O QUE FAZ**: Monitora Docker, recursos do sistema  
**QUANDO USAR**: Quando Docker está lento ou travado  
**RESULTADO**: Relatório de saúde da infraestrutura

---

## 🆘 **Problemas Mais Comuns**

### **"Dashboard não abre"**
```bash
# Verificar se porta está livre
lsof -i :8081

# Se ocupada, matar processo
kill -9 $(lsof -t -i:8081)

# Tentar novamente
python3 start_uptax_dashboard.py
```

### **"Credenciais inválidas"**
```bash
# Verificar arquivo de credenciais
cat credentials.json

# Validar credenciais
python3 unified_credentials_manager.py

# Se Nibo der erro 401, o header deve ser "apitoken", não "Authorization"
```

### **"Docker travado"**
```bash
# Recovery automático
./docker-recovery.sh

# Ou manual
docker system prune -f
docker-compose down && docker-compose up -d
```

### **"N8N não conecta"**
```bash
# Verificar se N8N Dev está rodando
curl http://localhost:5679/rest/workflows

# Se não, iniciar Docker N8N
docker-compose -f docker-compose.n8n-dev.yml up -d
```

### **"Claude Desktop MCP não funciona"**
```bash
# Verificar config
cat "/Users/kleberdossantosribeiro/Library/Application Support/Claude/claude_desktop_config.json"

# Testar servidor
python3 n8n_mcp_server_standard.py test

# Restart Claude Desktop se necessário
```

---

## 📁 **Estrutura Simples**

```
📱 PRINCIPAIS (use estes!)
├── start_uptax_dashboard.py      ← COMECE AQUI!
├── unified_credentials_manager.py ← Para credenciais
├── n8n_mcp_server_standard.py    ← Para Claude Desktop
└── orchestrated_n8n_integration_test.py ← Para testar tudo

🔧 UTILITÁRIOS (quando precisar)
├── docker-recovery.sh            ← Docker travado
├── setup_claude_desktop.py       ← Configurar Claude
└── infrastructure_agent_mcp.py   ← Monitor sistema

📊 DASHBOARDS (interfaces web)
├── omie-dashboard-v2/            ← Dashboard Omie
└── monitoring_dashboard.py       ← Monitor avançado

📚 DOCUMENTAÇÃO (para entender)
├── README.md                     ← Documentação completa
├── MCP_PROTOCOL_BEST_PRACTICES.md ← Padrões MCP
└── UPTAX_FINAL_STATUS_REPORT.md  ← Status final
```

---

## 🎯 **Cenários de Uso**

### **"Quero ver se está tudo funcionando"**
```bash
python3 start_uptax_dashboard.py
# Acesse: http://localhost:8081
```

### **"Quero testar as APIs"**
```bash
python3 unified_credentials_manager.py
```

### **"Quero usar no Claude Desktop"**
```bash
# Já está configurado! Apenas use as ferramentas N8N no Claude
```

### **"Quero automatizar algo"**
```bash
# Use o dashboard web ou Claude Desktop
# 8 workflows N8N estão prontos em: n8n_workflows_ready/
```

### **"Docker está travado"**
```bash
./docker-recovery.sh
```

### **"Quero ver logs"**
```bash
# Dashboard web: http://localhost:8081
# Ou arquivos: ls logs/
```

---

## 📊 **Status Atual**

✅ **Funcionando 100%**:
- Dashboard Web
- Credentials Manager  
- APIs Core (Omie + Nibo)
- MCP N8N Server
- Documentação

⚠️ **Funcionando Parcial**:
- N8N Dev (precisa Docker)
- N8N Prod (token issue)

❌ **Não Funcionando**:
- Nenhum serviço core está offline!

---

## 🚀 **Próximos Passos**

1. **Comece com**: `python3 start_uptax_dashboard.py`
2. **Se tudo OK**: Use normalmente
3. **Se algo falha**: `python3 unified_credentials_manager.py`
4. **Para Docker**: `./docker-recovery.sh`
5. **Para automação**: Use Claude Desktop (MCP já configurado)

---

**🎉 Sistema operacional e pronto para uso!**  
**📞 Qualquer problema**: Execute o dashboard e veja o status real-time

**⏰ Tempo total para começar**: 2 minutos