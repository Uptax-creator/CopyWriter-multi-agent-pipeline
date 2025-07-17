# 🔒 Universal Credentials Manager

**Serviço independente de gerenciamento de credenciais para MCP Servers**

## 🎯 Objetivo

Serviço reutilizável que gerencia credenciais de forma segura para múltiplos MCP servers (Omie, Nibo, etc.) com:

- 🔐 **Criptografia AES-256** para dados sensíveis
- 🏢 **Multi-empresa** por projeto
- 🔍 **Logs de auditoria** detalhados
- 🌐 **API REST** para integração
- 📁 **Banco JSON** simples e portátil

## 🏗️ Arquitetura

```
universal-credentials-manager/
├── src/
│   ├── core/
│   │   ├── encryption.py      # Sistema de criptografia
│   │   ├── credentials.py     # Modelos de credenciais
│   │   └── storage.py         # Persistência JSON
│   ├── api/
│   │   ├── server.py          # FastAPI REST server
│   │   └── routes/
│   │       ├── auth.py        # Autenticação do serviço
│   │       └── credentials.py # CRUD de credenciais
│   └── clients/
│       ├── omie_client.py     # Cliente específico Omie
│       └── nibo_client.py     # Cliente específico Nibo
├── config/
│   ├── projects/              # Configurações por projeto
│   │   ├── omie-mcp.json     # Credenciais projeto Omie
│   │   └── nibo-mcp.json     # Credenciais projeto Nibo
│   └── security.json         # Configurações de segurança
├── scripts/
│   ├── setup.py              # Configuração inicial
│   └── migrate.py            # Migração de projetos
└── tests/
    └── test_security.py      # Testes de segurança
```

## 🚀 Características

### Multi-Projeto
- Cada MCP server tem seu próprio arquivo de credenciais
- Isolamento completo entre projetos
- Fácil adição de novos projetos

### Segurança
- Criptografia AES-256 para app_key/app_secret
- Senhas mestras por projeto
- Logs de auditoria estruturados
- Controle de acesso por API key

### Integração
- API REST para todos os MCP servers
- Cliente Python para fácil integração
- Compatível com qualquer linguagem

## 📋 Casos de Uso

1. **Omie MCP Server** → `GET /api/v1/projects/omie-mcp/credentials/empresa1`
2. **Nibo MCP Server** → `GET /api/v1/projects/nibo-mcp/credentials/company1`
3. **Novo ERP MCP** → `POST /api/v1/projects/erp-xyz/credentials`

## 🔧 Configuração

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar projeto
python scripts/setup.py --project omie-mcp

# 3. Migrar credenciais existentes
python scripts/migrate.py --from ../credentials.json --to omie-mcp

# 4. Iniciar serviço
python src/api/server.py --port 8100
```

## 🌐 API Endpoints

```
GET    /api/v1/projects                    # Listar projetos
GET    /api/v1/projects/{project}/companies # Listar empresas
GET    /api/v1/projects/{project}/credentials/{company} # Obter credenciais
POST   /api/v1/projects/{project}/credentials # Adicionar empresa
PUT    /api/v1/projects/{project}/credentials/{company} # Atualizar empresa
DELETE /api/v1/projects/{project}/credentials/{company} # Remover empresa
```

## 🔗 Integração com MCP Servers

```python
# No seu MCP server (omie-mcp, nibo-mcp, etc.)
from universal_credentials_client import CredentialsClient

client = CredentialsClient(
    base_url="http://localhost:8100",
    project="omie-mcp",
    api_key="seu-api-key"
)

# Obter credenciais
credentials = await client.get_credentials("empresa1")
app_key = credentials.app_key
app_secret = credentials.app_secret
```

## 🛡️ Benefícios

- ✅ **Reutilização**: Um serviço para todos os MCP servers
- ✅ **Segurança**: Criptografia centralizada
- ✅ **Simplicidade**: JSON como banco de dados
- ✅ **Escalabilidade**: Fácil adição de novos projetos
- ✅ **Auditoria**: Logs centralizados de acesso
- ✅ **Portabilidade**: Arquivos de configuração simples