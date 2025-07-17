#!/usr/bin/env python3
"""
Servidor HTTP FastAPI para Omie MCP
Versão profissional para integração com N8N, Zapier e outros sistemas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import logging
import sys
import os
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-fastapi")

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.client.omie_client_fixed import OmieClient
except ImportError:
    try:
        from src.client.omie_client import OmieClient
    except ImportError:
        logger.error("Erro: Não foi possível importar OmieClient")
        sys.exit(1)

app = FastAPI(
    title="Omie MCP API",
    description="API REST para integração com Omie ERP via MCP",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ToolArguments(BaseModel):
    arguments: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None

class ToolInfo(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolsListResponse(BaseModel):
    tools: List[ToolInfo]
    count: int

# Cliente Omie global
omie_client = None

@app.on_event("startup")
async def startup_event():
    """Inicializar cliente Omie"""
    global omie_client
    try:
        omie_client = OmieClient()
        logger.info("Cliente Omie inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente Omie: {e}")
        raise

# Definição das ferramentas
TOOLS_REGISTRY = [
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
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
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
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
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
            },
            "required": []
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
            },
            "required": []
        }
    },
    {
        "name": "consultar_clientes",
        "description": "Consulta clientes cadastrados no Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "consultar_fornecedores",
        "description": "Consulta fornecedores cadastrados no Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "cadastrar_cliente_fornecedor",
        "description": "Cadastra cliente ou fornecedor no Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "razao_social": {"type": "string", "description": "Razão social"},
                "nome_fantasia": {"type": "string", "description": "Nome fantasia"},
                "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                "telefone1_ddd": {"type": "string", "description": "DDD do telefone"},
                "telefone1_numero": {"type": "string", "description": "Número do telefone"},
                "email": {"type": "string", "description": "Email"}
            },
            "required": ["razao_social", "cnpj_cpf"]
        }
    },
    {
        "name": "criar_conta_pagar",
        "description": "Cria conta a pagar no Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigo_cliente_fornecedor": {"type": "string", "description": "Código do fornecedor"},
                "valor_documento": {"type": "number", "description": "Valor do documento"},
                "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                "observacao": {"type": "string", "description": "Observação"}
            },
            "required": ["codigo_cliente_fornecedor", "valor_documento", "data_vencimento"]
        }
    },
    {
        "name": "criar_conta_receber",
        "description": "Cria conta a receber no Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigo_cliente": {"type": "string", "description": "Código do cliente"},
                "valor_documento": {"type": "number", "description": "Valor do documento"},
                "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                "observacao": {"type": "string", "description": "Observação"}
            },
            "required": ["codigo_cliente", "valor_documento", "data_vencimento"]
        }
    }
]

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Informações do servidor"""
    return {
        "service": "Omie MCP API",
        "version": "2.0.0-fastapi",
        "status": "online",
        "tools_count": len(TOOLS_REGISTRY),
        "endpoints": {
            "tools": "/tools",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/tools", response_model=ToolsListResponse)
async def list_tools():
    """Lista todas as ferramentas disponíveis"""
    return ToolsListResponse(
        tools=[ToolInfo(**tool) for tool in TOOLS_REGISTRY],
        count=len(TOOLS_REGISTRY)
    )

@app.post("/tools/{tool_name}", response_model=ToolResponse)
async def call_tool(tool_name: str, payload: ToolArguments):
    """Executa uma ferramenta específica"""
    
    # Verificar se ferramenta existe
    tool_exists = any(tool["name"] == tool_name for tool in TOOLS_REGISTRY)
    if not tool_exists:
        raise HTTPException(status_code=404, detail=f"Ferramenta '{tool_name}' não encontrada")
    
    if omie_client is None:
        raise HTTPException(status_code=500, detail="Cliente Omie não inicializado")
    
    try:
        # Executar ferramenta
        if tool_name == "testar_conexao":
            result = omie_client.testar_conexao()
        elif tool_name == "consultar_categorias":
            result = omie_client.consultar_categorias(**payload.arguments)
        elif tool_name == "consultar_departamentos":
            result = omie_client.consultar_departamentos(**payload.arguments)
        elif tool_name == "consultar_contas_pagar":
            result = omie_client.consultar_contas_pagar(**payload.arguments)
        elif tool_name == "consultar_contas_receber":
            result = omie_client.consultar_contas_receber(**payload.arguments)
        elif tool_name == "consultar_clientes":
            result = omie_client.consultar_clientes(**payload.arguments)
        elif tool_name == "consultar_fornecedores":
            result = omie_client.consultar_fornecedores(**payload.arguments)
        elif tool_name == "cadastrar_cliente_fornecedor":
            result = omie_client.cadastrar_cliente_fornecedor(**payload.arguments)
        elif tool_name == "criar_conta_pagar":
            result = omie_client.criar_conta_pagar(**payload.arguments)
        elif tool_name == "criar_conta_receber":
            result = omie_client.criar_conta_receber(**payload.arguments)
        else:
            raise HTTPException(status_code=501, detail=f"Ferramenta '{tool_name}' não implementada")
        
        return ToolResponse(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
        return ToolResponse(success=False, error=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de saúde para monitoramento"""
    return {"status": "healthy", "service": "omie-mcp-api"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Servidor HTTP FastAPI para Omie MCP')
    parser.add_argument('--port', type=int, default=3001, help='Porta do servidor')
    parser.add_argument('--host', default='127.0.0.1', help='Host do servidor')
    args = parser.parse_args()
    
    logger.info(f"🚀 Iniciando servidor Omie FastAPI em http://{args.host}:{args.port}")
    logger.info(f"📋 {len(TOOLS_REGISTRY)} ferramentas disponíveis")
    logger.info(f"📖 Documentação disponível em http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")