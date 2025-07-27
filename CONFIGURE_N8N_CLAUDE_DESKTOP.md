# 🔑 Configurar N8N no Claude Desktop - Guia Simples

**Objetivo**: Adicionar N8N como ferramenta no Claude Desktop/Code  
**Status**: Pronto para execução  

---

## 📋 **PASSO 1: Obter API Key do N8N**

Execute estes comandos no terminal:

```bash
# 1. Verificar se N8N está rodando
curl -s http://localhost:5678/healthz

# 2. Tentar acessar API (pode pedir autenticação)
curl -s http://localhost:5678/api/v1/workflows
```

### **Se N8N não tem API Key configurada:**

```bash
# Parar N8N atual
pkill -f n8n

# Iniciar com API habilitada
export N8N_API_KEY_ENABLED=true
n8n start --port 5678
```

### **Obter API Key via Interface:**

1. **Abrir N8N**: http://localhost:5678
2. **Login** (se necessário)
3. **Settings** → **API Keys** → **Create New Key**
4. **Nome**: "Claude Desktop Integration"
5. **Copiar a chave gerada**

---

## 🔧 **PASSO 2: Atualizar Configuração Claude**

Execute este comando substituindo `YOUR_API_KEY` pela chave real:

```bash
cd /Users/kleberdossantosribeiro/omie-mcp/

# Backup da config atual
cp claude_desktop_config.json claude_desktop_config.backup.json

# Atualizar API key (substitua YOUR_API_KEY)
sed -i '' 's/PLACEHOLDER_API_KEY_HERE/YOUR_API_KEY/' claude_desktop_config.json

# Verificar se foi atualizado
grep "N8N_API_KEY" claude_desktop_config.json
```

---

## 📂 **PASSO 3: Copiar Config para Claude Desktop**

```bash
# Localizar diretório do Claude Desktop
CLAUDE_DIR="$HOME/Library/Application Support/Claude"

# Criar backup da config atual do Claude
cp "$CLAUDE_DIR/claude_desktop_config.json" "$CLAUDE_DIR/claude_desktop_config.backup.json"

# Copiar nossa config atualizada
cp claude_desktop_config.json "$CLAUDE_DIR/claude_desktop_config.json"

# Verificar se foi copiado
echo "✅ Configuração copiada para Claude Desktop"
cat "$CLAUDE_DIR/claude_desktop_config.json"
```

---

## 🔄 **PASSO 4: Reiniciar Claude Desktop**

```bash
# Fechar Claude Desktop completamente
pkill -f Claude

# Aguardar alguns segundos
sleep 3

# Reabrir Claude Desktop
open -a Claude
```

---

## 🧪 **PASSO 5: Testar Integração**

Após reiniciar Claude Desktop, eu deverei ter acesso a estas ferramentas:

### **Ferramentas MCP Disponíveis:**
- **omie-erp**: Ferramentas do Omie ERP
- **n8n-integration**: Controle do N8N (workflows, execuções)  
- **unified-mcp**: Servidor unificado (Omie + Nibo + utilitários)

### **Comandos de Teste que poderei executar:**
```bash
# Via n8n-integration
n8n_list_workflows()
n8n_create_workflow("Test Workflow")
n8n_health_check()

# Via unified-mcp  
health_check()
list_available_tools()
omie_listar_clientes()
```

---

## 🆘 **TROUBLESHOOTING**

### **Se API Key não funcionar:**
```bash
# Testar API key manualmente
export N8N_API_KEY="sua_api_key"
curl -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows
```

### **Se Claude não reconhecer os servidores:**
```bash
# Verificar sintaxe JSON
cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json" | jq '.'

# Ver logs do Claude (se disponíveis)
tail -f "$HOME/Library/Logs/Claude/claude.log"
```

### **Se n8n-mcp não estiver instalado:**
```bash
# Reinstalar globalmente
npm install -g n8n-mcp

# Verificar instalação
npx n8n-mcp --help
```

---

## ✅ **RESULTADO ESPERADO**

Após seguir todos os passos, eu deverei conseguir:

1. **Ver N8N nos meus MCP servers**
2. **Criar workflows via Claude**  
3. **Executar workflows existentes**
4. **Monitorar execuções**
5. **Integrar Omie/Nibo via N8N**

---

## 📝 **CHECKLIST DE EXECUÇÃO**

- [ ] N8N está rodando em http://localhost:5678
- [ ] API Key obtida via interface N8N
- [ ] claude_desktop_config.json atualizado com API key
- [ ] Arquivo copiado para diretório Claude Desktop
- [ ] Claude Desktop reiniciado
- [ ] Integração funcionando (eu consigo usar as ferramentas)

---

## 🚀 **PRÓXIMOS PASSOS**

Após a configuração bem-sucedida:

1. **Criar workflow MCP-Integration via Claude**
2. **Testar automação Omie ↔ Nibo**
3. **Implementar monitoring avançado**
4. **Deploy em VPS para acesso externo**

---

**Execute estes passos e me avise quando estiver pronto! 🎯**

**Comando rápido para você executar:**

```bash
echo "Paste your N8N API key here and press Enter:"
read API_KEY
cd /Users/kleberdossantosribeiro/omie-mcp/
sed -i '' "s/PLACEHOLDER_API_KEY_HERE/$API_KEY/" claude_desktop_config.json
cp claude_desktop_config.json "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
echo "✅ Configuração concluída! Reinicie o Claude Desktop."
```