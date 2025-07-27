# ✅ N8N Docker Setup - UPTAX Platform Completo

## 🎯 **Otimização de Tokens Aplicada**

**Stack N8N Docker criada com máxima eficiência:**

### 📦 **Componentes Implementados**
- **N8N Container** + PostgreSQL + Redis + Nginx Proxy
- **Volumes persistentes** para dados
- **API Keys configuradas** (uptax_admin/UptaxN8N2024!)
- **Analytics integrado** com schema UPTAX
- **Context7 ready** para MCP integration

### 🚀 **Comandos Rápidos**

```bash
# Iniciar stack
./deploy-n8n-docker.sh

# Status containers  
docker ps | grep uptax

# Logs N8N
docker logs n8n-uptax-platform -f

# Parar tudo
docker-compose -f docker-compose.n8n-optimized.yml down
```

### 🌐 **Acesso**
- **N8N Interface**: http://localhost:5678
- **Proxy**: http://localhost:8678  
- **User**: `uptax_admin`
- **Password**: `UptaxN8N2024!`

### 🔧 **MCP Integration Ready**
- Context7 endpoint configurado
- Analytics schema criado
- Webhooks UPTAX habilitados
- API sem limitações 401

### 📊 **Monitoramento**
- Health checks automáticos
- Métricas em `/metrics`
- Logs estruturados
- Analytics PostgreSQL

**✅ Sistema pronto para importação automática dos 8 workflows UPTAX!**