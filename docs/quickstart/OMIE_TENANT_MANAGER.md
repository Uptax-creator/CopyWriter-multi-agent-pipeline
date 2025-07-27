# 🏢 Omie Tenant Manager - Guia de Início Rápido

> **Sistema de gerenciamento multi-empresa para o Omie MCP - Ready em 3 minutos**

## 📋 Visão Geral

O **Omie Tenant Manager** é o sistema de controle de acesso e gerenciamento multi-empresa do UPTAX, permitindo que múltiplas empresas usem o sistema com segurança e isolamento de dados.

### 🎯 **Principais Funcionalidades**
- ✅ **Multi-tenant**: Múltiplas empresas isoladas
- ✅ **Gestão de Usuários**: Controle de acesso por empresa  
- ✅ **OAuth 2.0**: Autenticação segura
- ✅ **API REST**: Interface padronizada
- ✅ **Auditoria**: Log de todas as operações

---

## 🚀 Instalação e Configuração

### 1. **Localização**
```bash
cd /Users/kleberdossantosribeiro/uptaxdev/omie-tenant-manager
```

### 2. **Verificar Dependências**
```bash
# Verificar Python
python --version  # Deve ser 3.12+

# Instalar dependências
pip install -r requirements.txt
```

### 3. **Configurar Banco de Dados**
```bash
# O banco SQLite é criado automaticamente
# Localização: data/omie_tenant.db

# Verificar se diretório existe
mkdir -p data
```

### 4. **Executar a Aplicação**
```bash
# Método 1: Executar diretamente
python -m src.main

# Método 2: Via uvicorn (produção)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Método 3: Via Docker
docker-compose up tenant-manager -d
```

---

## ⚡ Verificação de Funcionamento

### 1. **Acessar Documentação da API**
```bash
# Abrir no navegador
open http://localhost:8000/docs

# Ou via curl
curl http://localhost:8000/docs
```

### 2. **Verificar Health Check**
```bash
# Status da aplicação
curl http://localhost:8000/health

# Versão da API
curl http://localhost:8000/version
```

### 3. **Testar Criação de Empresa**
```bash
curl -X POST "http://localhost:8000/empresas/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Empresa Teste",
    "cnpj": "12.345.678/0001-90",
    "email": "contato@empresateste.com"
  }'
```

---

## 🛠️ Principais Endpoints da API

### 🏢 **Gestão de Empresas**
```bash
# Listar empresas
GET /empresas/

# Criar empresa
POST /empresas/
{
  "nome": "Nome da Empresa",
  "cnpj": "12.345.678/0001-90",
  "email": "email@empresa.com",
  "telefone": "(11) 99999-9999"
}

# Buscar empresa por ID
GET /empresas/{empresa_id}

# Atualizar empresa
PUT /empresas/{empresa_id}

# Deletar empresa
DELETE /empresas/{empresa_id}
```

### 👥 **Gestão de Usuários**
```bash
# Listar usuários
GET /usuarios/

# Criar usuário
POST /usuarios/
{
  "nome": "Nome do Usuário",
  "email": "usuario@empresa.com",
  "empresa_id": 1,
  "role": "admin"  # admin, user, readonly
}

# Buscar usuário por ID
GET /usuarios/{usuario_id}

# Atualizar usuário
PUT /usuarios/{usuario_id}

# Deletar usuário
DELETE /usuarios/{usuario_id}
```

### 🔑 **Gestão de Aplicações**
```bash
# Listar aplicações
GET /aplicacoes/

# Criar aplicação
POST /aplicacoes/
{
  "descricao": "Minha Aplicação",
  "empresa_id": 1,
  "redirect_uris": ["http://localhost:8080/callback"]
}

# Buscar aplicação por ID
GET /aplicacoes/{app_id}

# Regenerar credenciais
POST /aplicacoes/{app_id}/regenerate
```

### 🔐 **Autenticação**
```bash
# Obter token JWT
POST /auth/token
{
  "app_key": "sua_app_key",
  "app_secret": "seu_app_secret"
}

# Verificar token
GET /auth/verify
Authorization: Bearer SEU_JWT_TOKEN

# Refresh token
POST /auth/refresh
{
  "refresh_token": "seu_refresh_token"
}
```

---

## 📊 Fluxo de Uso Completo

### 1. **Configurar Nova Empresa**
```bash
# 1. Criar empresa
curl -X POST "http://localhost:8000/empresas/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Minha Empresa LTDA",
    "cnpj": "12.345.678/0001-90",
    "email": "admin@minhaempresa.com",
    "telefone": "(11) 99999-9999"
  }'

# Resposta: {"id": 1, "nome": "Minha Empresa LTDA", ...}
```

### 2. **Criar Usuário Administrador**
```bash
# 2. Criar usuário admin
curl -X POST "http://localhost:8000/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Administrador",
    "email": "admin@minhaempresa.com",
    "empresa_id": 1,
    "role": "admin"
  }'

# Resposta: {"id": 1, "nome": "Administrador", ...}
```

### 3. **Criar Aplicação OAuth**
```bash
# 3. Criar aplicação para acesso
curl -X POST "http://localhost:8000/aplicacoes/" \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Sistema Principal",
    "empresa_id": 1,
    "redirect_uris": ["http://localhost:8080/callback"]
  }'

# Resposta: {"id": 1, "app_key": "abc123", "app_secret": "xyz789", ...}
```

### 4. **Obter Token de Acesso**
```bash
# 4. Autenticar e obter JWT
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "app_key": "abc123",
    "app_secret": "xyz789"
  }'

# Resposta: {"access_token": "eyJ...", "token_type": "bearer", ...}
```

### 5. **Usar Token nas Requisições**
```bash
# 5. Usar token nas chamadas autenticadas
curl -X GET "http://localhost:8000/empresas/" \
  -H "Authorization: Bearer eyJ..."
```

---

## ⚙️ Configurações Avançadas

### 🔧 **Variáveis de Ambiente**
```bash
# Arquivo .env (opcional)
DATABASE_URL=sqlite:///./data/omie_tenant.db
SECRET_KEY=sua_chave_secreta_jwt
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:8080", "https://app.minhaempresa.com"]
DEBUG=false
```

### 📊 **Configuração do Banco**
```python
# src/database.py - Configurações do SQLite
DATABASE_URL = "sqlite:///./data/omie_tenant.db"

# Para PostgreSQL (produção):
# DATABASE_URL = "postgresql://user:pass@localhost/uptax_tenant"
```

### 🔐 **Configuração de Segurança**
```python
# src/auth.py - Configurações JWT
JWT_SECRET_KEY = "sua_chave_super_secreta"  # Trocar em produção
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 1440  # 24 horas
```

---

## 🚨 Resolução de Problemas

### ❌ **Erro: "Port already in use"**
```bash
# Verificar processo na porta 8000
lsof -i :8000

# Matar processo
kill -9 PID_DO_PROCESSO

# Usar porta diferente
uvicorn src.main:app --port 8001
```

### ❌ **Erro: "Database locked"**
```bash
# Verificar se arquivo existe
ls -la data/omie_tenant.db

# Remover lock se existir
rm -f data/omie_tenant.db-wal data/omie_tenant.db-shm

# Recriar banco se necessário
rm data/omie_tenant.db
python -m src.main  # Recria automaticamente
```

### ❌ **Erro: "JWT token invalid"**
```bash
# Verificar configuração do secret
grep SECRET_KEY .env

# Gerar novo token
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"app_key": "sua_key", "app_secret": "seu_secret"}'
```

### ❌ **Erro: "CORS policy"**
```bash
# Adicionar domínio permitido no .env
echo "CORS_ORIGINS=[\"http://localhost:3000\", \"https://seudominio.com\"]" >> .env

# Reiniciar aplicação
```

---

## 📊 Monitoramento e Logs

### 🔍 **Verificar Status**
```bash
# Health check
curl http://localhost:8000/health

# Estatísticas
curl http://localhost:8000/stats

# Lista de endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys'
```

### 📈 **Auditoria**
```bash
# Ver logs de auditoria
tail -f logs/audit.log

# Logs da aplicação
tail -f logs/app.log

# Filtrar logs por empresa
grep "empresa_id:1" logs/audit.log
```

---

## 🔗 Integração com Outras Aplicações

### 🎯 **Omie MCP Core**
```python
# Usar token do Tenant Manager no MCP Core
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "X-Empresa-ID": "1"
}
```

### 📊 **Dashboard Web**
```javascript
// JavaScript no dashboard
const token = localStorage.getItem('jwt_token');
fetch('/api/empresas', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

### 🔗 **N8N Workflows**
```json
{
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://localhost:8000/empresas/",
    "authentication": "genericCredential",
    "genericAuthType": "httpHeaderAuth",
    "httpHeaderAuth": {
      "name": "Authorization",
      "value": "Bearer {{$parameter['jwt_token']}}"
    }
  }
}
```

---

## 🎯 Economia de Créditos

### ⚡ **Otimizações do Sistema**
1. **Cache de Tokens**: JWT válidos por 24h
2. **Consultas Otimizadas**: Queries SQL eficientes
3. **Lazy Loading**: Carrega dados conforme necessário
4. **Paginação**: Limita resultados das consultas

### 📊 **Monitorar Performance**
```bash
# Verificar uso de recursos
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'RAM: {psutil.virtual_memory().percent}%')
"

# Tamanho do banco
ls -lh data/omie_tenant.db
```

---

## 🚀 Próximos Passos

### 1. **Configurar Frontend**
```bash
# Integrar com dashboard web
cd ../omie-dashboard-v2
# Configurar autenticação JWT
```

### 2. **Configurar Multi-tenant no MCP**
```bash
# Editar configuração do Omie MCP
cd ../ACTIVE_SERVICES
# Adicionar suporte a empresa_id
```

### 3. **Backup Automático**
```bash
# Configurar backup diário
crontab -e
# Adicionar: 0 2 * * * cp /path/to/data/omie_tenant.db /backup/$(date +\%Y\%m\%d).db
```

---

## 📚 Documentação Adicional

- **API Reference**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Architecture Guide**: [/docs/ARCHITECTURE.md](../ARCHITECTURE.md)
- **Security Guide**: [/docs/SECURITY.md](../SECURITY.md)
- **Database Schema**: [/docs/DATABASE.md](../DATABASE.md)

---

**🏢 Pronto! Tenant Manager rodando com controle multi-empresa.**

📧 **Suporte**: Para dúvidas sobre autenticação e multi-tenancy, consulte a documentação ou abra issue no GitHub.