#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - VERSÃO COMPLETA
Ferramentas expandidas para gerenciamento completo do Omie ERP

Ferramentas disponíveis:
1. Cadastrar Cliente/Fornecedor
2. Consultar Categorias  
3. Consultar Departamentos
4. Consultar Tipos de Documentos
5. Incluir Contas a Pagar
6. Consultar Contas a Pagar (por fornecedor, status)
7. Consultar Contas a Receber (por cliente, status)
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Credenciais do Omie via variáveis de ambiente
OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")

# Verificar credenciais
if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    print("❌ ERRO: Configure as variáveis de ambiente OMIE_APP_KEY e OMIE_APP_SECRET")
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
logger = logging.getLogger("omie-mcp-complete")

# ============================================================================
# MODELOS PYDANTIC EXPANDIDOS
# ============================================================================

class ClienteFornecedorRequest(BaseModel):
    razao_social: str
    cnpj_cpf: str
    email: str
    tipo_cliente: str
    nome_fantasia: Optional[str] = ""
    telefone1_ddd: Optional[str] = ""
    telefone1_numero: Optional[str] = ""
    endereco: Optional[str] = ""
    cidade: Optional[str] = ""
    estado: Optional[str] = ""
    cep: Optional[str] = ""

class ContaPagarRequest(BaseModel):
    codigo_cliente_fornecedor: int
    numero_documento: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: Optional[str] = "1.01.01"
    observacao: Optional[str] = ""
    numero_parcela: Optional[int] = 1

class ConsultaContasRequest(BaseModel):
    codigo_cliente_fornecedor: Optional[int] = None
    status: Optional[str] = None  # "ABERTO", "PAGO", "VENCIDO"
    data_inicio: Optional[str] = None  # DD/MM/AAAA
    data_fim: Optional[str] = None     # DD/MM/AAAA
    pagina: Optional[int] = 1
    registros_por_pagina: Optional[int] = 20

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Optional[Dict] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Optional[Dict] = None
    error: Optional[Dict] = None

# ============================================================================
# CLIENTE OMIE EXPANDIDO
# ============================================================================

class OmieClient:
    """Cliente HTTP expandido para comunicação com a API do Omie"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = OMIE_BASE_URL
        
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
                logger.info(f"📡 Requisição Omie: {endpoint}/{call}")
                logger.debug(f"Payload: {json.dumps(params, indent=2)}")
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Verificar se há erro na resposta
                if "faultstring" in result:
                    error_msg = result["faultstring"]
                    logger.error(f"❌ Erro Omie: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                
                logger.info(f"✅ Resposta Omie: Sucesso")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro HTTP: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na comunicação com Omie: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro interno: {e}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    # ========== MÉTODOS ORIGINAIS ==========
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    # ========== NOVOS MÉTODOS ==========
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
            params = {}
        return await self._make_request("geral/tiposdoc", "ListarTiposDocumento", params)
    
    async def consultar_contas_pagar(self, params: Dict) -> Dict:
        """Consulta contas a pagar com filtros"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", params)
    
    async def consultar_contas_receber(self, params: Dict) -> Dict:
        """Consulta contas a receber com filtros"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", params)

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)

# ============================================================================
# APLICAÇÃO FASTAPI EXPANDIDA
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Completo",
    description="Servidor MCP HTTP completo para integração com Omie ERP",
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
# ENDPOINTS MCP EXPANDIDOS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint de status expandido"""
    return {
        "service": "Omie MCP Server - Completo",
        "status": "running",
        "version": "2.0.0",
        "tools": [
            "cadastrar_cliente_fornecedor",
            "consultar_categorias",
            "consultar_departamentos", 
            "consultar_tipos_documento",
            "criar_conta_pagar",
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
    """Endpoint principal MCP expandido"""
    
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "omie-mcp-server-complete",
                        "version": "2.0.0"
                    }
                }
            )
        
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [
                        {
                            "name": "cadastrar_cliente_fornecedor",
                            "description": "Cadastra um novo cliente ou fornecedor no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "razao_social": {"type": "string", "description": "Razão social"},
                                    "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                                    "email": {"type": "string", "description": "E-mail"},
                                    "tipo_cliente": {"type": "string", "enum": ["cliente", "fornecedor", "ambos"]},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia"},
                                    "telefone1_ddd": {"type": "string", "description": "DDD"},
                                    "telefone1_numero": {"type": "string", "description": "Telefone"},
                                    "endereco": {"type": "string", "description": "Endereço"},
                                    "cidade": {"type": "string", "description": "Cidade"},
                                    "estado": {"type": "string", "description": "Estado"},
                                    "cep": {"type": "string", "description": "CEP"}
                                },
                                "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"]
                            }
                        },
                        {
                            "name": "consultar_categorias",
                            "description": "Consulta categorias de receita e despesa disponíveis no Omie",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "pagina": {"type": "integer", "description": "Página (padrão: 1)", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página (padrão: 50)", "default": 50}
                                }
                            }
                        },
                        {
                            "name": "consultar_departamentos",
                            "description": "Consulta departamentos cadastrados no Omie",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "pagina": {"type": "integer", "description": "Página (padrão: 1)", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página (padrão: 50)", "default": 50}
                                }
                            }
                        },
                        {
                            "name": "consultar_tipos_documento",
                            "description": "Consulta tipos de documentos disponíveis no Omie",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "criar_conta_pagar",
                            "description": "Cria uma nova conta a pagar no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor"},
                                    "numero_documento": {"type": "string", "description": "Número do documento"},
                                    "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento"},
                                    "codigo_categoria": {"type": "string", "description": "Categoria"},
                                    "observacao": {"type": "string", "description": "Observações"},
                                    "numero_parcela": {"type": "integer", "description": "Número da parcela"}
                                },
                                "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                            }
                        },
                        {
                            "name": "consultar_contas_pagar",
                            "description": "Consulta contas a pagar com filtros por fornecedor, status e período",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor (opcional)"},
                                    "status": {"type": "string", "enum": ["ABERTO", "PAGO", "VENCIDO"], "description": "Status da conta"},
                                    "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                                    "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                                    "pagina": {"type": "integer", "description": "Página", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                                }
                            }
                        },
                        {
                            "name": "consultar_contas_receber",
                            "description": "Consulta contas a receber com filtros por cliente, status e período",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente (opcional)"},
                                    "status": {"type": "string", "enum": ["ABERTO", "PAGO", "VENCIDO"], "description": "Status da conta"},
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
            
            if tool_name == "cadastrar_cliente_fornecedor":
                result = await handle_cadastrar_cliente_fornecedor(arguments)
            elif tool_name == "consultar_categorias":
                result = await handle_consultar_categorias(arguments)
            elif tool_name == "consultar_departamentos":
                result = await handle_consultar_departamentos(arguments)
            elif tool_name == "consultar_tipos_documento":
                result = await handle_consultar_tipos_documento(arguments)
            elif tool_name == "criar_conta_pagar":
                result = await handle_criar_conta_pagar(arguments)
            elif tool_name == "consultar_contas_pagar":
                result = await handle_consultar_contas_pagar(arguments)
            elif tool_name == "consultar_contas_receber":
                result = await handle_consultar_contas_receber(arguments)
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
# HANDLERS DAS FERRAMENTAS EXPANDIDOS
# ============================================================================

async def handle_cadastrar_cliente_fornecedor(args: Dict) -> str:
    """Handler para cadastrar cliente/fornecedor"""
    
    dados_omie = {
        "razao_social": args["razao_social"],
        "cnpj_cpf": args["cnpj_cpf"],
        "email": args["email"],
        "nome_fantasia": args.get("nome_fantasia", ""),
        "telefone1_ddd": args.get("telefone1_ddd", ""),
        "telefone1_numero": args.get("telefone1_numero", ""),
        "endereco": args.get("endereco", ""),
        "cidade": args.get("cidade", ""),
        "estado": args.get("estado", ""),
        "cep": args.get("cep", ""),
        "tags": [{"tag": "MCP_COMPLETO"}],
        "inativo": "N"
    }
    
    resultado = await omie_client.cadastrar_cliente_fornecedor(dados_omie)
    
    if "codigo_cliente_omie" in resultado:
        return f"""✅ Cliente/Fornecedor cadastrado com sucesso!

📋 Detalhes:
• Código Omie: {resultado['codigo_cliente_omie']}
• Razão Social: {args['razao_social']}
• CNPJ/CPF: {args['cnpj_cpf']}
• Tipo solicitado: {args.get('tipo_cliente', 'N/A')}
• E-mail: {args['email']}

🔗 Disponível no Omie ERP com tag MCP_COMPLETO"""
    else:
        return f"✅ Cadastrado! Resposta: {json.dumps(resultado, indent=2)}"

async def handle_consultar_categorias(args: Dict) -> str:
    """Handler para consultar categorias"""
    
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 50)
    }
    
    resultado = await omie_client.consultar_categorias(params)
    
    categorias = resultado.get("categoria_cadastro", [])
    total = resultado.get("total_de_registros", 0)
    
    if categorias:
        lista_categorias = []
        for cat in categorias[:10]:  # Mostrar apenas 10 primeiras
            codigo = cat.get("codigo", "N/A")
            descricao = cat.get("descricao", "N/A")
            tipo = cat.get("tipo", "N/A")
            lista_categorias.append(f"• {codigo} - {descricao} ({tipo})")
        
        resultado_texto = f"""📊 Categorias encontradas: {total}

🏷️ Principais categorias:
{chr(10).join(lista_categorias)}

{f"(Mostrando 10 de {total})" if total > 10 else ""}

💡 Use o código da categoria ao criar contas a pagar/receber"""
        
        return resultado_texto
    else:
        return "❌ Nenhuma categoria encontrada"

async def handle_consultar_departamentos(args: Dict) -> str:
    """Handler para consultar departamentos"""
    
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 50)
    }
    
    resultado = await omie_client.consultar_departamentos(params)
    
    departamentos = resultado.get("departamento_cadastro", [])
    total = resultado.get("total_de_registros", 0)
    
    if departamentos:
        lista_depts = []
        for dept in departamentos[:10]:
            codigo = dept.get("codigo", "N/A")
            descricao = dept.get("descricao", "N/A")
            lista_depts.append(f"• {codigo} - {descricao}")
        
        return f"""🏢 Departamentos encontrados: {total}

📋 Lista de departamentos:
{chr(10).join(lista_depts)}

{f"(Mostrando 10 de {total})" if total > 10 else ""}"""
    else:
        return "❌ Nenhum departamento encontrado"

async def handle_consultar_tipos_documento(args: Dict) -> str:
    """Handler para consultar tipos de documentos"""
    
    resultado = await omie_client.consultar_tipos_documento({})
    
    tipos = resultado.get("tipos_documento", [])
    
    if tipos:
        lista_tipos = []
        for tipo in tipos[:15]:  # Mostrar 15 primeiros
            codigo = tipo.get("codigo", "N/A")
            descricao = tipo.get("descricao", "N/A")
            lista_tipos.append(f"• {codigo} - {descricao}")
        
        return f"""📄 Tipos de documentos disponíveis:

📋 Lista:
{chr(10).join(lista_tipos)}

💡 Use o código do tipo ao criar contas a pagar/receber"""
    else:
        return "❌ Nenhum tipo de documento encontrado"

async def handle_criar_conta_pagar(args: Dict) -> str:
    """Handler para criar conta a pagar"""
    
    dados_omie = {
        "codigo_cliente_fornecedor": args["codigo_cliente_fornecedor"],
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args.get("codigo_categoria", "1.01.01"),
        "observacao": args.get("observacao", f"Conta criada via MCP Completo em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "numero_parcela": args.get("numero_parcela", 1),
        "codigo_tipo_documento": "01",
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "data_entrada": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    resultado = await omie_client.criar_conta_pagar(dados_omie)
    
    if "codigo_lancamento_omie" in resultado:
        return f"""💰 Conta a Pagar criada com sucesso!

📋 Detalhes:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Fornecedor: {args['codigo_cliente_fornecedor']}
• Documento: {args['numero_documento']}
• Valor: R$ {args['valor_documento']:,.2f}
• Vencimento: {args['data_vencimento']}
• Status: ABERTO

🔗 Disponível no módulo Financeiro do Omie ERP"""
    else:
        return f"💰 Conta criada! Resposta: {json.dumps(resultado, indent=2)}"

async def handle_consultar_contas_pagar(args: Dict) -> str:
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
    
    resultado = await omie_client.consultar_contas_pagar(params)
    
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
            fornecedor = conta.get("codigo_cliente_fornecedor", "N/A")
            
            total_valor += valor
            lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
        
        return f"""💰 Contas a Pagar encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💵 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}

📊 Filtros aplicados:
{f"• Fornecedor: {args.get('codigo_cliente_fornecedor', 'Todos')}" if args.get('codigo_cliente_fornecedor') else "• Fornecedor: Todos"}
{f"• Período: {args.get('data_inicio', 'N/A')} a {args.get('data_fim', 'N/A')}" if args.get('data_inicio') else "• Período: Todos"}"""
    else:
        return "❌ Nenhuma conta a pagar encontrada com os filtros especificados"

async def handle_consultar_contas_receber(args: Dict) -> str:
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
    
    resultado = await omie_client.consultar_contas_receber(params)
    
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
            cliente = conta.get("codigo_cliente_fornecedor", "N/A")
            
            total_valor += valor
            lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
        
        return f"""💵 Contas a Receber encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💰 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}

📊 Filtros aplicados:
{f"• Cliente: {args.get('codigo_cliente_fornecedor', 'Todos')}" if args.get('codigo_cliente_fornecedor') else "• Cliente: Todos"}
{f"• Período: {args.get('data_inicio', 'N/A')} a {args.get('data_fim', 'N/A')}" if args.get('data_inicio') else "• Período: Todos"}"""
    else:
        return "❌ Nenhuma conta a receber encontrada com os filtros especificados"

# ============================================================================
# ENDPOINTS DE TESTE EXPANDIDOS
# ============================================================================

@app.post("/test/cliente")
async def test_cliente(request: ClienteFornecedorRequest):
    """Endpoint para testar cadastro de cliente"""
    result = await handle_cadastrar_cliente_fornecedor(request.dict())
    return {"result": result}

@app.post("/test/conta-pagar")
async def test_conta_pagar(request: ContaPagarRequest):
    """Endpoint para testar criação de conta a pagar"""
    result = await handle_criar_conta_pagar(request.dict())
    return {"result": result}

@app.get("/test/categorias")
async def test_categorias():
    """Endpoint para testar consulta de categorias"""
    result = await handle_consultar_categorias({})
    return {"result": result}

@app.get("/test/departamentos")
async def test_departamentos():
    """Endpoint para testar consulta de departamentos"""
    result = await handle_consultar_departamentos({})
    return {"result": result}

@app.get("/test/tipos-documento")
async def test_tipos_documento():
    """Endpoint para testar consulta de tipos de documentos"""
    result = await handle_consultar_tipos_documento({})
    return {"result": result}

@app.post("/test/contas-pagar")
async def test_contas_pagar(request: ConsultaContasRequest):
    """Endpoint para testar consulta de contas a pagar"""
    result = await handle_consultar_contas_pagar(request.dict())
    return {"result": result}

@app.post("/test/contas-receber")
async def test_contas_receber(request: ConsultaContasRequest):
    """Endpoint para testar consulta de contas a receber"""
    result = await handle_consultar_contas_receber(request.dict())
    return {"result": result}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP completo"""
    
    print("🚀 Iniciando Servidor MCP HTTP para Omie ERP - VERSÃO COMPLETA")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("📡 Ferramentas disponíveis:")
    print("   • cadastrar_cliente_fornecedor")
    print("   • consultar_categorias")
    print("   • consultar_departamentos")
    print("   • consultar_tipos_documento")
    print("   • criar_conta_pagar")
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