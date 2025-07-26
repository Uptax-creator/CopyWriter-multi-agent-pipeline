#!/usr/bin/env python3
"""
Exemplo de Servidor Omie usando FastMCP 2.0
Para comparação com nossa implementação atual
"""

import asyncio
import os
import sys
from typing import Optional, Dict, Any
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

# Criar instância FastMCP
mcp = FastMCP("Omie ERP Integration 🚀")

# Cliente Omie global
omie_client = None

async def get_omie_client():
    """Obtém cliente Omie inicializado"""
    global omie_client
    if omie_client is None:
        try:
            omie_client = OmieClient()
            await omie_client.initialize()  # Se tiver método de inicialização
        except Exception as e:
            raise Exception(f"Erro ao inicializar cliente Omie: {e}")
    return omie_client

# FERRAMENTAS USANDO FASTMCP 2.0

@mcp.tool
async def testar_conexao() -> str:
    """
    Testa a conexão com a API do Omie ERP
    
    Returns:
        str: Status da conexão
    """
    try:
        client = await get_omie_client()
        result = await client.testar_conexao()
        return f"✅ Conexão OK: {result}"
    except Exception as e:
        return f"❌ Erro na conexão: {str(e)}"

@mcp.tool
async def consultar_categorias(
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """
    Consulta categorias cadastradas no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de categorias em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_categorias(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao consultar categorias: {str(e)}"

@mcp.tool
async def consultar_departamentos(
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """
    Consulta departamentos cadastrados no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de departamentos em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_departamentos(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao consultar departamentos: {str(e)}"

@mcp.tool
async def consultar_tipos_documento(codigo: Optional[str] = None) -> str:
    """
    Consulta tipos de documento no Omie ERP
    
    Args:
        codigo: Código específico do tipo de documento (opcional)
        
    Returns:
        str: Lista de tipos de documento em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_tipos_documento(codigo=codigo)
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao consultar tipos de documento: {str(e)}"

@mcp.tool
async def consultar_contas_pagar(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    registros_por_pagina: int = 20
) -> str:
    """
    Consulta contas a pagar no Omie ERP
    
    Args:
        data_inicio: Data de início da consulta (DD/MM/AAAA)
        data_fim: Data de fim da consulta (DD/MM/AAAA)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de contas a pagar em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_contas_pagar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao consultar contas a pagar: {str(e)}"

@mcp.tool
async def consultar_contas_receber(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    registros_por_pagina: int = 20
) -> str:
    """
    Consulta contas a receber no Omie ERP
    
    Args:
        data_inicio: Data de início da consulta (DD/MM/AAAA)
        data_fim: Data de fim da consulta (DD/MM/AAAA)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de contas a receber em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_contas_receber(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao consultar contas a receber: {str(e)}"

# RECURSOS USANDO FASTMCP 2.0

@mcp.resource("omie://config")
async def get_omie_config() -> str:
    """
    Retorna configuração atual do cliente Omie
    
    Returns:
        str: Configuração do cliente Omie (sem credenciais sensíveis)
    """
    try:
        client = await get_omie_client()
        config = {
            "base_url": getattr(client, 'base_url', 'https://app.omie.com.br/api/v1/'),
            "timeout": getattr(client, 'timeout', 30),
            "status": "conectado" if client else "desconectado"
        }
        import json
        return json.dumps(config, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ Erro ao obter configuração: {str(e)}"

@mcp.resource("omie://status")
async def get_omie_status() -> str:
    """
    Retorna status atual da conexão Omie
    
    Returns:
        str: Status da conexão em formato JSON
    """
    try:
        client = await get_omie_client()
        # Teste rápido de conectividade
        test_result = await client.testar_conexao()
        status = {
            "connection": "ok" if test_result else "failed",
            "timestamp": str(asyncio.get_event_loop().time()),
            "client_initialized": client is not None
        }
        import json
        return json.dumps(status, ensure_ascii=False, indent=2)
    except Exception as e:
        return f'{{"connection": "error", "message": "{str(e)}"}}'

# PROMPTS USANDO FASTMCP 2.0

@mcp.prompt("omie-financial-summary")
async def financial_summary_prompt(
    data_inicio: str,
    data_fim: str
) -> str:
    """
    Gera prompt para análise financeira do período
    
    Args:
        data_inicio: Data início (DD/MM/AAAA)
        data_fim: Data fim (DD/MM/AAAA)
        
    Returns:
        str: Prompt formatado para análise financeira
    """
    return f"""
Analise o desempenho financeiro da empresa no período de {data_inicio} a {data_fim}.

Considere:
1. Consulte contas a pagar do período
2. Consulte contas a receber do período  
3. Compare os valores
4. Identifique tendências
5. Sugira ações de melhoria

Use as ferramentas disponíveis para obter os dados necessários e forneça uma análise detalhada.
"""

@mcp.prompt("omie-data-validation")
async def data_validation_prompt() -> str:
    """
    Gera prompt para validação de dados Omie
    
    Returns:
        str: Prompt para validação de integridade dos dados
    """
    return """
Execute uma validação completa dos dados do Omie ERP:

1. Teste a conexão com a API
2. Verifique se as categorias estão carregadas
3. Valide se os departamentos estão configurados
4. Confirme se os tipos de documento estão disponíveis
5. Teste consultas de contas a pagar e receber

Reporte qualquer inconsistência ou erro encontrado.
"""

if __name__ == "__main__":
    # Executar servidor FastMCP
    print("🚀 Iniciando Servidor Omie FastMCP 2.0...")
    print("📋 Ferramentas disponíveis:")
    print("   - testar_conexao")
    print("   - consultar_categorias") 
    print("   - consultar_departamentos")
    print("   - consultar_tipos_documento")
    print("   - consultar_contas_pagar")
    print("   - consultar_contas_receber")
    print("📂 Recursos disponíveis:")
    print("   - omie://config")
    print("   - omie://status")
    print("📝 Prompts disponíveis:")
    print("   - omie-financial-summary")
    print("   - omie-data-validation")
    print()
    
    # Executar servidor
    mcp.run()