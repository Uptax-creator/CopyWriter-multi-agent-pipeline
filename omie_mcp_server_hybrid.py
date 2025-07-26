#!/usr/bin/env python3
"""
Servidor MCP Híbrido para Omie ERP
Suporta protocolo STDIO (Claude Desktop) e HTTP (Integrações Web)
"""

import asyncio
import argparse
import json
import logging
import sys
import os
import time
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-hybrid")

# Importar ferramentas do servidor HTTP existente
try:
    from src.client.omie_client import OmieClient
    from src.config import config
    from src.utils.logger import logger as http_logger
    from src.utils.sanitizers import json_sanitizer
    
    # Importar ferramentas
    from src.tools.consultas import (
        ConsultarCategoriasTool,
        ConsultarDepartamentosTool,
        ConsultarTiposDocumentoTool,
        ConsultarContasPagarTool,
        ConsultarContasReceberTool
    )
    
    HTTP_TOOLS_AVAILABLE = True
    logger.info("Ferramentas HTTP importadas com sucesso")
    
except ImportError as e:
    logger.warning(f"Ferramentas HTTP não disponíveis: {e}")
    HTTP_TOOLS_AVAILABLE = False
    config = None
    omie_client = None

class OmieToolRegistry:
    """Registro unificado de ferramentas Omie"""
    
    def __init__(self):
        self.tools = {}
        self.mcp_tools = []
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas as ferramentas disponíveis"""
        
        # Ferramentas básicas (sempre disponíveis)
        basic_tools = [
            {
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
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
                "name": "consultar_tipos_documento",
                "description": "Consulta tipos de documento no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string", "description": "Código do tipo documento (opcional)"}
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
            }
        ]
        
        # Registrar ferramentas básicas
        for tool in basic_tools:
            self.tools[tool["name"]] = tool
            self.mcp_tools.append(tool)
        
        # Registrar ferramentas HTTP avançadas se disponíveis
        if HTTP_TOOLS_AVAILABLE:
            try:
                http_tools = [
                    ConsultarCategoriasTool(),
                    ConsultarDepartamentosTool(),
                    ConsultarTiposDocumentoTool(),
                    ConsultarContasPagarTool(),
                    ConsultarContasReceberTool()
                ]
                
                for tool in http_tools:
                    tool_def = tool.get_tool_definition()
                    self.tools[tool_def["name"]] = {
                        "definition": tool_def,
                        "handler": tool,
                        "type": "http"
                    }
                
                logger.info(f"Registradas {len(http_tools)} ferramentas HTTP avançadas")
            except Exception as e:
                logger.warning(f"Erro ao registrar ferramentas HTTP: {e}")
        
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
            # Ferramenta básica
            if isinstance(tool, dict) and "handler" not in tool:
                return await self._call_basic_tool(name, arguments)
            
            # Ferramenta HTTP avançada
            elif isinstance(tool, dict) and tool.get("type") == "http":
                handler = tool["handler"]
                result = await handler.safe_execute(arguments)
                return result
            
            else:
                return json.dumps({
                    "erro": f"Tipo de ferramenta não suportado: {name}"
                }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {name}: {e}")
            return json.dumps({
                "erro": f"Erro ao executar {name}",
                "detalhes": str(e)
            }, ensure_ascii=False, indent=2)
    
    async def _call_basic_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa ferramenta básica"""
        
        if name == "testar_conexao":
            return json.dumps({
                "status": "conectado",
                "servidor": "Omie ERP",
                "modo": "híbrido",
                "ferramentas_disponíveis": len(self.tools),
                "ferramentas_http": HTTP_TOOLS_AVAILABLE,
                "configuracao": config is not None
            }, ensure_ascii=False, indent=2)
        
        # Para outras ferramentas básicas, simular resposta
        return json.dumps({
            "ferramenta": name,
            "argumentos": arguments,
            "modo": "simulação",
            "nota": "Configure src/client/omie_client.py para funcionalidade completa"
        }, ensure_ascii=False, indent=2)

class OmieMCPServer:
    """Servidor MCP para Omie ERP - Protocolo STDIO"""
    
    def __init__(self):
        self.tool_registry = OmieToolRegistry()
        logger.info("Servidor MCP STDIO inicializado")
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição ou gera um padrão"""
        request_id = request.get("id")
        if request_id is None:
            return "unknown"
        return str(request_id)
    
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
                            "name": "omie-mcp-server",
                            "version": "2.0.0-hybrid"
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

class OmieHTTPServer:
    """Servidor HTTP para Omie ERP"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Omie MCP Server",
            description="Servidor MCP Híbrido para integração com Omie ERP",
            version="2.0.0-hybrid"
        )
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.tool_registry = OmieToolRegistry()
        self._setup_routes()
        logger.info("Servidor HTTP inicializado")
    
    def _setup_routes(self):
        """Configura rotas HTTP"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "Omie MCP Server",
                "version": "2.0.0-hybrid",
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
                    "name": "omie-mcp-server",
                    "version": "2.0.0-hybrid"
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
            """Server-Sent Events endpoint para N8N"""
            async def event_generator():
                try:
                    while True:
                        # Enviar status do servidor
                        status_event = {
                            "event": "server_status",
                            "data": {
                                "timestamp": time.time(),
                                "status": "active",
                                "tools_available": len(self.tool_registry.tools),
                                "mode": "hybrid"
                            }
                        }
                        yield f"data: {json.dumps(status_event)}\n\n"
                        
                        # Aguardar 30 segundos antes do próximo evento
                        await asyncio.sleep(30)
                        
                except Exception as e:
                    logger.error(f"Erro no SSE stream: {e}")
                    error_event = {
                        "event": "error",
                        "data": {"error": str(e), "timestamp": time.time()}
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        
        @self.app.get("/sse/tools/{tool_name}")
        async def sse_tool_stream(tool_name: str):
            """SSE endpoint para execução de ferramentas específicas"""
            async def tool_event_generator():
                try:
                    # Evento de início
                    start_event = {
                        "event": "tool_start",
                        "data": {
                            "tool_name": tool_name,
                            "timestamp": time.time(),
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
                            "timestamp": time.time(),
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
                            "timestamp": time.time(),
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
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
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
    parser = argparse.ArgumentParser(description="Servidor MCP Híbrido Omie ERP")
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
        server = OmieMCPServer()
        asyncio.run(server.run())
    
    elif args.mode == "http":
        # Modo HTTP para integrações web
        server = OmieHTTPServer()
        server.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()