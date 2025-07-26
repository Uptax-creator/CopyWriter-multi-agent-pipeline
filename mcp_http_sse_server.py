#!/usr/bin/env python3
"""
🌐 OMIE MCP - SERVIDOR HTTP/SSE
Implementação para VS Code, N8N, Microsoft Copilot e outras plataformas
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.client.omie_client import OmieClient
except ImportError:
    print("⚠️ OmieClient não encontrado - usando mock")
    OmieClient = None

# FastAPI app
app = FastAPI(
    title="Omie MCP HTTP/SSE Server",
    description="Servidor MCP com suporte HTTP e Server-Sent Events",
    version="1.0.0"
)

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente global
omie_client = None

# Ferramentas disponíveis
AVAILABLE_TOOLS = {
    "consultar_categorias": {
        "description": "Consulta categorias cadastradas no Omie ERP",
        "parameters": {
            "pagina": {"type": "integer", "default": 1},
            "registros_por_pagina": {"type": "integer", "default": 50}
        }
    },
    "listar_clientes": {
        "description": "Lista clientes cadastrados no Omie ERP", 
        "parameters": {
            "pagina": {"type": "integer", "default": 1},
            "filtro_nome": {"type": "string", "optional": True}
        }
    },
    "consultar_contas_pagar": {
        "description": "Consulta contas a pagar com filtros de status",
        "parameters": {
            "status": {"type": "string", "default": "todos", "enum": ["vencido", "a_vencer", "pago", "todos"]},
            "pagina": {"type": "integer", "default": 1}
        }
    },
    "consultar_contas_receber": {
        "description": "Consulta contas a receber com filtros de status",
        "parameters": {
            "status": {"type": "string", "default": "todos", "enum": ["vencido", "a_vencer", "recebido", "todos"]},
            "pagina": {"type": "integer", "default": 1}
        }
    }
}

async def initialize_omie_client():
    """Inicializa cliente Omie"""
    global omie_client
    if omie_client is None and OmieClient:
        omie_client = OmieClient()
    return omie_client

@app.on_event("startup")
async def startup_event():
    """Inicialização do servidor"""
    await initialize_omie_client()
    print("🚀 Servidor MCP HTTP/SSE iniciado")

# ============================================================================
# ENDPOINTS MCP PROTOCOL
# ============================================================================

@app.get("/mcp/initialize")
async def mcp_initialize():
    """Inicialização MCP"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {},
            "prompts": {}
        },
        "serverInfo": {
            "name": "omie-mcp-http",
            "version": "1.0.0"
        }
    }

@app.get("/mcp/tools/list")
async def mcp_list_tools():
    """Lista ferramentas disponíveis"""
    tools = []
    for name, info in AVAILABLE_TOOLS.items():
        tools.append({
            "name": name,
            "description": info["description"],
            "inputSchema": {
                "type": "object",
                "properties": info["parameters"],
                "required": []
            }
        })
    
    return {"tools": tools}

@app.post("/mcp/tools/call")
async def mcp_call_tool(request: Dict[str, Any]):
    """Chama uma ferramenta MCP"""
    try:
        tool_name = request.get("name")
        arguments = request.get("arguments", {})
        
        if tool_name not in AVAILABLE_TOOLS:
            raise HTTPException(status_code=400, detail=f"Tool {tool_name} not found")
        
        result = await execute_tool(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS HTTP DIRETOS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Omie MCP HTTP/SSE Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp/*",
            "http": "/api/*",
            "sse": "/events",
            "tools": "/tools/*"
        },
        "tools_count": len(AVAILABLE_TOOLS),
        "status": "online"
    }

@app.get("/api/tools")
async def api_list_tools():
    """Lista ferramentas via API REST"""
    return {
        "tools": list(AVAILABLE_TOOLS.keys()),
        "details": AVAILABLE_TOOLS,
        "total": len(AVAILABLE_TOOLS)
    }

@app.post("/api/tools/{tool_name}")
async def api_call_tool(tool_name: str, payload: Dict[str, Any] = None):
    """Chama ferramenta via API REST"""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    try:
        arguments = payload or {}
        result = await execute_tool(tool_name, arguments)
        
        return {
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "tool": tool_name,
            "error": str(e),
            "success": False
        })

# ============================================================================
# SERVER-SENT EVENTS (SSE)
# ============================================================================

@app.get("/events")
async def event_stream(request: Request):
    """Stream de eventos Server-Sent Events"""
    
    async def generate_events():
        # Enviar evento de conexão
        connection_id = str(uuid.uuid4())
        yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Simular eventos periódicos
        counter = 0
        while True:
            if await request.is_disconnected():
                break
            
            # Evento de heartbeat a cada 30 segundos
            counter += 1
            event = {
                "type": "heartbeat",
                "counter": counter,
                "server_status": "online",
                "tools_available": len(AVAILABLE_TOOLS),
                "timestamp": datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(30)
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/events/tool-call")
async def sse_tool_call(tool_request: Dict[str, Any]):
    """Executa ferramenta e retorna via SSE"""
    tool_name = tool_request.get("name")
    arguments = tool_request.get("arguments", {})
    callback_id = tool_request.get("callback_id", str(uuid.uuid4()))
    
    if tool_name not in AVAILABLE_TOOLS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Tool {tool_name} not found", "callback_id": callback_id}
        )
    
    try:
        result = await execute_tool(tool_name, arguments)
        
        return {
            "callback_id": callback_id,
            "tool": tool_name,
            "result": result,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "callback_id": callback_id,
                "tool": tool_name,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }
        )

# ============================================================================
# EXECUTORES DE FERRAMENTAS
# ============================================================================

async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Executa uma ferramenta específica"""
    client = await initialize_omie_client()
    
    if not client:
        # Mock para desenvolvimento sem credenciais
        return create_mock_response(tool_name, arguments)
    
    try:
        if tool_name == "consultar_categorias":
            return await client.consultar_categorias(arguments)
        elif tool_name == "listar_clientes":
            return await client.listar_clientes(arguments)
        elif tool_name == "consultar_contas_pagar":
            return await client.consultar_contas_pagar(arguments)
        elif tool_name == "consultar_contas_receber":
            return await client.consultar_contas_receber(arguments)
        else:
            raise ValueError(f"Tool {tool_name} not implemented")
            
    except Exception as e:
        # Fallback para mock em caso de erro
        return create_mock_response(tool_name, arguments, error=str(e))

def create_mock_response(tool_name: str, arguments: Dict[str, Any], error: str = None) -> Dict[str, Any]:
    """Cria resposta mock para desenvolvimento"""
    base_response = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "mock": True
    }
    
    if error:
        base_response["error"] = error
        base_response["status"] = "error_with_fallback"
    
    # Mock específico por ferramenta
    if tool_name == "consultar_categorias":
        base_response["data"] = {
            "categoria": [
                {"codigo": "001", "descricao": "Receita de Vendas", "tipo": "R"},
                {"codigo": "002", "descricao": "Despesa Administrativa", "tipo": "D"}
            ],
            "total": 2
        }
    elif tool_name == "listar_clientes":
        base_response["data"] = {
            "clientes_cadastro": [
                {"codigo": 1, "nome_fantasia": "Empresa Teste", "razao_social": "Empresa Teste Ltda"},
                {"codigo": 2, "nome_fantasia": "Cliente Demo", "razao_social": "Cliente Demo SA"}
            ],
            "total": 2
        }
    else:
        base_response["data"] = {"message": f"Mock response for {tool_name}"}
    
    return base_response

# ============================================================================
# INTEGRAÇÕES ESPECÍFICAS
# ============================================================================

@app.get("/integrations/vscode")
async def vscode_integration_info():
    """Informações para integração VS Code"""
    return {
        "integration": "VS Code",
        "mcp_endpoint": "http://localhost:8000/mcp/",
        "http_endpoint": "http://localhost:8000/api/",
        "sse_endpoint": "http://localhost:8000/events",
        "tools": list(AVAILABLE_TOOLS.keys()),
        "setup_instructions": [
            "1. Instalar extensão MCP no VS Code",
            "2. Configurar endpoint: http://localhost:8000/mcp/",
            "3. Testar conexão com /mcp/initialize",
            "4. Usar ferramentas via Command Palette"
        ]
    }

@app.get("/integrations/n8n")
async def n8n_integration_info():
    """Informações para integração N8N"""
    return {
        "integration": "N8N",
        "webhook_endpoint": "http://localhost:8000/api/tools/{tool_name}",
        "method": "POST",
        "content_type": "application/json",
        "tools": AVAILABLE_TOOLS,
        "setup_instructions": [
            "1. Criar HTTP Request node no N8N",
            "2. URL: http://localhost:8000/api/tools/TOOL_NAME",
            "3. Method: POST",
            "4. Headers: Content-Type: application/json",
            "5. Body: JSON com parâmetros da ferramenta"
        ]
    }

@app.get("/integrations/copilot")
async def copilot_integration_info():
    """Informações para integração Microsoft Copilot"""
    return {
        "integration": "Microsoft Copilot",
        "api_endpoint": "http://localhost:8000/api/",
        "mcp_endpoint": "http://localhost:8000/mcp/",
        "openapi_spec": "http://localhost:8000/docs",
        "tools": AVAILABLE_TOOLS,
        "setup_instructions": [
            "1. Configurar Copilot Plugin manifest",
            "2. API URL: http://localhost:8000/api/",
            "3. Import OpenAPI spec from /docs",
            "4. Configure authentication if needed",
            "5. Test tools via Copilot interface"
        ]
    }

# ============================================================================
# SERVIDOR PRINCIPAL
# ============================================================================

def main():
    """Inicia servidor HTTP/SSE"""
    print("🌐 OMIE MCP - SERVIDOR HTTP/SSE")
    print("=" * 50)
    print("🔧 Multi-platform support:")
    print("   • VS Code MCP Extension")
    print("   • N8N HTTP Nodes") 
    print("   • Microsoft Copilot")
    print("   • Docker containers")
    print("   • Direct HTTP API")
    print("   • Server-Sent Events")
    print()
    print("🌐 Endpoints:")
    print("   • MCP Protocol: http://localhost:8000/mcp/")
    print("   • HTTP API: http://localhost:8000/api/")
    print("   • SSE Events: http://localhost:8000/events")
    print("   • Documentation: http://localhost:8000/docs")
    print()
    print("🚀 Starting server...")
    
    uvicorn.run(
        "mcp_http_sse_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()