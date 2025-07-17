#!/usr/bin/env python3
"""
Servidor MCP HTTP Único para Omie ERP
Funciona com Claude Desktop e outras integrações via HTTP
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("omie-mcp-http")

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
                logger.info(f"Credenciais carregadas do arquivo: {credentials_path}")
    except Exception as e:
        logger.error(f"Erro ao carregar credentials.json: {e}")

# Verificar se temos credenciais válidas
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    logger.error("Credenciais Omie não encontradas!")
    sys.exit(1)

MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", 3000))
logger.info(f"Servidor MCP HTTP iniciando na porta {MCP_SERVER_PORT}")

# ============================================================================
# CLIENTE OMIE
# ============================================================================

import httpx

class OmieClient:
    """Cliente HTTP para comunicação com a API do Omie"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://app.omie.com.br/api/v1"
        
    async def _make_request(self, endpoint: str, call: str, params: Dict) -> Dict:
        """Faz requisição para a API do Omie"""
        
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        url = f"{self.base_url}/{endpoint}/"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Erro HTTP {response.status_code}: {response.text}"
                    )
                
                result = response.json()
                
                # Verificar se há erro do Omie
                if isinstance(result, dict) and "faultstring" in result:
                    error_msg = result.get("faultstring", "Erro Omie")
                    raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                
                return result
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
    
    async def consultar_categorias(self, params: Dict = None) -> Dict:
        """Consulta categorias de receita/despesa"""
        if params is None:
            params = {"pagina": 1, "registros_por_pagina": 50}
        return await self._make_request("geral/categorias", "ListarCategorias", params)
    
    async def consultar_departamentos(self, params: Dict = None) -> Dict:
        """Consulta departamentos"""
        if params is None:
            params = {"pagina": 1, "registros_por_pagina": 50}
        return await self._make_request("geral/departamentos", "ListarDepartamentos", params)
    
    async def consultar_tipos_documento(self, params: Dict = None) -> Dict:
        """Consulta tipos de documentos"""
        if params is None:
            params = {"codigo": ""}
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", params)
    
    async def consultar_contas_pagar(self, params: Dict) -> Dict:
        """Consulta contas a pagar com filtros"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", params)
    
    async def consultar_contas_receber(self, params: Dict) -> Dict:
        """Consulta contas a receber com filtros"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", params)
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    async def criar_conta_receber(self, dados: Dict) -> Dict:
        """Cria conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "IncluirContaReceber", dados)

# ============================================================================
# HANDLERS
# ============================================================================

class OmieHandlers:
    """Handlers para as ferramentas do Omie"""
    
    def __init__(self, omie_client: OmieClient):
        self.omie_client = omie_client
    
    async def handle_consultar_categorias(self, args: Dict) -> str:
        """Handler para consultar categorias"""
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 50)
        }
        
        resultado = await self.omie_client.consultar_categorias(params)
        categorias = resultado.get("categoria_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if categorias:
            lista_categorias = []
            for categoria in categorias:
                codigo = categoria.get("codigo", "N/A")
                descricao = categoria.get("descricao", "N/A")
                lista_categorias.append(f"• {codigo} - {descricao}")
            
            return f"📋 Categorias encontradas: {total}\n\n" + "\n".join(lista_categorias) + "\n\n💡 Use os códigos acima para criar contas a pagar/receber"
        else:
            return "❌ Nenhuma categoria encontrada"
    
    async def handle_consultar_departamentos(self, args: Dict) -> str:
        """Handler para consultar departamentos"""
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 50)
        }
        
        resultado = await self.omie_client.consultar_departamentos(params)
        departamentos = resultado.get("departamentos", [])
        total = resultado.get("total_de_registros", 0)
        
        if departamentos:
            lista_departamentos = []
            for departamento in departamentos:
                codigo = departamento.get("codigo", "N/A")
                descricao = departamento.get("descricao", "N/A")
                estrutura = departamento.get("estrutura", "N/A")
                inativo = departamento.get("inativo", "N")
                status = "🔴 Inativo" if inativo == "S" else "🟢 Ativo"
                lista_departamentos.append(f"• {codigo} - {descricao} ({estrutura}) {status}")
            
            return f"🏢 Departamentos encontrados: {total}\n\n" + "\n".join(lista_departamentos) + "\n\n💡 Use os códigos acima para distribuir custos nas contas"
        else:
            return "❌ Nenhum departamento encontrado"
    
    async def handle_consultar_tipos_documento(self, args: Dict) -> str:
        """Handler para consultar tipos de documentos"""
        resultado = await self.omie_client.consultar_tipos_documento({})
        tipos = resultado.get("tipo_documento_cadastro", [])
        
        if tipos:
            lista_tipos = []
            for tipo in tipos:
                codigo = tipo.get("codigo", "N/A")
                descricao = tipo.get("descricao", "N/A")
                lista_tipos.append(f"• {codigo} - {descricao}")
            
            return f"📄 Tipos de documentos encontrados: {len(tipos)}\n\n" + "\n".join(lista_tipos) + "\n\n💡 Use os códigos acima para classificar documentos"
        else:
            return "❌ Nenhum tipo de documento encontrado"
    
    async def handle_consultar_contas_pagar(self, args: Dict) -> str:
        """Handler para consultar contas a pagar"""
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 20)
        }
        
        # Adicionar filtros se fornecidos
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await self.omie_client.consultar_contas_pagar(params)
        contas = resultado.get("conta_pagar_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"💰 Contas a Pagar encontradas: {total}\n\n📋 Lista de contas:\n" + "\n".join(lista_contas) + f"\n\n💵 Total (10 primeiras): R$ {total_valor:,.2f}" + (f"\n(Mostrando 10 de {total})" if total > 10 else "")
        else:
            return "❌ Nenhuma conta a pagar encontrada com os filtros especificados"
    
    async def handle_consultar_contas_receber(self, args: Dict) -> str:
        """Handler para consultar contas a receber"""
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 20)
        }
        
        # Adicionar filtros se fornecidos
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await self.omie_client.consultar_contas_receber(params)
        contas = resultado.get("conta_receber_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"💵 Contas a Receber encontradas: {total}\n\n📋 Lista de contas:\n" + "\n".join(lista_contas) + f"\n\n💰 Total (10 primeiras): R$ {total_valor:,.2f}" + (f"\n(Mostrando 10 de {total})" if total > 10 else "")
        else:
            return "❌ Nenhuma conta a receber encontrada com os filtros especificados"
    
    # ========== HANDLERS ADICIONAIS ==========
    
    async def handle_cadastrar_cliente_fornecedor(self, args: Dict) -> str:
        """Handler para cadastrar cliente/fornecedor"""
        import time
        codigo_integracao = f"MCP-{int(time.time())}"
        
        dados_omie = {
            "codigo_cliente_integracao": codigo_integracao,
            "razao_social": args["razao_social"],
            "cnpj_cpf": args["cnpj_cpf"],
            "email": args["email"]
        }
        
        resultado = await self.omie_client.cadastrar_cliente_fornecedor(dados_omie)
        
        if "codigo_cliente_omie" in resultado:
            return f"✅ {args['tipo_cliente'].title()} cadastrado com sucesso!\n\n📋 Detalhes:\n• Código Omie: {resultado['codigo_cliente_omie']}\n• Código Integração: {codigo_integracao}\n• Razão Social: {args['razao_social']}\n• CNPJ/CPF: {args['cnpj_cpf']}\n• E-mail: {args['email']}"
        else:
            return f"✅ Cadastrado! Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"

# ============================================================================
# SERVIDOR FASTAPI
# ============================================================================

# Instanciar cliente e handlers
omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)
omie_handlers = OmieHandlers(omie_client)

# Criar aplicação FastAPI
app = FastAPI(
    title="Omie MCP HTTP Server",
    description="Servidor MCP HTTP para Omie ERP - Compatível com Claude Desktop",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS MCP
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Omie MCP HTTP Server",
        "status": "running",
        "version": "1.0.0",
        "protocol": "HTTP",
        "compatible_with": ["Claude Desktop", "Copilot Studio", "N8N", "Zapier"],
        "tools": 6,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/mcp/initialize")
async def mcp_initialize():
    """Inicializar sessão MCP"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {"listChanged": True}},
        "serverInfo": {"name": "omie-mcp-http", "version": "1.0.0"}
    }

@app.get("/mcp/tools")
async def mcp_tools():
    """Listar ferramentas disponíveis"""
    return {
        "tools": [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias de receita/despesa do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Número da página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Número da página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_tipos_documento",
                "description": "Consulta tipos de documentos do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar do Omie ERP",
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
                "description": "Consulta contas a receber do Omie ERP",
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

@app.post("/mcp/tools/{tool_name}")
async def mcp_call_tool(tool_name: str, request: Request):
    """Executar ferramenta específica"""
    try:
        # Obter argumentos do corpo da requisição
        body = await request.json()
        arguments = body.get("arguments", {})
        
        # Executar ferramenta
        result = await call_tool(tool_name, arguments)
        
        return {
            "content": [{"type": "text", "text": result}]
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_tool(tool_name: str, arguments: Dict) -> str:
    """Chama ferramenta específica"""
    try:
        if tool_name == "consultar_categorias":
            return await omie_handlers.handle_consultar_categorias(arguments)
        elif tool_name == "consultar_departamentos":
            return await omie_handlers.handle_consultar_departamentos(arguments)
        elif tool_name == "consultar_tipos_documento":
            return await omie_handlers.handle_consultar_tipos_documento(arguments)
        elif tool_name == "consultar_contas_pagar":
            return await omie_handlers.handle_consultar_contas_pagar(arguments)
        elif tool_name == "consultar_contas_receber":
            return await omie_handlers.handle_consultar_contas_receber(arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Ferramenta não encontrada: {tool_name}")
            
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
        raise

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

@app.get("/test/contas-pagar")
async def test_contas_pagar():
    """Endpoint para testar consulta de contas a pagar"""
    result = await omie_handlers.handle_consultar_contas_pagar({})
    return {"result": result}

@app.get("/test/contas-receber")
async def test_contas_receber():
    """Endpoint para testar consulta de contas a receber"""
    result = await omie_handlers.handle_consultar_contas_receber({})
    return {"result": result}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP"""
    
    logger.info("🚀 Iniciando Servidor MCP HTTP para Omie ERP")
    logger.info(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    logger.info(f"🌐 Porta: {MCP_SERVER_PORT}")
    logger.info("📡 Protocolo: HTTP")
    logger.info("🔧 Compatível com: Claude Desktop, Copilot Studio, N8N, Zapier")
    logger.info("📋 Ferramentas: 5")
    logger.info(f"✅ Servidor HTTP rodando em: http://localhost:{MCP_SERVER_PORT}")
    logger.info(f"📖 Docs: http://localhost:{MCP_SERVER_PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()