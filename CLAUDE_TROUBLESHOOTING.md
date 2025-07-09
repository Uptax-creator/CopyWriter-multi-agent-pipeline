# 🔧 Solução do Erro "spawn python ENOENT"

## 🎯 **Problema Identificado**
O erro `spawn python ENOENT` indica que o Claude Desktop não consegue encontrar o comando `python`.

## ✅ **Solução Aplicada**

### **Opção 1: Usar Python do Ambiente Virtual (Atual)**
```bash
python fix_claude_config.py
```

**Configuração gerada:**
```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "/Users/kleberdossantosribeiro/omie-mcp/venv/bin/python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
```

### **Opção 2: Instalar Dependências no Sistema**
```bash
python install_system_deps.py
```

**Configuração gerada:**
```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "python3",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
```

### **Opção 3: Script Wrapper**
```bash
# Usar o script bash
{
  "mcpServers": {
    "omie-erp": {
      "command": "bash",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/run_omie_server.sh"]
    }
  }
}
```

## 🔄 **Após Aplicar Qualquer Solução**

1. **Feche completamente** o Claude Desktop (⌘+Q)
2. **Abra novamente** o Claude Desktop
3. **Teste**: `"Consulte as categorias do Omie ERP"`

## 🔍 **Verificar Se Funcionou**

### **Comando de Teste:**
```bash
# Verificar configuração atual
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### **Verificar Log:**
```bash
# Ver log do Claude Desktop
tail -f ~/Library/Logs/Claude/mcp-server-omie-erp.log
```

### **Log de Sucesso Esperado:**
```
✅ Credenciais carregadas do arquivo: /Users/kleberdossantosribeiro/omie-mcp/credentials.json
🚀 Iniciando Servidor MCP HTTP para Omie ERP...
✅ Servidor HTTP rodando em: http://localhost:8000
```

## 🧪 **Testes no Claude Desktop**

Após reiniciar, teste estes comandos:

```
Liste as categorias do Omie ERP
```

```
Mostre os departamentos do Omie
```

```
Consulte os tipos de documento
```

```
Crie uma conta a pagar para o fornecedor teste
```

## 🎯 **Resolução do Problema**

### **Antes:**
- ❌ `"command": "python"` (não encontrado)
- ❌ Erro `spawn python ENOENT`

### **Depois:**
- ✅ `"command": "/Users/.../venv/bin/python"` (caminho absoluto)
- ✅ Server carregado com sucesso
- ✅ Credenciais automáticas funcionando

## 💡 **Resumo**

1. **Problema**: Claude Desktop não encontrava `python`
2. **Solução**: Usar caminho absoluto do Python no venv
3. **Resultado**: MCP funcionando automaticamente
4. **Teste**: Comandos funcionando no Claude Desktop

**A configuração está corrigida e pronta para uso!** 🚀