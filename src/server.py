"""
Servidor HTTP MCP para Omie ERP - Estrutura Híbrida
"""

import asyncio
import sys
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar configuração e utilitários
from src.config import config
from src.utils.logger import logger
from src.utils.sanitizers import json_sanitizer

# Importar todas as ferramentas
from src.tools.consultas import (
    ConsultarCategoriasTool,
    ConsultarDepartamentosTool,
    ConsultarTiposDocumentoTool,
    ConsultarContasPagarTool,
    ConsultarContasReceberTool,
    ConsultarClientesTool,
    ConsultarFornecedoresTool,
    ConsultarClientePorCodigoTool,
    ConsultarFornecedorPorCodigoTool,
    BuscarDadosContatoClienteTool
)
from src.tools.cliente_tool import (
    IncluirClienteTool,
    IncluirFornecedorTool,
    AlterarClienteTool,
    AlterarFornecedorTool
)
from src.tools.contas_pagar import (
    IncluirContaPagarTool,
    AlterarContaPagarTool,
    ExcluirContaPagarTool
)
from src.tools.contas_receber import (
    IncluirContaReceberTool,
    AlterarContaReceberTool,
    ExcluirContaReceberTool
)

# ============================================================================
# CONFIGURAÇÃO DO SERVIDOR
# ============================================================================

app = FastAPI(
    title="Omie MCP Server",
    description="Servidor MCP HTTP para integração com Omie ERP",
    version="2.0.0",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REGISTRO DE FERRAMENTAS
# ============================================================================

class ToolRegistry:
    """Registro de todas as ferramentas disponíveis"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Registrar todas as ferramentas"""
        
        # Ferramentas de consulta
        self._register_tool(ConsultarCategoriasTool())
        self._register_tool(ConsultarDepartamentosTool())
        self._register_tool(ConsultarTiposDocumentoTool())
        self._register_tool(ConsultarContasPagarTool())
        self._register_tool(ConsultarContasReceberTool())
        self._register_tool(ConsultarClientesTool())
        self._register_tool(ConsultarFornecedoresTool())
        
        # Ferramentas de consulta avançada
        self._register_tool(ConsultarClientePorCodigoTool())
        self._register_tool(ConsultarFornecedorPorCodigoTool())
        self._register_tool(BuscarDadosContatoClienteTool())
        
        # Ferramentas de cliente/fornecedor
        self._register_tool(IncluirClienteTool())
        self._register_tool(IncluirFornecedorTool())
        self._register_tool(AlterarClienteTool())
        self._register_tool(AlterarFornecedorTool())
        
        # Ferramentas de contas a pagar
        self._register_tool(IncluirContaPagarTool())
        self._register_tool(AlterarContaPagarTool())
        self._register_tool(ExcluirContaPagarTool())
        
        # Ferramentas de contas a receber
        self._register_tool(IncluirContaReceberTool())
        self._register_tool(AlterarContaReceberTool())
        self._register_tool(ExcluirContaReceberTool())
        
        logger.info(f"Registradas {len(self.tools)} ferramentas")
    
    def _register_tool(self, tool):
        """Registrar uma ferramenta"""
        self.tools[tool.name] = tool
        logger.debug(f"Ferramenta registrada: {tool.name}")
    
    def get_tool(self, name: str):
        """Obter ferramenta por nome"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Obter todas as ferramentas"""
        return [tool.get_tool_definition() for tool in self.tools.values()]

# Instância global do registro
tool_registry = ToolRegistry()

# ============================================================================
# HANDLERS MCP
# ============================================================================

async def call_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executar ferramenta específica"""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Ferramenta '{tool_name}' não encontrada")
    
    try:
        result = await tool.safe_execute(arguments)
        return result
    except Exception as e:
        logger.error(f"Erro na ferramenta {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na ferramenta: {str(e)}")

# ============================================================================
# ENDPOINTS MCP
# ============================================================================

@app.post("/mcp/initialize")
async def mcp_initialize():
    """Inicializar sessão MCP"""
    logger.info("Sessão MCP inicializada")
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True}
        },
        "serverInfo": {
            "name": "omie-mcp-server",
            "version": "2.0.0"
        }
    }

@app.get("/mcp/tools")
async def mcp_list_tools():
    """Listar ferramentas disponíveis"""
    tools = tool_registry.get_all_tools()
    logger.info(f"Listadas {len(tools)} ferramentas")
    return {"tools": tools}

@app.post("/mcp/tools/{tool_name}")
async def mcp_call_tool(tool_name: str, request: Request):
    """Executar ferramenta específica"""
    try:
        body = await request.json()
        arguments = body.get("arguments", {})
        
        # Sanitizar argumentos
        sanitized_args = json_sanitizer.sanitize_json(arguments)
        
        # Executar ferramenta
        result = await call_tool(tool_name, sanitized_args)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS DE TESTE
# ============================================================================

@app.get("/test/categorias")
async def test_categorias():
    """Teste rápido de categorias"""
    try:
        result = await call_tool("consultar_categorias", {"pagina": 1, "registros_por_pagina": 5})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/departamentos")
async def test_departamentos():
    """Teste rápido de departamentos"""
    try:
        result = await call_tool("consultar_departamentos", {"pagina": 1, "registros_por_pagina": 5})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/tipos-documento")
async def test_tipos_documento():
    """Teste rápido de tipos de documento"""
    try:
        result = await call_tool("consultar_tipos_documento", {})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/contas-pagar")
async def test_contas_pagar():
    """Teste rápido de contas a pagar"""
    try:
        result = await call_tool("consultar_contas_pagar", {"pagina": 1, "registros_por_pagina": 5})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/contas-receber")
async def test_contas_receber():
    """Teste rápido de contas a receber"""
    try:
        result = await call_tool("consultar_contas_receber", {"pagina": 1, "registros_por_pagina": 5})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# ENDPOINTS DE INFORMAÇÃO
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check do servidor"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "config": config.to_dict()
    }

@app.get("/")
async def root():
    """Informações do servidor"""
    return {
        "name": "Omie MCP Server",
        "version": "2.0.0",
        "architecture": "hybrid",
        "endpoints": {
            "mcp": {
                "initialize": "/mcp/initialize",
                "tools": "/mcp/tools",
                "call_tool": "/mcp/tools/{tool_name}"
            },
            "test": {
                "categorias": "/test/categorias",
                "departamentos": "/test/departamentos",
                "tipos_documento": "/test/tipos-documento",
                "contas_pagar": "/test/contas-pagar",
                "contas_receber": "/test/contas-receber"
            },
            "info": {
                "health": "/health",
                "docs": "/docs" if config.debug else None
            }
        },
        "tools_count": len(tool_registry.tools)
    }

# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Tratamento de exceções HTTP"""
    logger.error(f"Erro HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Tratamento de exceções gerais"""
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Erro interno do servidor"}}
    )

# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

async def start_server():
    """Inicializar servidor HTTP"""
    logger.info("🚀 Iniciando Omie MCP Server v2.0.0")
    logger.info(f"🔧 Configuração: {config.to_dict()}")
    logger.info(f"🛠️  Ferramentas registradas: {len(tool_registry.tools)}")
    
    # Configurar uvicorn
    uvicorn_config = uvicorn.Config(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level=config.log_level.lower(),
        access_log=config.debug
    )
    
    # Iniciar servidor
    server = uvicorn.Server(uvicorn_config)
    await server.serve()

def main():
    """Função principal"""
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()