#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - VERSÃO MODULAR
Servidor organizado em módulos para melhor manutenibilidade
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Importar módulos locais
from modules.models import *
from modules.omie_client import OmieClient
from modules.handlers import OmieHandlers
from modules.validators import OmieValidators

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Credenciais do Omie - prioridade: variáveis de ambiente > arquivo credentials.json
OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")

# Se não há variáveis de ambiente, tentar carregar do arquivo credentials.json
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    try:
        credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                credentials = json.load(f)
                OMIE_APP_KEY = OMIE_APP_KEY or credentials.get("app_key")
                OMIE_APP_SECRET = OMIE_APP_SECRET or credentials.get("app_secret")
                print(f"✅ Credenciais carregadas do arquivo: {credentials_path}")
        else:
            print(f"⚠️  Arquivo credentials.json não encontrado em: {credentials_path}")
    except Exception as e:
        print(f"⚠️  Erro ao carregar credentials.json: {e}")

# Verificar se temos credenciais válidas
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    print("""❌ ERRO: Credenciais Omie não encontradas!

Opções para configurar:
1. Variáveis de ambiente:
   export OMIE_APP_KEY="sua_app_key"
   export OMIE_APP_SECRET="seu_app_secret"

2. Arquivo credentials.json:
   {
     "app_key": "sua_app_key",
     "app_secret": "seu_app_secret"
   }
""")
    sys.exit(1)

OMIE_BASE_URL = "https://app.omie.com.br/api/v1"
MCP_SERVER_PORT = 8000

# ============================================================================
# CONFIGURAÇÃO DE LOGS
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("omie-mcp-modular")

# ============================================================================
# INSTÂNCIAS GLOBAIS
# ============================================================================

omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET, OMIE_BASE_URL)
omie_handlers = OmieHandlers(omie_client)
omie_validators = OmieValidators(omie_client)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Versão Modular",
    description="Servidor MCP HTTP para Omie ERP com arquitetura modular",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz com informações do servidor"""
    return {
        "service": "Omie MCP Server - Versão Modular",
        "status": "running",
        "version": "2.0.0",
        "architecture": "modular",
        "modules": [
            "models - Modelos Pydantic",
            "omie_client - Cliente HTTP para API Omie",
            "handlers - Handlers das ferramentas MCP",
            "validators - Validadores de códigos"
        ],
        "tools": [
            "cadastrar_cliente_fornecedor",
            "consultar_categorias",
            "consultar_departamentos", 
            "consultar_tipos_documento",
            "criar_conta_pagar",
            "atualizar_conta_pagar",
            "criar_conta_receber",
            "atualizar_conta_receber",
            "consultar_contas_pagar",
            "consultar_contas_receber"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    """Endpoint principal MCP"""
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "omie-mcp-modular", "version": "2.0.0"}
                }
            )
        
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [
                        {
                            "name": "cadastrar_cliente_fornecedor",
                            "description": "Cadastra cliente/fornecedor no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "razao_social": {"type": "string", "description": "Razão social"},
                                    "cnpj_cpf": {"type": "string", "description": "CNPJ/CPF"},
                                    "email": {"type": "string", "description": "E-mail"},
                                    "tipo_cliente": {"type": "string", "enum": ["cliente", "fornecedor", "ambos"]},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia"},
                                    "cidade": {"type": "string", "description": "Cidade"},
                                    "estado": {"type": "string", "description": "Estado"}
                                },
                                "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"]
                            }
                        },
                        {
                            "name": "consultar_categorias",
                            "description": "Consulta categorias de receita/despesa",
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
                            "description": "Consulta departamentos",
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
                            "description": "Consulta tipos de documentos",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "consultar_contas_pagar",
                            "description": "Consulta contas a pagar",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor"},
                                    "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                                    "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                                    "pagina": {"type": "integer", "description": "Página", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                                }
                            }
                        },
                        {
                            "name": "consultar_contas_receber",
                            "description": "Consulta contas a receber",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente"},
                                    "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                                    "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                                    "pagina": {"type": "integer", "description": "Página", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                                }
                            }
                        }
                    ]
                }
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            # Roteamento para handlers
            if tool_name == "cadastrar_cliente_fornecedor":
                result = await omie_handlers.handle_cadastrar_cliente_fornecedor(arguments)
            elif tool_name == "consultar_categorias":
                result = await omie_handlers.handle_consultar_categorias(arguments)
            elif tool_name == "consultar_departamentos":
                result = await omie_handlers.handle_consultar_departamentos(arguments)
            elif tool_name == "consultar_tipos_documento":
                result = await omie_handlers.handle_consultar_tipos_documento(arguments)
            elif tool_name == "consultar_contas_pagar":
                result = await omie_handlers.handle_consultar_contas_pagar(arguments)
            elif tool_name == "consultar_contas_receber":
                result = await omie_handlers.handle_consultar_contas_receber(arguments)
            else:
                raise HTTPException(status_code=400, detail=f"Ferramenta desconhecida: {tool_name}")
            
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Método não suportado: {request.method}")
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint MCP: {e}")
        return MCPResponse(
            id=request.id,
            error={"code": -1, "message": str(e)}
        )

# ============================================================================
# ENDPOINTS DE TESTE
# ============================================================================

@app.get("/test/categorias")
async def test_categorias():
    """Endpoint para testar consulta de categorias"""
    result = await omie_handlers.handle_consultar_categorias({})
    return {"result": result}

@app.get("/test/departamentos")
async def test_departamentos():
    """Endpoint para testar consulta de departamentos"""
    result = await omie_handlers.handle_consultar_departamentos({})
    return {"result": result}

@app.get("/test/tipos-documento")
async def test_tipos_documento():
    """Endpoint para testar consulta de tipos de documentos"""
    result = await omie_handlers.handle_consultar_tipos_documento({})
    return {"result": result}

@app.post("/test/contas-pagar")
async def test_contas_pagar(request: ConsultaContasRequest):
    """Endpoint para testar consulta de contas a pagar"""
    result = await omie_handlers.handle_consultar_contas_pagar(request.dict())
    return {"result": result}

@app.post("/test/contas-receber")
async def test_contas_receber(request: ConsultaContasRequest):
    """Endpoint para testar consulta de contas a receber"""
    result = await omie_handlers.handle_consultar_contas_receber(request.dict())
    return {"result": result}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP modular"""
    
    print("🚀 Iniciando Servidor MCP HTTP para Omie ERP - VERSÃO MODULAR")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("📦 Arquitetura modular ativada:")
    print("   • modules/models.py - Modelos Pydantic")
    print("   • modules/omie_client.py - Cliente HTTP")
    print("   • modules/handlers.py - Handlers das ferramentas")
    print("   • modules/validators.py - Validadores de códigos")
    print("📡 Ferramentas disponíveis:")
    print("   • cadastrar_cliente_fornecedor")
    print("   • consultar_categorias")
    print("   • consultar_departamentos")
    print("   • consultar_tipos_documento")
    print("   • consultar_contas_pagar")
    print("   • consultar_contas_receber")
    print(f"✅ Servidor HTTP rodando em: http://localhost:{MCP_SERVER_PORT}")
    print(f"📖 Docs: http://localhost:{MCP_SERVER_PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()