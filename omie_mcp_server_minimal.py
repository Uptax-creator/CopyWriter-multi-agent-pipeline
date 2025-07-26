#!/usr/bin/env python3
"""
Servidor MCP Minimal para Omie ERP
Versão super simples que resolve erro "Could not find property option"
"""

import asyncio
import json
import logging
import sys
import argparse
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-minimal")

class OmieToolRegistry:
    """Registro de ferramentas com schemas corrigidos"""
    
    def __init__(self):
        self.tools = {}
        self.mcp_tools = []
        self._register_tools()
    
    def _register_tools(self):
        """Registra ferramentas com schemas válidos"""
        
        # Tools com schemas super simples para evitar problemas
        tools_data = [
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
                            "description": "Numero da pagina"
                        },
                        "registros_por_pagina": {
                            "type": "integer", 
                            "description": "Registros por pagina"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos cadastrados no Omie ERP", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {
                            "type": "integer",
                            "description": "Numero da pagina"
                        },
                        "registros_por_pagina": {
                            "type": "integer",
                            "description": "Registros por pagina"
                        }
                    },
                    "required": []
                }
            }
        ]
        
        # Registrar tools
        for tool_data in tools_data:
            self.tools[tool_data["name"]] = tool_data
            self.mcp_tools.append(tool_data)
        
        logger.info(f"Registradas {len(self.tools)} ferramentas")
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de tools para MCP"""
        return self.mcp_tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa ferramenta"""
        
        if name not in self.tools:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não encontrada",
                "ferramentas_disponiveis": list(self.tools.keys())
            }, ensure_ascii=False, indent=2)
        
        # Execução simulada para testar
        if name == "testar_conexao":
            return json.dumps({
                "status": "conectado",
                "servidor": "Omie ERP",
                "modo": "mcp-minimal",
                "ferramentas_disponiveis": len(self.tools)
            }, ensure_ascii=False, indent=2)
        
        elif name == "consultar_categorias":
            pagina = arguments.get("pagina", 1)
            registros = arguments.get("registros_por_pagina", 50)
            return json.dumps({
                "pagina": pagina,
                "registros_por_pagina": registros,
                "categorias": [
                    {"codigo": "01", "descricao": "Categoria Teste 1"},
                    {"codigo": "02", "descricao": "Categoria Teste 2"}
                ],
                "modo": "simulacao"
            }, ensure_ascii=False, indent=2)
        
        elif name == "consultar_departamentos":
            pagina = arguments.get("pagina", 1) 
            registros = arguments.get("registros_por_pagina", 50)
            return json.dumps({
                "pagina": pagina,
                "registros_por_pagina": registros,
                "departamentos": [
                    {"codigo": "01", "descricao": "Departamento Teste 1"},
                    {"codigo": "02", "descricao": "Departamento Teste 2"}
                ],
                "modo": "simulacao"
            }, ensure_ascii=False, indent=2)
        
        return json.dumps({
            "ferramenta": name,
            "argumentos": arguments,
            "modo": "simulacao"
        }, ensure_ascii=False, indent=2)

class OmieMCPServer:
    """Servidor MCP minimal"""
    
    def __init__(self):
        self.tool_registry = OmieToolRegistry()
        logger.info("Servidor MCP minimal inicializado")
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição"""
        request_id = request.get("id")
        if request_id is None:
            return "unknown"
        return str(request_id)
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        try:
            response_json = json.dumps(response, ensure_ascii=False)
            print(response_json, flush=True)
        except Exception as e:
            logger.error(f"Erro ao enviar resposta: {e}")
    
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
                            "name": "omie-mcp-minimal",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {
                        "tools": self.tool_registry.get_mcp_tools()
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
                            "message": "Invalid params"
                        }
                    }
                
                result = await self.tool_registry.call_tool(tool_name, arguments)
                
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
    
    async def run_stdio(self):
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
                    logger.error(f"Erro JSON: {e}")
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

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Servidor MCP Omie Minimal")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = OmieMCPServer()
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())