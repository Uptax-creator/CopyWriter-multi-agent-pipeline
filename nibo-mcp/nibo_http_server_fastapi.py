#!/usr/bin/env python3
"""
Servidor HTTP FastAPI para Nibo MCP
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
logger = logging.getLogger("nibo-fastapi")

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.nibo_client import NiboClient
    from src.core.credentials_manager import CredentialsManager
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    logger.info("Tentando importar versão simplificada...")
    try:
        # Fallback para versão simplificada
        import requests
        
        class SimpleNiboClient:
            def __init__(self, credentials_manager):
                self.credentials = credentials_manager
                
            def testar_conexao(self):
                return {"status": "ok", "message": "Conexão simulada"}
                
            def consultar_categorias(self, **kwargs):
                return {"categorias": [], "total": 0}
        
        NiboClient = SimpleNiboClient
        
    except Exception as e2:
        logger.error(f"Erro crítico: {e2}")
        sys.exit(1)

app = FastAPI(
    title="Nibo MCP API",
    description="API REST para integração com Nibo ERP via MCP",
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

# Cliente Nibo global
nibo_client = None
credentials_manager = None

@app.on_event("startup")
async def startup_event():
    """Inicializar cliente Nibo"""
    global nibo_client, credentials_manager
    try:
        credentials_manager = CredentialsManager()
        nibo_client = NiboClient(credentials_manager)
        logger.info("Cliente Nibo inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente Nibo: {e}")
        raise

# Definição das ferramentas
TOOLS_REGISTRY = [
    {
        "name": "testar_conexao",
        "description": "Testa conexão com a API do Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "consultar_categorias",
        "description": "Consulta categorias cadastradas no Nibo",
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
        "name": "consultar_centros_custo",
        "description": "Consulta centros de custo cadastrados no Nibo",
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
        "name": "consultar_socios",
        "description": "Consulta sócios da empresa no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do sócio (filtro)"},
                "documento": {"type": "string", "description": "Documento do sócio (filtro)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "consultar_clientes",
        "description": "Consulta clientes cadastrados no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do cliente (filtro)"},
                "documento": {"type": "string", "description": "Documento do cliente (filtro)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "consultar_fornecedores",
        "description": "Consulta fornecedores cadastrados no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do fornecedor (filtro)"},
                "documento": {"type": "string", "description": "Documento do fornecedor (filtro)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "consultar_contas_pagar",
        "description": "Consulta contas a pagar no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "valor_minimo": {"type": "number", "description": "Valor mínimo"},
                "valor_maximo": {"type": "number", "description": "Valor máximo"},
                "data_inicio": {"type": "string", "description": "Data início (YYYY-MM-DD)"},
                "data_fim": {"type": "string", "description": "Data fim (YYYY-MM-DD)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "consultar_contas_receber",
        "description": "Consulta contas a receber no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "valor_minimo": {"type": "number", "description": "Valor mínimo"},
                "valor_maximo": {"type": "number", "description": "Valor máximo"},
                "data_inicio": {"type": "string", "description": "Data início (YYYY-MM-DD)"},
                "data_fim": {"type": "string", "description": "Data fim (YYYY-MM-DD)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
            },
            "required": []
        }
    },
    {
        "name": "incluir_socio",
        "description": "Inclui novo sócio na empresa",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do sócio"},
                "documento": {"type": "string", "description": "CPF/CNPJ do sócio"},
                "participacao": {"type": "number", "description": "Percentual de participação"},
                "email": {"type": "string", "description": "Email do sócio"}
            },
            "required": ["nome", "documento", "participacao"]
        }
    },
    {
        "name": "incluir_cliente",
        "description": "Inclui novo cliente no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do cliente"},
                "documento": {"type": "string", "description": "CPF/CNPJ do cliente"},
                "email": {"type": "string", "description": "Email do cliente"},
                "telefone": {"type": "string", "description": "Telefone do cliente"}
            },
            "required": ["nome", "documento"]
        }
    },
    {
        "name": "incluir_fornecedor",
        "description": "Inclui novo fornecedor no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome do fornecedor"},
                "documento": {"type": "string", "description": "CPF/CNPJ do fornecedor"},
                "email": {"type": "string", "description": "Email do fornecedor"},
                "telefone": {"type": "string", "description": "Telefone do fornecedor"}
            },
            "required": ["nome", "documento"]
        }
    },
    {
        "name": "incluir_conta_pagar",
        "description": "Inclui nova conta a pagar no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fornecedor_id": {"type": "string", "description": "ID do fornecedor"},
                "valor": {"type": "number", "description": "Valor da conta"},
                "data_vencimento": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                "descricao": {"type": "string", "description": "Descrição"}
            },
            "required": ["fornecedor_id", "valor", "data_vencimento"]
        }
    },
    {
        "name": "incluir_conta_receber",
        "description": "Inclui nova conta a receber no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "string", "description": "ID do cliente"},
                "valor": {"type": "number", "description": "Valor da conta"},
                "data_vencimento": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                "descricao": {"type": "string", "description": "Descrição"}
            },
            "required": ["cliente_id", "valor", "data_vencimento"]
        }
    },
    {
        "name": "alterar_cliente",
        "description": "Altera dados de cliente no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "string", "description": "ID do cliente"},
                "nome": {"type": "string", "description": "Nome do cliente"},
                "email": {"type": "string", "description": "Email do cliente"},
                "telefone": {"type": "string", "description": "Telefone do cliente"}
            },
            "required": ["cliente_id"]
        }
    },
    {
        "name": "alterar_fornecedor",
        "description": "Altera dados de fornecedor no Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fornecedor_id": {"type": "string", "description": "ID do fornecedor"},
                "nome": {"type": "string", "description": "Nome do fornecedor"},
                "email": {"type": "string", "description": "Email do fornecedor"},
                "telefone": {"type": "string", "description": "Telefone do fornecedor"}
            },
            "required": ["fornecedor_id"]
        }
    },
    {
        "name": "excluir_cliente",
        "description": "Exclui cliente do Nibo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "string", "description": "ID do cliente"}
            },
            "required": ["cliente_id"]
        }
    }
]

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Informações do servidor"""
    empresa_info = "N/A"
    if credentials_manager:
        try:
            empresa_info = credentials_manager.get_company_info()["name"]
        except:
            pass
    
    return {
        "service": "Nibo MCP API",
        "version": "2.0.0-fastapi",
        "status": "online",
        "empresa": empresa_info,
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
    
    if nibo_client is None:
        raise HTTPException(status_code=500, detail="Cliente Nibo não inicializado")
    
    try:
        # Executar ferramenta
        if tool_name == "testar_conexao":
            result = nibo_client.testar_conexao()
        elif tool_name == "consultar_categorias":
            result = nibo_client.consultar_categorias(**payload.arguments)
        elif tool_name == "consultar_centros_custo":
            result = nibo_client.consultar_centros_custo(**payload.arguments)
        elif tool_name == "consultar_socios":
            result = nibo_client.consultar_socios(**payload.arguments)
        elif tool_name == "consultar_clientes":
            result = nibo_client.consultar_clientes(**payload.arguments)
        elif tool_name == "consultar_fornecedores":
            result = nibo_client.consultar_fornecedores(**payload.arguments)
        elif tool_name == "consultar_contas_pagar":
            result = nibo_client.consultar_contas_pagar(**payload.arguments)
        elif tool_name == "consultar_contas_receber":
            result = nibo_client.consultar_contas_receber(**payload.arguments)
        elif tool_name == "incluir_socio":
            result = nibo_client.incluir_socio(**payload.arguments)
        elif tool_name == "incluir_cliente":
            result = nibo_client.incluir_cliente(**payload.arguments)
        elif tool_name == "incluir_fornecedor":
            result = nibo_client.incluir_fornecedor(**payload.arguments)
        elif tool_name == "incluir_conta_pagar":
            result = nibo_client.incluir_conta_pagar(**payload.arguments)
        elif tool_name == "incluir_conta_receber":
            result = nibo_client.incluir_conta_receber(**payload.arguments)
        elif tool_name == "alterar_cliente":
            result = nibo_client.alterar_cliente(**payload.arguments)
        elif tool_name == "alterar_fornecedor":
            result = nibo_client.alterar_fornecedor(**payload.arguments)
        elif tool_name == "excluir_cliente":
            result = nibo_client.excluir_cliente(**payload.arguments)
        else:
            raise HTTPException(status_code=501, detail=f"Ferramenta '{tool_name}' não implementada")
        
        return ToolResponse(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
        return ToolResponse(success=False, error=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de saúde para monitoramento"""
    return {"status": "healthy", "service": "nibo-mcp-api"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Servidor HTTP FastAPI para Nibo MCP')
    parser.add_argument('--port', type=int, default=3002, help='Porta do servidor')
    parser.add_argument('--host', default='127.0.0.1', help='Host do servidor')
    args = parser.parse_args()
    
    logger.info(f"🚀 Iniciando servidor Nibo FastAPI em http://{args.host}:{args.port}")
    logger.info(f"📋 {len(TOOLS_REGISTRY)} ferramentas disponíveis")
    logger.info(f"📖 Documentação disponível em http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")