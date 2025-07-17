# 🚀 Quick Start - Universal Credentials Manager

## ✅ **Status: PRONTO PARA USO**

O Universal Credentials Manager está **100% funcional** e testado!

## 🎯 **O que foi criado:**

### 🔒 **Sistema de Credenciais Seguro**
- ✅ Criptografia AES-256 para dados sensíveis
- ✅ Suporte multi-empresa e multi-projeto  
- ✅ Storage híbrido (Local + S3)
- ✅ Logs de auditoria completos

### 🌐 **API REST Completa**
- ✅ FastAPI com documentação automática
- ✅ Auth0 integrado (opcional)
- ✅ CRUD completo de credenciais
- ✅ Endpoints de auditoria

### ☁️ **Cloud Storage Ready**
- ✅ AWS S3 com criptografia server-side
- ✅ Fallback para storage local
- ✅ Sincronização automática

## 🚀 **Como usar AGORA:**

### **1. Teste Local (5 minutos)**

```bash
# 1. Entrar no diretório
cd universal-credentials-manager

# 2. Instalar dependências (se não fez)
pip install -r requirements.txt

# 3. Configurar ambiente
export PYTHONPATH=$(pwd):$PYTHONPATH

# 4. Testar sistema completo
python scripts/test_integration.py

# 5. Iniciar API
python src/api/server.py
```

**✅ API funcionando em:** http://localhost:8100  
**📚 Documentação:** http://localhost:8100/docs

### **2. Configurar AWS S3 (Opcional)**

```bash
# Configurar credenciais AWS
aws configure

# Definir bucket no .env
echo "AWS_S3_BUCKET=meu-bucket-credenciais" >> .env
echo "STORAGE_TYPE=hybrid" >> .env

# Testar S3
python -c "
import asyncio
from src.storage.cloud_storage import create_storage
async def test():
    storage = create_storage('s3', bucket_name='meu-bucket')
    success = await storage.save_project_data('test', {'test': True})
    print('S3 funcionando!' if success else 'Erro no S3')
asyncio.run(test())
"
```

### **3. Usar com Docker (Produção)**

```bash
# Construir e executar
docker-compose up -d

# Verificar serviços
docker-compose ps

# Logs
docker-compose logs -f ucm-api
```

## 🔧 **Integração com Omie MCP**

### **No omie-mcp, substituir:**

```python
# ANTES (credentials.json direto)
with open('credentials.json') as f:
    credentials = json.load(f)

# DEPOIS (Universal Credentials Manager)
import httpx

async def get_credentials(company_key="empresa1"):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8100/api/v1/projects/omie-mcp/credentials/{company_key}"
        )
        return response.json()

# Usar
credentials = await get_credentials("empresa1")
app_key = credentials["app_key"]
app_secret = credentials["app_secret"]
```

## 📊 **API Endpoints Disponíveis**

```http
# Projetos
GET    /api/v1/projects                    # Listar projetos
GET    /api/v1/projects/{project}/companies # Listar empresas

# Credenciais
GET    /api/v1/projects/{project}/credentials/{company} # Obter credenciais
POST   /api/v1/projects/{project}/credentials # Adicionar empresa
PUT    /api/v1/projects/{project}/credentials/{company} # Atualizar
DELETE /api/v1/projects/{project}/credentials/{company} # Remover

# Auditoria
GET    /api/v1/audit/logs                  # Logs de acesso
```

## 🔍 **Testar API Manualmente**

```bash
# 1. Listar projetos
curl http://localhost:8100/api/v1/projects

# 2. Listar empresas do omie-mcp
curl http://localhost:8100/api/v1/projects/omie-mcp/companies

# 3. Obter credenciais (modo dev - sem auth)
curl http://localhost:8100/api/v1/projects/omie-mcp/credentials/empresa_exemplo

# 4. Ver logs de auditoria
curl http://localhost:8100/api/v1/audit/logs
```

## 🎨 **Frontend (Opcional)**

```bash
# Instalar Next.js frontend
cd frontend
npm install

# Configurar .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8100" > .env.local

# Executar frontend
npm run dev
```

**Frontend em:** http://localhost:3000

## 🌍 **Deploy na AWS (Produção)**

### **Configuração Rápida:**

```bash
# 1. Criar bucket S3
aws s3 mb s3://ucm-prod-credentials

# 2. Configurar IAM permissions
aws iam create-policy --policy-name UCMPolicy --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::ucm-prod-credentials/*"
    }
  ]
}'

# 3. Deploy com ECS Fargate
# (usar docker-compose.prod.yml)
```

## 🔐 **Configuração Auth0 (Produção)**

```bash
# 1. Criar conta Auth0 gratuita
# https://auth0.com

# 2. Criar Application (SPA)
# 3. Criar API (identifier: https://ucm-api)

# 4. Configurar .env
AUTH0_DOMAIN=myapp.auth0.com
AUTH0_CLIENT_ID=abc123...
AUTH0_API_AUDIENCE=https://ucm-api
```

## 📋 **Arquivos de Configuração Criados**

```
universal-credentials-manager/
├── config/projects/
│   └── omie-mcp.json          # ✅ Projeto exemplo criado
├── .env                       # ✅ Configuração ambiente
├── logs/                      # ✅ Logs de sistema
└── backups/                   # ✅ Backups automáticos
```

## 🎯 **Próximos Passos**

### **Para Desenvolvimento:**
1. ✅ **Sistema funcionando** - pode usar agora!
2. 🔧 **Integrar com omie-mcp** - trocar credentials.json pela API
3. 🎨 **Customizar frontend** - adicionar sua marca
4. 📊 **Monitorar logs** - acompanhar uso

### **Para Produção:**
1. ☁️ **Deploy na AWS** - ECS + S3 + RDS
2. 🔐 **Configurar Auth0** - autenticação real
3. 🏢 **Multi-tenancy** - separar por cliente
4. 📈 **Monitoramento** - Grafana + Prometheus

## 🏆 **Benefícios Imediatos**

- ✅ **Segurança**: Credenciais criptografadas AES-256
- ✅ **Escalabilidade**: Suporta múltiplos projetos/empresas  
- ✅ **Auditoria**: Logs completos de acesso
- ✅ **Flexibilidade**: Local ou cloud storage
- ✅ **API First**: Reutilizável por qualquer sistema
- ✅ **Docker Ready**: Deploy simples em produção

## 🆘 **Suporte**

```bash
# Verificar saúde do sistema
curl http://localhost:8100/

# Executar testes
python scripts/test_integration.py

# Ver logs detalhados
tail -f logs/ucm.log
```

---

## 🎉 **PARABÉNS!**

Você agora tem um **sistema empresarial completo** de gerenciamento de credenciais que pode:

- 🔒 **Substituir** arquivos credentials.json inseguros
- 🌐 **Centralizar** credenciais de múltiplos projetos
- 📊 **Auditar** todos os acessos
- ☁️ **Escalar** para a nuvem quando necessário
- 🔧 **Integrar** com qualquer sistema via API REST

**Ready to go! 🚀**