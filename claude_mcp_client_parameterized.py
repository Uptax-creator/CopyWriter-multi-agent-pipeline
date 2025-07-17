#!/usr/bin/env python3
"""
Cliente MCP HTTP Parameterizado para Claude Desktop
Conecta Claude Desktop (STDIO) com servidores HTTP MCP
"""

import asyncio
import json
import logging
import sys
import argparse
import requests
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("claude-mcp-http-client")

class HTTPMCPClient:
    """Cliente que converte STDIO MCP para HTTP MCP"""
    
    def __init__(self, server_url: str, server_name: str):
        self.server_url = server_url.rstrip('/')
        self.server_name = server_name
        logger.info(f"Cliente MCP HTTP inicializado para {server_name} em {server_url}")
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição"""
        request_id = request.get("id")
        if request_id is None:
            return "unknown"
        return str(request_id)
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta via STDIO"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição de inicialização"""
        request_id = self.get_request_id(request)
        
        try:
            # Testar conexão com servidor HTTP
            response = requests.get(f"{self.server_url}/", timeout=5, headers={'Connection': 'close'})
            
            if response.status_code == 200:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": f"{self.server_name}-http-client",
                            "version": "2.0.0-http"
                        }
                    }
                }
            else:
                raise Exception(f"Servidor HTTP retornou status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao conectar com servidor HTTP: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro de conexão com servidor {self.server_name}: {str(e)}"
                }
            }
    
    async def handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Lista ferramentas do servidor HTTP"""
        request_id = self.get_request_id(request)
        
        try:
            response = requests.get(f"{self.server_url}/mcp/tools", timeout=10, headers={'Connection': 'close'})
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", [])
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
            else:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro ao listar ferramentas: {str(e)}"
                }
            }
    
    async def handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Chama ferramenta no servidor HTTP"""
        request_id = self.get_request_id(request)
        
        try:
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": "Tool name is required"}
                }
            
            # Chamar ferramenta via HTTP
            url = f"{self.server_url}/mcp/tools/{tool_name}"
            payload = {"arguments": arguments}
            
            response = requests.post(url, json=payload, timeout=30, headers={'Connection': 'close'})
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": data
                }
            else:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro ao executar ferramenta: {str(e)}"
                }
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        method = request.get("method")
        request_id = self.get_request_id(request)
        
        try:
            if method == "initialize":
                return await self.handle_initialize(request)
            
            elif method == "tools/list":
                return await self.handle_tools_list(request)
            
            elif method == "tools/call":
                return await self.handle_tool_call(request)
            
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
    
    async def run(self):
        """Executa cliente MCP"""
        logger.info(f"Cliente MCP HTTP iniciado para {self.server_name}")
        logger.info(f"Conectando com: {self.server_url}")
        
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
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    self.send_response(error_response)
                except Exception as e:
                    logger.error(f"Erro ao processar linha: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Cliente interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no cliente: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Cliente MCP HTTP para Claude Desktop')
    parser.add_argument('--server-url', required=True, help='URL do servidor HTTP MCP')
    parser.add_argument('--server-name', required=True, help='Nome do servidor MCP')
    
    args = parser.parse_args()
    
    # Validar URL
    if not args.server_url.startswith('http'):
        logger.error("URL do servidor deve começar com http:// ou https://")
        sys.exit(1)
    
    # Criar e executar cliente
    client = HTTPMCPClient(args.server_url, args.server_name)
    asyncio.run(client.run())

if __name__ == "__main__":
    main()