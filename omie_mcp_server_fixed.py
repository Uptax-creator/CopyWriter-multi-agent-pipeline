#!/usr/bin/env python3
"""
Servidor MCP para Omie ERP - Versão corrigida com protocolo JSON-RPC válido
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-server")

# Importar cliente Omie
try:
    from src.client.omie_client import OmieClient
    from src.config import config
    omie_client = OmieClient(config)
    logger.info("Cliente Omie importado com sucesso")
except Exception as e:
    logger.error(f"Erro ao importar cliente Omie: {e}")
    omie_client = None

class OmieMCPServer:
    """Servidor MCP para Omie ERP"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
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
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
    
    def get_request_id(self, request: Dict[str, Any]) -> Optional[str]:
        """Obtém ID da requisição ou gera um padrão"""
        request_id = request.get("id")
        if request_id is None:
            return "unknown"
        return str(request_id)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        method = request.get("method")
        request_id = self.get_request_id(request)
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "omie-mcp-server", "version": "1.0.0"}
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "Tool name is required"}
                    }
                
                result = await self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(result)}]}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not supported: {method}"}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Chama ferramenta específica"""
        try:
            if tool_name == "testar_conexao":
                return json.dumps({
                    "status": "conectado",
                    "servidor": "Omie ERP",
                    "ferramentas_disponíveis": len(self.tools),
                    "cliente_disponível": omie_client is not None
                }, ensure_ascii=False, indent=2)
            
            if not omie_client:
                return json.dumps({
                    "erro": "Cliente Omie não disponível",
                    "ferramenta": tool_name,
                    "argumentos": arguments
                }, ensure_ascii=False, indent=2)
            
            if tool_name == "consultar_categorias":
                result = await omie_client.consultar_categorias(arguments)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_departamentos":
                result = await omie_client.consultar_departamentos(arguments)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_contas_pagar":
                result = await omie_client.consultar_contas_pagar(arguments)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_contas_receber":
                result = await omie_client.consultar_contas_receber(arguments)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            elif tool_name == "cadastrar_cliente_fornecedor":
                result = await omie_client.cadastrar_cliente_fornecedor(arguments)
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({
                    "erro": f"Ferramenta '{tool_name}' não implementada",
                    "ferramentas_disponíveis": [tool["name"] for tool in self.tools],
                    "argumentos_recebidos": arguments
                }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return json.dumps({
                "erro": f"Erro ao executar {tool_name}",
                "detalhes": str(e),
                "ferramenta": tool_name,
                "argumentos": arguments
            }, ensure_ascii=False, indent=2)

async def main():
    """Função principal do servidor MCP"""
    server = OmieMCPServer()
    logger.info("Servidor MCP Omie iniciado (versão corrigida)")
    
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:
                break
                
            request = json.loads(line)
            response = await server.handle_request(request)
            server.send_response(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": "parse_error",
                "error": {"code": -32700, "message": "Parse error"}
            }
            server.send_response(error_response)
            
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": "internal_error",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            server.send_response(error_response)

if __name__ == "__main__":
    asyncio.run(main())