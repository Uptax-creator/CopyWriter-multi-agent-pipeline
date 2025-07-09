# 🚀 Omie MCP Server

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/kleberdossantosribeiro/omie-mcp)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Servidor MCP HTTP para integração com Omie ERP** - Arquitetura híbrida com estrutura modular e API REST.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Ferramentas Disponíveis](#ferramentas-disponíveis)
- [Integrações](#integrações)
- [Desenvolvimento](#desenvolvimento)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Omie MCP Server** é um servidor HTTP que implementa o protocolo MCP (Model Context Protocol) para integração com o Omie ERP. Ele permite que assistentes de IA como Claude Desktop interajam com o sistema Omie de forma segura e eficiente.

### ✨ Principais Características

- 🏗️ **Arquitetura Híbrida**: Combina HTTP REST com protocolo MCP
- 📦 **Estrutura Modular**: Código organizado e fácil de manter
- 🔒 **Validação Robusta**: Validação completa de dados (CNPJ, CPF, email, etc.)
- 🧹 **Sanitização de Dados**: Prevenção de problemas de encoding
- 📊 **Logs Estruturados**: Monitoramento e debugging facilitados
- 🔧 **Configuração Unificada**: Gerenciamento centralizado de configurações
- 🧪 **Testes Abrangentes**: Cobertura completa com scripts de validação

## 🏗️ Arquitetura

### Estrutura do Projeto

```
omie-mcp/
├── src/                        # Código principal
│   ├── __init__.py
│   ├── server.py              # Servidor HTTP MCP principal
│   ├── config.py              # Configurações unificadas
│   ├── client/                # Clientes HTTP
│   │   ├── omie_client.py     # Cliente para API Omie
│   │   └── mcp_client.py      # Cliente MCP para Claude Desktop
│   ├── tools/                 # Ferramentas MCP
│   │   ├── base.py            # Classe base para tools
│   │   ├── consultas.py       # Ferramentas de consulta
│   │   ├── cliente_tool.py    # Gerenciamento de clientes/fornecedores
│   │   ├── contas_pagar.py    # Gerenciamento de contas a pagar
│   │   └── contas_receber.py  # Gerenciamento de contas a receber
│   ├── utils/                 # Utilitários
│   │   ├── logger.py          # Configuração de logs
│   │   ├── validators.py      # Validadores de dados
│   │   └── sanitizers.py      # Sanitizadores JSON
│   └── models/                # Modelos de dados
│       └── schemas.py         # Schemas Pydantic
├── tests/                     # Testes
│   ├── test_basic.py          # Testes básicos
│   └── test_tools/            # Testes de ferramentas
├── scripts/                   # Scripts de execução
│   ├── start_server.py        # Iniciar servidor
│   ├── configure_claude.py    # Configurar Claude Desktop
│   ├── test_tool.py           # Testar ferramentas
│   └── validate_all.py        # Validação completa
├── docs/                      # Documentação
├── integrations/              # Integrações
├── requirements.txt           # Dependências
├── credentials.json           # Credenciais locais
└── run_server.py             # Entry point principal
```

### Fluxo de Funcionamento

```
Claude Desktop → HTTP Client → HTTP Server → Omie API
     ↓
Copilot Studio → HTTP Server → Omie API
     ↓
N8N/Zapier → HTTP Server → Omie API
```

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- Credenciais do Omie ERP (app_key e app_secret)
- Claude Desktop (para integração MCP)

### Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/kleberdossantosribeiro/omie-mcp.git
cd omie-mcp

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\\Scripts\\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar credenciais
cp credentials.json.example credentials.json
# Editar credentials.json com suas credenciais Omie
```

### Configuração de Credenciais

Crie o arquivo `credentials.json` na raiz do projeto:

```json
{
  "app_key": "sua_app_key_omie",
  "app_secret": "seu_app_secret_omie"
}
```

## 🚀 Uso

### 1. Iniciar o Servidor

```bash
python scripts/start_server.py
```

O servidor estará disponível em: `http://localhost:3000`

### 2. Configurar Claude Desktop

```bash
python scripts/configure_claude.py
```

### 3. Testar Funcionamento

```bash
# Validar sistema completo
python scripts/validate_all.py

# Testar ferramenta específica
python scripts/test_tool.py consultar_categorias
```

### 4. Usar no Claude Desktop

Após configurar, você pode usar comandos como:

- "Consulte as categorias do Omie ERP"
- "Liste os departamentos cadastrados"
- "Inclua um novo cliente com CNPJ 12.345.678/0001-90"

## 🛠️ Ferramentas Disponíveis

### 🔍 Consultas

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `consultar_categorias` | Lista categorias | `pagina`, `registros_por_pagina`, `filtrar_por_codigo` |
| `consultar_departamentos` | Lista departamentos | `pagina`, `registros_por_pagina`, `filtrar_por_codigo` |
| `consultar_tipos_documento` | Lista tipos de documento | `filtrar_por_codigo` |
| `consultar_clientes` | Lista clientes | `pagina`, `cnpj_cpf`, `filtrar_por_nome` |
| `consultar_fornecedores` | Lista fornecedores | `pagina`, `cnpj_cpf`, `filtrar_por_nome` |
| `consultar_contas_pagar` | Lista contas a pagar | `pagina`, `filtrar_por_fornecedor` |
| `consultar_contas_receber` | Lista contas a receber | `pagina`, `filtrar_por_cliente` |

### 👥 Clientes e Fornecedores

| Ferramenta | Descrição | Parâmetros Obrigatórios |
|------------|-----------|-------------------------|
| `incluir_cliente` | Inclui novo cliente | `cnpj_cpf`, `razao_social` |
| `incluir_fornecedor` | Inclui novo fornecedor | `cnpj_cpf`, `razao_social` |
| `alterar_cliente` | Altera cliente existente | `codigo_cliente_omie` |
| `alterar_fornecedor` | Altera fornecedor existente | `codigo_fornecedor_omie` |

### 💰 Contas a Pagar

| Ferramenta | Descrição | Parâmetros Obrigatórios |
|------------|-----------|-------------------------|
| `incluir_conta_pagar` | Inclui nova conta a pagar | `cnpj_fornecedor`, `data_vencimento`, `valor_documento`, `codigo_categoria` |
| `alterar_conta_pagar` | Altera conta a pagar | `codigo_lancamento_omie` |
| `excluir_conta_pagar` | Exclui conta a pagar | `codigo_lancamento_omie` |

### 💵 Contas a Receber

| Ferramenta | Descrição | Parâmetros Obrigatórios |
|------------|-----------|-------------------------|
| `incluir_conta_receber` | Inclui nova conta a receber | `cnpj_cliente`, `data_vencimento`, `valor_documento`, `codigo_categoria` |
| `alterar_conta_receber` | Altera conta a receber | `codigo_lancamento_omie` |
| `excluir_conta_receber` | Exclui conta a receber | `codigo_lancamento_omie` |

## 🔗 Integrações

### Claude Desktop

O servidor foi otimizado para funcionar com Claude Desktop através do protocolo MCP:

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

### Microsoft Copilot Studio

Integração via API REST padrão - veja `integrations/copilot/` para detalhes.

### N8N

Workflows prontos disponíveis em `integrations/n8n/`.

### Zapier

Configuração disponível em `integrations/zapier/`.

## 🧪 Desenvolvimento

### Executar Testes

```bash
# Testes básicos
python tests/test_basic.py

# Validação completa
python scripts/validate_all.py

# Testar ferramenta específica
python scripts/test_tool.py <nome_ferramenta> '<argumentos_json>'
```

### Adicionar Nova Ferramenta

1. Crie a classe da ferramenta em `src/tools/`
2. Herde de `BaseTool`, `ConsultaTool` ou `CrudTool`
3. Implemente os métodos obrigatórios
4. Registre no `src/server.py`

Exemplo:

```python
class MinhaNovaFerramenta(BaseTool):
    def get_name(self) -> str:
        return "minha_ferramenta"
    
    def get_description(self) -> str:
        return "Descrição da ferramenta"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "parametro": {"type": "string"}
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Implementar lógica
        return "Resultado"
```

### Estrutura de Logs

O sistema usa logs estruturados:

```python
from src.utils.logger import logger

logger.info("Mensagem informativa")
logger.error("Mensagem de erro")
logger.debug("Mensagem de debug")
```

## 📚 Documentação Adicional

- [Arquitetura HTTP](HTTP_ARCHITECTURE.md) - Detalhes da arquitetura
- [Plano de Reestruturação](RESTRUCTURE_PLAN.md) - Processo de desenvolvimento
- [Guia de Troubleshooting](TROUBLESHOOTING.md) - Solução de problemas
- [Contexto do Projeto](PROJECT_CONTEXT.md) - Histórico e contexto

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

- 📧 Email: [seu-email@exemplo.com]
- 🐛 Issues: [GitHub Issues](https://github.com/kleberdossantosribeiro/omie-mcp/issues)
- 📖 Wiki: [GitHub Wiki](https://github.com/kleberdossantosribeiro/omie-mcp/wiki)

## 🏆 Reconhecimentos

- [Omie ERP](https://omie.com.br) - Sistema ERP integrado
- [Claude Desktop](https://claude.ai) - Assistente de IA
- [FastAPI](https://fastapi.tiangolo.com) - Framework web moderno
- [Pydantic](https://pydantic-docs.helpmanual.io) - Validação de dados

---

**Desenvolvido com ❤️ para a comunidade brasileira de desenvolvedores**