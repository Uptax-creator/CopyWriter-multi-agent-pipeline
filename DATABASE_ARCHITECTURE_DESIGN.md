# 🗄️ ARQUITETURA DE BANCO DE DADOS - SISTEMA DE CONTROLE DE PROCESSOS OMIE

## 📋 Análise de Requisitos

### Necessidades Identificadas
1. **Controle de ID de processos de integração** - rastreabilidade completa
2. **Histórico de operações** - auditoria e logs detalhados  
3. **Métricas de performance** - tempo de resposta, taxa de sucesso
4. **Gestão de configurações** - credenciais, endpoints, parâmetros
5. **Sistema de alertas** - falhas, timeouts, limites excedidos
6. **Dashboard operacional** - visão em tempo real do sistema

## 🔍 Comparação de Soluções de Banco de Dados

### 1. RELACIONAL (PostgreSQL)
**✅ Vantagens:**
- ACID compliance garantido
- Relacionamentos complexos bem estruturados
- Consultas SQL maduras e otimizadas
- Suporte nativo a JSON (JSONB)
- Backup e recovery robustos
- Ampla expertise disponível

**❌ Desvantagens:**
- Esquema rígido (migrações necessárias)
- Escalabilidade horizontal limitada
- Performance pode degradar com volume alto

**💡 Adequação: 9/10** - Ideal para sistema de auditoria e controle

### 2. NÃO-RELACIONAL (MongoDB)
**✅ Vantagens:**
- Esquema flexível (evolução fácil)
- Performance excelente para leitura
- Escalabilidade horizontal nativa
- Armazenamento natural de documentos JSON
- Agregações poderosas

**❌ Desvantagens:**
- Consistência eventual (não ACID total)
- Relacionamentos complexos mais difíceis
- Maior consumo de espaço
- Curva de aprendizado para queries complexas

**💡 Adequação: 7/10** - Bom para logs e métricas volumosas

### 3. GRAPH (Neo4j)
**✅ Vantagens:**
- Relacionamentos como entidades de primeira classe
- Queries de traversal muito eficientes
- Visualização natural de dependências
- Ótimo para análises de conectividade

**❌ Desvantagens:**
- Curva de aprendizado alta (Cypher)
- Menos adequado para dados tabulares simples
- Overhead para operações simples
- Menos ferramentas de BI disponíveis

**💡 Adequação: 5/10** - Overkill para nosso caso de uso

## 🏆 SOLUÇÃO RECOMENDADA: HÍBRIDA PostgreSQL + Redis

### Arquitetura Principal: PostgreSQL
**Responsabilidades:**
- Controle de processos e IDs
- Histórico de operações (auditoria)
- Configurações do sistema
- Métricas consolidadas
- Relacionamentos entre entidades

### Cache/Performance: Redis  
**Responsabilidades:**
- Cache de respostas da API Omie
- Sessões ativas de processos
- Métricas em tempo real
- Rate limiting
- Fila de jobs assíncronos

## 📊 SCHEMA DO BANCO DE DADOS

### Tabelas Principais

#### 1. process_executions
```sql
CREATE TABLE process_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_type VARCHAR(100) NOT NULL, -- 'consultar_clientes', 'criar_conta_pagar', etc
    execution_id VARCHAR(100) UNIQUE NOT NULL, -- ID único por execução
    status execution_status NOT NULL DEFAULT 'running', -- running, completed, failed, timeout
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Request data
    input_parameters JSONB,
    omie_endpoint VARCHAR(200),
    request_payload JSONB,
    
    -- Response data  
    response_status_code INTEGER,
    response_data JSONB,
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Metadata
    user_agent TEXT,
    ip_address INET,
    fastmcp_session_id VARCHAR(100),
    
    -- Indices
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE execution_status AS ENUM ('running', 'completed', 'failed', 'timeout', 'cancelled');
```

#### 2. omie_api_metrics
```sql
CREATE TABLE omie_api_metrics (
    id BIGSERIAL PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'POST',
    
    -- Performance metrics
    response_time_ms INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    
    -- Request size metrics
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- Rate limiting
    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,
    
    -- Relationships
    process_execution_id UUID REFERENCES process_executions(id),
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3. system_configurations
```sql
CREATE TABLE system_configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type VARCHAR(50) NOT NULL, -- 'credentials', 'endpoint', 'threshold', 'feature_flag'
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4. integration_alerts
```sql
CREATE TABLE integration_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL, -- 'api_timeout', 'rate_limit', 'error_rate_high', 'system_resource'
    severity alert_severity NOT NULL, -- info, warning, critical
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Context data
    context_data JSONB,
    process_execution_id UUID REFERENCES process_executions(id),
    endpoint VARCHAR(200),
    
    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical');
```

#### 5. tool_usage_analytics
```sql
CREATE TABLE tool_usage_analytics (
    id BIGSERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    category tool_category NOT NULL,
    complexity tool_complexity NOT NULL,
    
    -- Usage metrics
    usage_count INTEGER DEFAULT 1,
    total_execution_time_ms BIGINT DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Time periods
    date_key DATE NOT NULL, -- Para agregação diária
    hour_key INTEGER NOT NULL, -- 0-23 para agregação horária
    
    -- Derived metrics
    avg_response_time_ms INTEGER,
    success_rate DECIMAL(5,2),
    
    UNIQUE(tool_name, date_key, hour_key)
);

CREATE TYPE tool_category AS ENUM ('sistema', 'organizacional', 'financeiro', 'comercial', 'produtos', 'relatorios');
CREATE TYPE tool_complexity AS ENUM ('basica', 'intermediaria', 'avancada', 'especializada');
```

### Índices para Performance

```sql
-- Índices principais para process_executions
CREATE INDEX idx_process_executions_status ON process_executions(status);
CREATE INDEX idx_process_executions_type_created ON process_executions(process_type, created_at DESC);
CREATE INDEX idx_process_executions_execution_id ON process_executions(execution_id);
CREATE INDEX idx_process_executions_created_at ON process_executions(created_at DESC);

-- Índices para métricas
CREATE INDEX idx_omie_metrics_endpoint_timestamp ON omie_api_metrics(endpoint, timestamp DESC);
CREATE INDEX idx_omie_metrics_success_timestamp ON omie_api_metrics(success, timestamp DESC);

-- Índices para alertas
CREATE INDEX idx_alerts_severity_created ON integration_alerts(severity, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON integration_alerts(is_resolved, created_at DESC) WHERE NOT is_resolved;

-- Índices para analytics
CREATE INDEX idx_tool_analytics_date_tool ON tool_usage_analytics(date_key DESC, tool_name);
```

## 🔧 IMPLEMENTAÇÃO DO SISTEMA

### 1. Database Connection Manager
```python
# database_manager.py
import asyncpg
import aioredis
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

class DatabaseManager:
    def __init__(self):
        self.pg_pool = None
        self.redis = None
    
    async def initialize(self):
        """Inicializa conexões com PostgreSQL e Redis"""
        # PostgreSQL
        self.pg_pool = await asyncpg.create_pool(
            host='localhost',
            port=5432,
            database='omie_mcp',
            user='omie_user',
            password='omie_password',
            min_size=2,
            max_size=10
        )
        
        # Redis
        self.redis = await aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
```

### 2. Process Control System
```python
class ProcessController:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def start_process(self, process_type: str, input_params: Dict[str, Any]) -> str:
        """Inicia novo processo e retorna execution_id"""
        execution_id = f"{process_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        async with self.db.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO process_executions 
                (process_type, execution_id, input_parameters, status)
                VALUES ($1, $2, $3, 'running')
            """, process_type, execution_id, json.dumps(input_params))
        
        # Cache no Redis para acesso rápido
        await self.db.redis.setex(
            f"process:{execution_id}",
            3600,  # 1 hora TTL
            json.dumps({
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'process_type': process_type
            })
        )
        
        return execution_id
    
    async def complete_process(self, execution_id: str, success: bool, 
                             response_data: Optional[Dict] = None, 
                             error_message: Optional[str] = None):
        """Marca processo como completo"""
        status = 'completed' if success else 'failed'
        
        async with self.db.pg_pool.acquire() as conn:
            await conn.execute("""
                UPDATE process_executions 
                SET status = $1, completed_at = NOW(), 
                    response_data = $2, error_message = $3,
                    duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000
                WHERE execution_id = $4
            """, status, json.dumps(response_data) if response_data else None, 
                error_message, execution_id)
        
        # Atualizar cache
        await self.db.redis.setex(
            f"process:{execution_id}",
            86400,  # 24 horas para processos completos
            json.dumps({
                'status': status,
                'completed_at': datetime.now().isoformat(),
                'success': success
            })
        )
```

## 📈 MÉTRICAS E MONITORAMENTO

### Dashboard Queries
```sql
-- Processos ativos
SELECT COUNT(*) as active_processes 
FROM process_executions 
WHERE status = 'running' AND started_at > NOW() - INTERVAL '1 hour';

-- Taxa de sucesso por tool (últimas 24h)
SELECT 
    process_type,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE status = 'completed') as successful,
    ROUND(COUNT(*) FILTER (WHERE status = 'completed')::decimal / COUNT(*) * 100, 2) as success_rate
FROM process_executions 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY process_type
ORDER BY total_executions DESC;

-- Performance por endpoint
SELECT 
    endpoint,
    COUNT(*) as requests,
    AVG(response_time_ms) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time
FROM omie_api_metrics
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY endpoint
ORDER BY requests DESC;
```

## 🚀 PRÓXIMOS PASSOS

1. **Implementar DatabaseManager** - Conexões PostgreSQL + Redis
2. **Criar ProcessController** - Sistema de controle de ID
3. **Integrar com FastMCP tools** - Decoradores automáticos
4. **Dashboard em tempo real** - Interface web para monitoramento
5. **Sistema de alertas** - Notificações automáticas
6. **Backup e recovery** - Estratégia de dados críticos

## 🔒 SEGURANÇA E COMPLIANCE

- **Criptografia**: Credenciais sempre criptografadas
- **Auditoria**: Log completo de todas as operações
- **Retenção**: Dados históricos com política de limpeza
- **Access Control**: Controle granular de acesso
- **Backup**: Backup incremental diário + recovery point

Este design fornece uma base sólida para controle completo dos processos de integração com capacidade de monitoramento, análise e alertas em tempo real.