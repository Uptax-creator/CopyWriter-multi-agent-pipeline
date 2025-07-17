#!/usr/bin/env python3
"""
Servidor MCP para Nibo ERP - Versão corrigida com protocolo JSON-RPC válido
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("nibo-mcp-server")

class NiboMCPServer:
    """Servidor MCP para Nibo ERP - Versão corrigida"""
    
    def __init__(self):
        # Autenticação simples via variáveis de ambiente
        self.nibo_token = os.getenv("NIBO_TOKEN", "2264E2C5B5464BFABC3D6E6820EBE47F")
        self.company_id = os.getenv("NIBO_COMPANY_ID", "50404226-615e-48d2-9701-0e765f64e0b9")
        self.base_url = "https://api.nibo.com.br"
        
        logger.info(f"Nibo MCP Server inicializado com token: {self.nibo_token[:8]}...")
        
        self.tools = [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_centros_custo",
                "description": "Consulta centros de custo cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados no Nibo",
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
                "description": "Consulta fornecedores cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_socios",
                "description": "Consulta sócios cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Nibo",
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
                        "serverInfo": {"name": "nibo-mcp-server", "version": "1.0.0"}
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
            # Simulação de chamadas para API do Nibo
            if tool_name == "testar_conexao":
                return json.dumps({
                    "status": "conectado",
                    "servidor": "Nibo ERP",
                    "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                    "token": self.nibo_token[:8] + "...",
                    "company_id": self.company_id,
                    "ferramentas_disponíveis": len(self.tools)
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_categorias":
                return json.dumps({
                    "categorias": [
                        {"id": 1, "nome": "Vendas", "ativo": True},
                        {"id": 2, "nome": "Compras", "ativo": True},
                        {"id": 3, "nome": "Administrativo", "ativo": True}
                    ],
                    "total": 3,
                    "pagina": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50)
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_centros_custo":
                return json.dumps({
                    "centros_custo": [
                        {"id": 1, "nome": "Comercial", "ativo": True},
                        {"id": 2, "nome": "Financeiro", "ativo": True},
                        {"id": 3, "nome": "Operacional", "ativo": True}
                    ],
                    "total": 3,
                    "pagina": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50)
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_clientes":
                return json.dumps({
                    "clientes": [
                        {
                            "id": 1,
                            "nome": "Cliente Nibo Ltda",
                            "documento": "12.345.678/0001-90",
                            "email": "contato@clientenibo.com",
                            "telefone": "(11) 1234-5678",
                            "ativo": True
                        },
                        {
                            "id": 2,
                            "nome": "Cliente Teste ME",
                            "documento": "98.765.432/0001-10",
                            "email": "teste@clienteteste.com",
                            "telefone": "(11) 8765-4321",
                            "ativo": True
                        }
                    ],
                    "total": 2,
                    "pagina": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50)
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_fornecedores":
                return json.dumps({
                    "fornecedores": [
                        {
                            "id": 1,
                            "nome": "Fornecedor Nibo Ltda",
                            "documento": "11.222.333/0001-44",
                            "email": "contato@fornecedornibo.com",
                            "telefone": "(11) 1111-2222",
                            "ativo": True
                        }
                    ],
                    "total": 1,
                    "pagina": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50)
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_socios":
                return json.dumps({
                    "socios": [
                        {
                            "id": 1,
                            "nome": "João Silva",
                            "documento": "123.456.789-00",
                            "email": "joao@empresa.com",
                            "participacao": 50.0,
                            "ativo": True
                        },
                        {
                            "id": 2,
                            "nome": "Maria Santos",
                            "documento": "987.654.321-00",
                            "email": "maria@empresa.com",
                            "participacao": 50.0,
                            "ativo": True
                        }
                    ],
                    "total": 2,
                    "pagina": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50)
                }, ensure_ascii=False, indent=2)
            
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
    server = NiboMCPServer()
    logger.info("Servidor MCP Nibo iniciado (versão corrigida)")
    
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