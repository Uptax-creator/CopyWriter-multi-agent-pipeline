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
        
        async def consultar_cliente_por_codigo(self, params: Dict) -> Dict:
            return await self._make_request("geral/clientes", "ConsultarCliente", params)
        
        async def consultar_fornecedor_por_codigo(self, params: Dict) -> Dict:
            return await self._make_request("geral/clientes", "ConsultarCliente", params)
        
        async def buscar_dados_contato_cliente(self, params: Dict) -> Dict:
            return await self._make_request("geral/clientes", "ConsultarCliente", params)
        
        async def buscar_dados_contato_fornecedor(self, params: Dict) -> Dict:
            return await self._make_request("geral/clientes", "ConsultarCliente", params)
        
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
            },
            {
                "name": "consultar_cliente_por_codigo",
                "description": "Consulta cliente específico pelo código no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do cliente no Omie"},
                        "codigo_cliente_integracao": {"type": "string", "description": "Código de integração do cliente"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF do cliente"}
                    }
                }
            },
            {
                "name": "consultar_fornecedor_por_codigo",
                "description": "Consulta fornecedor específico pelo código no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do fornecedor no Omie"},
                        "codigo_cliente_integracao": {"type": "string", "description": "Código de integração do fornecedor"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF do fornecedor"}
                    }
                }
            },
            {
                "name": "buscar_dados_contato_cliente",
                "description": "Busca dados de contato específicos do cliente (nome, email, telefone, endereço)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do cliente no Omie"},
                        "codigo_cliente_integracao": {"type": "string", "description": "Código de integração do cliente"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF do cliente"}
                    }
                }
            },
            {
                "name": "buscar_dados_contato_fornecedor",
                "description": "Busca dados de contato específicos do fornecedor (nome, email, telefone, endereço)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "integer", "description": "Código do fornecedor no Omie"},
                        "codigo_cliente_integracao": {"type": "string", "description": "Código de integração do fornecedor"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF do fornecedor"}
                    }
                }
            },
            {
                "name": "relatorio_contas_receber_detalhado",
                "description": "Relatório detalhado de contas a receber por status, clientes, categorias e departamentos",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "status": {"type": "string", "description": "Status: vencido, aberto, recebido, cancelado"},
                        "codigo_cliente": {"type": "integer", "description": "Código do cliente"},
                        "codigo_categoria": {"type": "string", "description": "Código da categoria"},
                        "codigo_departamento": {"type": "string", "description": "Código do departamento"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "relatorio_contas_pagar_detalhado",
                "description": "Relatório detalhado de contas a pagar por status, fornecedores, categorias e departamentos",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "status": {"type": "string", "description": "Status: vencido, aberto, pago, cancelado"},
                        "codigo_fornecedor": {"type": "integer", "description": "Código do fornecedor"},
                        "codigo_categoria": {"type": "string", "description": "Código da categoria"},
                        "codigo_departamento": {"type": "string", "description": "Código do departamento"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_contas_receber_com_cliente_detalhado",
                "description": "Consulta contas a receber com dados completos do cliente (nome, email, telefone, endereço) em uma única chamada",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "status": {"type": "array", "items": {"type": "string", "enum": ["ABERTO", "A_VENCER", "VENCIDO", "RECEBIDO", "LIQUIDADO", "CANCELADO"]}, "description": "Status das contas (pode ser múltiplos)"},
                        "codigo_cliente": {"type": "integer", "description": "Código específico do cliente"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20},
                        "campos_cliente": {"type": "array", "items": {"type": "string", "enum": ["nome", "email", "telefone", "endereco", "cnpj_cpf", "nome_fantasia"]}, "description": "Campos do cliente a exibir", "default": ["nome", "email", "telefone"]},
                        "campos_conta": {"type": "array", "items": {"type": "string", "enum": ["numero_documento", "valor", "vencimento", "status", "categoria", "observacao"]}, "description": "Campos da conta a exibir", "default": ["numero_documento", "valor", "vencimento", "status"]},
                        "formato_saida": {"type": "string", "enum": ["detalhado", "resumido", "tabela"], "description": "Formato do resultado", "default": "detalhado"}
                    }
                }
            },
            {
                "name": "consultar_contas_pagar_com_fornecedor_detalhado",
                "description": "Consulta contas a pagar com dados completos do fornecedor (nome, email, telefone, endereço) em uma única chamada",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "status": {"type": "array", "items": {"type": "string", "enum": ["ABERTO", "A_VENCER", "VENCIDO", "PAGO", "LIQUIDADO", "CANCELADO", "AGENDADO"]}, "description": "Status das contas (pode ser múltiplos)"},
                        "codigo_fornecedor": {"type": "integer", "description": "Código específico do fornecedor"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20},
                        "campos_fornecedor": {"type": "array", "items": {"type": "string", "enum": ["nome", "email", "telefone", "endereco", "cnpj_cpf", "nome_fantasia"]}, "description": "Campos do fornecedor a exibir", "default": ["nome", "email", "telefone"]},
                        "campos_conta": {"type": "array", "items": {"type": "string", "enum": ["numero_documento", "valor", "vencimento", "status", "categoria", "observacao"]}, "description": "Campos da conta a exibir", "default": ["numero_documento", "valor", "vencimento", "status"]},
                        "formato_saida": {"type": "string", "enum": ["detalhado", "resumido", "tabela"], "description": "Formato do resultado", "default": "detalhado"}
                    }
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
                elif tool_name == "consultar_cliente_por_codigo":
                    return await omie_handlers.handle_consultar_cliente_por_codigo(arguments)
                elif tool_name == "consultar_fornecedor_por_codigo":
                    return await omie_handlers.handle_consultar_fornecedor_por_codigo(arguments)
                elif tool_name == "buscar_dados_contato_cliente":
                    return await omie_handlers.handle_buscar_dados_contato_cliente(arguments)
                elif tool_name == "buscar_dados_contato_fornecedor":
                    return await omie_handlers.handle_buscar_dados_contato_fornecedor(arguments)
                elif tool_name == "relatorio_contas_receber_detalhado":
                    return await omie_handlers.handle_relatorio_contas_receber_detalhado(arguments)
                elif tool_name == "relatorio_contas_pagar_detalhado":
                    return await omie_handlers.handle_relatorio_contas_pagar_detalhado(arguments)
                elif tool_name == "consultar_contas_receber_com_cliente_detalhado":
                    return await omie_handlers.handle_consultar_contas_receber_com_cliente_detalhado(arguments)
                elif tool_name == "consultar_contas_pagar_com_fornecedor_detalhado":
                    return await omie_handlers.handle_consultar_contas_pagar_com_fornecedor_detalhado(arguments)
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
                elif tool_name == "consultar_cliente_por_codigo":
                    return await self.handle_consultar_cliente_por_codigo(arguments)
                elif tool_name == "consultar_fornecedor_por_codigo":
                    return await self.handle_consultar_fornecedor_por_codigo(arguments)
                elif tool_name == "buscar_dados_contato_cliente":
                    return await self.handle_buscar_dados_contato_cliente(arguments)
                elif tool_name == "buscar_dados_contato_fornecedor":
                    return await self.handle_buscar_dados_contato_fornecedor(arguments)
                elif tool_name == "relatorio_contas_receber_detalhado":
                    return await self.handle_relatorio_contas_receber_detalhado(arguments)
                elif tool_name == "relatorio_contas_pagar_detalhado":
                    return await self.handle_relatorio_contas_pagar_detalhado(arguments)
                elif tool_name == "consultar_contas_receber_com_cliente_detalhado":
                    return await self.handle_consultar_contas_receber_com_cliente_detalhado(arguments)
                elif tool_name == "consultar_contas_pagar_com_fornecedor_detalhado":
                    return await self.handle_consultar_contas_pagar_com_fornecedor_detalhado(arguments)
            
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
    
    async def handle_consultar_cliente_por_codigo(self, args: Dict) -> str:
        """Handler inline para consultar cliente por código"""
        resultado = await omie_client.consultar_cliente_por_codigo(args)
        
        if resultado:
            nome = resultado.get("razao_social", "N/A")
            codigo = resultado.get("codigo_cliente_omie", "N/A")
            cnpj_cpf = resultado.get("cnpj_cpf", "N/A")
            email = resultado.get("email", "N/A")
            telefone = resultado.get("telefone1_numero", "N/A")
            
            return f"✅ Cliente encontrado:\n\nCódigo: {codigo}\nRazão Social: {nome}\nCNPJ/CPF: {cnpj_cpf}\nEmail: {email}\nTelefone: {telefone}"
        else:
            return "❌ Cliente não encontrado"
    
    async def handle_consultar_fornecedor_por_codigo(self, args: Dict) -> str:
        """Handler inline para consultar fornecedor por código"""
        resultado = await omie_client.consultar_fornecedor_por_codigo(args)
        
        if resultado:
            nome = resultado.get("razao_social", "N/A")
            codigo = resultado.get("codigo_cliente_omie", "N/A")
            cnpj_cpf = resultado.get("cnpj_cpf", "N/A")
            email = resultado.get("email", "N/A")
            telefone = resultado.get("telefone1_numero", "N/A")
            
            return f"✅ Fornecedor encontrado:\n\nCódigo: {codigo}\nRazão Social: {nome}\nCNPJ/CPF: {cnpj_cpf}\nEmail: {email}\nTelefone: {telefone}"
        else:
            return "❌ Fornecedor não encontrado"
    
    async def handle_buscar_dados_contato_cliente(self, args: Dict) -> str:
        """Handler inline para buscar dados de contato do cliente"""
        resultado = await omie_client.buscar_dados_contato_cliente(args)
        
        if resultado:
            nome = resultado.get("razao_social", "N/A")
            nome_fantasia = resultado.get("nome_fantasia", "N/A")
            email = resultado.get("email", "N/A")
            email_nfe = resultado.get("email_nfe", "N/A")
            
            # Telefones
            telefone1 = resultado.get("telefone1_numero", "N/A")
            telefone2 = resultado.get("telefone2_numero", "N/A")
            
            # Endereço
            endereco = resultado.get("endereco", "N/A")
            numero = resultado.get("numero_endereco", "N/A")
            complemento = resultado.get("complemento_endereco", "N/A")
            bairro = resultado.get("bairro", "N/A")
            cidade = resultado.get("cidade", "N/A")
            estado = resultado.get("estado", "N/A")
            cep = resultado.get("cep", "N/A")
            
            return f"✅ Dados de contato do cliente:\n\n📝 Nome completo: {nome}\n🏪 Nome fantasia: {nome_fantasia}\n\n📧 Emails:\n• Principal: {email}\n• NFe: {email_nfe}\n\n📞 Telefones:\n• Principal: {telefone1}\n• Secundário: {telefone2}\n\n🏠 Endereço:\n{endereco}, {numero} {complemento}\n{bairro} - {cidade}/{estado}\nCEP: {cep}"
        else:
            return "❌ Dados de contato não encontrados"
    
    async def handle_buscar_dados_contato_fornecedor(self, args: Dict) -> str:
        """Handler inline para buscar dados de contato do fornecedor"""
        resultado = await omie_client.buscar_dados_contato_fornecedor(args)
        
        if resultado:
            nome = resultado.get("razao_social", "N/A")
            nome_fantasia = resultado.get("nome_fantasia", "N/A")
            email = resultado.get("email", "N/A")
            email_nfe = resultado.get("email_nfe", "N/A")
            
            # Telefones
            telefone1 = resultado.get("telefone1_numero", "N/A")
            telefone2 = resultado.get("telefone2_numero", "N/A")
            
            # Endereço
            endereco = resultado.get("endereco", "N/A")
            numero = resultado.get("numero_endereco", "N/A")
            complemento = resultado.get("complemento_endereco", "N/A")
            bairro = resultado.get("bairro", "N/A")
            cidade = resultado.get("cidade", "N/A")
            estado = resultado.get("estado", "N/A")
            cep = resultado.get("cep", "N/A")
            
            return f"✅ Dados de contato do fornecedor:\n\n📝 Nome completo: {nome}\n🏪 Nome fantasia: {nome_fantasia}\n\n📧 Emails:\n• Principal: {email}\n• NFe: {email_nfe}\n\n📞 Telefones:\n• Principal: {telefone1}\n• Secundário: {telefone2}\n\n🏠 Endereço:\n{endereco}, {numero} {complemento}\n{bairro} - {cidade}/{estado}\nCEP: {cep}"
        else:
            return "❌ Dados de contato não encontrados"
    
    async def handle_relatorio_contas_receber_detalhado(self, args: Dict) -> str:
        """Handler inline para relatório detalhado de contas a receber"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 50)}
        
        # Filtros
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        if args.get("codigo_cliente"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente"]
        if args.get("codigo_categoria"):
            params["codigo_categoria"] = args["codigo_categoria"]
        if args.get("codigo_departamento"):
            params["codigo_departamento"] = args["codigo_departamento"]
        if args.get("status"):
            params["status"] = args["status"]
        
        resultado = await omie_client.consultar_contas_receber(params)
        contas = resultado.get("conta_receber_cadastro", [])
        
        if contas:
            # Agrupamento por status
            status_counts = {}
            status_values = {}
            total_geral = 0
            
            for conta in contas:
                status = conta.get("status_titulo", "N/A")
                valor = conta.get("valor_documento", 0)
                
                if status not in status_counts:
                    status_counts[status] = 0
                    status_values[status] = 0
                
                status_counts[status] += 1
                status_values[status] += valor
                total_geral += valor
            
            # Montar relatório
            relatorio = f"📊 Relatório Detalhado - Contas a Receber\n\n"
            relatorio += f"📋 Total de contas: {len(contas)}\n"
            relatorio += f"💰 Valor total: R$ {total_geral:,.2f}\n\n"
            relatorio += "📈 Por Status:\n"
            
            for status, count in status_counts.items():
                valor = status_values[status]
                relatorio += f"• {status}: {count} contas - R$ {valor:,.2f}\n"
            
            # Detalhes das primeiras 10 contas
            relatorio += "\n🔍 Detalhes (10 primeiras):\n"
            for i, conta in enumerate(contas[:10], 1):
                numero_doc = conta.get("numero_documento", "N/A")
                cliente = conta.get("razao_social", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                relatorio += f"{i}. Doc: {numero_doc} | Cliente: {cliente} | R$ {valor:,.2f} | Venc: {vencimento} | {status}\n"
            
            return relatorio
        else:
            return "❌ Nenhuma conta a receber encontrada com os filtros especificados"
    
    async def handle_relatorio_contas_pagar_detalhado(self, args: Dict) -> str:
        """Handler inline para relatório detalhado de contas a pagar"""
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 50)}
        
        # Filtros
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        if args.get("codigo_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_fornecedor"]
        if args.get("codigo_categoria"):
            params["codigo_categoria"] = args["codigo_categoria"]
        if args.get("codigo_departamento"):
            params["codigo_departamento"] = args["codigo_departamento"]
        if args.get("status"):
            params["status"] = args["status"]
        
        resultado = await omie_client.consultar_contas_pagar(params)
        contas = resultado.get("conta_pagar_cadastro", [])
        
        if contas:
            # Agrupamento por status
            status_counts = {}
            status_values = {}
            total_geral = 0
            
            for conta in contas:
                status = conta.get("status_titulo", "N/A")
                valor = conta.get("valor_documento", 0)
                
                if status not in status_counts:
                    status_counts[status] = 0
                    status_values[status] = 0
                
                status_counts[status] += 1
                status_values[status] += valor
                total_geral += valor
            
            # Montar relatório
            relatorio = f"📊 Relatório Detalhado - Contas a Pagar\n\n"
            relatorio += f"📋 Total de contas: {len(contas)}\n"
            relatorio += f"💰 Valor total: R$ {total_geral:,.2f}\n\n"
            relatorio += "📈 Por Status:\n"
            
            for status, count in status_counts.items():
                valor = status_values[status]
                relatorio += f"• {status}: {count} contas - R$ {valor:,.2f}\n"
            
            # Detalhes das primeiras 10 contas
            relatorio += "\n🔍 Detalhes (10 primeiras):\n"
            for i, conta in enumerate(contas[:10], 1):
                numero_doc = conta.get("numero_documento", "N/A")
                fornecedor = conta.get("razao_social", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                relatorio += f"{i}. Doc: {numero_doc} | Fornecedor: {fornecedor} | R$ {valor:,.2f} | Venc: {vencimento} | {status}\n"
            
            return relatorio
        else:
            return "❌ Nenhuma conta a pagar encontrada com os filtros especificados"
    
    async def handle_consultar_contas_receber_com_cliente_detalhado(self, args: Dict) -> str:
        """Handler inline para consultar contas a receber com dados completos do cliente"""
        # Parâmetros para consulta de contas
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 20)}
        
        # Aplicar filtros
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        if args.get("codigo_cliente"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente"]
        
        # Filtro de status - se for array, usar apenas o primeiro para a API
        if args.get("status"):
            if isinstance(args["status"], list) and len(args["status"]) > 0:
                params["status"] = args["status"][0]
            elif isinstance(args["status"], str):
                params["status"] = args["status"]
        
        # Consultar contas a receber
        resultado = await omie_client.consultar_contas_receber(params)
        contas = resultado.get("conta_receber_cadastro", [])
        
        if not contas:
            return "❌ Nenhuma conta a receber encontrada com os filtros especificados"
        
        # Filtrar por múltiplos status se necessário
        if args.get("status") and isinstance(args["status"], list) and len(args["status"]) > 1:
            contas = [conta for conta in contas if conta.get("status_titulo") in args["status"]]
        
        # Obter códigos únicos de clientes
        codigos_clientes = set()
        for conta in contas:
            codigo = conta.get("codigo_cliente_fornecedor")
            if codigo:
                codigos_clientes.add(codigo)
        
        # Buscar dados dos clientes
        dados_clientes = {}
        for codigo in codigos_clientes:
            try:
                cliente = await omie_client.consultar_cliente_por_codigo({"codigo_cliente_omie": codigo})
                if cliente:
                    dados_clientes[codigo] = cliente
            except Exception as e:
                logger.warning(f"Erro ao buscar cliente {codigo}: {e}")
                dados_clientes[codigo] = None
        
        # Configurações de exibição
        campos_cliente = args.get("campos_cliente", ["nome", "email", "telefone"])
        campos_conta = args.get("campos_conta", ["numero_documento", "valor", "vencimento", "status"])
        formato_saida = args.get("formato_saida", "detalhado")
        
        # Montar relatório baseado no formato
        if formato_saida == "resumido":
            return self._format_contas_receber_resumido(contas, dados_clientes, campos_cliente, campos_conta)
        elif formato_saida == "tabela":
            return self._format_contas_receber_tabela(contas, dados_clientes, campos_cliente, campos_conta)
        else:
            return self._format_contas_receber_detalhado(contas, dados_clientes, campos_cliente, campos_conta, len(codigos_clientes))
    
    def _format_contas_receber_detalhado(self, contas, dados_clientes, campos_cliente, campos_conta, total_clientes):
        """Formata resultado detalhado para contas a receber"""
        relatorio = f"📊 Contas a Receber com Dados de Cliente\n\n"
        relatorio += f"📋 Total de contas: {len(contas)}\n"
        relatorio += f"👥 Clientes únicos: {total_clientes}\n\n"
        
        total_valor = 0
        for i, conta in enumerate(contas, 1):
            codigo_cliente = conta.get("codigo_cliente_fornecedor")
            cliente = dados_clientes.get(codigo_cliente)
            
            relatorio += f"{i}. "
            
            # Campos da conta
            if "numero_documento" in campos_conta:
                relatorio += f"Doc: {conta.get('numero_documento', 'N/A')} | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                relatorio += f"R$ {valor:,.2f} | "
            if "vencimento" in campos_conta:
                relatorio += f"Venc: {conta.get('data_vencimento', 'N/A')} | "
            if "status" in campos_conta:
                relatorio += f"{conta.get('status_titulo', 'N/A')}"
            
            relatorio = relatorio.rstrip(" | ") + "\n"
            
            # Dados do cliente
            if cliente:
                if "nome" in campos_cliente:
                    relatorio += f"   👤 Cliente: {cliente.get('razao_social', 'N/A')}\n"
                if "email" in campos_cliente:
                    relatorio += f"   📧 Email: {cliente.get('email', 'N/A')}\n"
                if "telefone" in campos_cliente:
                    relatorio += f"   📞 Telefone: {cliente.get('telefone1_numero', 'N/A')}\n"
                if "endereco" in campos_cliente:
                    endereco = f"{cliente.get('endereco', 'N/A')}, {cliente.get('numero_endereco', 'N/A')}"
                    relatorio += f"   🏠 Endereço: {endereco}\n"
                if "cnpj_cpf" in campos_cliente:
                    relatorio += f"   📄 CNPJ/CPF: {cliente.get('cnpj_cpf', 'N/A')}\n"
                if "nome_fantasia" in campos_cliente:
                    relatorio += f"   🏪 Nome Fantasia: {cliente.get('nome_fantasia', 'N/A')}\n"
            else:
                relatorio += f"   ❌ Cliente não encontrado (código: {codigo_cliente})\n"
            
            relatorio += "\n"
        
        if "valor" in campos_conta:
            relatorio += f"💰 Valor total: R$ {total_valor:,.2f}"
        
        return relatorio
    
    def _format_contas_receber_resumido(self, contas, dados_clientes, campos_cliente, campos_conta):
        """Formata resultado resumido para contas a receber"""
        relatorio = f"📊 Resumo - Contas a Receber ({len(contas)} contas)\n\n"
        
        total_valor = 0
        for i, conta in enumerate(contas, 1):
            codigo_cliente = conta.get("codigo_cliente_fornecedor")
            cliente = dados_clientes.get(codigo_cliente)
            
            linha = f"{i}. "
            
            if "numero_documento" in campos_conta:
                linha += f"{conta.get('numero_documento', 'N/A')} | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                linha += f"R$ {valor:,.2f} | "
            if "status" in campos_conta:
                linha += f"{conta.get('status_titulo', 'N/A')} | "
            
            if cliente and "nome" in campos_cliente:
                linha += f"{cliente.get('razao_social', 'N/A')}"
            
            relatorio += linha.rstrip(" | ") + "\n"
        
        if "valor" in campos_conta:
            relatorio += f"\n💰 Total: R$ {total_valor:,.2f}"
        
        return relatorio
    
    def _format_contas_receber_tabela(self, contas, dados_clientes, campos_cliente, campos_conta):
        """Formata resultado em tabela para contas a receber"""
        relatorio = f"📊 Contas a Receber - Formato Tabela\n\n"
        
        # Cabeçalho
        cabecalho = ""
        if "numero_documento" in campos_conta:
            cabecalho += "Doc".ljust(15) + " | "
        if "valor" in campos_conta:
            cabecalho += "Valor".ljust(12) + " | "
        if "vencimento" in campos_conta:
            cabecalho += "Vencimento".ljust(12) + " | "
        if "status" in campos_conta:
            cabecalho += "Status".ljust(10) + " | "
        if "nome" in campos_cliente:
            cabecalho += "Cliente".ljust(30)
        
        relatorio += cabecalho.rstrip(" | ") + "\n"
        relatorio += "-" * len(cabecalho) + "\n"
        
        # Dados
        total_valor = 0
        for conta in contas:
            codigo_cliente = conta.get("codigo_cliente_fornecedor")
            cliente = dados_clientes.get(codigo_cliente)
            
            linha = ""
            if "numero_documento" in campos_conta:
                linha += str(conta.get("numero_documento", "N/A")).ljust(15) + " | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                linha += f"R$ {valor:,.2f}".ljust(12) + " | "
            if "vencimento" in campos_conta:
                linha += str(conta.get("data_vencimento", "N/A")).ljust(12) + " | "
            if "status" in campos_conta:
                linha += str(conta.get("status_titulo", "N/A")).ljust(10) + " | "
            if "nome" in campos_cliente and cliente:
                linha += str(cliente.get("razao_social", "N/A")).ljust(30)
            
            relatorio += linha.rstrip(" | ") + "\n"
        
        if "valor" in campos_conta:
            relatorio += f"\n💰 Total: R$ {total_valor:,.2f}"
        
        return relatorio
    
    async def handle_consultar_contas_pagar_com_fornecedor_detalhado(self, args: Dict) -> str:
        """Handler inline para consultar contas a pagar com dados completos do fornecedor"""
        # Parâmetros para consulta de contas
        params = {"pagina": args.get("pagina", 1), "registros_por_pagina": args.get("registros_por_pagina", 20)}
        
        # Aplicar filtros
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        if args.get("codigo_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_fornecedor"]
        
        # Filtro de status - se for array, usar apenas o primeiro para a API
        if args.get("status"):
            if isinstance(args["status"], list) and len(args["status"]) > 0:
                params["status"] = args["status"][0]
            elif isinstance(args["status"], str):
                params["status"] = args["status"]
        
        # Consultar contas a pagar
        resultado = await omie_client.consultar_contas_pagar(params)
        contas = resultado.get("conta_pagar_cadastro", [])
        
        if not contas:
            return "❌ Nenhuma conta a pagar encontrada com os filtros especificados"
        
        # Filtrar por múltiplos status se necessário
        if args.get("status") and isinstance(args["status"], list) and len(args["status"]) > 1:
            contas = [conta for conta in contas if conta.get("status_titulo") in args["status"]]
        
        # Obter códigos únicos de fornecedores
        codigos_fornecedores = set()
        for conta in contas:
            codigo = conta.get("codigo_cliente_fornecedor")
            if codigo:
                codigos_fornecedores.add(codigo)
        
        # Buscar dados dos fornecedores
        dados_fornecedores = {}
        for codigo in codigos_fornecedores:
            try:
                fornecedor = await omie_client.consultar_fornecedor_por_codigo({"codigo_cliente_omie": codigo})
                if fornecedor:
                    dados_fornecedores[codigo] = fornecedor
            except Exception as e:
                logger.warning(f"Erro ao buscar fornecedor {codigo}: {e}")
                dados_fornecedores[codigo] = None
        
        # Configurações de exibição
        campos_fornecedor = args.get("campos_fornecedor", ["nome", "email", "telefone"])
        campos_conta = args.get("campos_conta", ["numero_documento", "valor", "vencimento", "status"])
        formato_saida = args.get("formato_saida", "detalhado")
        
        # Montar relatório baseado no formato
        if formato_saida == "resumido":
            return self._format_contas_pagar_resumido(contas, dados_fornecedores, campos_fornecedor, campos_conta)
        elif formato_saida == "tabela":
            return self._format_contas_pagar_tabela(contas, dados_fornecedores, campos_fornecedor, campos_conta)
        else:
            return self._format_contas_pagar_detalhado(contas, dados_fornecedores, campos_fornecedor, campos_conta, len(codigos_fornecedores))
    
    def _format_contas_pagar_detalhado(self, contas, dados_fornecedores, campos_fornecedor, campos_conta, total_fornecedores):
        """Formata resultado detalhado para contas a pagar"""
        relatorio = f"📊 Contas a Pagar com Dados de Fornecedor\n\n"
        relatorio += f"📋 Total de contas: {len(contas)}\n"
        relatorio += f"🏢 Fornecedores únicos: {total_fornecedores}\n\n"
        
        total_valor = 0
        for i, conta in enumerate(contas, 1):
            codigo_fornecedor = conta.get("codigo_cliente_fornecedor")
            fornecedor = dados_fornecedores.get(codigo_fornecedor)
            
            relatorio += f"{i}. "
            
            # Campos da conta
            if "numero_documento" in campos_conta:
                relatorio += f"Doc: {conta.get('numero_documento', 'N/A')} | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                relatorio += f"R$ {valor:,.2f} | "
            if "vencimento" in campos_conta:
                relatorio += f"Venc: {conta.get('data_vencimento', 'N/A')} | "
            if "status" in campos_conta:
                relatorio += f"{conta.get('status_titulo', 'N/A')}"
            
            relatorio = relatorio.rstrip(" | ") + "\n"
            
            # Dados do fornecedor
            if fornecedor:
                if "nome" in campos_fornecedor:
                    relatorio += f"   🏢 Fornecedor: {fornecedor.get('razao_social', 'N/A')}\n"
                if "email" in campos_fornecedor:
                    relatorio += f"   📧 Email: {fornecedor.get('email', 'N/A')}\n"
                if "telefone" in campos_fornecedor:
                    relatorio += f"   📞 Telefone: {fornecedor.get('telefone1_numero', 'N/A')}\n"
                if "endereco" in campos_fornecedor:
                    endereco = f"{fornecedor.get('endereco', 'N/A')}, {fornecedor.get('numero_endereco', 'N/A')}"
                    relatorio += f"   🏠 Endereço: {endereco}\n"
                if "cnpj_cpf" in campos_fornecedor:
                    relatorio += f"   📄 CNPJ/CPF: {fornecedor.get('cnpj_cpf', 'N/A')}\n"
                if "nome_fantasia" in campos_fornecedor:
                    relatorio += f"   🏪 Nome Fantasia: {fornecedor.get('nome_fantasia', 'N/A')}\n"
            else:
                relatorio += f"   ❌ Fornecedor não encontrado (código: {codigo_fornecedor})\n"
            
            relatorio += "\n"
        
        if "valor" in campos_conta:
            relatorio += f"💰 Valor total: R$ {total_valor:,.2f}"
        
        return relatorio
    
    def _format_contas_pagar_resumido(self, contas, dados_fornecedores, campos_fornecedor, campos_conta):
        """Formata resultado resumido para contas a pagar"""
        relatorio = f"📊 Resumo - Contas a Pagar ({len(contas)} contas)\n\n"
        
        total_valor = 0
        for i, conta in enumerate(contas, 1):
            codigo_fornecedor = conta.get("codigo_cliente_fornecedor")
            fornecedor = dados_fornecedores.get(codigo_fornecedor)
            
            linha = f"{i}. "
            
            if "numero_documento" in campos_conta:
                linha += f"{conta.get('numero_documento', 'N/A')} | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                linha += f"R$ {valor:,.2f} | "
            if "status" in campos_conta:
                linha += f"{conta.get('status_titulo', 'N/A')} | "
            
            if fornecedor and "nome" in campos_fornecedor:
                linha += f"{fornecedor.get('razao_social', 'N/A')}"
            
            relatorio += linha.rstrip(" | ") + "\n"
        
        if "valor" in campos_conta:
            relatorio += f"\n💰 Total: R$ {total_valor:,.2f}"
        
        return relatorio
    
    def _format_contas_pagar_tabela(self, contas, dados_fornecedores, campos_fornecedor, campos_conta):
        """Formata resultado em tabela para contas a pagar"""
        relatorio = f"📊 Contas a Pagar - Formato Tabela\n\n"
        
        # Cabeçalho
        cabecalho = ""
        if "numero_documento" in campos_conta:
            cabecalho += "Doc".ljust(15) + " | "
        if "valor" in campos_conta:
            cabecalho += "Valor".ljust(12) + " | "
        if "vencimento" in campos_conta:
            cabecalho += "Vencimento".ljust(12) + " | "
        if "status" in campos_conta:
            cabecalho += "Status".ljust(10) + " | "
        if "nome" in campos_fornecedor:
            cabecalho += "Fornecedor".ljust(30)
        
        relatorio += cabecalho.rstrip(" | ") + "\n"
        relatorio += "-" * len(cabecalho) + "\n"
        
        # Dados
        total_valor = 0
        for conta in contas:
            codigo_fornecedor = conta.get("codigo_cliente_fornecedor")
            fornecedor = dados_fornecedores.get(codigo_fornecedor)
            
            linha = ""
            if "numero_documento" in campos_conta:
                linha += str(conta.get("numero_documento", "N/A")).ljust(15) + " | "
            if "valor" in campos_conta:
                valor = conta.get("valor_documento", 0)
                total_valor += valor
                linha += f"R$ {valor:,.2f}".ljust(12) + " | "
            if "vencimento" in campos_conta:
                linha += str(conta.get("data_vencimento", "N/A")).ljust(12) + " | "
            if "status" in campos_conta:
                linha += str(conta.get("status_titulo", "N/A")).ljust(10) + " | "
            if "nome" in campos_fornecedor and fornecedor:
                linha += str(fornecedor.get("razao_social", "N/A")).ljust(30)
            
            relatorio += linha.rstrip(" | ") + "\n"
        
        if "valor" in campos_conta:
            relatorio += f"\n💰 Total: R$ {total_valor:,.2f}"
        
        return relatorio

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