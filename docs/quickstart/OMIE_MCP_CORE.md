# 🎯 Omie MCP Core - Guia de Início Rápido

> **Servidor MCP principal para integração com Omie ERP - Ready em 5 minutos**

## 📋 Visão Geral

O **Omie MCP Core** é o coração do sistema UPTAX, fornecendo todas as 25+ ferramentas essenciais para automação do Omie ERP através do protocolo MCP (Model Context Protocol).

### 🎯 **Principais Funcionalidades**
- ✅ **25+ Ferramentas**: Clientes, vendas, financeiro, produtos
- ✅ **Cache Inteligente**: Reduz 60% das chamadas API
- ✅ **Multi-tenant**: Suporte a múltiplas empresas
- ✅ **Webhooks**: Notificações em tempo real
- ✅ **Performance**: Otimizado para economia de créditos

---

## 🚀 Instalação e Configuração

### 1. **Localização**
```bash
cd /Users/kleberdossantosribeiro/uptaxdev/ACTIVE_SERVICES
```

### 2. **Verificar Dependências**
```bash
# Verificar Python
python --version  # Deve ser 3.12+

# Verificar se fastmcp está instalado
pip show fastmcp
```

### 3. **Configurar Credenciais**
```bash
# Verificar se existe o arquivo de credenciais
ls -la ../credentials.json

# Se não existir, copiar do template
cp ../credentials.json.example ../credentials.json

# Editar com suas credenciais Omie
nano ../credentials.json
```

**Template de credenciais:**
```json
{
  "omie": {
    "app_key": "SUA_APP_KEY_OMIE",
    "app_secret": "SEU_APP_SECRET_OMIE",
    "base_url": "https://app.omie.com.br/api/v1/"
  }
}
```

### 4. **Executar o Servidor**
```bash
# Método 1: Executar diretamente
python omie_fastmcp_unified.py

# Método 2: Como servidor HTTP (recomendado)
python omie_fastmcp_unified.py --transport sse --port 8001

# Método 3: Via Docker (produção)
cd .. && docker-compose up omie-mcp-core -d
```

---

## ⚡ Verificação de Funcionamento

### 1. **Teste Básico**
```bash
# Voltar ao diretório raiz
cd ..

# Executar teste rápido
python quick_test_mcp.py
```

### 2. **Verificar Logs**
```bash
# Ver logs em tempo real
tail -f logs/service.log

# Ou verificar output direto do servidor
# (se executando em modo direto)
```

### 3. **Testar via Claude Desktop**
Se você tem Claude Desktop configurado:
1. Abra Claude Desktop
2. Digite: "Listar clientes Omie"
3. Deve retornar lista de clientes do seu ERP

---

## 🛠️ Ferramentas Disponíveis

### 📊 **Clientes & Vendas**
- `listar_clientes` - Lista todos os clientes
- `incluir_cliente` - Adiciona novo cliente
- `alterar_cliente` - Edita cliente existente
- `consultar_pedido_venda` - Busca pedidos de venda
- `incluir_pedido_venda` - Cria novo pedido

### 💰 **Financeiro**
- `listar_contas_receber` - Contas a receber
- `incluir_conta_receber` - Nova conta a receber
- `listar_contas_pagar` - Contas a pagar
- `incluir_conta_pagar` - Nova conta a pagar
- `consultar_extrato_cc` - Extrato conta corrente

### 📦 **Produtos & Estoque**
- `listar_produtos` - Lista produtos
- `incluir_produto` - Adiciona produto
- `consultar_estoque` - Consulta estoque
- `alterar_produto` - Edita produto

### 📈 **Relatórios & Consultas**
- `obter_empresas` - Lista empresas cadastradas
- `consultar_nfe` - Consulta notas fiscais
- `obter_categorias` - Lista categorias
- `consultar_movimento_financeiro` - Extrato financeiro

---

## ⚙️ Configurações Avançadas

### 🔧 **Variáveis de Ambiente**
```bash
# Arquivo .env (opcional)
OMIE_APP_KEY=sua_app_key
OMIE_APP_SECRET=seu_app_secret
CACHE_ENABLED=true
CACHE_TTL=300
DEBUG_MODE=false
```

### 📊 **Configuração de Cache**
O servidor possui cache inteligente configurado por padrão:
- **TTL**: 5 minutos para consultas
- **TTL**: 1 minuto para listas dinâmicas
- **TTL**: 30 segundos para dados em tempo real

### 🔗 **Webhooks (Opcional)**
Para receber notificações automáticas:
```python
# Configuração de webhook no arquivo
WEBHOOK_URL = "https://seu-webhook.com/omie"
WEBHOOK_EVENTS = ["cliente.criado", "pedido.alterado"]
```

---

## 🚨 Resolução de Problemas

### ❌ **Erro: "Module not found"**
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install fastmcp requests python-dotenv
```

### ❌ **Erro: "Credenciais inválidas"**
```bash
# Verificar credenciais
cat ../credentials.json

# Testar credenciais direto na API Omie
curl -X POST "https://app.omie.com.br/api/v1/geral/empresas/" \
  -H "Content-Type: application/json" \
  -d '{"call":"ListarEmpresas","app_key":"SUA_KEY","app_secret":"SEU_SECRET"}'
```

### ❌ **Erro: "Port already in use"**
```bash
# Verificar portas em uso
lsof -i :8001

# Matar processo se necessário
kill -9 PID_DO_PROCESSO

# Usar porta diferente
python omie_fastmcp_unified.py --port 8002
```

### ❌ **Performance lenta**
```bash
# Habilitar cache (se não estiver)
export CACHE_ENABLED=true

# Verificar uso de memória
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Monitorar performance
python ../performance_monitor.py
```

---

## 📊 Monitoramento

### 🔍 **Verificar Status**
```bash
# Status do servidor
curl http://localhost:8001/health

# Métricas de performance
curl http://localhost:8001/metrics

# Lista de ferramentas disponíveis
curl http://localhost:8001/tools
```

### 📈 **Dashboard de Monitoramento**
```bash
# Iniciar dashboard (terminal separado)
cd ..
python monitoring_dashboard.py

# Acessar: http://localhost:8090
```

---

## 🎯 Economia de Créditos

### ⚡ **Otimizações Ativas**
1. **Cache Inteligente**: Evita consultas repetidas
2. **Classificação de Consultas**: Usa modelo adequado
3. **Batching**: Agrupa operações similares
4. **Compressão de Response**: Reduz tokens de resposta

### 📊 **Monitorar Economia**
```bash
# Verificar economia de créditos
python ../budget_tracker.py --service omie-mcp-core

# Relatório de usage
python ../performance_monitor.py --report daily
```

---

## 🚀 Próximos Passos

### 1. **Integrar com Claude Desktop**
- Configure o `claude_desktop_config.json`
- Teste ferramentas via chat

### 2. **Explorar Dashboard Web**
```bash
cd ../omie-dashboard-v2
python -m http.server 8080
# Acesse: http://localhost:8080
```

### 3. **Configurar Automações N8N**
```bash
cd ../github_projects/n8n-mcp-integration
# Seguir guia específico
```

### 4. **Expandir para Multi-tenant**
```bash
cd ../omie-tenant-manager
python -m src.main
# Acesse: http://localhost:8000/docs
```

---

## 📚 Documentação Adicional

- **API Reference**: [/docs/OMIE_API.md](../OMIE_API.md)
- **MCP Protocol**: [/docs/MCP_PROTOCOL.md](../MCP_PROTOCOL.md)
- **Troubleshooting**: [/docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Performance**: [/docs/PERFORMANCE.md](../PERFORMANCE.md)

---

## 💡 Dicas de Produtividade

### ✅ **Comandos Úteis**
```bash
# Reiniciar servidor rapidamente
pkill -f omie_fastmcp && python omie_fastmcp_unified.py

# Monitorar logs em tempo real
tail -f ../logs/service.log | grep -i error

# Backup das configurações
cp ../credentials.json ../backup/credentials_$(date +%Y%m%d).json
```

### ✅ **Atalhos de Desenvolvimento**
```bash
# Alias úteis (adicionar ao .bashrc/.zshrc)
alias omie-start="cd ACTIVE_SERVICES && python omie_fastmcp_unified.py"
alias omie-test="python quick_test_mcp.py"
alias omie-logs="tail -f logs/service.log"
```

---

**🎯 Pronto! Omie MCP Core rodando e otimizado para economia de créditos.**

📧 **Suporte**: Para dúvidas, consulte [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) ou abra issue no GitHub.