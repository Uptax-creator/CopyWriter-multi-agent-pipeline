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
    codigo_cliente_fornecedor: Optional[int] = None
    cnpj_cpf_fornecedor: Optional[str] = None
    razao_social_fornecedor: Optional[str] = None
    email_fornecedor: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    numero_documento: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    codigo_departamento: Optional[str] = None
    codigo_tipo_documento: Optional[str] = None
    observacao: Optional[str] = ""

class AtualizarContaPagarRequest(BaseModel):
    codigo_lancamento_omie: Optional[int] = None
    codigo_lancamento_integracao: Optional[str] = None
    codigo_cliente_fornecedor: Optional[int] = None
    cnpj_cpf_fornecedor: Optional[str] = None
    razao_social_fornecedor: Optional[str] = None
    email_fornecedor: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    numero_documento: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    codigo_departamento: str
    codigo_tipo_documento: str
    nota_fiscal: str
    observacao: Optional[str] = ""

class ContaReceberRequest(BaseModel):
    codigo_cliente_fornecedor: Optional[int] = None
    cnpj_cpf_cliente: Optional[str] = None
    razao_social_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    numero_documento: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    codigo_departamento: Optional[str] = None
    codigo_tipo_documento: Optional[str] = None
    observacao: Optional[str] = ""

class AtualizarContaReceberRequest(BaseModel):
    codigo_lancamento_omie: Optional[int] = None
    codigo_lancamento_integracao: Optional[str] = None
    codigo_cliente_fornecedor: Optional[int] = None
    cnpj_cpf_cliente: Optional[str] = None
    razao_social_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    numero_documento: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    codigo_departamento: str
    codigo_tipo_documento: str
    nota_fiscal: str
    observacao: Optional[str] = ""

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
                
                # Tentar pegar o JSON mesmo em caso de erro 500
                try:
                    result = response.json()
                except:
                    response.raise_for_status()  # Se não conseguir parsear, raise o erro HTTP
                    result = {}
                
                # Verificar se há erro na resposta
                if "faultstring" in result:
                    error_msg = result["faultstring"]
                    logger.error(f"❌ Erro Omie: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                
                # Se chegou aqui e não é 200, raise erro HTTP
                if response.status_code != 200:
                    response.raise_for_status()
                
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
    
    async def atualizar_conta_pagar(self, dados: Dict) -> Dict:
        """Atualiza conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "AlterarContaPagar", dados)
    
    async def criar_conta_receber(self, dados: Dict) -> Dict:
        """Cria conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "IncluirContaReceber", dados)
    
    async def atualizar_conta_receber(self, dados: Dict) -> Dict:
        """Atualiza conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "AlterarContaReceber", dados)
    
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
            params = {"codigo": ""}
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", params)
    
    async def consultar_contas_pagar(self, params: Dict) -> Dict:
        """Consulta contas a pagar com filtros"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", params)
    
    async def consultar_contas_receber(self, params: Dict) -> Dict:
        """Consulta contas a receber com filtros"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", params)
    
    async def consultar_cliente_fornecedor_por_cnpj(self, cnpj_cpf: str) -> Dict:
        """Consulta cliente/fornecedor por CNPJ/CPF (busca em todas as páginas)"""
        
        # Remover formatação do CNPJ para comparação
        cnpj_limpo = cnpj_cpf.replace(".", "").replace("/", "").replace("-", "")
        
        pagina = 1
        while True:
            params = {
                "pagina": pagina,
                "registros_por_pagina": 50,
                "apenas_importado_api": "N"
            }
            
            resultado = await self._make_request("geral/clientes", "ListarClientes", params)
            clientes = resultado.get("clientes_cadastro", [])
            
            if not clientes:
                break
                
            # Buscar cliente com CNPJ correspondente
            for cliente in clientes:
                cnpj_cliente = cliente.get("cnpj_cpf", "").replace(".", "").replace("/", "").replace("-", "")
                if cnpj_cliente == cnpj_limpo:
                    return {"clientes_cadastro": [cliente]}
            
            # Se chegou ao final, parar
            if len(clientes) < 50:
                break
                
            pagina += 1
            
        # Não encontrou
        return {"clientes_cadastro": []}

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
            "atualizar_conta_pagar",
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
                            "description": "Cria uma nova conta a pagar no Omie ERP com consulta/criação automática de fornecedor",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor (alternativa - ex: 2675632305)"},
                                    "cnpj_cpf_fornecedor": {"type": "string", "description": "CNPJ/CPF do fornecedor (será consultado/criado automaticamente)"},
                                    "razao_social_fornecedor": {"type": "string", "description": "Razão social (usado se fornecedor não existir)"},
                                    "email_fornecedor": {"type": "string", "description": "Email do fornecedor (opcional)"},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia (opcional)"},
                                    "cidade": {"type": "string", "description": "Cidade (opcional)"},
                                    "estado": {"type": "string", "description": "Estado (opcional)"},
                                    "numero_documento": {"type": "string", "description": "Número do documento"},
                                    "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria (obrigatório - use consultar_categorias)"},
                                    "codigo_departamento": {"type": "string", "description": "Código do departamento (opcional - use consultar_departamentos)"},
                                    "codigo_tipo_documento": {"type": "string", "description": "Código do tipo de documento (opcional - use consultar_tipos_documento)"},
                                    "observacao": {"type": "string", "description": "Observações"}
                                },
                                "required": ["numero_documento", "data_vencimento", "valor_documento", "codigo_categoria"]
                            }
                        },
                        {
                            "name": "atualizar_conta_pagar",
                            "description": "Atualiza uma conta a pagar existente no Omie ERP com campos obrigatórios",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento Omie (alternativa)"},
                                    "codigo_lancamento_integracao": {"type": "string", "description": "Código de integração (alternativa)"},
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor (alternativa)"},
                                    "cnpj_cpf_fornecedor": {"type": "string", "description": "CNPJ/CPF do fornecedor (será consultado/criado automaticamente)"},
                                    "razao_social_fornecedor": {"type": "string", "description": "Razão social (usado se fornecedor não existir)"},
                                    "email_fornecedor": {"type": "string", "description": "Email do fornecedor (opcional)"},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia (opcional)"},
                                    "cidade": {"type": "string", "description": "Cidade (opcional)"},
                                    "estado": {"type": "string", "description": "Estado (opcional)"},
                                    "numero_documento": {"type": "string", "description": "Número do documento (obrigatório)"},
                                    "data_vencimento": {"type": "string", "description": "Data vencimento DD/MM/AAAA (obrigatório)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento (obrigatório)"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria (obrigatório - use consultar_categorias)"},
                                    "codigo_departamento": {"type": "string", "description": "Código do departamento (obrigatório - use consultar_departamentos)"},
                                    "codigo_tipo_documento": {"type": "string", "description": "Código do tipo de documento (obrigatório - use consultar_tipos_documento)"},
                                    "nota_fiscal": {"type": "string", "description": "Número da nota fiscal (obrigatório)"},
                                    "observacao": {"type": "string", "description": "Observações"}
                                },
                                "required": ["numero_documento", "data_vencimento", "valor_documento", "codigo_categoria", "codigo_departamento", "codigo_tipo_documento", "nota_fiscal"]
                            }
                        },
                        {
                            "name": "criar_conta_receber",
                            "description": "Cria uma nova conta a receber no Omie ERP com consulta/criação automática de cliente",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente (alternativa - ex: 2675632305)"},
                                    "cnpj_cpf_cliente": {"type": "string", "description": "CNPJ/CPF do cliente (será consultado/criado automaticamente)"},
                                    "razao_social_cliente": {"type": "string", "description": "Razão social (usado se cliente não existir)"},
                                    "email_cliente": {"type": "string", "description": "Email do cliente (opcional)"},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia (opcional)"},
                                    "cidade": {"type": "string", "description": "Cidade (opcional)"},
                                    "estado": {"type": "string", "description": "Estado (opcional)"},
                                    "numero_documento": {"type": "string", "description": "Número do documento"},
                                    "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria (obrigatório - use consultar_categorias)"},
                                    "codigo_departamento": {"type": "string", "description": "Código do departamento (opcional - use consultar_departamentos)"},
                                    "codigo_tipo_documento": {"type": "string", "description": "Código do tipo de documento (opcional - use consultar_tipos_documento)"},
                                    "observacao": {"type": "string", "description": "Observações"}
                                },
                                "required": ["numero_documento", "data_vencimento", "valor_documento", "codigo_categoria"]
                            }
                        },
                        {
                            "name": "atualizar_conta_receber",
                            "description": "Atualiza uma conta a receber existente no Omie ERP com campos obrigatórios",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_lancamento_omie": {"type": "integer", "description": "Código do lançamento Omie (alternativa)"},
                                    "codigo_lancamento_integracao": {"type": "string", "description": "Código de integração (alternativa)"},
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente (alternativa)"},
                                    "cnpj_cpf_cliente": {"type": "string", "description": "CNPJ/CPF do cliente (será consultado/criado automaticamente)"},
                                    "razao_social_cliente": {"type": "string", "description": "Razão social (usado se cliente não existir)"},
                                    "email_cliente": {"type": "string", "description": "Email do cliente (opcional)"},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia (opcional)"},
                                    "cidade": {"type": "string", "description": "Cidade (opcional)"},
                                    "estado": {"type": "string", "description": "Estado (opcional)"},
                                    "numero_documento": {"type": "string", "description": "Número do documento (obrigatório)"},
                                    "data_vencimento": {"type": "string", "description": "Data vencimento DD/MM/AAAA (obrigatório)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento (obrigatório)"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria (obrigatório - use consultar_categorias)"},
                                    "codigo_departamento": {"type": "string", "description": "Código do departamento (obrigatório - use consultar_departamentos)"},
                                    "codigo_tipo_documento": {"type": "string", "description": "Código do tipo de documento (obrigatório - use consultar_tipos_documento)"},
                                    "nota_fiscal": {"type": "string", "description": "Número da nota fiscal (obrigatório)"},
                                    "observacao": {"type": "string", "description": "Observações"}
                                },
                                "required": ["numero_documento", "data_vencimento", "valor_documento", "codigo_categoria", "codigo_departamento", "codigo_tipo_documento", "nota_fiscal"]
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
            elif tool_name == "atualizar_conta_pagar":
                result = await handle_atualizar_conta_pagar(arguments)
            elif tool_name == "criar_conta_receber":
                result = await handle_criar_conta_receber(arguments)
            elif tool_name == "atualizar_conta_receber":
                result = await handle_atualizar_conta_receber(arguments)
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
    
    # Gerar código único de integração
    import time
    timestamp = int(time.time())
    
    dados_omie = {
        "codigo_cliente_integracao": f"MCP-{timestamp}",
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
• Código Integração: {resultado.get('codigo_cliente_integracao', 'N/A')}
• Razão Social: {args['razao_social']}
• CNPJ/CPF: {args['cnpj_cpf']}
• E-mail: {args['email']}

🔗 Disponível no Omie ERP com tag MCP_COMPLETO
✅ Erro 500 SOAP resolvido!"""
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
            conta_receita = cat.get("conta_receita", "N")
            conta_despesa = cat.get("conta_despesa", "N")
            conta_inativa = cat.get("conta_inativa", "N")
            totalizadora = cat.get("totalizadora", "N")
            transferencia = cat.get("transferencia", "N")
            
            # Identificar tipo baseado na estrutura do código
            nivel = codigo.count('.')
            if nivel == 0:
                tipo_estrutura = "Sintético (Nível 1)"
            elif nivel == 1:
                tipo_estrutura = "Analítico (Nível 2)"
            else:
                tipo_estrutura = f"Analítico (Nível {nivel + 1})"
            
            # Identificar natureza
            if transferencia == "S":
                natureza = "Transferência"
            elif conta_receita == "S":
                natureza = "Receita"
            elif conta_despesa == "S":
                natureza = "Despesa"
            else:
                natureza = "Indefinida"
            
            # Status
            status = "Inativo" if conta_inativa == "S" else "Ativo"
            
            # Tipo de conta
            tipo_conta = "Totalizadora" if totalizadora == "S" else "Movimentação"
            
            lista_categorias.append(f"• {codigo} - {descricao}")
            lista_categorias.append(f"  └─ {tipo_estrutura} | {natureza} | {tipo_conta} | {status}")
        
        resultado_texto = f"""📊 Categorias encontradas: {total}

🏷️ Principais categorias:
{chr(10).join(lista_categorias)}

{f"(Mostrando 10 de {total})" if total > 10 else ""}

💡 Estrutura: Sintético (sem pontos) | Analítico (com pontos)
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
    
    departamentos = resultado.get("departamentos", [])
    total = resultado.get("total_de_registros", 0)
    
    if departamentos:
        lista_depts = []
        for dept in departamentos[:10]:
            codigo = dept.get("codigo", "N/A")
            descricao = dept.get("descricao", "N/A")
            estrutura = dept.get("estrutura", "N/A")
            inativo = dept.get("inativo", "N/A")
            
            # Identificar se é Sintético ou Analítico
            tipo = "Sintético" if estrutura.count('.') == 0 else "Analítico"
            status = "Ativo" if inativo == "N" else "Inativo"
            
            lista_depts.append(f"• {codigo} - {descricao}")
            lista_depts.append(f"  └─ Estrutura: {estrutura} ({tipo}) | Status: {status}")
        
        return f"""🏢 Departamentos encontrados: {total}

📋 Lista de departamentos:
{chr(10).join(lista_depts)}

{f"(Mostrando 10 de {total})" if total > 10 else ""}

💡 Estrutura: Sintético (sem pontos) | Analítico (com pontos)"""
    else:
        return "❌ Nenhum departamento encontrado"

async def handle_consultar_tipos_documento(args: Dict) -> str:
    """Handler para consultar tipos de documentos"""
    
    resultado = await omie_client.consultar_tipos_documento()
    
    tipos = resultado.get("tipo_documento_cadastro", [])
    total = len(tipos)
    
    if tipos:
        lista_tipos = []
        for tipo in tipos[:20]:  # Mostrar 20 primeiros
            codigo = tipo.get("codigo", "N/A")
            descricao = tipo.get("descricao", "N/A")
            
            # Formatação mais organizada
            lista_tipos.append(f"• {codigo} - {descricao}")
        
        return f"""📄 Tipos de documentos encontrados: {total}

📋 Lista (primeiros 20):
{chr(10).join(lista_tipos)}

{f"(Mostrando 20 de {total})" if total > 20 else ""}

💡 Use o código do tipo ao criar contas a pagar/receber
💡 Códigos comuns: DUP (Duplicata), BOL (Boleto), NF (Nota Fiscal), FAT (Fatura)"""
    else:
        return "❌ Nenhum tipo de documento encontrado"

async def validar_codigo_categoria(codigo: str) -> str:
    """Valida se o código da categoria existe"""
    try:
        resultado = await omie_client.consultar_categorias({"pagina": 1, "registros_por_pagina": 200})
        categorias = resultado.get("categoria_cadastro", [])
        
        for categoria in categorias:
            if categoria.get("codigo") == codigo:
                return categoria.get("descricao", "N/A")
        
        return None
    except:
        return None

async def validar_codigo_departamento(codigo: str) -> str:
    """Valida se o código do departamento existe"""
    try:
        resultado = await omie_client.consultar_departamentos({"pagina": 1, "registros_por_pagina": 100})
        departamentos = resultado.get("departamentos", [])
        
        for departamento in departamentos:
            if departamento.get("codigo") == codigo:
                return departamento.get("descricao", "N/A")
        
        return None
    except:
        return None

async def validar_codigo_tipo_documento(codigo: str) -> str:
    """Valida se o código do tipo de documento existe"""
    try:
        resultado = await omie_client.consultar_tipos_documento()
        tipos = resultado.get("tipo_documento_cadastro", [])
        
        for tipo in tipos:
            if tipo.get("codigo") == codigo:
                return tipo.get("descricao", "N/A")
        
        return None
    except:
        return None

async def handle_criar_conta_pagar(args: Dict) -> str:
    """Handler para criar conta a pagar com fluxo completo de consulta/criação de fornecedor"""
    
    # Verificar se foi fornecido CNPJ ou código do fornecedor
    if args.get("cnpj_cpf_fornecedor"):
        # FLUXO NOVO: Buscar/criar fornecedor por CNPJ
        cnpj_cpf = args["cnpj_cpf_fornecedor"]
        
        # Campos obrigatórios para fluxo com CNPJ
        campos_obrigatorios = {
            "cnpj_cpf_fornecedor": "CNPJ/CPF do fornecedor",
            "numero_documento": "Número do documento",
            "data_vencimento": "Data de vencimento", 
            "valor_documento": "Valor do documento",
            "codigo_categoria": "Código da categoria",
            "codigo_departamento": "Código do departamento",
            "codigo_tipo_documento": "Código do tipo de documento"
        }
        
        # Verificar campos obrigatórios
        campos_faltando = []
        for campo, descricao in campos_obrigatorios.items():
            if not args.get(campo):
                campos_faltando.append(f"• {descricao} ({campo})")
        
        if campos_faltando:
            return f"""❌ Erro: Campos obrigatórios não informados:

{chr(10).join(campos_faltando)}

💡 Fluxo automático com CNPJ:
• Informar CNPJ do fornecedor (será consultado/criado automaticamente)
• Se não existir, informar razao_social_fornecedor e email_fornecedor"""

        # ETAPA 0: Validar códigos obrigatórios
        validacoes_codigo = []
        
        # Validar categoria
        if args.get("codigo_categoria"):
            categoria_desc = await validar_codigo_categoria(args["codigo_categoria"])
            if categoria_desc is None:
                validacoes_codigo.append(f"• Categoria '{args['codigo_categoria']}' não encontrada")
        
        # Validar departamento
        if args.get("codigo_departamento"):
            departamento_desc = await validar_codigo_departamento(args["codigo_departamento"])
            if departamento_desc is None:
                validacoes_codigo.append(f"• Departamento '{args['codigo_departamento']}' não encontrado")
        
        # Validar tipo documento
        if args.get("codigo_tipo_documento"):
            tipo_doc_desc = await validar_codigo_tipo_documento(args["codigo_tipo_documento"])
            if tipo_doc_desc is None:
                validacoes_codigo.append(f"• Tipo documento '{args['codigo_tipo_documento']}' não encontrado")
        
        if validacoes_codigo:
            return f"""❌ Erro: Códigos inválidos:

{chr(10).join(validacoes_codigo)}

💡 Use as ferramentas de consulta para obter códigos válidos:
• consultar_categorias - Para códigos de categoria
• consultar_departamentos - Para códigos de departamento
• consultar_tipos_documento - Para códigos de tipo de documento"""

        # ETAPA 1: Consultar se fornecedor existe
        try:
            logger.info(f"🔍 Consultando fornecedor por CNPJ: {cnpj_cpf}")
            resultado_consulta = await omie_client.consultar_cliente_fornecedor_por_cnpj(cnpj_cpf)
            
            clientes = resultado_consulta.get("clientes_cadastro", [])
            
            if clientes:
                # Fornecedor encontrado
                codigo_fornecedor = clientes[0].get("codigo_cliente_omie")
                razao_social = clientes[0].get("razao_social", "N/A")
                logger.info(f"✅ Fornecedor encontrado: {codigo_fornecedor} - {razao_social}")
                
            else:
                # ETAPA 2: Fornecedor não existe, vamos criar
                logger.info(f"❌ Fornecedor não encontrado, criando novo...")
                
                # Verificar se temos dados suficientes para criar
                if not args.get("razao_social_fornecedor"):
                    return f"""❌ Fornecedor não encontrado para CNPJ {cnpj_cpf}

Para criar automaticamente, informe também:
• razao_social_fornecedor (obrigatório)
• email_fornecedor (opcional, padrão: contato@fornecedor.com)
• nome_fantasia (opcional)
• cidade (opcional)
• estado (opcional)"""
                
                # Dados para criar fornecedor
                import time
                codigo_integracao_fornecedor = f"MCP-FORN-{int(time.time())}"
                
                dados_fornecedor = {
                    "codigo_cliente_integracao": codigo_integracao_fornecedor,
                    "razao_social": args["razao_social_fornecedor"],
                    "cnpj_cpf": cnpj_cpf,
                    "email": args.get("email_fornecedor", "contato@fornecedor.com"),
                    "nome_fantasia": args.get("nome_fantasia", ""),
                    "cidade": args.get("cidade", ""),
                    "estado": args.get("estado", "")
                }
                
                resultado_cadastro = await omie_client.cadastrar_cliente_fornecedor(dados_fornecedor)
                
                if "codigo_cliente_omie" in resultado_cadastro:
                    codigo_fornecedor = resultado_cadastro["codigo_cliente_omie"]
                    razao_social = dados_fornecedor["razao_social"]
                    logger.info(f"✅ Fornecedor criado: {codigo_fornecedor} - {razao_social}")
                else:
                    return f"❌ Erro ao criar fornecedor: {resultado_cadastro}"
        
        except Exception as e:
            return f"❌ Erro ao consultar/criar fornecedor: {str(e)}"
            
    elif args.get("codigo_cliente_fornecedor"):
        # FLUXO ANTIGO: Usar código direto do fornecedor
        codigo_fornecedor = args["codigo_cliente_fornecedor"]
        razao_social = "Fornecedor"
        cnpj_cpf = "N/A"
        
    else:
        return """❌ Erro: Informe o fornecedor

Opções:
• codigo_cliente_fornecedor: Código direto (ex: 2675632305)
• cnpj_cpf_fornecedor: CNPJ para busca/criação automática"""
    
    # ETAPA 1: Criar conta a pagar
    import time
    codigo_integracao = f"MCP-CP-{int(time.time())}"
    
    dados_omie = {
        "codigo_lancamento_integracao": codigo_integracao,
        "codigo_cliente_fornecedor": codigo_fornecedor,
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args["codigo_categoria"],
        "data_previsao": args["data_vencimento"],  # Usar mesma data do vencimento
        "observacao": args.get("observacao", f"Conta criada via MCP Completo em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    }
    
    # Adicionar campos opcionais se fornecidos
    if args.get("codigo_departamento"):
        dados_omie["distribuicao"] = [{
            "cCodDep": args["codigo_departamento"],
            "nPerDep": 100,
            "nValDep": args["valor_documento"]
        }]
    if args.get("codigo_tipo_documento"):
        dados_omie["codigo_tipo_documento"] = args["codigo_tipo_documento"]
    
    resultado = await omie_client.criar_conta_pagar(dados_omie)
    
    if "codigo_lancamento_omie" in resultado:
        return f"""💰 Conta a Pagar criada com sucesso!

📋 Detalhes da conta:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Código Integração: {codigo_integracao}
• Documento: {args['numero_documento']}
• Valor: R$ {args['valor_documento']:,.2f}
• Vencimento: {args['data_vencimento']}
• Categoria: {args['codigo_categoria']}

👥 Fornecedor processado:
• Código: {codigo_fornecedor}
• Nome: {razao_social}
{f"• CNPJ/CPF: {cnpj_cpf}" if cnpj_cpf != "N/A" else ""}

🔗 Disponível no módulo Financeiro do Omie ERP
✅ Fluxo completo: Consulta/Criação automática de fornecedor + Conta a pagar!"""
    else:
        return f"💰 Conta criada! Resposta: {json.dumps(resultado, indent=2)}"

async def handle_atualizar_conta_pagar(args: Dict) -> str:
    """Handler para atualizar conta a pagar com campos obrigatórios"""
    
    # Validar campos obrigatórios
    campos_obrigatorios = {
        "numero_documento": "Número do documento",
        "data_vencimento": "Data de vencimento",
        "valor_documento": "Valor do documento",
        "codigo_categoria": "Código da categoria",
        "codigo_departamento": "Código do departamento",
        "codigo_tipo_documento": "Código do tipo de documento",
        "nota_fiscal": "Número da nota fiscal"
    }
    
    # Verificar se todos os campos obrigatórios estão presentes
    campos_faltando = []
    for campo, descricao in campos_obrigatorios.items():
        if not args.get(campo):
            campos_faltando.append(f"• {descricao} ({campo})")
    
    if campos_faltando:
        return f"""❌ Erro: Campos obrigatórios não informados:

{chr(10).join(campos_faltando)}

💡 Campos obrigatórios para atualização:
• numero_documento e nota_fiscal (mesmo valor)
• codigo_categoria (use consultar_categorias)
• codigo_departamento (use consultar_departamentos)
• codigo_tipo_documento (use consultar_tipos_documento)"""

    # Verificar identificador da conta (código Omie ou código integração)
    if not args.get("codigo_lancamento_omie") and not args.get("codigo_lancamento_integracao"):
        return """❌ Erro: Informe o identificador da conta a pagar

Opções:
• codigo_lancamento_omie: Código do lançamento Omie (ex: 2682811481)
• codigo_lancamento_integracao: Código de integração (ex: MCP-CP-1752082514)"""

    # ETAPA 0: Validar códigos obrigatórios
    validacoes_codigo = []
    
    # Validar categoria
    if args.get("codigo_categoria"):
        categoria_desc = await validar_codigo_categoria(args["codigo_categoria"])
        if categoria_desc is None:
            validacoes_codigo.append(f"• Categoria '{args['codigo_categoria']}' não encontrada")
    
    # Validar departamento
    if args.get("codigo_departamento"):
        departamento_desc = await validar_codigo_departamento(args["codigo_departamento"])
        if departamento_desc is None:
            validacoes_codigo.append(f"• Departamento '{args['codigo_departamento']}' não encontrado")
    
    # Validar tipo documento
    if args.get("codigo_tipo_documento"):
        tipo_doc_desc = await validar_codigo_tipo_documento(args["codigo_tipo_documento"])
        if tipo_doc_desc is None:
            validacoes_codigo.append(f"• Tipo documento '{args['codigo_tipo_documento']}' não encontrado")
    
    if validacoes_codigo:
        return f"""❌ Erro: Códigos inválidos:

{chr(10).join(validacoes_codigo)}

💡 Use as ferramentas de consulta para obter códigos válidos:
• consultar_categorias - Para códigos de categoria
• consultar_departamentos - Para códigos de departamento
• consultar_tipos_documento - Para códigos de tipo de documento"""

    # Processar fornecedor se necessário
    codigo_fornecedor = args.get("codigo_cliente_fornecedor")
    razao_social = "Fornecedor"
    cnpj_cpf = "N/A"
    
    if args.get("cnpj_cpf_fornecedor"):
        # Mesmo fluxo de consulta/criação do criar_conta_pagar
        try:
            cnpj_cpf = args["cnpj_cpf_fornecedor"]
            logger.info(f"🔍 Consultando fornecedor por CNPJ: {cnpj_cpf}")
            resultado_consulta = await omie_client.consultar_cliente_fornecedor_por_cnpj(cnpj_cpf)
            
            clientes = resultado_consulta.get("clientes_cadastro", [])
            
            if clientes:
                codigo_fornecedor = clientes[0].get("codigo_cliente_omie")
                razao_social = clientes[0].get("razao_social", "N/A")
                logger.info(f"✅ Fornecedor encontrado: {codigo_fornecedor} - {razao_social}")
            else:
                if not args.get("razao_social_fornecedor"):
                    return f"""❌ Fornecedor não encontrado para CNPJ {cnpj_cpf}
                    
Para criar automaticamente, informe também:
• razao_social_fornecedor (obrigatório)"""
                
                # Criar fornecedor
                import time
                codigo_integracao_fornecedor = f"MCP-FORN-{int(time.time())}"
                
                dados_fornecedor = {
                    "codigo_cliente_integracao": codigo_integracao_fornecedor,
                    "razao_social": args["razao_social_fornecedor"],
                    "cnpj_cpf": cnpj_cpf,
                    "email": args.get("email_fornecedor", "contato@fornecedor.com"),
                    "nome_fantasia": args.get("nome_fantasia", ""),
                    "cidade": args.get("cidade", ""),
                    "estado": args.get("estado", "")
                }
                
                resultado_cadastro = await omie_client.cadastrar_cliente_fornecedor(dados_fornecedor)
                
                if "codigo_cliente_omie" in resultado_cadastro:
                    codigo_fornecedor = resultado_cadastro["codigo_cliente_omie"]
                    razao_social = dados_fornecedor["razao_social"]
                    logger.info(f"✅ Fornecedor criado: {codigo_fornecedor} - {razao_social}")
                else:
                    return f"❌ Erro ao criar fornecedor: {resultado_cadastro}"
        
        except Exception as e:
            return f"❌ Erro ao consultar/criar fornecedor: {str(e)}"

    # Preparar dados para atualização
    dados_omie = {
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args["codigo_categoria"],
        "codigo_tipo_documento": args["codigo_tipo_documento"],
        "numero_documento_fiscal": args["nota_fiscal"],  # Campo para nota fiscal no Omie
        "data_previsao": args["data_vencimento"],
        "observacao": args.get("observacao", f"Conta atualizada via MCP em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "distribuicao": [{
            "cCodDep": args["codigo_departamento"],
            "nPerDep": 100,
            "nValDep": args["valor_documento"]
        }]
    }
    
    # Adicionar identificador
    if args.get("codigo_lancamento_omie"):
        dados_omie["codigo_lancamento_omie"] = args["codigo_lancamento_omie"]
    if args.get("codigo_lancamento_integracao"):
        dados_omie["codigo_lancamento_integracao"] = args["codigo_lancamento_integracao"]
    
    # Adicionar fornecedor se especificado
    if codigo_fornecedor:
        dados_omie["codigo_cliente_fornecedor"] = codigo_fornecedor
    
    # Atualizar conta a pagar
    try:
        resultado = await omie_client.atualizar_conta_pagar(dados_omie)
        
        if "codigo_lancamento_omie" in resultado:
            return f"""🔄 Conta a Pagar atualizada com sucesso!

📋 Detalhes da conta:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Documento: {args['numero_documento']}
• Nota Fiscal: {args['nota_fiscal']}
• Valor: R$ {args['valor_documento']:,.2f}
• Vencimento: {args['data_vencimento']}
• Categoria: {args['codigo_categoria']}
• Departamento: {args['codigo_departamento']}
• Tipo Documento: {args['codigo_tipo_documento']}

👥 Fornecedor:
• Código: {codigo_fornecedor}
• Nome: {razao_social}
{f"• CNPJ/CPF: {cnpj_cpf}" if cnpj_cpf != "N/A" else ""}

🔗 Disponível no módulo Financeiro do Omie ERP
✅ Todos os campos obrigatórios atualizados!"""
        else:
            return f"🔄 Conta atualizada! Resposta: {json.dumps(resultado, indent=2)}"
            
    except Exception as e:
        return f"❌ Erro ao atualizar conta a pagar: {str(e)}"

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

async def handle_criar_conta_receber(args: Dict) -> str:
    """Handler para criar conta a receber com fluxo completo de consulta/criação de cliente"""
    
    # Verificar se foi fornecido CNPJ ou código do cliente
    if args.get("cnpj_cpf_cliente"):
        # FLUXO NOVO: Buscar/criar cliente por CNPJ
        cnpj_cpf = args["cnpj_cpf_cliente"]
        
        # Campos obrigatórios para fluxo com CNPJ
        campos_obrigatorios = {
            "cnpj_cpf_cliente": "CNPJ/CPF do cliente",
            "numero_documento": "Número do documento",
            "data_vencimento": "Data de vencimento", 
            "valor_documento": "Valor do documento",
            "codigo_categoria": "Código da categoria"
        }
        
        # Verificar campos obrigatórios
        campos_faltando = []
        for campo, descricao in campos_obrigatorios.items():
            if not args.get(campo):
                campos_faltando.append(f"• {descricao} ({campo})")
        
        if campos_faltando:
            return f"""❌ Erro: Campos obrigatórios não informados:

{chr(10).join(campos_faltando)}

💡 Fluxo automático com CNPJ:
• Informar CNPJ do cliente (será consultado/criado automaticamente)
• Se não existir, informar razao_social_cliente e email_cliente"""

        # ETAPA 0: Validar códigos obrigatórios
        validacoes_codigo = []
        
        # Validar categoria
        if args.get("codigo_categoria"):
            categoria_desc = await validar_codigo_categoria(args["codigo_categoria"])
            if categoria_desc is None:
                validacoes_codigo.append(f"• Categoria '{args['codigo_categoria']}' não encontrada")
        
        # Validar departamento
        if args.get("codigo_departamento"):
            departamento_desc = await validar_codigo_departamento(args["codigo_departamento"])
            if departamento_desc is None:
                validacoes_codigo.append(f"• Departamento '{args['codigo_departamento']}' não encontrado")
        
        # Validar tipo documento
        if args.get("codigo_tipo_documento"):
            tipo_doc_desc = await validar_codigo_tipo_documento(args["codigo_tipo_documento"])
            if tipo_doc_desc is None:
                validacoes_codigo.append(f"• Tipo documento '{args['codigo_tipo_documento']}' não encontrado")
        
        if validacoes_codigo:
            return f"""❌ Erro: Códigos inválidos:

{chr(10).join(validacoes_codigo)}

💡 Use as ferramentas de consulta para obter códigos válidos:
• consultar_categorias - Para códigos de categoria
• consultar_departamentos - Para códigos de departamento
• consultar_tipos_documento - Para códigos de tipo de documento"""

        # ETAPA 1: Consultar se cliente existe
        try:
            logger.info(f"🔍 Consultando cliente por CNPJ: {cnpj_cpf}")
            resultado_consulta = await omie_client.consultar_cliente_fornecedor_por_cnpj(cnpj_cpf)
            
            clientes = resultado_consulta.get("clientes_cadastro", [])
            
            if clientes:
                # Cliente encontrado
                codigo_cliente = clientes[0].get("codigo_cliente_omie")
                razao_social = clientes[0].get("razao_social", "N/A")
                logger.info(f"✅ Cliente encontrado: {codigo_cliente} - {razao_social}")
                
            else:
                # ETAPA 2: Cliente não existe, vamos criar
                logger.info(f"❌ Cliente não encontrado, criando novo...")
                
                # Verificar se temos dados suficientes para criar
                if not args.get("razao_social_cliente"):
                    return f"""❌ Cliente não encontrado para CNPJ {cnpj_cpf}

Para criar automaticamente, informe também:
• razao_social_cliente (obrigatório)
• email_cliente (opcional, padrão: contato@cliente.com)
• nome_fantasia (opcional)
• cidade (opcional)
• estado (opcional)"""
                
                # Dados para criar cliente
                import time
                codigo_integracao_cliente = f"MCP-CLI-{int(time.time())}"
                
                dados_cliente = {
                    "codigo_cliente_integracao": codigo_integracao_cliente,
                    "razao_social": args["razao_social_cliente"],
                    "cnpj_cpf": cnpj_cpf,
                    "email": args.get("email_cliente", "contato@cliente.com"),
                    "nome_fantasia": args.get("nome_fantasia", ""),
                    "cidade": args.get("cidade", ""),
                    "estado": args.get("estado", "")
                }
                
                resultado_cadastro = await omie_client.cadastrar_cliente_fornecedor(dados_cliente)
                
                if "codigo_cliente_omie" in resultado_cadastro:
                    codigo_cliente = resultado_cadastro["codigo_cliente_omie"]
                    razao_social = dados_cliente["razao_social"]
                    logger.info(f"✅ Cliente criado: {codigo_cliente} - {razao_social}")
                else:
                    return f"❌ Erro ao criar cliente: {resultado_cadastro}"
        
        except Exception as e:
            return f"❌ Erro ao consultar/criar cliente: {str(e)}"
            
    elif args.get("codigo_cliente_fornecedor"):
        # FLUXO ANTIGO: Usar código direto do cliente
        codigo_cliente = args["codigo_cliente_fornecedor"]
        razao_social = "Cliente"
        cnpj_cpf = "N/A"
        
    else:
        return """❌ Erro: Informe o cliente

Opções:
• codigo_cliente_fornecedor: Código direto (ex: 2675632305)
• cnpj_cpf_cliente: CNPJ para busca/criação automática"""
    
    # ETAPA 1: Criar conta a receber
    import time
    codigo_integracao = f"MCP-CR-{int(time.time())}"
    
    dados_omie = {
        "codigo_lancamento_integracao": codigo_integracao,
        "codigo_cliente_fornecedor": codigo_cliente,
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args["codigo_categoria"],
        "data_previsao": args["data_vencimento"],  # Usar mesma data do vencimento
        "observacao": args.get("observacao", f"Conta criada via MCP Completo em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    }
    
    # Adicionar campos opcionais se fornecidos
    if args.get("codigo_departamento"):
        dados_omie["distribuicao"] = [{
            "cCodDep": args["codigo_departamento"],
            "nPerDep": 100,
            "nValDep": args["valor_documento"]
        }]
    if args.get("codigo_tipo_documento"):
        dados_omie["codigo_tipo_documento"] = args["codigo_tipo_documento"]
    
    resultado = await omie_client.criar_conta_receber(dados_omie)
    
    if "codigo_lancamento_omie" in resultado:
        return f"""💰 Conta a Receber criada com sucesso!

📋 Detalhes da conta:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Código Integração: {codigo_integracao}
• Documento: {args['numero_documento']}
• Valor: R$ {args['valor_documento']:,.2f}
• Vencimento: {args['data_vencimento']}
• Categoria: {args['codigo_categoria']}

👥 Cliente processado:
• Código: {codigo_cliente}
• Nome: {razao_social}
{f"• CNPJ/CPF: {cnpj_cpf}" if cnpj_cpf != "N/A" else ""}

🔗 Disponível no módulo Financeiro do Omie ERP
✅ Fluxo completo: Consulta/Criação automática de cliente + Conta a receber!"""
    else:
        return f"💰 Conta criada! Resposta: {json.dumps(resultado, indent=2)}"

async def handle_atualizar_conta_receber(args: Dict) -> str:
    """Handler para atualizar conta a receber com campos obrigatórios"""
    
    # Validar campos obrigatórios
    campos_obrigatorios = {
        "numero_documento": "Número do documento",
        "data_vencimento": "Data de vencimento",
        "valor_documento": "Valor do documento",
        "codigo_categoria": "Código da categoria",
        "codigo_departamento": "Código do departamento",
        "codigo_tipo_documento": "Código do tipo de documento",
        "nota_fiscal": "Número da nota fiscal"
    }
    
    # Verificar se todos os campos obrigatórios estão presentes
    campos_faltando = []
    for campo, descricao in campos_obrigatorios.items():
        if not args.get(campo):
            campos_faltando.append(f"• {descricao} ({campo})")
    
    if campos_faltando:
        return f"""❌ Erro: Campos obrigatórios não informados:

{chr(10).join(campos_faltando)}

💡 Campos obrigatórios para atualização:
• numero_documento e nota_fiscal (mesmo valor)
• codigo_categoria (use consultar_categorias)
• codigo_departamento (use consultar_departamentos)
• codigo_tipo_documento (use consultar_tipos_documento)"""

    # Verificar identificador da conta (código Omie ou código integração)
    if not args.get("codigo_lancamento_omie") and not args.get("codigo_lancamento_integracao"):
        return """❌ Erro: Informe o identificador da conta a receber

Opções:
• codigo_lancamento_omie: Código do lançamento Omie (ex: 2682811481)
• codigo_lancamento_integracao: Código de integração (ex: MCP-CR-1752082514)"""

    # ETAPA 0: Validar códigos obrigatórios
    validacoes_codigo = []
    
    # Validar categoria
    if args.get("codigo_categoria"):
        categoria_desc = await validar_codigo_categoria(args["codigo_categoria"])
        if categoria_desc is None:
            validacoes_codigo.append(f"• Categoria '{args['codigo_categoria']}' não encontrada")
    
    # Validar departamento
    if args.get("codigo_departamento"):
        departamento_desc = await validar_codigo_departamento(args["codigo_departamento"])
        if departamento_desc is None:
            validacoes_codigo.append(f"• Departamento '{args['codigo_departamento']}' não encontrado")
    
    # Validar tipo documento
    if args.get("codigo_tipo_documento"):
        tipo_doc_desc = await validar_codigo_tipo_documento(args["codigo_tipo_documento"])
        if tipo_doc_desc is None:
            validacoes_codigo.append(f"• Tipo documento '{args['codigo_tipo_documento']}' não encontrado")
    
    if validacoes_codigo:
        return f"""❌ Erro: Códigos inválidos:

{chr(10).join(validacoes_codigo)}

💡 Use as ferramentas de consulta para obter códigos válidos:
• consultar_categorias - Para códigos de categoria
• consultar_departamentos - Para códigos de departamento
• consultar_tipos_documento - Para códigos de tipo de documento"""

    # Processar cliente se necessário
    codigo_cliente = args.get("codigo_cliente_fornecedor")
    razao_social = "Cliente"
    cnpj_cpf = "N/A"
    
    if args.get("cnpj_cpf_cliente"):
        # Mesmo fluxo de consulta/criação do criar_conta_receber
        try:
            cnpj_cpf = args["cnpj_cpf_cliente"]
            logger.info(f"🔍 Consultando cliente por CNPJ: {cnpj_cpf}")
            resultado_consulta = await omie_client.consultar_cliente_fornecedor_por_cnpj(cnpj_cpf)
            
            clientes = resultado_consulta.get("clientes_cadastro", [])
            
            if clientes:
                codigo_cliente = clientes[0].get("codigo_cliente_omie")
                razao_social = clientes[0].get("razao_social", "N/A")
                logger.info(f"✅ Cliente encontrado: {codigo_cliente} - {razao_social}")
            else:
                if not args.get("razao_social_cliente"):
                    return f"""❌ Cliente não encontrado para CNPJ {cnpj_cpf}
                    
Para criar automaticamente, informe também:
• razao_social_cliente (obrigatório)"""
                
                # Criar cliente
                import time
                codigo_integracao_cliente = f"MCP-CLI-{int(time.time())}"
                
                dados_cliente = {
                    "codigo_cliente_integracao": codigo_integracao_cliente,
                    "razao_social": args["razao_social_cliente"],
                    "cnpj_cpf": cnpj_cpf,
                    "email": args.get("email_cliente", "contato@cliente.com"),
                    "nome_fantasia": args.get("nome_fantasia", ""),
                    "cidade": args.get("cidade", ""),
                    "estado": args.get("estado", "")
                }
                
                resultado_cadastro = await omie_client.cadastrar_cliente_fornecedor(dados_cliente)
                
                if "codigo_cliente_omie" in resultado_cadastro:
                    codigo_cliente = resultado_cadastro["codigo_cliente_omie"]
                    razao_social = dados_cliente["razao_social"]
                    logger.info(f"✅ Cliente criado: {codigo_cliente} - {razao_social}")
                else:
                    return f"❌ Erro ao criar cliente: {resultado_cadastro}"
        
        except Exception as e:
            return f"❌ Erro ao consultar/criar cliente: {str(e)}"

    # Preparar dados para atualização
    dados_omie = {
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args["codigo_categoria"],
        "codigo_tipo_documento": args["codigo_tipo_documento"],
        "numero_documento_fiscal": args["nota_fiscal"],  # Campo para nota fiscal no Omie
        "data_previsao": args["data_vencimento"],
        "observacao": args.get("observacao", f"Conta atualizada via MCP em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "distribuicao": [{
            "cCodDep": args["codigo_departamento"],
            "nPerDep": 100,
            "nValDep": args["valor_documento"]
        }]
    }
    
    # Adicionar identificador
    if args.get("codigo_lancamento_omie"):
        dados_omie["codigo_lancamento_omie"] = args["codigo_lancamento_omie"]
    if args.get("codigo_lancamento_integracao"):
        dados_omie["codigo_lancamento_integracao"] = args["codigo_lancamento_integracao"]
    
    # Adicionar cliente se especificado
    if codigo_cliente:
        dados_omie["codigo_cliente_fornecedor"] = codigo_cliente
    
    # Atualizar conta a receber
    try:
        resultado = await omie_client.atualizar_conta_receber(dados_omie)
        
        if "codigo_lancamento_omie" in resultado:
            return f"""🔄 Conta a Receber atualizada com sucesso!

📋 Detalhes da conta:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Documento: {args['numero_documento']}
• Valor: R$ {args['valor_documento']:,.2f}
• Vencimento: {args['data_vencimento']}
• Categoria: {args['codigo_categoria']}
• Departamento: {args['codigo_departamento']}
• Tipo Documento: {args['codigo_tipo_documento']}
• Nota Fiscal: {args['nota_fiscal']}

👥 Cliente processado:
• Código: {codigo_cliente}
• Nome: {razao_social}
{f"• CNPJ/CPF: {cnpj_cpf}" if cnpj_cpf != "N/A" else ""}

🔗 Disponível no módulo Financeiro do Omie ERP
✅ Conta a receber atualizada com validação completa!"""
        else:
            return f"🔄 Conta atualizada! Resposta: {json.dumps(resultado, indent=2)}"
    
    except Exception as e:
        return f"❌ Erro ao atualizar conta a receber: {str(e)}"

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

@app.post("/test/atualizar-conta-pagar")
async def test_atualizar_conta_pagar(request: AtualizarContaPagarRequest):
    """Endpoint para testar atualização de conta a pagar"""
    result = await handle_atualizar_conta_pagar(request.dict())
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

@app.post("/test/criar-conta-receber")
async def test_criar_conta_receber(request: ContaReceberRequest):
    """Endpoint para testar criação de conta a receber"""
    result = await handle_criar_conta_receber(request.dict())
    return {"result": result}

@app.post("/test/atualizar-conta-receber")
async def test_atualizar_conta_receber(request: AtualizarContaReceberRequest):
    """Endpoint para testar atualização de conta a receber"""
    result = await handle_atualizar_conta_receber(request.dict())
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
    print("   • atualizar_conta_pagar")
    print("   • criar_conta_receber")
    print("   • atualizar_conta_receber")
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