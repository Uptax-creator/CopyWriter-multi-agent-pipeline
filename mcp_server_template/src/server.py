#!/usr/bin/env python3
"""
Template para Servidor MCP Híbrido
Suporta STDIO (Claude Desktop) e HTTP (N8N, Zapier, etc.)
"""

import asyncio
import argparse
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("mcp-server-template")

class ToolRegistry:
    """Registro de ferramentas MCP"""
    
    def __init__(self):
        self.tools = {}
        self.mcp_tools = []
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas as ferramentas disponíveis"""
        
        # Ferramenta de exemplo
        example_tool = {
            "name": "exemplo",
            "description": "Ferramenta de exemplo do template",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mensagem": {"type": "string", "description": "Mensagem de exemplo"}
                }
            }
        }
        
        self.tools["exemplo"] = example_tool
        self.mcp_tools.append(example_tool)
        
        logger.info(f"Total de ferramentas registradas: {len(self.tools)}")
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Retorna ferramentas no formato MCP"""
        return self.mcp_tools
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém ferramenta por nome"""
        return self.tools.get(name)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa ferramenta"""
        tool = self.get_tool(name)
        if not tool:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não encontrada",
                "ferramentas_disponíveis": list(self.tools.keys())
            }, ensure_ascii=False, indent=2)
        
        try:
            if name == "exemplo":
                return await self._execute_example(arguments)
            
            return json.dumps({
                "erro": f"Ferramenta '{name}' não implementada"
            }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {name}: {e}")
            return json.dumps({
                "erro": f"Erro ao executar {name}",
                "detalhes": str(e)
            }, ensure_ascii=False, indent=2)
    
    async def _execute_example(self, arguments: Dict[str, Any]) -> str:
        """Executa ferramenta de exemplo"""
        mensagem = arguments.get("mensagem", "Olá do template!")
        
        return json.dumps({
            "ferramenta": "exemplo",
            "mensagem_recebida": mensagem,
            "resposta": f"Processado: {mensagem}",
            "timestamp": asyncio.get_event_loop().time(),
            "status": "sucesso"
        }, ensure_ascii=False, indent=2)

class MCPServer:
    """Servidor MCP - Protocolo STDIO"""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        logger.info("Servidor MCP STDIO inicializado")
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição"""
        return str(request.get("id", "unknown"))
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
    
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
                        "serverInfo": {
                            "name": "mcp-server-template",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tool_registry.get_mcp_tools()}
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
                
                result = await self.tool_registry.call_tool(tool_name, arguments)
                
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
    
    async def run(self):
        """Executa servidor MCP STDIO"""
        logger.info("Servidor MCP STDIO iniciado")
        
        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    break
                    
                request = json.loads(line)
                response = await self.handle_request(request)
                self.send_response(response)
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": "parse_error",
                    "error": {"code": -32700, "message": "Parse error"}
                }
                self.send_response(error_response)
                
            except Exception as e:
                logger.error(f"Erro geral: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": "internal_error",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                self.send_response(error_response)

class HTTPServer:
    """Servidor HTTP para integrações web"""
    
    def __init__(self):
        self.app = FastAPI(
            title="MCP Server Template",
            description="Servidor MCP Template com suporte híbrido",
            version="1.0.0"
        )
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.tool_registry = ToolRegistry()
        self._setup_routes()
        logger.info("Servidor HTTP inicializado")
    
    def _setup_routes(self):
        """Configura rotas HTTP"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "MCP Server Template",
                "version": "1.0.0",
                "mode": "HTTP",
                "tools": len(self.tool_registry.tools),
                "endpoints": [
                    "/mcp/initialize",
                    "/mcp/tools",
                    "/mcp/tools/{tool_name}",
                    "/test/{tool_name}",
                    "/sse/events",
                    "/sse/tools/{tool_name}"
                ],
                "features": {
                    "mcp_protocol": True,
                    "server_sent_events": True,
                    "n8n_compatible": True,
                    "real_time_streaming": True
                }
            }
        
        @self.app.post("/mcp/initialize")
        async def mcp_initialize():
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {
                    "name": "mcp-server-template",
                    "version": "1.0.0"
                }
            }
        
        @self.app.get("/mcp/tools")
        async def mcp_list_tools():
            return {"tools": self.tool_registry.get_mcp_tools()}
        
        @self.app.post("/mcp/tools/{tool_name}")
        async def mcp_call_tool(tool_name: str, request: Request):
            try:
                body = await request.json()
                arguments = body.get("arguments", {})
                
                result = await self.tool_registry.call_tool(tool_name, arguments)
                
                return {
                    "content": [{"type": "text", "text": result}]
                }
            except Exception as e:
                logger.error(f"Erro ao executar {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/test/{tool_name}")
        async def test_tool(tool_name: str):
            """Endpoint de teste para ferramentas"""
            try:
                result = await self.tool_registry.call_tool(tool_name, {})
                return {"status": "success", "data": result}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.app.get("/sse/events")
        async def sse_events():
            """Server-Sent Events endpoint"""
            async def event_generator():
                try:
                    while True:
                        status_event = {
                            "event": "server_status",
                            "data": {
                                "timestamp": asyncio.get_event_loop().time(),
                                "status": "active",
                                "tools_available": len(self.tool_registry.tools),
                                "mode": "template"
                            }
                        }
                        yield f"data: {json.dumps(status_event)}\n\n"
                        await asyncio.sleep(30)
                        
                except Exception as e:
                    logger.error(f"Erro no SSE stream: {e}")
                    error_event = {
                        "event": "error",
                        "data": {"error": str(e)}
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
        @self.app.get("/sse/tools/{tool_name}")
        async def sse_tool_stream(tool_name: str):
            """SSE endpoint para ferramentas específicas"""
            async def tool_event_generator():
                try:
                    # Evento de início
                    start_event = {
                        "event": "tool_start",
                        "data": {
                            "tool_name": tool_name,
                            "timestamp": asyncio.get_event_loop().time(),
                            "status": "starting"
                        }
                    }
                    yield f"data: {json.dumps(start_event)}\n\n"
                    
                    # Executar ferramenta
                    result = await self.tool_registry.call_tool(tool_name, {})
                    
                    # Evento de resultado
                    result_event = {
                        "event": "tool_result",
                        "data": {
                            "tool_name": tool_name,
                            "result": result,
                            "timestamp": asyncio.get_event_loop().time(),
                            "status": "completed"
                        }
                    }
                    yield f"data: {json.dumps(result_event)}\n\n"
                    
                except Exception as e:
                    error_event = {
                        "event": "tool_error",
                        "data": {
                            "tool_name": tool_name,
                            "error": str(e),
                            "timestamp": asyncio.get_event_loop().time(),
                            "status": "error"
                        }
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
            
            return StreamingResponse(
                tool_event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    
    def run(self, host: str = "0.0.0.0", port: int = 3000, debug: bool = False):
        """Executa servidor HTTP"""
        logger.info(f"Servidor HTTP iniciado em http://{host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="debug" if debug else "info"
        )

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Servidor MCP Template")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio",
                       help="Modo de execução (default: stdio)")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host para servidor HTTP (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3000,
                       help="Porta para servidor HTTP (default: 3000)")
    parser.add_argument("--debug", action="store_true",
                       help="Modo debug")
    
    args = parser.parse_args()
    
    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.mode == "stdio":
        # Modo STDIO para Claude Desktop
        server = MCPServer()
        asyncio.run(server.run())
    
    elif args.mode == "http":
        # Modo HTTP para integrações web
        server = HTTPServer()
        server.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()