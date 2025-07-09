# 🚀 Comandos Simples para Configurar Claude MCP

## ✅ **Configuração Automática**

### Opção 1: Script Python (Recomendado)
```bash
cd /Users/kleberdossantosribeiro/omie-mcp
python configure_claude.py
```

### Opção 2: Script Bash
```bash
cd /Users/kleberdossantosribeiro/omie-mcp
bash setup_claude_mcp.sh
```

### Opção 3: Comando Manual Único
```bash
mkdir -p ~/Library/Application\ Support/Claude/ && cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "omie-erp": {
      "command": "python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
EOF && echo "✅ Configuração criada! Reinicie o Claude Desktop."
```

## 🔄 **Após executar qualquer comando acima:**

1. **Feche completamente** o Claude Desktop
2. **Abra novamente** o Claude Desktop  
3. **Teste com**: `"Consulte as categorias do Omie ERP"`

## 🎯 **Comandos de Teste no Claude Desktop:**

```
Liste as categorias do Omie ERP
```

```
Mostre os departamentos disponíveis no Omie
```

```
Consulte os tipos de documento do Omie
```

```
Crie uma conta a pagar para o fornecedor com CNPJ 16.726.230/0001-78, razão social "Fornecedor Teste", documento "NF-001", valor R$ 1.500,00, vencimento 31/12/2024, categoria "0.01"
```

```
Consulte as contas a pagar do Omie
```

## 🔧 **Se não funcionar:**

1. **Verificar se o arquivo foi criado:**
```bash
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. **Ver conteúdo do arquivo:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. **Testar servidor manualmente:**
```bash
cd /Users/kleberdossantosribeiro/omie-mcp
python omie_http_server.py
```

## 💡 **Resumo:**
- ✅ **Credenciais automáticas**: Carregadas do `credentials.json`
- ✅ **Configuração simples**: Apenas 1 comando
- ✅ **Testado**: Scripts verificam se tudo está funcionando
- ✅ **Seguro**: Credenciais não ficam expostas

---

**Execute um dos comandos acima e reinicie o Claude Desktop!** 🚀