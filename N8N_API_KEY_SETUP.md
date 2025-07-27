# 🔑 Como Criar API Key no N8N Docker

## ✅ **N8N Local Removido**
A instância N8N local foi parada. Agora usamos apenas o Docker.

## 🚀 **Passos para Criar API Key**

### 1. **Acessar N8N Docker**
🌐 **URL**: http://localhost:5678

### 2. **Login Credentials**
- **Username**: `uptax_admin`
- **Password**: `UptaxN8N2024!`

### 3. **Criar API Key**
Após fazer login, siga estes passos:

1. **Clique no menu do usuário** (canto superior direito)
2. **Vá em "Settings"** 
3. **Selecione "API Keys"** no menu lateral
4. **Clique em "Create API Key"**
5. **Nome**: `UPTAX-Platform-Key`
6. **Copie a API Key** gerada

### 4. **Configurar no Sistema**
Após gerar, me passe a API key para eu atualizar:
- MCP Tools N8N
- Configurações de integração
- Testes automatizados

## 🔧 **Links Diretos**

**Se N8N Docker estiver rodando:**
- **Interface Principal**: http://localhost:5678
- **API Settings**: http://localhost:5678/settings/api
- **Proxy Alternative**: http://localhost:8678

## 🆘 **Se N8N não estiver acessível**

Execute:
```bash
# Verificar containers
docker ps | grep n8n

# Iniciar se necessário  
./deploy-n8n-docker.sh

# Logs para debug
docker logs n8n-uptax-platform
```

**Depois que você criar a API key, me passe ela para eu integrar no sistema!** 🚀