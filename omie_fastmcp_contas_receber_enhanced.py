#!/usr/bin/env python3
"""
🎯 OMIE FASTMCP - CONTAS A RECEBER ENHANCED
Implementação da ferramenta consultar_contas_receber com filtros de status
Baseado na estrutura do consultar_contas_pagar
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
    from src.client.omie_client import OmieClient
except ImportError:
    print("Erro: Não foi possível importar OmieClient")
    sys.exit(1)

# Criar instância FastMCP
mcp = FastMCP("Omie ERP - Contas a Receber Enhanced 💰📈")

# Instância global
omie_client = None

async def initialize_system():
    """Inicializa cliente Omie"""
    global omie_client
    if omie_client is None:
        omie_client = OmieClient()
    return omie_client

async def get_omie_client():
    """Obtém cliente Omie inicializado"""
    return await initialize_system()

def format_response(status: str, data: Any, **kwargs) -> str:
    """Formatar resposta padronizada"""
    response = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "data": data,
        **kwargs
    }
    
    return json.dumps(response, ensure_ascii=False, indent=2, default=str)

@mcp.tool()
async def consultar_contas_receber(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: str = "todos",  # "vencido", "a_vencer", "recebido", "aberto", "a_receber", "todos"
    pagina: int = 1,
    registros_por_pagina: int = 20,
    filtro_cliente: Optional[str] = None
) -> str:
    """
    Consulta contas a receber no Omie ERP com filtros avançados por status
    
    Args:
        data_inicio: Data início no formato DD/MM/AAAA (opcional)
        data_fim: Data fim no formato DD/MM/AAAA (opcional)
        status: "vencido", "a_vencer", "recebido", "aberto", "a_receber", "todos"
            - "vencido": títulos vencidos e não recebidos
            - "a_vencer": títulos a vencer e não recebidos  
            - "recebido": títulos já recebidos
            - "aberto": todos os títulos não recebidos (vencidos + a vencer)
            - "a_receber": mesmo que "aberto"
            - "todos": todos os títulos
        pagina: Número da página (padrão: 1)
        registros_por_pagina: Registros por página (padrão: 20, máx: 500)
        filtro_cliente: Filtro por nome do cliente (opcional)
    
    Returns:
        JSON com contas a receber filtradas por status
    
    Examples:
        - consultar_contas_receber(status="vencido") - títulos vencidos
        - consultar_contas_receber(status="a_vencer") - títulos a vencer
        - consultar_contas_receber(status="recebido") - títulos recebidos
        - consultar_contas_receber(status="aberto") - títulos em aberto
    """
    start_time = datetime.now()
    
    try:
        client = await get_omie_client()
        
        # Ajustar datas baseado no status
        if status == "vencido" and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        elif status == "a_vencer" and not data_inicio:
            data_inicio = datetime.now().strftime("%d/%m/%Y")
        
        # Montar parâmetros conforme esperado pelo OmieClient
        param = {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, 500)
        }
        
        # Adicionar filtros de data se fornecidos
        if data_inicio:
            param["data_de"] = data_inicio
        if data_fim:
            param["data_ate"] = data_fim
            
        # Adicionar filtro de cliente se fornecido
        if filtro_cliente:
            param["cliente_fornecedor"] = filtro_cliente
        
        print(f"🔍 Consultando contas a receber - Status: {status}")
        print(f"📄 Página: {pagina}, Registros: {registros_por_pagina}")
        
        # Fazer requisição
        resultado = await client.consultar_contas_receber(param)
        
        if not resultado:
            return format_response(
                "error", 
                "Nenhum resultado retornado pela API",
                filtros_aplicados={
                    "status": status,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "pagina": pagina
                }
            )
        
        # Processar resultado baseado no status solicitado
        contas_receber = resultado.get("conta_receber_cadastro", [])
        
        if not contas_receber:
            return format_response(
                "warning",
                "Nenhuma conta a receber encontrada",
                total_registros=0,
                filtros_aplicados={
                    "status": status,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "filtro_cliente": filtro_cliente
                },
                metadata=resultado
            )
        
        # Filtrar por status se necessário
        contas_filtradas = []
        data_hoje = datetime.now()
        
        for conta in contas_receber:
            # Obter status da conta
            status_titulo = conta.get("status_titulo", "").lower()
            data_vencimento_str = conta.get("data_vencimento", "")
            
            # Converter data de vencimento
            data_vencimento = None
            if data_vencimento_str:
                try:
                    data_vencimento = datetime.strptime(data_vencimento_str, "%d/%m/%Y")
                except:
                    pass
            
            # Aplicar filtros de status
            incluir_conta = False
            
            if status == "todos":
                incluir_conta = True
            elif status == "recebido":
                incluir_conta = status_titulo in ["recebido", "liquidado", "baixado"]
            elif status == "vencido":
                incluir_conta = (
                    status_titulo not in ["recebido", "liquidado", "baixado"] and
                    data_vencimento and data_vencimento < data_hoje
                )
            elif status == "a_vencer":
                incluir_conta = (
                    status_titulo not in ["recebido", "liquidado", "baixado"] and
                    data_vencimento and data_vencimento >= data_hoje
                )
            elif status in ["aberto", "a_receber"]:
                incluir_conta = status_titulo not in ["recebido", "liquidado", "baixado"]
            
            if incluir_conta:
                contas_filtradas.append(conta)
        
        # Calcular totais
        total_valor = sum(float(str(c.get("valor_documento", 0)).replace(",", ".")) for c in contas_filtradas)
        
        # Estatísticas por status
        stats_por_status = {}
        for conta in contas_filtradas:
            status_conta = conta.get("status_titulo", "indefinido").lower()
            if status_conta not in stats_por_status:
                stats_por_status[status_conta] = {"count": 0, "valor": 0}
            stats_por_status[status_conta]["count"] += 1
            stats_por_status[status_conta]["valor"] += float(str(conta.get("valor_documento", 0)).replace(",", "."))
        
        # Tempo de execução
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return format_response(
            "success",
            contas_filtradas,
            total_registros=len(contas_filtradas),
            total_valor=total_valor,
            pagina_atual=pagina,
            registros_por_pagina=registros_por_pagina,
            total_paginas=resultado.get("total_de_paginas", 1),
            total_registros_api=resultado.get("total_de_registros", 0),
            filtros_aplicados={
                "status": status,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "filtro_cliente": filtro_cliente
            },
            estatisticas_status=stats_por_status,
            performance={
                "execution_time_ms": round(execution_time, 2),
                "records_per_second": round(len(contas_filtradas) / (execution_time / 1000), 2) if execution_time > 0 else 0
            }
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        error_msg = f"Erro ao consultar contas a receber: {str(e)}"
        print(f"❌ {error_msg}")
        
        return format_response(
            "error",
            error_msg,
            execution_time_ms=round(execution_time, 2),
            filtros_tentados={
                "status": status,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "filtro_cliente": filtro_cliente
            }
        )

@mcp.tool()
async def status_contas_receber() -> str:
    """
    Retorna resumo do status das contas a receber
    Mostra totais por categoria: vencido, a vencer, recebido, etc.
    """
    try:
        client = await get_omie_client()
        
        # Buscar todas as contas a receber (primeira página para análise)
        param = {
            "pagina": 1,
            "registros_por_pagina": 500
        }
        
        resultado = await client.consultar_contas_receber(param)
        contas_receber = resultado.get("conta_receber_cadastro", [])
        
        if not contas_receber:
            return format_response("warning", "Nenhuma conta a receber encontrada")
        
        # Análise por status
        status_summary = {
            "vencido": {"count": 0, "valor": 0},
            "a_vencer": {"count": 0, "valor": 0},
            "recebido": {"count": 0, "valor": 0},
            "total": {"count": len(contas_receber), "valor": 0}
        }
        
        data_hoje = datetime.now()
        
        for conta in contas_receber:
            valor = float(str(conta.get("valor_documento", 0)).replace(",", "."))
            status_titulo = conta.get("status_titulo", "").lower()
            data_vencimento_str = conta.get("data_vencimento", "")
            
            status_summary["total"]["valor"] += valor
            
            # Converter data de vencimento
            data_vencimento = None
            if data_vencimento_str:
                try:
                    data_vencimento = datetime.strptime(data_vencimento_str, "%d/%m/%Y")
                except:
                    pass
            
            # Classificar por status
            if status_titulo in ["recebido", "liquidado", "baixado"]:
                status_summary["recebido"]["count"] += 1
                status_summary["recebido"]["valor"] += valor
            elif data_vencimento and data_vencimento < data_hoje:
                status_summary["vencido"]["count"] += 1
                status_summary["vencido"]["valor"] += valor
            else:
                status_summary["a_vencer"]["count"] += 1
                status_summary["a_vencer"]["valor"] += valor
        
        return format_response(
            "success",
            status_summary,
            metadata={
                "data_analise": datetime.now().isoformat(),
                "total_analisado": len(contas_receber),
                "fonte": "Primeiras 500 contas a receber"
            }
        )
        
    except Exception as e:
        return format_response(
            "error",
            f"Erro ao obter status das contas a receber: {str(e)}"
        )

# Executar servidor se chamado diretamente
if __name__ == "__main__":
    print("🎯 OMIE FASTMCP - CONTAS A RECEBER ENHANCED")
    print("=" * 50)
    print("📊 Tools disponíveis:")
    print("   1. consultar_contas_receber - Consulta com filtros de status")
    print("   2. status_contas_receber - Resumo por status")
    print()
    print("🚀 Iniciando servidor MCP...")
    
    mcp.run()