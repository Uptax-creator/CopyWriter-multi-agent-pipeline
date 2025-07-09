# 🚀 Configuração Simplificada do Omie MCP no Claude

## ✅ **Configuração Automática (Recomendada)**

Execute este comando no terminal para configurar automaticamente:

```bash
# Criar configuração do Claude Desktop
mkdir -p ~/Library/Application\ Support/Claude/

cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "omie-erp": {
      "command": "python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
EOF

echo "✅ Configuração criada! Reinicie o Claude Desktop para ativar."
```

## 📍 **O que foi feito**

### 1. **Credenciais Automáticas**
- ✅ O servidor agora carrega credenciais automaticamente do `credentials.json`
- ✅ Não precisa mais configurar variáveis de ambiente no Claude

### 2. **Configuração Simplificada**
- ✅ Apenas 1 comando para configurar tudo
- ✅ Não precisa inserir credenciais na configuração
- ✅ Mais seguro (credenciais ficam apenas no arquivo local)

### 3. **Arquivo de Configuração Gerado**
Localização: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
```

## 🔄 **Passos para Ativar**

### 1. **Executar comando de configuração:**
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
EOF
```

### 2. **Fechar completamente o Claude Desktop**

### 3. **Abrir novamente o Claude Desktop**

### 4. **Testar a integração:**
```
Consulte as categorias do Omie ERP para mim
```

## 🧪 **Comandos de Teste**

Após configurar, teste com estas frases no Claude Desktop:

```
Liste as categorias do Omie ERP
```

```
Mostre os departamentos disponíveis
```

```
Consulte os tipos de documento do Omie
```

```
Crie uma conta a pagar para o fornecedor 16.726.230/0001-78 no valor de R$ 1.500,00 com vencimento em 31/12/2024
```

## 🔧 **Troubleshooting**

### Se não funcionar:

1. **Verificar se o arquivo foi criado:**
```bash
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. **Verificar conteúdo do arquivo:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. **Testar servidor manualmente:**
```bash
cd /Users/kleberdossantosribeiro/omie-mcp
python omie_http_server.py
```

4. **Verificar se Python está funcionando:**
```bash
which python
python --version
```

## 🎯 **Vantagens da Nova Configuração**

- ✅ **Mais simples**: Apenas 1 comando
- ✅ **Mais seguro**: Credenciais não expostas na configuração
- ✅ **Automático**: Carrega credenciais do arquivo `credentials.json`
- ✅ **Flexível**: Funciona com variáveis de ambiente OU arquivo
- ✅ **Rápido**: Configuração em segundos

---

**Execute o comando acima e reinicie o Claude Desktop!** 🚀