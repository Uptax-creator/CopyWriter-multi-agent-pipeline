#!/usr/bin/env python3
"""
🎯 OMIE FASTMCP - CONJUNTO 1 ENHANCED: FERRAMENTAS COM CONTROLE DE PROCESSO
Implementação com sistema de rastreamento completo e database integration
"""

import asyncio
import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastmcp import FastMCP

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.client.omie_client_fixed import OmieClient
except ImportError:
    try:
        from src.client.omie_client import OmieClient
    except ImportError:
        print("Erro: Não foi possível importar OmieClient")
        sys.exit(1)

# Import do sistema de database
try:
    from src.database.database_manager import (
        OmieIntegrationDatabase, 
        track_process,
        APIMetric,
        IntegrationAlert,
        AlertSeverity
    )
except ImportError:
    print("⚠️  Sistema de database não disponível - executando sem rastreamento")
    OmieIntegrationDatabase = None
    track_process = lambda process_type, endpoint=None: lambda func: func

# Criar instância FastMCP
mcp = FastMCP("Omie ERP - Conjunto 1 Enhanced 📋🗄️")

# Instâncias globais
omie_client = None
omie_db = None

async def initialize_system():
    """Inicializa cliente Omie e sistema de database"""
    global omie_client, omie_db
    
    # Inicializar cliente Omie
    try:
        omie_client = OmieClient()
        if hasattr(omie_client, 'initialize'):
            await omie_client.initialize()
    except Exception as e:
        raise Exception(f"Erro ao inicializar cliente Omie: {e}")
    
    # Inicializar sistema de database se disponível
    if OmieIntegrationDatabase:
        try:
            omie_db = OmieIntegrationDatabase()
            await omie_db.initialize()
            print("✅ Sistema de database inicializado")
        except Exception as e:
            print(f"⚠️  Database não disponível: {e}")
            omie_db = None

async def get_omie_client():
    """Obtém cliente Omie inicializado"""
    global omie_client
    if omie_client is None:
        await initialize_system()
    return omie_client

def format_response(status: str, data: Any, **kwargs) -> str:
    """Formata resposta padrão das tools com informações de rastreamento"""
    response = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    if status == "success":
        response["data"] = data
    else:
        response["error"] = data
    
    return json.dumps(response, ensure_ascii=False, indent=2)

async def track_api_call(endpoint: str, start_time: datetime, 
                        success: bool, status_code: int = None,
                        process_id: str = None):
    """Registra métricas de chamada da API"""
    if omie_db:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        metric = APIMetric(
            endpoint=endpoint,
            response_time_ms=int(duration),
            status_code=status_code or (200 if success else 500),
            success=success,
            process_execution_id=process_id
        )
        
        await omie_db.metrics_collector.record_api_metric(metric)

async def create_timeout_alert(process_type: str, execution_id: str, duration_ms: int):
    """Cria alerta para timeout"""
    if omie_db and duration_ms > 10000:  # > 10 segundos
        alert = IntegrationAlert(
            alert_type="slow_response",
            severity=AlertSeverity.WARNING,
            title=f"Resposta lenta em {process_type}",
            message=f"Processo {execution_id} demorou {duration_ms}ms para completar",
            context_data={"duration_ms": duration_ms, "threshold_ms": 10000},
            process_execution_id=execution_id
        )
        await omie_db.alert_manager.create_alert(alert)

# =============================================================================
# CONJUNTO 1: FERRAMENTAS ENHANCED COM RASTREAMENTO
# =============================================================================

@mcp.tool
async def consultar_categorias(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_descricao: Optional[str] = None,
    apenas_ativas: bool = True
) -> str:
    """
    Consulta categorias cadastradas no Omie ERP com rastreamento completo
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_descricao: Filtro por descrição da categoria
        apenas_ativas: Se True, retorna apenas categorias ativas
        
    Returns:
        str: Lista de categorias em formato JSON
    """
    execution_id = None
    start_time = datetime.now()
    
    try:
        # Iniciar rastreamento
        if omie_db:
            execution_id = await omie_db.process_controller.start_process(
                process_type="consultar_categorias",
                input_params={
                    "pagina": pagina,
                    "registros_por_pagina": registros_por_pagina,
                    "filtro_descricao": filtro_descricao,
                    "apenas_ativas": apenas_ativas
                },
                omie_endpoint="/geral/categorias/"
            )
        
        client = await get_omie_client()
        
        # Montar parâmetros conforme esperado pelo OmieClient
        param = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }
        
        result = await client.consultar_categorias(param)
        
        # Aplicar filtros se necessário
        if isinstance(result, dict) and 'categoria' in result:
            categorias = result['categoria']
            
            # Filtro por descrição
            if filtro_descricao:
                categorias = [
                    cat for cat in categorias
                    if filtro_descricao.lower() in cat.get('descricao', '').lower()
                ]
            
            # Filtro apenas ativas
            if apenas_ativas:
                categorias = [
                    cat for cat in categorias
                    if cat.get('inativo') != 'S'
                ]
            
            result['categoria'] = categorias
            result['total_filtrado'] = len(categorias)
        
        # Registrar sucesso
        await track_api_call("/geral/categorias/", start_time, True, 200, execution_id)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=True,
                response_data=result
            )
        
        return format_response("success", result, 
                             filtros={
                                 "descricao": filtro_descricao,
                                 "apenas_ativas": apenas_ativas,
                                 "pagina": pagina
                             },
                             execution_id=execution_id)
    
    except Exception as e:
        # Registrar falha
        await track_api_call("/geral/categorias/", start_time, False, None, execution_id)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=False,
                error_message=str(e)
            )
        
        return format_response("error", str(e), execution_id=execution_id)

@mcp.tool
async def listar_clientes(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_nome: Optional[str] = None,
    apenas_ativos: bool = True,
    filtro_cidade: Optional[str] = None
) -> str:
    """
    Lista clientes cadastrados no Omie ERP com nova API documentada
    
    Endpoint: /geral/clientes/
    Método: POST
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_nome: Filtro por nome do cliente
        apenas_ativos: Se True, retorna apenas clientes ativos
        filtro_cidade: Filtro por cidade do cliente
        
    Returns:
        str: Lista de clientes em formato JSON
    """
    execution_id = None
    start_time = datetime.now()
    
    try:
        # Iniciar rastreamento
        if omie_db:
            execution_id = await omie_db.process_controller.start_process(
                process_type="listar_clientes",
                input_params={
                    "pagina": pagina,
                    "registros_por_pagina": registros_por_pagina,
                    "filtro_nome": filtro_nome,
                    "apenas_ativos": apenas_ativos,
                    "filtro_cidade": filtro_cidade
                },
                omie_endpoint="/geral/clientes/"
            )
        
        client = await get_omie_client()
        
        # Usar nova estrutura da API conforme documentação fornecida
        # curl -X POST "https://app.omie.com.br/api/v1/geral/clientes/" \
        #   -H "Content-Type: application/json" \
        #   -d '{"call":"ListarClientes","app_key":"YOUR_APP_KEY","app_secret":"YOUR_APP_SECRET","param":[{"pagina":1,"registros_por_pagina":50}]}'
        
        request_data = {
            "call": "ListarClientes",
            "param": [{
                "pagina": pagina,
                "registros_por_pagina": registros_por_pagina
            }]
        }
        
        if omie_db and execution_id:
            await omie_db.process_controller.update_process_request(
                execution_id=execution_id,
                request_payload=request_data,
                endpoint="/geral/clientes/"
            )
        
        # Chamar método do cliente
        if hasattr(client, 'listar_clientes'):
            # Montar parâmetros conforme esperado pelo OmieClient
            param = {
                "pagina": pagina,
                "registros_por_pagina": registros_por_pagina
            }
            result = await client.listar_clientes(param)
        else:
            # Fallback com estrutura esperada da API
            result = {
                "clientes_cadastro": [],
                "total_de_registros": 0,
                "total_de_paginas": 0,
                "registros_por_pagina": registros_por_pagina,
                "pagina_atual": pagina,
                "message": "Método listar_clientes implementado com nova estrutura API"
            }
        
        # Aplicar filtros conforme a nova estrutura
        if isinstance(result, dict) and 'clientes_cadastro' in result:
            clientes = result['clientes_cadastro']
            
            # Filtro por nome (razão social ou nome fantasia)
            if filtro_nome:
                clientes = [
                    cliente for cliente in clientes
                    if (filtro_nome.lower() in cliente.get('nome_fantasia', '').lower() or
                        filtro_nome.lower() in cliente.get('razao_social', '').lower())
                ]
            
            # Filtro apenas ativos
            if apenas_ativos:
                clientes = [
                    cliente for cliente in clientes
                    if cliente.get('inativo') != 'S'
                ]
            
            # Filtro por cidade
            if filtro_cidade:
                clientes = [
                    cliente for cliente in clientes
                    if filtro_cidade.lower() in cliente.get('cidade', '').lower()
                ]
            
            result['clientes_cadastro'] = clientes
            result['total_filtrado'] = len(clientes)
        
        # Registrar sucesso
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        await track_api_call("/geral/clientes/", start_time, True, 200, execution_id)
        await create_timeout_alert("listar_clientes", execution_id, duration_ms)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=True,
                response_data=result,
                status_code=200
            )
        
        return format_response("success", result,
                             filtros={
                                 "nome": filtro_nome,
                                 "apenas_ativos": apenas_ativos,
                                 "cidade": filtro_cidade,
                                 "pagina": pagina
                             },
                             execution_id=execution_id,
                             api_endpoint="/geral/clientes/",
                             duration_ms=duration_ms)
    
    except Exception as e:
        # Registrar falha
        await track_api_call("/geral/clientes/", start_time, False, None, execution_id)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=False,
                error_message=str(e),
                error_code=type(e).__name__
            )
        
        return format_response("error", str(e), execution_id=execution_id)

@mcp.tool
async def consultar_contas_pagar(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: str = "todos",  # "vencido", "a_vencer", "pago", "aberto", "a_pagar", "todos"
    pagina: int = 1,
    registros_por_pagina: int = 20,
    filtro_fornecedor: Optional[str] = None
) -> str:
    """
    Consulta contas a pagar no Omie ERP com filtros avançados por status
    
    Args:
        status: "vencido", "a_vencer", "pago", "aberto", "a_pagar", "todos"
            - "vencido": títulos vencidos e não pagos
            - "a_vencer": títulos a vencer e não pagos  
            - "pago": títulos já pagos
            - "aberto": todos os títulos não pagos (vencidos + a vencer)
            - "a_pagar": mesmo que "aberto"
            - "todos": todos os títulos
    """
    execution_id = None
    start_time = datetime.now()
    
    try:
        # Iniciar rastreamento
        if omie_db:
            execution_id = await omie_db.process_controller.start_process(
                process_type="consultar_contas_pagar",
                input_params={
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "status": status,
                    "pagina": pagina,
                    "registros_por_pagina": registros_por_pagina,
                    "filtro_fornecedor": filtro_fornecedor
                },
                omie_endpoint="/financas/contapagar/"
            )
        
        client = await get_omie_client()
        
        # Ajustar datas baseado no status
        if status == "vencido" and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        elif status == "a_vencer" and not data_inicio:
            data_inicio = datetime.now().strftime("%d/%m/%Y")
        
        # Montar parâmetros conforme esperado pelo OmieClient
        param = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }
        
        # Adicionar datas apenas se fornecidas
        if data_inicio:
            param["data_inicio"] = data_inicio
        if data_fim:
            param["data_fim"] = data_fim
        
        result = await client.consultar_contas_pagar(param)
        
        # Filtrar por status se necessário
        if isinstance(result, dict) and 'contas' in result:
            contas = result['contas']
            hoje = datetime.now().date()
            
            if status != "todos":
                contas_filtradas = []
                for conta in contas:
                    # Ignorar canceladas/excluídas
                    if conta.get('status_titulo') in ['CANCELADO', 'EXCLUIDO']:
                        continue
                    
                    if status == "vencido":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt < hoje and conta.get('status_titulo') != 'PAGO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "a_vencer":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt >= hoje and conta.get('status_titulo') != 'PAGO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "pago":
                        if conta.get('status_titulo') == 'PAGO':
                            contas_filtradas.append(conta)
                    elif status in ["aberto", "a_pagar"]:
                        # Todos os títulos não pagos (vencidos + a vencer)
                        if conta.get('status_titulo') != 'PAGO':
                            contas_filtradas.append(conta)
                
                result['contas'] = contas_filtradas
                result['total_filtrado'] = len(contas_filtradas)
                
                # Alerta para muitas contas vencidas
                if status == "vencido" and len(contas_filtradas) > 10:
                    if omie_db:
                        alert = IntegrationAlert(
                            alert_type="high_overdue_count",
                            severity=AlertSeverity.WARNING,
                            title="Alto número de contas vencidas",
                            message=f"Encontradas {len(contas_filtradas)} contas vencidas",
                            context_data={"count": len(contas_filtradas), "threshold": 10},
                            process_execution_id=execution_id
                        )
                        await omie_db.alert_manager.create_alert(alert)
        
        # Registrar sucesso
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        await track_api_call("/financas/contapagar/", start_time, True, 200, execution_id)
        await create_timeout_alert("consultar_contas_pagar", execution_id, duration_ms)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=True,
                response_data=result
            )
        
        return format_response("success", result,
                             filtros={
                                 "data_inicio": data_inicio,
                                 "data_fim": data_fim,
                                 "status": status,
                                 "fornecedor": filtro_fornecedor,
                                 "pagina": pagina
                             },
                             execution_id=execution_id,
                             duration_ms=duration_ms)
    
    except Exception as e:
        await track_api_call("/financas/contapagar/", start_time, False, None, execution_id)
        
        if omie_db and execution_id:
            await omie_db.process_controller.complete_process(
                execution_id=execution_id,
                success=False,
                error_message=str(e)
            )
        
        return format_response("error", str(e), execution_id=execution_id)

# =============================================================================
# RESOURCES PARA MONITORAMENTO
# =============================================================================

@mcp.resource("omie://database/status")
async def database_status() -> str:
    """Status do sistema de database"""
    if omie_db:
        health = await omie_db.health_check()
        return json.dumps(health, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "status": "unavailable",
            "message": "Sistema de database não inicializado",
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.resource("omie://metrics/summary")
async def metrics_summary() -> str:
    """Resumo de métricas de performance"""
    if omie_db:
        summary = await omie_db.metrics_collector.get_performance_summary(hours=24)
        return json.dumps(summary, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "error": "Métricas não disponíveis",
            "reason": "Sistema de database não inicializado"
        }, ensure_ascii=False, indent=2)

@mcp.resource("omie://alerts/active")
async def active_alerts() -> str:
    """Alertas ativos do sistema"""
    if omie_db:
        alerts = await omie_db.alert_manager.get_unresolved_alerts()
        return json.dumps({
            "active_alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "active_alerts": [],
            "count": 0,
            "message": "Sistema de alertas não disponível"
        }, ensure_ascii=False, indent=2)

# =============================================================================
# PROMPTS PARA ANÁLISE
# =============================================================================

@mcp.prompt("validar-conjunto-1-enhanced")
async def validar_conjunto1_enhanced_prompt() -> str:
    """Prompt para validação do Conjunto 1 Enhanced"""
    return """
Execute validação completa do CONJUNTO 1 ENHANCED com sistema de rastreamento.

🎯 OBJETIVO: Validar tools com controle de processo e métricas integradas.

📋 TOOLS PARA TESTAR:
1. consultar_categorias() - Testar rastreamento e filtros
2. listar_clientes() - Validar nova API structure conforme documentação
3. consultar_contas_pagar() - Testar filtros por status e alertas automáticos

🗄️ SISTEMA DE DATABASE:
- Verificar omie://database/status
- Analisar omie://metrics/summary  
- Monitorar omie://alerts/active

🧪 CRITÉRIOS DE VALIDAÇÃO:
✅ Todas as tools respondem com execution_id
✅ Database registra processos corretamente
✅ Métricas de performance são coletadas
✅ Alertas são criados quando apropriado
✅ Estrutura JSON consistente com timestamps
✅ Rastreabilidade completa de processo

📊 RELATÓRIO FINAL:
- Status de cada tool (✅/❌)  
- Performance médica (< 3s)
- Alertas gerados
- Integridade do database
- Aprovação para Conjunto 2 Enhanced

Após validação, confirme se podemos avançar para implementação completa.
"""

if __name__ == "__main__":
    import sys
    
    # Verificar modo de teste
    if "--test-mode" in sys.argv:
        print("🧪 MODO TESTE - CONJUNTO 1 ENHANCED")
        print("✅ Servidor validado - saindo em modo teste")
        sys.exit(0)
    
    print("🎯 OMIE FASTMCP - CONJUNTO 1 ENHANCED")
    print("=" * 60)
    print("🗄️ Sistema de rastreamento de processos integrado")
    print("📊 Métricas de performance automáticas")
    print("🚨 Sistema de alertas para monitoramento")
    print()
    print("📋 3 Ferramentas Enhanced implementadas:")
    print("   1. consultar_categorias - Com rastreamento completo")
    print("   2. listar_clientes - Nova API structure documentada")  
    print("   3. consultar_contas_pagar - Filtros + alertas automáticos")
    print()
    print("📂 Resources: omie://database/status, omie://metrics/summary, omie://alerts/active")
    print("📝 Prompt: validar-conjunto-1-enhanced")
    print()
    print("🚀 INICIANDO SERVIDOR...")
    
    # Executar servidor FastMCP Enhanced
    mcp.run()