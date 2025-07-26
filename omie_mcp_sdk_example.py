#!/usr/bin/env python3
"""
Exemplo de Servidor MCP usando Python SDK Oficial
Para comparação com nossa implementação atual
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

# Imports do SDK oficial MCP
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Nosso cliente Omie
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.client.omie_client_fixed import OmieClient
except ImportError:
    try:
        from src.client.omie_client import OmieClient
    except ImportError:
        print("Erro: Não foi possível importar OmieClient")
        sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omie-mcp-sdk")

# Criar servidor MCP usando SDK oficial
server = Server("omie-mcp-sdk")

# Cliente Omie global
omie_client = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Lista todas as ferramentas disponíveis usando SDK oficial"""
    
    return [
        types.Tool(
            name="testar_conexao",
            description="Testa conexão com a API do Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="consultar_categorias",
            description="Consulta categorias cadastradas no Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {
                        "type": "integer",
                        "description": "Número da página para paginação",
                        "default": 1
                    },
                    "registros_por_pagina": {
                        "type": "integer", 
                        "description": "Quantidade de registros por página",
                        "default": 50
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="consultar_departamentos",
            description="Consulta departamentos cadastrados no Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {
                        "type": "integer",
                        "description": "Número da página para paginação",
                        "default": 1
                    },
                    "registros_por_pagina": {
                        "type": "integer",
                        "description": "Quantidade de registros por página", 
                        "default": 50
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="consultar_tipos_documento",
            description="Consulta tipos de documento no Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "Código específico do tipo de documento (opcional)"
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="consultar_contas_pagar",
            description="Consulta contas a pagar no Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_inicio": {
                        "type": "string",
                        "description": "Data de início da consulta (DD/MM/AAAA)"
                    },
                    "data_fim": {
                        "type": "string", 
                        "description": "Data de fim da consulta (DD/MM/AAAA)"
                    },
                    "pagina": {
                        "type": "integer",
                        "description": "Número da página para paginação",
                        "default": 1
                    },
                    "registros_por_pagina": {
                        "type": "integer",
                        "description": "Quantidade de registros por página",
                        "default": 20
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="consultar_contas_receber",
            description="Consulta contas a receber no Omie ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_inicio": {
                        "type": "string",
                        "description": "Data de início da consulta (DD/MM/AAAA)"
                    },
                    "data_fim": {
                        "type": "string",
                        "description": "Data de fim da consulta (DD/MM/AAAA)"
                    },
                    "pagina": {
                        "type": "integer",
                        "description": "Número da página para paginação",
                        "default": 1
                    },
                    "registros_por_pagina": {
                        "type": "integer",
                        "description": "Quantidade de registros por página",
                        "default": 20
                    }
                },
                "required": []
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> List[types.TextContent]:
    """Executa uma ferramenta usando SDK oficial"""
    
    global omie_client
    
    # Inicializar cliente se necessário
    if omie_client is None:
        try:
            omie_client = OmieClient()
            logger.info("Cliente Omie inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Omie: {e}")
            return [types.TextContent(
                type="text",
                text=f"Erro ao inicializar cliente Omie: {str(e)}"
            )]
    
    # Processar argumentos
    args = arguments or {}
    
    try:
        if name == "testar_conexao":
            result = await omie_client.testar_conexao()
            
        elif name == "consultar_categorias":
            pagina = args.get("pagina", 1)
            registros_por_pagina = args.get("registros_por_pagina", 50)
            result = await omie_client.consultar_categorias(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
            
        elif name == "consultar_departamentos":
            pagina = args.get("pagina", 1)
            registros_por_pagina = args.get("registros_por_pagina", 50)
            result = await omie_client.consultar_departamentos(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
            
        elif name == "consultar_tipos_documento":
            codigo = args.get("codigo")
            result = await omie_client.consultar_tipos_documento(codigo=codigo)
            
        elif name == "consultar_contas_pagar":
            data_inicio = args.get("data_inicio")
            data_fim = args.get("data_fim")
            pagina = args.get("pagina", 1)
            registros_por_pagina = args.get("registros_por_pagina", 20)
            result = await omie_client.consultar_contas_pagar(
                data_inicio=data_inicio,
                data_fim=data_fim,
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
            
        elif name == "consultar_contas_receber":
            data_inicio = args.get("data_inicio")
            data_fim = args.get("data_fim")
            pagina = args.get("pagina", 1)
            registros_por_pagina = args.get("registros_por_pagina", 20)
            result = await omie_client.consultar_contas_receber(
                data_inicio=data_inicio,
                data_fim=data_fim,
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
            
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
        
        # Converter resultado para string se necessário
        if isinstance(result, dict):
            result_text = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            result_text = str(result)
            
        return [types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Erro ao executar {name}: {str(e)}"
        )]

async def main():
    """Função principal usando SDK oficial"""
    
    # Configurações de inicialização usando SDK
    init_options = InitializationOptions(
        server_name="omie-mcp-sdk",
        server_version="1.0.0",
        capabilities=types.ServerCapabilities(
            tools=types.ToolsCapability(),
        ),
    )
    
    # Executar servidor STDIO usando SDK oficial
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream, 
            init_options
        )

if __name__ == "__main__":
    import json
    asyncio.run(main())