# 🏗️ Omie Tenant Manager

Sistema de gerenciamento multi-tenant para o Omie MCP Server.

## 📋 Funcionalidades

- ✅ **Gestão de Empresas**: CRUD completo
- ✅ **Gestão de Usuários**: Vinculação por empresa  
- ✅ **Gestão de Aplicações**: Credenciais OAuth 2.0
- ✅ **Vinculação Cliente-Aplicação**: Multi-tenant
- ✅ **Autenticação JWT**: Tokens seguros
- ✅ **Auditoria**: Log de todas as operações
- ✅ **Backup Automático**: SQLite + Cloud

## 🚀 Quick Start

### 1. Instalação
```bash
cd omie-tenant-manager
pip install -r requirements.txt
```

### 2. Executar Aplicação
```bash
python -m src.main
```

### 3. Acessar Documentação
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura

```
omie-tenant-manager/
├── src/
│   ├── models/database.py   # Modelos SQLAlchemy
│   ├── routers/            # Endpoints da API
│   ├── auth.py             # Autenticação OAuth 2.0
│   ├── database.py         # Configuração SQLite
│   └── main.py             # Aplicação FastAPI
├── docs/                   # Documentação
├── data/                   # Banco SQLite
└── requirements.txt
```

## 🔐 Autenticação

### 1. Criar Aplicação
```bash
curl -X POST "http://localhost:8000/aplicacoes/" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "Minha Aplicação"}'
```

### 2. Obter Token
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"app_key": "sua_app_key", "app_secret": "seu_app_secret"}'
```

## 💾 Tecnologias

- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco leve e eficiente
- **BCrypt**: Hashing seguro de senhas
- **JWT**: Tokens de autenticação