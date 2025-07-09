"""
Cliente MCP para comunicação com Claude Desktop
"""

import json
import sys
import asyncio
from typing import Dict, Any, List
from src.utils.logger import logger

class MCPClient:
    """Cliente MCP para comunicação com Claude Desktop"""
    
    def __init__(self):
        self.capabilities = {
            "tools": {"listChanged": True}
        }
        self.server_info = {
            "name": "omie-mcp-server",
            "version": "2.0.0"
        }
        self.protocol_version = "2024-11-05"
    
    def send_response(self, response: Dict[str, Any]):
        """Enviar resposta via stdout"""
        try:
            output = json.dumps(response, ensure_ascii=False)
            print(output, flush=True)
            logger.debug(f"Resposta enviada: {response.get('id', 'N/A')}")
        except Exception as e:
            logger.error(f"Erro ao enviar resposta: {e}")
    
    def create_response(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Criar resposta MCP padrão"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def create_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Criar resposta de erro MCP"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    def create_tool_response(self, content: str) -> Dict[str, Any]:
        """Criar resposta de ferramenta"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        }
    
    def handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Manipular requisição de inicialização"""
        return self.create_response(request_id, {
            "protocolVersion": self.protocol_version,
            "capabilities": self.capabilities,
            "serverInfo": self.server_info
        })
    
    def handle_tools_list(self, request_id: Any, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Manipular requisição de lista de ferramentas"""
        return self.create_response(request_id, {
            "tools": tools
        })
    
    def handle_tools_call(self, request_id: Any, result: str) -> Dict[str, Any]:
        """Manipular requisição de chamada de ferramenta"""
        return self.create_response(request_id, self.create_tool_response(result))
    
    def handle_unknown_method(self, request_id: Any, method: str) -> Dict[str, Any]:
        """Manipular método desconhecido"""
        return self.create_error_response(
            request_id, 
            -32601, 
            f"Método não suportado: {method}"
        )
    
    def handle_error(self, request_id: Any, error: Exception) -> Dict[str, Any]:
        """Manipular erro genérico"""
        return self.create_error_response(
            request_id, 
            -32603, 
            str(error)
        )
    
    async def read_stdin(self) -> str:
        """Ler linha da stdin de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sys.stdin.readline)
    
    async def process_request(self, line: str) -> Dict[str, Any]:
        """Processar requisição JSON"""
        try:
            request = json.loads(line.strip())
            logger.debug(f"Requisição recebida: {request}")
            return request
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise ValueError(f"JSON inválido: {e}")
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validar estrutura da requisição"""
        required_fields = ["jsonrpc", "method", "id"]
        for field in required_fields:
            if field not in request:
                logger.error(f"Campo obrigatório ausente: {field}")
                return False
        
        if request["jsonrpc"] != "2.0":
            logger.error(f"Versão JSON-RPC inválida: {request['jsonrpc']}")
            return False
        
        return True

# Instância global do cliente MCP
mcp_client = MCPClient()