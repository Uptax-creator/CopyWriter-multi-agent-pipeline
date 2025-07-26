#!/usr/bin/env python3
"""
🗄️ DATABASE MANAGER - SISTEMA DE CONTROLE DE PROCESSOS OMIE
Gestão de PostgreSQL + Redis para rastreabilidade completa
"""

import asyncio
import asyncpg
import aioredis
import json
import uuid
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# =============================================================================
# ENUMS E DATACLASSES
# =============================================================================

class ExecutionStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed" 
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class ProcessExecution:
    execution_id: str
    process_type: str
    status: ExecutionStatus
    started_at: datetime
    input_parameters: Dict[str, Any]
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    omie_endpoint: Optional[str] = None

@dataclass
class APIMetric:
    endpoint: str
    response_time_ms: int
    status_code: int
    success: bool
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    process_execution_id: Optional[str] = None

@dataclass
class IntegrationAlert:
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str
    context_data: Optional[Dict[str, Any]] = None
    process_execution_id: Optional[str] = None

# =============================================================================
# DATABASE MANAGER
# =============================================================================

class DatabaseManager:
    """Gerenciador central do banco de dados PostgreSQL + Redis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
    def _default_config(self) -> Dict[str, Any]:
        """Configuração padrão do banco"""
        return {
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'database': 'omie_mcp',
                'user': 'omie_user',
                'password': 'omie_password',
                'min_size': 2,
                'max_size': 10
            },
            'redis': {
                'url': 'redis://localhost:6379',
                'encoding': 'utf-8',
                'decode_responses': True
            }
        }
    
    async def initialize(self) -> bool:
        """Inicializa conexões com PostgreSQL e Redis"""
        try:
            # PostgreSQL
            pg_config = self.config['postgresql']
            self.pg_pool = await asyncpg.create_pool(
                host=pg_config['host'],
                port=pg_config['port'],
                database=pg_config['database'],
                user=pg_config['user'],
                password=pg_config['password'],
                min_size=pg_config['min_size'],
                max_size=pg_config['max_size']
            )
            
            # Redis
            redis_config = self.config['redis']
            self.redis = await aioredis.from_url(
                redis_config['url'],
                encoding=redis_config['encoding'],
                decode_responses=redis_config['decode_responses']
            )
            
            # Testar conexões
            await self._test_connections()
            
            self.logger.info("✅ DatabaseManager inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar DatabaseManager: {e}")
            return False
    
    async def _test_connections(self):
        """Testa conectividade com ambos os bancos"""
        # Test PostgreSQL
        async with self.pg_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1
        
        # Test Redis
        await self.redis.ping()
    
    async def close(self):
        """Fecha todas as conexões"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis:
            await self.redis.close()
        self.logger.info("🔌 Conexões de banco fechadas")

# =============================================================================
# PROCESS CONTROLLER
# =============================================================================

class ProcessController:
    """Controlador de processos de integração com rastreamento completo"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def _generate_execution_id(self, process_type: str) -> str:
        """Gera ID único para execução"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uuid_short = str(uuid.uuid4())[:8]
        return f"{process_type}_{timestamp}_{uuid_short}"
    
    async def start_process(self, 
                          process_type: str, 
                          input_params: Dict[str, Any],
                          omie_endpoint: Optional[str] = None,
                          user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Inicia novo processo e retorna execution_id
        
        Args:
            process_type: Nome da tool/processo (ex: 'consultar_clientes')
            input_params: Parâmetros de entrada da tool
            omie_endpoint: Endpoint específico da API Omie
            user_context: Contexto do usuário (IP, session, etc)
            
        Returns:
            str: execution_id único do processo
        """
        execution_id = self._generate_execution_id(process_type)
        
        try:
            # Inserir no PostgreSQL
            async with self.db.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO process_executions 
                    (execution_id, process_type, status, input_parameters, omie_endpoint,
                     user_agent, ip_address, fastmcp_session_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, 
                    execution_id,
                    process_type, 
                    ExecutionStatus.RUNNING.value,
                    json.dumps(input_params),
                    omie_endpoint,
                    user_context.get('user_agent') if user_context else None,
                    user_context.get('ip_address') if user_context else None,
                    user_context.get('session_id') if user_context else None
                )
            
            # Cache no Redis para acesso rápido
            process_cache = {
                'status': ExecutionStatus.RUNNING.value,
                'started_at': datetime.now().isoformat(),
                'process_type': process_type,
                'input_params': input_params
            }
            
            await self.db.redis.setex(
                f"process:{execution_id}",
                3600,  # 1 hora TTL para processos ativos
                json.dumps(process_cache)
            )
            
            # Incrementar contador de processos ativos
            await self.db.redis.incr("active_processes_count")
            
            self.logger.info(f"🚀 Processo iniciado: {execution_id} ({process_type})")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar processo {process_type}: {e}")
            raise
    
    async def update_process_request(self, 
                                   execution_id: str,
                                   request_payload: Dict[str, Any],
                                   endpoint: str):
        """Atualiza dados da requisição"""
        try:
            async with self.db.pg_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE process_executions 
                    SET request_payload = $1, omie_endpoint = $2, updated_at = NOW()
                    WHERE execution_id = $3
                """, json.dumps(request_payload), endpoint, execution_id)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar request {execution_id}: {e}")
    
    async def complete_process(self, 
                             execution_id: str, 
                             success: bool,
                             response_data: Optional[Dict[str, Any]] = None,
                             error_message: Optional[str] = None,
                             error_code: Optional[str] = None,
                             status_code: Optional[int] = None) -> bool:
        """
        Marca processo como completo
        
        Args:
            execution_id: ID do processo
            success: Se foi bem-sucedido
            response_data: Dados da resposta
            error_message: Mensagem de erro (se houver)
            error_code: Código do erro
            status_code: Status HTTP da resposta
            
        Returns:
            bool: True se atualização foi bem-sucedida
        """
        status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
        
        try:
            # Atualizar PostgreSQL
            async with self.db.pg_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE process_executions 
                    SET status = $1, 
                        completed_at = NOW(), 
                        response_data = $2, 
                        error_message = $3,
                        error_code = $4,
                        response_status_code = $5,
                        duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000,
                        updated_at = NOW()
                    WHERE execution_id = $6
                """, 
                    status.value,
                    json.dumps(response_data) if response_data else None,
                    error_message,
                    error_code,
                    status_code,
                    execution_id
                )
            
            # Atualizar cache Redis
            process_cache = {
                'status': status.value,
                'completed_at': datetime.now().isoformat(),
                'success': success,
                'duration_ms': 0  # Será calculado no próximo get se necessário
            }
            
            await self.db.redis.setex(
                f"process:{execution_id}",
                86400,  # 24 horas para processos completos
                json.dumps(process_cache)
            )
            
            # Decrementar contador de processos ativos
            await self.db.redis.decr("active_processes_count")
            
            # Log da conclusão
            if success:
                self.logger.info(f"✅ Processo concluído: {execution_id}")
            else:
                self.logger.warning(f"❌ Processo falhou: {execution_id} - {error_message}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao completar processo {execution_id}: {e}")
            return False
    
    async def get_process_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status atual do processo"""
        try:
            # Tentar cache primeiro
            cached = await self.db.redis.get(f"process:{execution_id}")
            if cached:
                return json.loads(cached)
            
            # Buscar no PostgreSQL
            async with self.db.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT execution_id, process_type, status, started_at, completed_at,
                           duration_ms, error_message, response_status_code
                    FROM process_executions 
                    WHERE execution_id = $1
                """, execution_id)
                
                if row:
                    return dict(row)
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar status {execution_id}: {e}")
        
        return None
    
    async def get_active_processes(self) -> List[Dict[str, Any]]:
        """Lista todos os processos ativos"""
        try:
            async with self.db.pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT execution_id, process_type, started_at, input_parameters
                    FROM process_executions 
                    WHERE status = 'running' 
                    ORDER BY started_at DESC
                """)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar processos ativos: {e}")
            return []

# =============================================================================
# METRICS COLLECTOR
# =============================================================================

class MetricsCollector:
    """Coletor de métricas de performance e uso"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    async def record_api_metric(self, metric: APIMetric) -> bool:
        """Registra métrica de API"""
        try:
            async with self.db.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO omie_api_metrics 
                    (endpoint, response_time_ms, status_code, success,
                     request_size_bytes, response_size_bytes, process_execution_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    metric.endpoint,
                    metric.response_time_ms,
                    metric.status_code,
                    metric.success,
                    metric.request_size_bytes,
                    metric.response_size_bytes,
                    metric.process_execution_id
                )
            
            # Métricas em tempo real no Redis
            current_hour = datetime.now().hour
            redis_key = f"metrics:hourly:{metric.endpoint}:{current_hour}"
            
            await self.db.redis.hincrby(redis_key, "count", 1)
            await self.db.redis.hincrby(redis_key, "total_time", metric.response_time_ms)
            if metric.success:
                await self.db.redis.hincrby(redis_key, "success_count", 1)
            
            # TTL de 25 horas para dados horários
            await self.db.redis.expire(redis_key, 90000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao registrar métrica: {e}")
            return False
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém resumo de performance das últimas N horas"""
        try:
            async with self.db.pg_pool.acquire() as conn:
                # Métricas gerais
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(*) FILTER (WHERE success) as successful_requests,
                        AVG(response_time_ms) as avg_response_time,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time
                    FROM omie_api_metrics 
                    WHERE timestamp > NOW() - INTERVAL '%s hours'
                """, hours)
                
                # Top endpoints
                top_endpoints = await conn.fetch("""
                    SELECT 
                        endpoint,
                        COUNT(*) as requests,
                        AVG(response_time_ms) as avg_time
                    FROM omie_api_metrics 
                    WHERE timestamp > NOW() - INTERVAL '%s hours'
                    GROUP BY endpoint
                    ORDER BY requests DESC
                    LIMIT 10
                """, hours)
                
                return {
                    'summary': dict(summary) if summary else {},
                    'top_endpoints': [dict(row) for row in top_endpoints],
                    'period_hours': hours,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar resumo de performance: {e}")
            return {}

# =============================================================================
# ALERT MANAGER
# =============================================================================

class AlertManager:
    """Gerenciador de alertas do sistema"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    async def create_alert(self, alert: IntegrationAlert) -> bool:
        """Cria novo alerta"""
        try:
            async with self.db.pg_pool.acquire() as conn:
                alert_id = await conn.fetchval("""
                    INSERT INTO integration_alerts 
                    (alert_type, severity, title, message, context_data, process_execution_id)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """,
                    alert.alert_type,
                    alert.severity.value,
                    alert.title,
                    alert.message,
                    json.dumps(alert.context_data) if alert.context_data else None,
                    alert.process_execution_id
                )
            
            # Cache de alertas críticos no Redis
            if alert.severity == AlertSeverity.CRITICAL:
                await self.db.redis.lpush(
                    "critical_alerts",
                    json.dumps({
                        'id': alert_id,
                        'title': alert.title,
                        'message': alert.message,
                        'created_at': datetime.now().isoformat()
                    })
                )
                # Manter apenas os 50 alertas críticos mais recentes
                await self.db.redis.ltrim("critical_alerts", 0, 49)
            
            self.logger.warning(f"🚨 Alerta criado: {alert.alert_type} - {alert.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar alerta: {e}")
            return False
    
    async def get_unresolved_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Lista alertas não resolvidos"""
        try:
            query = """
                SELECT id, alert_type, severity, title, message, created_at, context_data
                FROM integration_alerts 
                WHERE NOT is_resolved
            """
            params = []
            
            if severity:
                query += " AND severity = $1"
                params.append(severity.value)
            
            query += " ORDER BY created_at DESC LIMIT 100"
            
            async with self.db.pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar alertas: {e}")
            return []

# =============================================================================
# SISTEMA INTEGRADO
# =============================================================================

class OmieIntegrationDatabase:
    """Sistema integrado de banco de dados para Omie MCP"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.db_manager = DatabaseManager(config)
        self.process_controller = ProcessController(self.db_manager)
        self.metrics_collector = MetricsCollector(self.db_manager)
        self.alert_manager = AlertManager(self.db_manager)
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Inicializa todo o sistema"""
        success = await self.db_manager.initialize()
        if success:
            self.logger.info("🗄️ Sistema de banco de dados Omie MCP inicializado")
        return success
    
    async def close(self):
        """Finaliza sistema"""
        await self.db_manager.close()
        self.logger.info("🔌 Sistema de banco de dados finalizado")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de banco"""
        try:
            # Test PostgreSQL
            async with self.db_manager.pg_pool.acquire() as conn:
                pg_status = await conn.fetchval("SELECT 1")
            
            # Test Redis
            redis_status = await self.db_manager.redis.ping()
            
            # Contar processos ativos
            active_count = await self.db_manager.redis.get("active_processes_count") or 0
            
            return {
                'postgresql': pg_status == 1,
                'redis': redis_status,
                'active_processes': int(active_count),
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'postgresql': False,
                'redis': False,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# =============================================================================
# DECORADOR PARA TOOLS
# =============================================================================

def track_process(process_type: str, endpoint: str = None):
    """
    Decorador para rastrear automaticamente execução de tools
    
    Args:
        process_type: Nome da tool/processo
        endpoint: Endpoint específico da API Omie
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Obter instância do database (assumindo que está disponível globalmente)
            # Em implementação real, seria injetado ou obtido de contexto
            from src.database.database_manager import omie_db
            
            # Iniciar rastreamento
            execution_id = await omie_db.process_controller.start_process(
                process_type=process_type,
                input_params=kwargs,
                omie_endpoint=endpoint
            )
            
            try:
                # Executar função original
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Registrar sucesso
                await omie_db.process_controller.complete_process(
                    execution_id=execution_id,
                    success=True,
                    response_data=result if isinstance(result, dict) else {'result': str(result)}
                )
                
                # Métrica de performance
                await omie_db.metrics_collector.record_api_metric(
                    APIMetric(
                        endpoint=endpoint or process_type,
                        response_time_ms=int(duration),
                        status_code=200,
                        success=True,
                        process_execution_id=execution_id
                    )
                )
                
                return result
                
            except Exception as e:
                # Registrar falha
                await omie_db.process_controller.complete_process(
                    execution_id=execution_id,
                    success=False,
                    error_message=str(e),
                    error_code=type(e).__name__
                )
                
                # Alerta se necessário
                if "timeout" in str(e).lower():
                    await omie_db.alert_manager.create_alert(
                        IntegrationAlert(
                            alert_type="api_timeout",
                            severity=AlertSeverity.WARNING,
                            title=f"Timeout em {process_type}",
                            message=f"Processo {execution_id} teve timeout: {str(e)}",
                            process_execution_id=execution_id
                        )
                    )
                
                raise
        
        return wrapper
    return decorator

# Instância global (será inicializada no startup da aplicação)
omie_db: Optional[OmieIntegrationDatabase] = None

if __name__ == "__main__":
    async def test_database():
        """Teste básico do sistema"""
        print("🧪 Testando sistema de banco de dados...")
        
        db = OmieIntegrationDatabase()
        
        try:
            # Inicializar
            if await db.initialize():
                print("✅ Inicialização OK")
                
                # Testar processo
                execution_id = await db.process_controller.start_process(
                    "test_process",
                    {"param1": "value1"}
                )
                print(f"✅ Processo iniciado: {execution_id}")
                
                # Completar processo
                await db.process_controller.complete_process(
                    execution_id,
                    success=True,
                    response_data={"result": "success"}
                )
                print("✅ Processo completado")
                
                # Health check
                health = await db.health_check()
                print(f"✅ Health check: {health}")
                
            else:
                print("❌ Falha na inicialização")
                
        finally:
            await db.close()
    
    # Executar teste
    asyncio.run(test_database())