#!/usr/bin/env python3
"""
Cliente MCP HTTP para Claude Desktop
Este cliente conecta o Claude Desktop ao servidor HTTP do Omie
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any
import httpx

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("claude-http-client")

# ============================================================================
# CLIENTE HTTP MCP
# ============================================================================

class MCPHttpClient:
    """Cliente HTTP MCP para comunicação com o servidor Omie"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        
    async def initialize(self):
        """Inicializar cliente"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/mcp/initialize")
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao inicializar: {e}")
            raise
    
    async def get_tools(self):
        """Obter lista de ferramentas"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/mcp/tools")
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Executar ferramenta"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/mcp/tools/{tool_name}",
                    json={"arguments": arguments}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                
                result = response.json()
                return result.get("content", [{}])[0].get("text", "Erro: resposta inválida")
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return f"Erro ao executar {tool_name}: {str(e)}"

# ============================================================================
# SERVIDOR MCP PARA CLAUDE DESKTOP
# ============================================================================

class MCPServer:
    """Servidor MCP que atua como proxy para o servidor HTTP"""
    
    def __init__(self):
        self.client = MCPHttpClient()
        self.tools = []
        
    async def init_server(self):
        """Inicializar servidor"""
        try:
            # Inicializar cliente HTTP
            await self.client.initialize()
            
            # Obter ferramentas disponíveis
            tools_response = await self.client.get_tools()
            self.tools = tools_response.get("tools", [])
            
            logger.info(f"Servidor inicializado com {len(self.tools)} ferramentas")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar servidor: {e}")
            self.tools = []
    
    def send_response(self, response: Dict):
        """Enviar resposta via stdout"""
        print(json.dumps(response, ensure_ascii=False), flush=True)
    
    async def handle_request(self, request: Dict) -> Dict:
        """Processar requisição MCP"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                await self.init_server()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "omie-mcp-http-client", "version": "2.0.0"}
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
                
                # Executar ferramenta via HTTP
                result = await self.client.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Método não suportado: {method}"}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }

# ============================================================================
# MAIN LOOP
# ============================================================================

async def main():
    """Loop principal do cliente MCP"""
    server = MCPServer()
    logger.info("Cliente MCP HTTP iniciado")
    
    # Aguardar inicialização
    await asyncio.sleep(0.1)
    
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
            logger.info("Cliente interrompido")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")

if __name__ == "__main__":
    asyncio.run(main())