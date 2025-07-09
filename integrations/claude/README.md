# Integração com Claude Desktop

Este guia explica como integrar o Omie MCP Server com Claude Desktop.

## Pré-requisitos

- Claude Desktop instalado
- Omie MCP Server configurado
- Python 3.8+ com dependências instaladas

## Instalação

### 1. Configuração Automática

Execute o script de configuração:

```bash
python scripts/configure_claude.py
```

### 2. Configuração Manual

Edite o arquivo de configuração do Claude Desktop:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Adicione a configuração:

```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "python3",
      "args": ["/caminho/para/claude_http_client.py"]
    }
  }
}
```

### 3. Iniciar o Servidor

Em um terminal, execute:

```bash
python scripts/start_server.py
```

### 4. Reiniciar Claude Desktop

Feche completamente o Claude Desktop e reabra.

## Uso

Após a configuração, você pode usar comandos como:

- "Consulte as categorias do Omie ERP"
- "Liste os departamentos cadastrados"
- "Inclua um novo cliente com CNPJ 12.345.678/0001-90"
- "Crie uma conta a pagar para o fornecedor 98.765.432/0001-10"

## Troubleshooting

### Erro: spawn python ENOENT

**Solução**: Especifique o caminho completo do Python:

```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "/Users/seu-usuario/omie-mcp/venv/bin/python",
      "args": ["/Users/seu-usuario/omie-mcp/claude_http_client.py"]
    }
  }
}
```

### Erro: JSON parsing error

**Solução**: Certifique-se de que o servidor HTTP está rodando:

```bash
python scripts/start_server.py
```

### Logs do Claude Desktop

**macOS**: `~/Library/Application Support/Claude/mcp-server-*.log`
**Windows**: `%APPDATA%/Claude/mcp-server-*.log`
**Linux**: `~/.config/Claude/mcp-server-*.log`

## Arquitetura

```
Claude Desktop → claude_http_client.py → HTTP Server → Omie API
```

O `claude_http_client.py` atua como um proxy MCP que comunica com o servidor HTTP na porta 3000.