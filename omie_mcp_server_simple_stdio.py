#!/usr/bin/env python3
"""
Servidor MCP STDIO Super Simples para Omie ERP
Versão minimalista para resolver erro "Could not find property option"
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-simple")

class SimpleMCPServer:
    """Servidor MCP super simples"""
    
    def __init__(self):
        self.tools = self._get_tools()
        logger.info("Servidor MCP simples inicializado")
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista simples de tools"""
        return [
            {
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {
                            "type": "integer",
                            "description": "Página",
                            "default": 1
                        },
                        "registros_por_pagina": {
                            "type": "integer", 
                            "description": "Registros por página",
                            "default": 50
                        }
                    },
                    "required": []
                }
            }
        ]
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição"""
        return str(request.get("id", "unknown"))
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
        logger.debug(f"Enviada resposta: {response_json}")
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa uma ferramenta simples"""
        
        if name == "testar_conexao":
            return json.dumps({
                "status": "conectado",
                "servidor": "Omie ERP",
                "modo": "stdio-simples",
                "timestamp": asyncio.get_event_loop().time()
            }, ensure_ascii=False, indent=2)
        
        elif name == "consultar_categorias":
            pagina = arguments.get("pagina", 1)
            registros = arguments.get("registros_por_pagina", 50)
            return json.dumps({
                "pagina": pagina,
                "registros_por_pagina": registros,
                "resultado": "Simulação - categorias encontradas",
                "modo": "stdio-simples"
            }, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não encontrada",
                "ferramentas_disponíveis": [tool["name"] for tool in self.tools]
            }, ensure_ascii=False, indent=2)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        method = request.get("method")
        request_id = self.get_request_id(request)
        
        logger.info(f"Processando método: {method}")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "omie-mcp-simple",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                    }
                
                result = await self.execute_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Executa servidor em modo STDIO"""
        logger.info("Servidor MCP STDIO iniciado")
        
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    self.send_response(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": "unknown",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    self.send_response(error_response)
                except Exception as e:
                    logger.error(f"Erro inesperado: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Servidor interrompido")
        except Exception as e:
            logger.error(f"Erro no servidor: {e}")

async def main():
    """Função principal"""
    server = SimpleMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())