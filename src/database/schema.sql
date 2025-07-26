-- =============================================================================
-- OMIE MCP DATABASE SCHEMA
-- Sistema de Controle de Processos e Métricas
-- =============================================================================

-- Criar database (executar como superuser)
-- CREATE DATABASE omie_mcp OWNER omie_user;

-- Conectar ao database omie_mcp
\c omie_mcp;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE execution_status AS ENUM (
    'running', 
    'completed', 
    'failed', 
    'timeout', 
    'cancelled'
);

CREATE TYPE alert_severity AS ENUM (
    'info', 
    'warning', 
    'critical'
);

CREATE TYPE tool_category AS ENUM (
    'sistema', 
    'organizacional', 
    'financeiro', 
    'comercial', 
    'produtos', 
    'relatorios',
    'administrativo'
);

CREATE TYPE tool_complexity AS ENUM (
    'basica', 
    'intermediaria', 
    'avancada', 
    'especializada'
);

-- =============================================================================
-- TABELAS PRINCIPAIS
-- =============================================================================

-- 1. Execuções de Processos
CREATE TABLE process_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    process_type VARCHAR(100) NOT NULL,
    status execution_status NOT NULL DEFAULT 'running',
    
    -- Timestamps
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
    
    -- Context metadata
    user_agent TEXT,
    ip_address INET,
    fastmcp_session_id VARCHAR(100),
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Métricas da API Omie
CREATE TABLE omie_api_metrics (
    id BIGSERIAL PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'POST',
    
    -- Performance metrics
    response_time_ms INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    
    -- Size metrics
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- Rate limiting info
    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,
    
    -- Relationships
    process_execution_id UUID REFERENCES process_executions(id),
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Configurações do Sistema
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

-- 4. Alertas de Integração
CREATE TABLE integration_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL, -- 'api_timeout', 'rate_limit', 'error_rate_high', 'system_resource'
    severity alert_severity NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Context data
    context_data JSONB,
    process_execution_id UUID REFERENCES process_executions(id),
    endpoint VARCHAR(200),
    
    -- Resolution status
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Analytics de Uso de Tools
CREATE TABLE tool_usage_analytics (
    id BIGSERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    category tool_category NOT NULL,
    complexity tool_complexity NOT NULL,
    
    -- Usage metrics (agregados por período)
    usage_count INTEGER DEFAULT 1,
    total_execution_time_ms BIGINT DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Time aggregation keys
    date_key DATE NOT NULL,
    hour_key INTEGER NOT NULL CHECK (hour_key >= 0 AND hour_key <= 23),
    
    -- Derived metrics
    avg_response_time_ms INTEGER,
    success_rate DECIMAL(5,2),
    
    -- Constraint for uniqueness
    UNIQUE(tool_name, date_key, hour_key)
);

-- 6. Log de Auditoria
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    process_execution_id UUID REFERENCES process_executions(id)
);

-- 7. Cache de Dados Omie (para otimização)
CREATE TABLE omie_data_cache (
    id BIGSERIAL PRIMARY KEY,
    cache_key VARCHAR(200) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    parameters_hash VARCHAR(64) NOT NULL, -- MD5 dos parâmetros
    cached_data JSONB NOT NULL,
    
    -- TTL management
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Performance tracking
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(cache_key, parameters_hash)
);

-- =============================================================================
-- ÍNDICES PARA PERFORMANCE
-- =============================================================================

-- Índices principais para process_executions
CREATE INDEX idx_process_executions_status ON process_executions(status);
CREATE INDEX idx_process_executions_type_created ON process_executions(process_type, created_at DESC);
CREATE INDEX idx_process_executions_execution_id ON process_executions(execution_id);
CREATE INDEX idx_process_executions_created_at ON process_executions(created_at DESC);
CREATE INDEX idx_process_executions_active ON process_executions(status, started_at) WHERE status = 'running';

-- Índices para métricas de API
CREATE INDEX idx_omie_metrics_endpoint_timestamp ON omie_api_metrics(endpoint, timestamp DESC);
CREATE INDEX idx_omie_metrics_success_timestamp ON omie_api_metrics(success, timestamp DESC);
CREATE INDEX idx_omie_metrics_process_id ON omie_api_metrics(process_execution_id);

-- Índices para alertas
CREATE INDEX idx_alerts_severity_created ON integration_alerts(severity, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON integration_alerts(is_resolved, created_at DESC) WHERE NOT is_resolved;
CREATE INDEX idx_alerts_type_created ON integration_alerts(alert_type, created_at DESC);

-- Índices para analytics
CREATE INDEX idx_tool_analytics_date_tool ON tool_usage_analytics(date_key DESC, tool_name);
CREATE INDEX idx_tool_analytics_category_date ON tool_usage_analytics(category, date_key DESC);

-- Índices para cache
CREATE INDEX idx_cache_expires ON omie_data_cache(expires_at);
CREATE INDEX idx_cache_key_hash ON omie_data_cache(cache_key, parameters_hash);
CREATE INDEX idx_cache_endpoint_created ON omie_data_cache(endpoint, created_at DESC);

-- =============================================================================
-- FUNÇÕES E TRIGGERS
-- =============================================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para process_executions
CREATE TRIGGER update_process_executions_updated_at 
    BEFORE UPDATE ON process_executions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger para system_configurations
CREATE TRIGGER update_system_configurations_updated_at 
    BEFORE UPDATE ON system_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para limpeza automática de cache expirado
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM omie_data_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Função para calcular métricas agregadas de tools
CREATE OR REPLACE FUNCTION update_tool_analytics(
    p_tool_name VARCHAR(100),
    p_category tool_category,
    p_complexity tool_complexity,
    p_execution_time_ms INTEGER,
    p_success BOOLEAN
)
RETURNS VOID AS $$
DECLARE
    current_date DATE := CURRENT_DATE;
    current_hour INTEGER := EXTRACT(HOUR FROM NOW());
BEGIN
    INSERT INTO tool_usage_analytics (
        tool_name, category, complexity, date_key, hour_key,
        usage_count, total_execution_time_ms, success_count, error_count
    )
    VALUES (
        p_tool_name, p_category, p_complexity, current_date, current_hour,
        1, p_execution_time_ms, 
        CASE WHEN p_success THEN 1 ELSE 0 END,
        CASE WHEN p_success THEN 0 ELSE 1 END
    )
    ON CONFLICT (tool_name, date_key, hour_key)
    DO UPDATE SET
        usage_count = tool_usage_analytics.usage_count + 1,
        total_execution_time_ms = tool_usage_analytics.total_execution_time_ms + p_execution_time_ms,
        success_count = tool_usage_analytics.success_count + CASE WHEN p_success THEN 1 ELSE 0 END,
        error_count = tool_usage_analytics.error_count + CASE WHEN p_success THEN 0 ELSE 1 END,
        avg_response_time_ms = (tool_usage_analytics.total_execution_time_ms + p_execution_time_ms) / (tool_usage_analytics.usage_count + 1),
        success_rate = ROUND(
            (tool_usage_analytics.success_count + CASE WHEN p_success THEN 1 ELSE 0 END)::DECIMAL / 
            (tool_usage_analytics.usage_count + 1) * 100, 2
        );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- VIEWS PARA RELATÓRIOS
-- =============================================================================

-- View para dashboard de processos ativos
CREATE VIEW v_active_processes AS
SELECT 
    execution_id,
    process_type,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - started_at))::INTEGER AS running_seconds,
    input_parameters
FROM process_executions 
WHERE status = 'running'
ORDER BY started_at DESC;

-- View para métricas de performance (última hora)
CREATE VIEW v_performance_metrics_1h AS
SELECT 
    endpoint,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE success) as successful_requests,
    ROUND(AVG(response_time_ms), 2) as avg_response_time_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms), 2) as p95_response_time_ms,
    ROUND(COUNT(*) FILTER (WHERE success)::DECIMAL / COUNT(*) * 100, 2) as success_rate
FROM omie_api_metrics 
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY endpoint
ORDER BY total_requests DESC;

-- View para alertas críticos não resolvidos
CREATE VIEW v_critical_alerts AS
SELECT 
    id,
    alert_type,
    title,
    message,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))::INTEGER AS age_seconds
FROM integration_alerts 
WHERE severity = 'critical' AND NOT is_resolved
ORDER BY created_at DESC;

-- View para top tools por uso (último dia)
CREATE VIEW v_top_tools_24h AS
SELECT 
    tool_name,
    category,
    complexity,
    SUM(usage_count) as total_usage,
    ROUND(AVG(avg_response_time_ms), 2) as avg_response_time,
    ROUND(AVG(success_rate), 2) as avg_success_rate
FROM tool_usage_analytics 
WHERE date_key > CURRENT_DATE - INTERVAL '1 day'
GROUP BY tool_name, category, complexity
ORDER BY total_usage DESC
LIMIT 20;

-- =============================================================================
-- DADOS INICIAIS
-- =============================================================================

-- Configurações padrão do sistema
INSERT INTO system_configurations (config_key, config_value, config_type, description) VALUES
('omie_api_base_url', '"https://app.omie.com.br/api/v1/"', 'endpoint', 'URL base da API Omie'),
('omie_request_timeout', '30', 'threshold', 'Timeout para requisições Omie em segundos'),
('max_retry_attempts', '3', 'threshold', 'Máximo de tentativas para requisições'),
('cache_ttl_minutes', '15', 'threshold', 'TTL padrão do cache em minutos'),
('rate_limit_per_minute', '100', 'threshold', 'Limite de requisições por minuto'),
('monitoring_enabled', 'true', 'feature_flag', 'Ativar monitoramento de métricas'),
('alert_email_enabled', 'false', 'feature_flag', 'Ativar notificações por email'),
('debug_mode', 'false', 'feature_flag', 'Modo debug para desenvolvimento');

-- =============================================================================
-- POLÍTICAS DE LIMPEZA E MANUTENÇÃO
-- =============================================================================

-- Função para limpeza de dados antigos (executar via cron)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS TABLE (
    table_name TEXT,
    deleted_count BIGINT
) AS $$
BEGIN
    -- Limpar process_executions > 90 dias
    DELETE FROM process_executions WHERE created_at < NOW() - INTERVAL '90 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'process_executions';
    RETURN NEXT;
    
    -- Limpar omie_api_metrics > 30 dias
    DELETE FROM omie_api_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'omie_api_metrics';
    RETURN NEXT;
    
    -- Limpar integration_alerts resolvidos > 7 dias
    DELETE FROM integration_alerts 
    WHERE is_resolved = true AND resolved_at < NOW() - INTERVAL '7 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'integration_alerts';
    RETURN NEXT;
    
    -- Limpar tool_usage_analytics > 1 ano
    DELETE FROM tool_usage_analytics WHERE date_key < CURRENT_DATE - INTERVAL '1 year';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'tool_usage_analytics';
    RETURN NEXT;
    
    -- Limpar cache expirado
    PERFORM cleanup_expired_cache();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'omie_data_cache';
    RETURN NEXT;
    
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GRANTS E PERMISSÕES
-- =============================================================================

-- Usuário da aplicação (omie_user)
GRANT USAGE ON SCHEMA public TO omie_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO omie_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO omie_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO omie_user;

-- Usuário read-only para relatórios (omie_readonly)
CREATE USER omie_readonly WITH PASSWORD 'readonly_password';
GRANT USAGE ON SCHEMA public TO omie_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO omie_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO omie_readonly;

-- =============================================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =============================================================================

COMMENT ON TABLE process_executions IS 'Log completo de execuções de processos MCP com rastreabilidade total';
COMMENT ON TABLE omie_api_metrics IS 'Métricas de performance da API Omie para monitoramento';
COMMENT ON TABLE system_configurations IS 'Configurações dinâmicas do sistema';
COMMENT ON TABLE integration_alerts IS 'Sistema de alertas para falhas e problemas';
COMMENT ON TABLE tool_usage_analytics IS 'Analytics agregadas de uso das tools';
COMMENT ON TABLE omie_data_cache IS 'Cache de dados da API Omie para otimização';

COMMENT ON COLUMN process_executions.execution_id IS 'ID único legível para rastreamento (process_type_timestamp_uuid)';
COMMENT ON COLUMN process_executions.duration_ms IS 'Duração total da execução em milissegundos';
COMMENT ON COLUMN omie_api_metrics.response_time_ms IS 'Tempo de resposta da API Omie em milissegundos';
COMMENT ON COLUMN tool_usage_analytics.success_rate IS 'Taxa de sucesso calculada automaticamente (0-100)';

-- =============================================================================
-- SCRIPT COMPLETO
-- =============================================================================

-- Para executar este script:
-- 1. Conectar como superuser: psql -U postgres
-- 2. Criar usuário: CREATE USER omie_user WITH PASSWORD 'omie_password';
-- 3. Criar database: CREATE DATABASE omie_mcp OWNER omie_user;
-- 4. Executar este script: \i schema.sql

\echo 'Schema Omie MCP criado com sucesso!'
\echo 'Tabelas criadas: process_executions, omie_api_metrics, system_configurations, integration_alerts, tool_usage_analytics, audit_log, omie_data_cache'
\echo 'Views criadas: v_active_processes, v_performance_metrics_1h, v_critical_alerts, v_top_tools_24h'
\echo 'Funções criadas: update_tool_analytics, cleanup_old_data, cleanup_expired_cache'