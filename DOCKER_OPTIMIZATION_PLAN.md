# 🚀 PLANO DE OTIMIZAÇÃO DOCKER - UPTAX AI PLATFORM

## 🎯 ESTRATÉGIA: CLEAN SLATE + SINGLE COMPOSE

### **OPÇÃO A: LIMPEZA TOTAL (RECOMENDADO)**

#### **1. CLEAN SLATE APPROACH**
```bash
# Parar TUDO exceto business-integrations-graph (manter Neo4j)
docker stop $(docker ps -aq --filter "name=uptax*")
docker rm $(docker ps -aq --filter "name=uptax*")

# Remover imagens órfãs (manter apenas essenciais)
docker image prune -a -f

# Remover volumes não utilizados
docker volume prune -f

# Manter apenas: Neo4j + imagens base essenciais
```

#### **2. SINGLE COMPOSE STRATEGY**
Criar **UM ÚNICO** docker-compose.yml otimizado:

```yaml
# docker-compose.uptax-optimized.yml
version: '3.8'

# UPTAX AI PLATFORM - CONFIGURAÇÃO OTIMIZADA
# 5 containers essenciais: N8N, PostgreSQL, Redis, Neo4j, Monitoring

services:
  # =============================================================================
  # CORE DATABASE LAYER
  # =============================================================================
  
  postgres:
    image: postgres:15-alpine
    container_name: uptax-postgres
    environment:
      - POSTGRES_DB=uptax_db
      - POSTGRES_USER=uptax
      - POSTGRES_PASSWORD=uptax_2025
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U uptax -d uptax_db"]
      interval: 10s
      timeout: 5s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: uptax-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # =============================================================================
  # AUTOMATION PLATFORM
  # =============================================================================
  
  n8n:
    image: n8nio/n8n:latest
    container_name: uptax-n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=uptax
      - N8N_BASIC_AUTH_PASSWORD=uptax2025
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/Sao_Paulo
      # PostgreSQL
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=uptax
      - DB_POSTGRESDB_PASSWORD=uptax_2025
      # Redis Queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
      - QUEUE_BULL_REDIS_DB=0
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n_workflows:/home/node/.n8n/workflows:ro
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # =============================================================================
  # INTELLIGENCE LAYER (Future Evolution)
  # =============================================================================
  
  neo4j:
    image: neo4j:5.15-community
    container_name: uptax-neo4j
    environment:
      - NEO4J_AUTH=neo4j/uptax_neo4j_2025
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_memory_heap_initial__size=512M
      - NEO4J_dbms_memory_heap_max__size=1G
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "uptax_neo4j_2025", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # =============================================================================
  # MONITORING LAYER
  # =============================================================================
  
  monitoring:
    image: prom/prometheus:latest
    container_name: uptax-monitoring
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  n8n_data:
  neo4j_data:
  neo4j_logs:
  prometheus_data:

networks:
  default:
    name: uptax-network
    driver: bridge
```

#### **3. DEPLOYMENT SEQUENCIAL**
```bash
# Fase 1: Databases primeiro
docker-compose -f docker-compose.uptax-optimized.yml up -d postgres redis

# Aguardar health checks (30s)
sleep 30

# Fase 2: N8N com dependências prontas
docker-compose -f docker-compose.uptax-optimized.yml up -d n8n

# Fase 3: Serviços auxiliares
docker-compose -f docker-compose.uptax-optimized.yml up -d neo4j monitoring
```

### **OPÇÃO B: REORGANIZAÇÃO INCREMENTAL**

#### **1. CONSOLIDAÇÃO GRADUAL**
```bash
# Manter containers funcionais
# Remover apenas conflitos
docker-compose -f docker-compose.essential.yml down
docker-compose -f docker-compose.development.yml down

# Consolidar em nova configuração
cp docker-compose.essential.yml docker-compose.uptax-unified.yml
# Editar e otimizar
```

## 📊 COMPARAÇÃO DE OPÇÕES

### **OPÇÃO A: CLEAN SLATE**
**Vantagens:**
- ✅ Ambiente limpo e otimizado
- ✅ Uma única configuração
- ✅ Menos conflitos
- ✅ Mais controle

**Desvantagens:**
- ⚠️ Perda de configurações atuais
- ⚠️ Requer reconfiguração
- ⚠️ Tempo: 2-3 horas

**Timeline:** 1 dia

### **OPÇÃO B: INCREMENTAL**
**Vantagens:**
- ✅ Preserva configurações
- ✅ Menos disruptivo
- ✅ Aproveitamento do trabalho

**Desvantagens:**
- ❌ Mantém complexidade
- ❌ Possíveis conflitos residuais
- ❌ 11 compose files ainda

**Timeline:** 2-3 dias

## 🎯 RECOMENDAÇÃO FINAL

### **ESCOLHA: OPÇÃO A - CLEAN SLATE**

**Justificativa:**
1. **Eficiência**: Resolver de uma vez
2. **Clareza**: Uma configuração, uma verdade
3. **Manutenibilidade**: Mais fácil evoluir
4. **Performance**: Otimizado desde o início

### **PLANO DE EXECUÇÃO (4 HORAS)**

**Hora 1:** Backup e limpeza
- Backup configurações importantes
- Clean slate Docker

**Hora 2:** Deploy otimizado
- Subir nova configuração
- Testar conectividade

**Hora 3:** Integração MCP
- Conectar Omie/Nibo MCP
- Configurar N8N workflows

**Hora 4:** Validação completa
- Testes end-to-end
- Documentação

## 📋 DELIVERABLES

1. **docker-compose.uptax-optimized.yml** - Configuração única
2. **start-uptax-platform.sh** - Script de inicialização
3. **UPTAX_DOCKER_GUIDE.md** - Documentação operacional
4. **health-check.sh** - Monitoramento automático

**Resultado:** Plataforma estável, documentada, com uma única fonte de configuração.