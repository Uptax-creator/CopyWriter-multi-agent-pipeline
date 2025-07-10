#!/usr/bin/env python3
"""
Servidor MCP para Omie ERP - Versão específica para Claude Desktop
Esta versão não imprime mensagens de log na stdout para evitar conflitos com o protocolo MCP
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict

# Configurar logging apenas para arquivo/stderr, não stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log para stderr, não stdout
    ]
)
logger = logging.getLogger("omie-mcp-server")

# Importar módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.models import *
    from modules.omie_client import OmieClient
    from modules.handlers import OmieHandlers
    from modules.validators import OmieValidators
    logger.info("Módulos importados com sucesso")
except ImportError:
    # Fallback para versão monolítica
    logger.info("Usando versão monolítica (módulos não encontrados)")
    pass

# ============================================================================
# CONFIGURAÇÕES - SEM PRINT NA STDOUT
# ============================================================================

# Credenciais do Omie - prioridade: variáveis de ambiente > arquivo credentials.json
OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")

# Se não há variáveis de ambiente, tentar carregar do arquivo credentials.json
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    try:
        credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
                OMIE_APP_KEY = OMIE_APP_KEY or credentials.get("app_key")
                OMIE_APP_SECRET = OMIE_APP_SECRET or credentials.get("app_secret")
                logger.info(f"Credenciais carregadas do arquivo: {credentials_path}")
        else:
            logger.warning(f"Arquivo credentials.json não encontrado em: {credentials_path}")
    except Exception as e:
        logger.error(f"Erro ao carregar credentials.json: {e}")

# Verificar se temos credenciais válidas
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    logger.error("Credenciais Omie não encontradas! Configure OMIE_APP_KEY e OMIE_APP_SECRET")
    sys.exit(1)

logger.info(f"Credenciais carregadas: {OMIE_APP_KEY[:8]}...****")

# ============================================================================
# CLIENTE E HANDLERS
# ============================================================================

try:
    from modules.omie_client import OmieClient
    from modules.handlers import OmieHandlers
    omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)
    omie_handlers = OmieHandlers(omie_client)
    logger.info("Usando versão modular")
except ImportError:
    # Fallback para versão monolítica
    logger.info("Usando cliente inline")
    
    import httpx
    from fastapi import HTTPException
    
    class SimpleOmieClient:
        def __init__(self, app_key: str, app_secret: str):
            self.app_key = app_key
            self.app_secret = app_secret
            self.base_url = "https://app.omie.com.br/api/v1"
            
        async def _make_request(self, endpoint: str, call: str, params: Dict) -> Dict:
            payload = {
                "call": call,
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "param": [params]
            }
            
            url = f"{self.base_url}/{endpoint}/"
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code != 200:
                        raise HTTPException(status_code=response.status_code, detail=response.text)
                    
                    result = response.json()
                    
                    if isinstance(result, dict) and "faultstring" in result:
                        error_msg = result.get("faultstring", "Erro Omie")
                        raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                    
                    return result
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
        
        async def consultar_categorias(self, params: Dict = None) -> Dict:
            if params is None:
                params = {"pagina": 1, "registros_por_pagina": 50}
            return await self._make_request("geral/categorias", "ListarCategorias", params)
        
        async def consultar_departamentos(self, params: Dict = None) -> Dict:
            if params is None:
                params = {"pagina": 1, "registros_por_pagina": 50}
            return await self._make_request("geral/departamentos", "ListarDepartamentos", params)
        
        async def consultar_tipos_documento(self, params: Dict = None) -> Dict:
            if params is None:
                params = {"codigo": ""}
            return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", params)
        
        async def consultar_contas_pagar(self, params: Dict) -> Dict:
            return await self._make_request("financas/contapagar", "ListarContasPagar", params)
        
        async def consultar_contas_receber(self, params: Dict) -> Dict:
            return await self._make_request("financas/contareceber", "ListarContasReceber", params)
    
    omie_client = SimpleOmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)
    omie_handlers = None

# ============================================================================
# PROTOCOLO MCP
# ============================================================================

class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias de receita/despesa do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Número da página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Número da página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_tipos_documento",
                "description": "Consulta tipos de documentos do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor"},
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    }
                }
            },
            {
                "name": "consultar_contas_receber",
                "description": "Consulta contas a receber do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente"},
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    }
                }
            },
            {
                "name": "cadastrar_cliente_fornecedor",
                "description": "Cadastra cliente ou fornecedor no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "razao_social": {"type": "string", "description": "Razão social"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                        "email": {"type": "string", "description": "Email"},
                        "tipo_cliente": {"type": "string", "description": "Tipo: cliente ou fornecedor"}
                    },
                    "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"]
                }
            },
            {
                "name": "criar_conta_pagar",
                "description": "Cria uma nova conta a pagar no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cnpj_cpf_fornecedor": {"type": "string", "description": "CNPJ/CPF do fornecedor"},
                        "razao_social_fornecedor": {"type": "string", "description": "Razão social do fornecedor"},
                        "numero_documento": {"type": "string", "description": "Número do documento"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                        "valor_documento": {"type": "number", "description": "Valor do documento"},
                        "codigo_categoria": {"type": "string", "description": "Código da categoria"}
                    },
                    "required": ["cnpj_cpf_fornecedor", "numero_documento", "data_vencimento", "valor_documento", "codigo_categoria"]
                }
            },
            {
                "name": "atualizar_conta_pagar",
                "description": "Atualiza uma conta a pagar existente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_lancamento": {"type": "integer", "description": "Código do lançamento"},
                        "valor_documento": {"type": "number", "description": "Novo valor do documento"},
                        "data_vencimento": {"type": "string", "description": "Nova data vencimento (DD/MM/AAAA)"}
                    },
                    "required": ["codigo_lancamento"]
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_fornecedores",
                "description": "Consulta fornecedores cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "incluir_cliente",
                "description": "Inclui novo cliente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "razao_social": {"type": "string", "description": "Razão social"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                        "email": {"type": "string", "description": "Email"},
                        "telefone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["razao_social", "cnpj_cpf", "email"]
                }
            },
            {
                "name": "incluir_fornecedor",
                "description": "Inclui novo fornecedor no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "razao_social": {"type": "string", "description": "Razão social"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                        "email": {"type": "string", "description": "Email"},
                        "telefone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["razao_social", "cnpj_cpf", "email"]
                }
            },
            {
                "name": "alterar_cliente",
                "description": "Altera cliente existente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do cliente"},
                        "razao_social": {"type": "string", "description": "Nova razão social"},
                        "email": {"type": "string", "description": "Novo email"},
                        "telefone": {"type": "string", "description": "Novo telefone"}
                    },
                    "required": ["codigo_cliente_omie"]
                }
            },
            {
                "name": "alterar_fornecedor",
                "description": "Altera fornecedor existente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do fornecedor"},
                        "razao_social": {"type": "string", "description": "Nova razão social"},
                        "email": {"type": "string", "description": "Novo email"},
                        "telefone": {"type": "string", "description": "Novo telefone"}
                    },
                    "required": ["codigo_cliente_omie"]
                }
            },
            {
                "name": "incluir_conta_pagar",
                "description": "Inclui nova conta a pagar no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor"},
                        "numero_documento": {"type": "string", "description": "Número do documento"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                        "valor_documento": {"type": "number", "description": "Valor do documento"},
                        "codigo_categoria": {"type": "string", "description": "Código da categoria"}
                    },
                    "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                }
            },
            {
                "name": "alterar_conta_pagar",
                "description": "Altera conta a pagar existente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento"},
                        "valor_documento": {"type": "number", "description": "Novo valor"},
                        "data_vencimento": {"type": "string", "description": "Nova data vencimento"}
                    },
                    "required": ["codigo_lancamento_omie"]
                }
            },
            {
                "name": "excluir_conta_pagar",
                "description": "Exclui conta a pagar do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento"}
                    },
                    "required": ["codigo_lancamento_omie"]
                }
            },
            {
                "name": "incluir_conta_receber",
                "description": "Inclui nova conta a receber no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente"},
                        "numero_documento": {"type": "string", "description": "Número do documento"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                        "valor_documento": {"type": "number", "description": "Valor do documento"}
                    },
                    "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                }
            },
            {
                "name": "alterar_conta_receber",
                "description": "Altera conta a receber existente no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento"},
                        "valor_documento": {"type": "number", "description": "Novo valor"},
                        "data_vencimento": {"type": "string", "description": "Nova data vencimento"}
                    },
                    "required": ["codigo_lancamento_omie"]
                }
            },
            {
                "name": "excluir_conta_receber",
                "description": "Exclui conta a receber do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento"}
                    },
                    "required": ["codigo_lancamento_omie"]
                }
            }
        ]
    
    def send_response(self, response):
        """Envia resposta MCP via stdout"""
        print(json.dumps(response, ensure_ascii=False), flush=True)
    
    async def handle_request(self, request):
        """Processa requisição MCP"""
        try:
            if request.get("method") == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "omie-mcp-server", "version": "1.0.0"}
                    }
                }
            
            elif request.get("method") == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": self.tools}
                }
            
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Método não suportado: {request.get('method')}"}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Chama ferramenta específica"""
        try:
            if omie_handlers:
                # Usar versão modular
                if tool_name == "consultar_categorias":
                    return await omie_handlers.handle_consultar_categorias(arguments)
                elif tool_name == "consultar_departamentos":
                    return await omie_handlers.handle_consultar_departamentos(arguments)
                elif tool_name == "consultar_tipos_documento":
                    return await omie_handlers.handle_consultar_tipos_documento(arguments)
                elif tool_name == "consultar_contas_pagar":
                    return await omie_handlers.handle_consultar_contas_pagar(arguments)
                elif tool_name == "consultar_contas_receber":
                    return await omie_handlers.handle_consultar_contas_receber(arguments)
                elif tool_name == "cadastrar_cliente_fornecedor":
                    return await omie_handlers.handle_cadastrar_cliente_fornecedor(arguments)
                elif tool_name == "criar_conta_pagar":
                    return await omie_handlers.handle_criar_conta_pagar(arguments)
                elif tool_name == "atualizar_conta_pagar":
                    return await omie_handlers.handle_atualizar_conta_pagar(arguments)
                elif tool_name == "consultar_clientes":
                    return await omie_handlers.handle_consultar_clientes(arguments)
                elif tool_name == "consultar_fornecedores":
                    return await omie_handlers.handle_consultar_fornecedores(arguments)
                elif tool_name == "incluir_cliente":
                    return await omie_handlers.handle_incluir_cliente(arguments)
                elif tool_name == "incluir_fornecedor":
                    return await omie_handlers.handle_incluir_fornecedor(arguments)
                elif tool_name == "alterar_cliente":
                    return await omie_handlers.handle_alterar_cliente(arguments)
                elif tool_name == "alterar_fornecedor":
                    return await omie_handlers.handle_alterar_fornecedor(arguments)
                elif tool_name == "incluir_conta_pagar":
                    return await omie_handlers.handle_incluir_conta_pagar(arguments)
                elif tool_name == "alterar_conta_pagar":
                    return await omie_handlers.handle_alterar_conta_pagar(arguments)
                elif tool_name == "excluir_conta_pagar":
                    return await omie_handlers.handle_excluir_conta_pagar(arguments)
                elif tool_name == "incluir_conta_receber":
                    return await omie_handlers.handle_incluir_conta_receber(arguments)
                elif tool_name == "alterar_conta_receber":
                    return await omie_handlers.handle_alterar_conta_receber(arguments)
                elif tool_name == "excluir_conta_receber":
                    return await omie_handlers.handle_excluir_conta_receber(arguments)
            else:
                # Usar versão inline
                if tool_name == "consultar_categorias":
                    return await self.handle_consultar_categorias(arguments)
                elif tool_name == "consultar_departamentos":
                    return await self.handle_consultar_departamentos(arguments)
                elif tool_name == "consultar_tipos_documento":
                    return await self.handle_consultar_tipos_documento(arguments)
                elif tool_name == "consultar_contas_pagar":
                    return await self.handle_consultar_contas_pagar(arguments)
                elif tool_name == "consultar_contas_receber":
                    return await self.handle_consultar_contas_receber(arguments)
                elif tool_name == "cadastrar_cliente_fornecedor":
                    return await self.handle_cadastrar_cliente_fornecedor(arguments)
                elif tool_name == "criar_conta_pagar":
                    return await self.handle_criar_conta_pagar(arguments)
                elif tool_name == "atualizar_conta_pagar":
                    return await self.handle_atualizar_conta_pagar(arguments)
                elif tool_name == "consultar_clientes":
                    return await self.handle_consultar_clientes(arguments)
                elif tool_name == "consultar_fornecedores":
                    return await self.handle_consultar_fornecedores(arguments)
                elif tool_name == "incluir_cliente":
                    return await self.handle_incluir_cliente(arguments)
                elif tool_name == "incluir_fornecedor":
                    return await self.handle_incluir_fornecedor(arguments)
                elif tool_name == "alterar_cliente":
                    return await self.handle_alterar_cliente(arguments)
                elif tool_name == "alterar_fornecedor":
                    return await self.handle_alterar_fornecedor(arguments)
                elif tool_name == "incluir_conta_pagar":
                    return await self.handle_incluir_conta_pagar(arguments)
                elif tool_name == "alterar_conta_pagar":
                    return await self.handle_alterar_conta_pagar(arguments)
                elif tool_name == "excluir_conta_pagar":
                    return await self.handle_excluir_conta_pagar(arguments)
                elif tool_name == "incluir_conta_receber":
                    return await self.handle_incluir_conta_receber(arguments)
                elif tool_name == "alterar_conta_receber":
                    return await self.handle_alterar_conta_receber(arguments)
                elif tool_name == "excluir_conta_receber":
                    return await self.handle_excluir_conta_receber(arguments)
            
            raise ValueError(f"Ferramenta não encontrada: {tool_name}")
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return f"Erro ao executar {tool_name}: {str(e)}"
    
    async def handle_consultar_categorias(self, args: Dict) -> str:
        """Handler inline para consultar categorias"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 50)}
        resultado = await omie_client.consultar_categorias(params)
        categorias = resultado.get("categoria_cadastro", [])
        
        if categorias:
            lista_categorias = []
            for categoria in categorias:
                codigo = categoria.get("codigo", "N/A")
                descricao = categoria.get("descricao", "N/A")
                lista_categorias.append(f"• {codigo} - {descricao}")
            
            return f"Categorias encontradas: {len(categorias)}\n\n" + "\n".join(lista_categorias)
        else:
            return "Nenhuma categoria encontrada"
    
    async def handle_consultar_departamentos(self, args: Dict) -> str:
        """Handler inline para consultar departamentos"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 50)}
        resultado = await omie_client.consultar_departamentos(params)
        departamentos = resultado.get("departamentos", [])
        
        if departamentos:
            lista_departamentos = []
            for departamento in departamentos:
                codigo = departamento.get("codigo", "N/A")
                descricao = departamento.get("descricao", "N/A")
                estrutura = departamento.get("estrutura", "N/A")
                lista_departamentos.append(f"• {codigo} - {descricao} ({estrutura})")
            
            return f"Departamentos encontrados: {len(departamentos)}\n\n" + "\n".join(lista_departamentos)
        else:
            return "Nenhum departamento encontrado"
    
    async def handle_consultar_tipos_documento(self, args: Dict) -> str:
        """Handler inline para consultar tipos de documento"""
        resultado = await omie_client.consultar_tipos_documento({})
        tipos = resultado.get("tipo_documento_cadastro", [])
        
        if tipos:
            lista_tipos = []
            for tipo in tipos:
                codigo = tipo.get("codigo", "N/A")
                descricao = tipo.get("descricao", "N/A")
                lista_tipos.append(f"• {codigo} - {descricao}")
            
            return f"Tipos de documento encontrados: {len(tipos)}\n\n" + "\n".join(lista_tipos)
        else:
            return "Nenhum tipo de documento encontrado"
    
    async def handle_consultar_contas_pagar(self, args: Dict) -> str:
        """Handler inline para consultar contas a pagar"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 20)}
        
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await omie_client.consultar_contas_pagar(params)
        contas = resultado.get("conta_pagar_cadastro", [])
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"Contas a Pagar encontradas: {len(contas)}\n\n" + "\n".join(lista_contas) + f"\n\nTotal (10 primeiras): R$ {total_valor:,.2f}"
        else:
            return "Nenhuma conta a pagar encontrada"
    
    async def handle_consultar_contas_receber(self, args: Dict) -> str:
        """Handler inline para consultar contas a receber"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 20)}
        
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await omie_client.consultar_contas_receber(params)
        contas = resultado.get("conta_receber_cadastro", [])
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"Contas a Receber encontradas: {len(contas)}\n\n" + "\n".join(lista_contas) + f"\n\nTotal (10 primeiras): R$ {total_valor:,.2f}"
        else:
            return "Nenhuma conta a receber encontrada"
    
    async def handle_cadastrar_cliente_fornecedor(self, args: Dict) -> str:
        """Handler inline para cadastrar cliente/fornecedor"""
        dados = {
            "razao_social": args["razao_social"],
            "cnpj_cpf": args["cnpj_cpf"],
            "email": args["email"],
            "tipo_cliente": args["tipo_cliente"]
        }
        
        resultado = await omie_client.cadastrar_cliente_fornecedor(dados)
        
        if resultado.get("codigo_cliente_omie"):
            return f"✅ {args['tipo_cliente'].title()} cadastrado com sucesso!\n\nCódigo: {resultado['codigo_cliente_omie']}\nRazão Social: {args['razao_social']}\nCNPJ/CPF: {args['cnpj_cpf']}"
        else:
            return f"❌ Erro ao cadastrar {args['tipo_cliente']}: {resultado}"
    
    async def handle_criar_conta_pagar(self, args: Dict) -> str:
        """Handler inline para criar conta a pagar"""
        dados = {
            "cnpj_cpf": args["cnpj_cpf_fornecedor"],
            "razao_social": args["razao_social_fornecedor"],
            "numero_documento": args["numero_documento"],
            "data_vencimento": args["data_vencimento"],
            "valor_documento": args["valor_documento"],
            "codigo_categoria": args["codigo_categoria"]
        }
        
        resultado = await omie_client.criar_conta_pagar(dados)
        
        if resultado.get("codigo_lancamento_omie"):
            return f"✅ Conta a pagar criada com sucesso!\n\nCódigo: {resultado['codigo_lancamento_omie']}\nDocumento: {args['numero_documento']}\nValor: R$ {args['valor_documento']:,.2f}\nVencimento: {args['data_vencimento']}"
        else:
            return f"❌ Erro ao criar conta a pagar: {resultado}"
    
    async def handle_atualizar_conta_pagar(self, args: Dict) -> str:
        """Handler inline para atualizar conta a pagar"""
        dados = {
            "codigo_lancamento_omie": args["codigo_lancamento"]
        }
        
        if args.get("valor_documento"):
            dados["valor_documento"] = args["valor_documento"]
        if args.get("data_vencimento"):
            dados["data_vencimento"] = args["data_vencimento"]
        
        resultado = await omie_client.atualizar_conta_pagar(dados)
        
        if resultado.get("codigo_lancamento_omie"):
            return f"✅ Conta a pagar atualizada com sucesso!\n\nCódigo: {resultado['codigo_lancamento_omie']}"
        else:
            return f"❌ Erro ao atualizar conta a pagar: {resultado}"

# ============================================================================
# MAIN LOOP
# ============================================================================

async def main():
    """Loop principal do servidor MCP"""
    server = MCPServer()
    logger.info("Servidor MCP iniciado")
    
    # Ler requisições da stdin
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            logger.info(f"Requisição recebida: {request.get('method')}")
            
            response = await server.handle_request(request)
            server.send_response(response)
            
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON")
        except KeyboardInterrupt:
            logger.info("Servidor interrompido")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")

if __name__ == "__main__":
    asyncio.run(main())