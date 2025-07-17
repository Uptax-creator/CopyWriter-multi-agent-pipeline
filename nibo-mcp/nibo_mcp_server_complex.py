#!/usr/bin/env python3
"""
Servidor MCP para Nibo ERP - Versão específica para Claude Desktop
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configurar logging apenas para arquivo/stderr, não stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log para stderr, não stdout
    ]
)
logger = logging.getLogger("nibo-mcp-server")

# Importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.config import NiboConfig
    from src.core.nibo_client import NiboClient
    from src.tools.consultas import NiboConsultas
    from src.tools.clientes_fornecedores import NiboClientesFornecedores
    from src.tools.financeiro import NiboFinanceiro
    from src.tools.socios import NiboSocios
    from src.utils.compatibility import CompatibilityMapper
    logger.info("Módulos do Nibo importados com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Importar MCP
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
    import mcp.types as types
    logger.info("Biblioteca MCP importada com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar MCP: {e}")
    sys.exit(1)

# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

# Inicializar configuração base (sem empresa específica)
script_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(script_dir, "credentials.json")
base_config = NiboConfig(credentials_file=credentials_path)

# Variáveis globais para instâncias ativas
active_clients = {}
active_consultas = {}
active_clientes_fornecedores = {}
active_financeiro = {}
active_socios = {}

def get_or_create_client(company_key: str = None):
    """Obtém ou cria cliente para uma empresa específica"""
    if not company_key:
        company_key = base_config.credentials_manager.default_company
    
    if company_key not in active_clients:
        config = NiboConfig(company_key)
        if not config.is_configured():
            raise ValueError(f"Credenciais não configuradas para empresa '{company_key}'")
        
        client = NiboClient(config)
        active_clients[company_key] = client
        active_consultas[company_key] = NiboConsultas(client)
        active_clientes_fornecedores[company_key] = NiboClientesFornecedores(client)
        active_financeiro[company_key] = NiboFinanceiro(client)
        active_socios[company_key] = NiboSocios(client)
    
    return (
        active_clients[company_key],
        active_consultas[company_key],
        active_clientes_fornecedores[company_key],
        active_financeiro[company_key],
        active_socios[company_key]
    )

# Criar servidor MCP
server = Server("nibo-mcp")

# ============================================================================
# FERRAMENTAS MCP
# ============================================================================

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Lista todas as ferramentas disponíveis"""
    return [
        # Ferramentas de consulta
        Tool(
            name="consultar_clientes",
            description="Consulta clientes cadastrados no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "filtrar_por_nome": {"type": "string"},
                    "filtrar_por_documento": {"type": "string"}
                }
            }
        ),
        Tool(
            name="consultar_fornecedores",
            description="Consulta fornecedores cadastrados no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "filtrar_por_nome": {"type": "string"},
                    "filtrar_por_documento": {"type": "string"}
                }
            }
        ),
        Tool(
            name="consultar_contas_pagar",
            description="Consulta contas a pagar no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "filtrar_por_valor_maximo": {"type": "number"},
                    "filtrar_por_data_vencimento_inicial": {"type": "string"},
                    "filtrar_por_data_vencimento_final": {"type": "string"}
                }
            }
        ),
        Tool(
            name="consultar_contas_receber",
            description="Consulta contas a receber no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "filtrar_por_valor_maximo": {"type": "number"},
                    "filtrar_por_data_vencimento_inicial": {"type": "string"},
                    "filtrar_por_data_vencimento_final": {"type": "string"}
                }
            }
        ),
        Tool(
            name="consultar_categorias",
            description="Consulta categorias cadastradas no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500}
                }
            }
        ),
        Tool(
            name="consultar_centros_custo",
            description="Consulta centros de custo cadastrados no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500}
                }
            }
        ),
        # Ferramentas de criação
        Tool(
            name="incluir_cliente",
            description="Inclui um novo cliente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"}
                },
                "required": ["nome", "documento"]
            }
        ),
        Tool(
            name="incluir_fornecedor",
            description="Inclui um novo fornecedor no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"}
                },
                "required": ["nome", "documento"]
            }
        ),
        Tool(
            name="incluir_conta_pagar",
            description="Inclui uma nova conta a pagar no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "fornecedor_id": {"type": "string"},
                    "valor": {"type": "number"},
                    "data_vencimento": {"type": "string"},
                    "categoria_id": {"type": "string"},
                    "centro_custo_id": {"type": "string"},
                    "descricao": {"type": "string"},
                    "numero_documento": {"type": "string"}
                },
                "required": ["fornecedor_id", "valor", "data_vencimento"]
            }
        ),
        Tool(
            name="incluir_conta_receber",
            description="Inclui uma nova conta a receber no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "valor": {"type": "number"},
                    "data_vencimento": {"type": "string"},
                    "categoria_id": {"type": "string"},
                    "centro_custo_id": {"type": "string"},
                    "descricao": {"type": "string"},
                    "numero_documento": {"type": "string"}
                },
                "required": ["cliente_id", "valor", "data_vencimento"]
            }
        ),
        Tool(
            name="testar_conexao",
            description="Testa a conexão com a API do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional, usa padrão se não especificado)"}
                }
            }
        ),
        Tool(
            name="listar_empresas",
            description="Lista todas as empresas disponíveis no sistema",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="selecionar_empresa",
            description="Seleciona uma empresa para as operações seguintes",
            inputSchema={
                "type": "object",
                "properties": {
                    "empresa": {"type": "string", "description": "Chave da empresa"}
                },
                "required": ["empresa"]
            }
        ),
        Tool(
            name="info_empresa_atual",
            description="Mostra informações da empresa atualmente selecionada",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        # Ferramentas de alteração
        Tool(
            name="alterar_cliente",
            description="Altera um cliente existente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["cliente_id"]
            }
        ),
        Tool(
            name="alterar_fornecedor",
            description="Altera um fornecedor existente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "fornecedor_id": {"type": "string"},
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["fornecedor_id"]
            }
        ),
        Tool(
            name="alterar_conta_pagar",
            description="Altera uma conta a pagar existente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "conta_id": {"type": "string"},
                    "fornecedor_id": {"type": "string"},
                    "valor": {"type": "number"},
                    "data_vencimento": {"type": "string"},
                    "categoria_id": {"type": "string"},
                    "centro_custo_id": {"type": "string"},
                    "descricao": {"type": "string"},
                    "numero_documento": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["conta_id"]
            }
        ),
        Tool(
            name="alterar_conta_receber",
            description="Altera uma conta a receber existente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "conta_id": {"type": "string"},
                    "cliente_id": {"type": "string"},
                    "valor": {"type": "number"},
                    "data_vencimento": {"type": "string"},
                    "categoria_id": {"type": "string"},
                    "centro_custo_id": {"type": "string"},
                    "descricao": {"type": "string"},
                    "numero_documento": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["conta_id"]
            }
        ),
        # Ferramentas de exclusão
        Tool(
            name="excluir_conta_pagar",
            description="Exclui uma conta a pagar do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "conta_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["conta_id"]
            }
        ),
        Tool(
            name="excluir_conta_receber",
            description="Exclui uma conta a receber do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "conta_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["conta_id"]
            }
        ),
        # Ferramentas de exclusão de clientes/fornecedores
        Tool(
            name="excluir_cliente",
            description="Exclui um cliente do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["cliente_id"]
            }
        ),
        Tool(
            name="excluir_fornecedor",
            description="Exclui um fornecedor do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "fornecedor_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["fornecedor_id"]
            }
        ),
        # Ferramentas de Sócios (exclusiva do Nibo)
        Tool(
            name="consultar_socios",
            description="Consulta sócios cadastrados no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "filtrar_por_nome": {"type": "string"},
                    "filtrar_por_documento": {"type": "string"},
                    "filtrar_por_ativo": {"type": "boolean"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                }
            }
        ),
        Tool(
            name="incluir_socio",
            description="Inclui um novo sócio no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"},
                    "participacao_percentual": {"type": "number"},
                    "ativo": {"type": "boolean", "default": True},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["nome", "documento"]
            }
        ),
        Tool(
            name="alterar_socio",
            description="Altera um sócio existente no Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "socio_id": {"type": "string"},
                    "nome": {"type": "string"},
                    "documento": {"type": "string"},
                    "email": {"type": "string"},
                    "telefone": {"type": "string"},
                    "endereco": {"type": "object"},
                    "participacao_percentual": {"type": "number"},
                    "ativo": {"type": "boolean"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["socio_id"]
            }
        ),
        Tool(
            name="excluir_socio",
            description="Exclui um sócio do Nibo ERP",
            inputSchema={
                "type": "object",
                "properties": {
                    "socio_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["socio_id"]
            }
        ),
        # Ferramentas de consulta individual
        Tool(
            name="obter_cliente_por_id",
            description="Obtém um cliente específico por ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["cliente_id"]
            }
        ),
        Tool(
            name="obter_fornecedor_por_id",
            description="Obtém um fornecedor específico por ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "fornecedor_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["fornecedor_id"]
            }
        ),
        Tool(
            name="obter_socio_por_id",
            description="Obtém um sócio específico por ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "socio_id": {"type": "string"},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                },
                "required": ["socio_id"]
            }
        ),
        # Ferramentas de compatibilidade (aliases)
        Tool(
            name="consultar_departamentos",
            description="Consulta departamentos (alias para centros de custo - compatibilidade Omie)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50, "maximum": 500},
                    "empresa": {"type": "string", "description": "Chave da empresa (opcional)"}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Processa chamadas de ferramentas"""
    try:
        result = None
        
        # Ferramentas de gerenciamento de empresas
        if name == "listar_empresas":
            result = {
                "empresas": base_config.get_company_list(),
                "empresa_padrao": base_config.credentials_manager.default_company,
                "total_empresas": base_config.credentials_manager.get_company_count()
            }
        
        elif name == "selecionar_empresa":
            empresa = arguments.get("empresa")
            try:
                # Criar cliente para a empresa específica
                get_or_create_client(empresa)
                result = {
                    "success": True,
                    "message": f"Empresa '{empresa}' selecionada com sucesso",
                    "empresa_info": NiboConfig(empresa).get_current_company_info()
                }
            except Exception as e:
                result = {
                    "success": False,
                    "message": f"Erro ao selecionar empresa '{empresa}': {str(e)}"
                }
        
        elif name == "info_empresa_atual":
            empresa_padrao = base_config.credentials_manager.default_company
            if empresa_padrao:
                config = NiboConfig(empresa_padrao)
                result = config.get_current_company_info()
            else:
                result = {"error": "Nenhuma empresa padrão configurada"}
        
        elif name == "testar_conexao":
            empresa = arguments.get("empresa")
            client, _, _, _ = get_or_create_client(empresa)
            result = await client.testar_conexao()
            
        else:
            # Para todas as outras ferramentas, usar empresa especificada ou padrão
            empresa = arguments.pop("empresa", None)  # Remove empresa dos argumentos
            client, consultas, clientes_fornecedores, financeiro, socios = get_or_create_client(empresa)
            
            # Resolver aliases de compatibilidade
            original_name = name
            name = CompatibilityMapper.resolve_tool_name(name)
            
            # Ferramentas de consulta
            if name == "consultar_clientes":
                result = await consultas.consultar_clientes(**arguments)
            elif name == "consultar_fornecedores":
                result = await consultas.consultar_fornecedores(**arguments)
            elif name == "consultar_contas_pagar":
                result = await consultas.consultar_contas_pagar(**arguments)
            elif name == "consultar_contas_receber":
                result = await consultas.consultar_contas_receber(**arguments)
            elif name == "consultar_categorias":
                result = await consultas.consultar_categorias(**arguments)
            elif name == "consultar_centros_custo":
                result = await consultas.consultar_centros_custo(**arguments)
                
            # Ferramentas de criação
            elif name == "incluir_cliente":
                result = await clientes_fornecedores.incluir_cliente(**arguments)
            elif name == "incluir_fornecedor":
                result = await clientes_fornecedores.incluir_fornecedor(**arguments)
            elif name == "incluir_conta_pagar":
                result = await financeiro.incluir_conta_pagar(**arguments)
            elif name == "incluir_conta_receber":
                result = await financeiro.incluir_conta_receber(**arguments)
                
            # Ferramentas de alteração
            elif name == "alterar_cliente":
                result = await clientes_fornecedores.alterar_cliente(**arguments)
            elif name == "alterar_fornecedor":
                result = await clientes_fornecedores.alterar_fornecedor(**arguments)
            elif name == "alterar_conta_pagar":
                result = await financeiro.alterar_conta_pagar(**arguments)
            elif name == "alterar_conta_receber":
                result = await financeiro.alterar_conta_receber(**arguments)
                
            # Ferramentas de exclusão
            elif name == "excluir_conta_pagar":
                result = await financeiro.excluir_conta_pagar(**arguments)
            elif name == "excluir_conta_receber":
                result = await financeiro.excluir_conta_receber(**arguments)
                
            # Ferramentas de exclusão de clientes/fornecedores
            elif name == "excluir_cliente":
                result = await clientes_fornecedores.excluir_cliente(**arguments)
            elif name == "excluir_fornecedor":
                result = await clientes_fornecedores.excluir_fornecedor(**arguments)
                
            # Ferramentas de Sócios
            elif name == "consultar_socios":
                result = await socios.consultar_socios(**arguments)
            elif name == "incluir_socio":
                result = await socios.incluir_socio(**arguments)
            elif name == "alterar_socio":
                result = await socios.alterar_socio(**arguments)
            elif name == "excluir_socio":
                result = await socios.excluir_socio(**arguments)
                
            # Ferramentas de consulta individual
            elif name == "obter_cliente_por_id":
                result = await clientes_fornecedores.obter_cliente_por_id(**arguments)
            elif name == "obter_fornecedor_por_id":
                result = await clientes_fornecedores.obter_fornecedor_por_id(**arguments)
            elif name == "obter_socio_por_id":
                result = await socios.obter_socio_por_id(**arguments)
                
            # Aliases de compatibilidade
            elif original_name == "consultar_departamentos":
                # Alias para consultar_centros_custo
                result = await consultas.consultar_centros_custo(**arguments)
                # Adicionar nota de compatibilidade
                if isinstance(result, dict):
                    result["_compatibility_note"] = "Esta consulta foi redirecionada de 'departamentos' para 'centros de custo' para compatibilidade com Omie"
                
            else:
                raise ValueError(f"Ferramenta desconhecida: {name} (original: {original_name})")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {name}: {e}")
        error_result = {
            "error": True,
            "message": str(e),
            "tool": name,
            "timestamp": datetime.now().isoformat()
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2, ensure_ascii=False))]

# ============================================================================
# EXECUÇÃO DO SERVIDOR
# ============================================================================

async def main():
    """Função principal do servidor"""
    # Importar e usar o driver stdio
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nibo-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    logger.info("Iniciando Nibo MCP Server...")
    asyncio.run(main())