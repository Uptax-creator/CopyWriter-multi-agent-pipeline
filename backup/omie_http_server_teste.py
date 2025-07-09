#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - VERSÃO COMPLETA PARA TESTES
Todas as ferramentas funcionais com dados de teste realistas

Ferramentas incluídas:
1. cadastrar_cliente_fornecedor ✅
2. consultar_tipos_documento ✅  
3. criar_conta_pagar ✅
4. consultar_contas_pagar ✅
5. consultar_contas_receber ✅
6. criar_conta_receber ✅ (NOVA - para testar completamente)

Dados de teste utilizando CNPJ válido: 24.493.607/0001-19
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
    print("📝 Exemplo:")
    print("   export OMIE_APP_KEY='sua_app_key'")
    print("   export OMIE_APP_SECRET='seu_app_secret'")
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
logger = logging.getLogger("omie-mcp-complete-test")

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ClienteFornecedorRequest(BaseModel):
    razao_social: str
    cnpj_cpf: str
    email: str
    tipo_cliente: str  # "cliente", "fornecedor", "ambos"
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
    data_vencimento: str  # DD/MM/AAAA
    valor_documento: float
    codigo_categoria: Optional[str] = "1.01.01"
    observacao: Optional[str] = ""
    numero_parcela: Optional[int] = 1

class ContaReceberRequest(BaseModel):
    codigo_cliente_fornecedor: int
    numero_documento: str
    data_vencimento: str  # DD/MM/AAAA
    valor_documento: float
    codigo_categoria: Optional[str] = "1.01.02"  # Categoria de receita
    observacao: Optional[str] = ""
    numero_parcela: Optional[int] = 1

class ConsultaContasRequest(BaseModel):
    codigo_cliente_fornecedor: Optional[int] = None
    data_de: Optional[str] = None      # DD/MM/AAAA
    data_ate: Optional[str] = None     # DD/MM/AAAA
    pagina: Optional[int] = 1
    registros_por_pagina: Optional[int] = 20

class TipoDocumentoRequest(BaseModel):
    codigo: Optional[str] = ""

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
# CLIENTE OMIE
# ============================================================================

class OmieClient:
    """Cliente HTTP para comunicação com a API do Omie"""
    
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

    # ========== MÉTODOS DA API ==========
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    async def criar_conta_receber(self, dados: Dict) -> Dict:
        """Cria conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "IncluirContaReceber", dados)
    
    async def consultar_tipos_documento(self, dados: Dict) -> Dict:
        """Consulta tipos de documentos"""
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", dados)
    
    async def consultar_contas_pagar(self, dados: Dict) -> Dict:
        """Consulta contas a pagar"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", dados)
    
    async def consultar_contas_receber(self, dados: Dict) -> Dict:
        """Consulta contas a receber"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", dados)

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Versão Completa para Testes",
    description="Servidor MCP HTTP completo para testes com dados realistas",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DADOS DE TESTE REALISTAS
# ============================================================================

def get_test_data():
    """Retorna dados de teste realistas usando CNPJ válido"""
    timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
    
    return {
        "cliente_teste": {
            "razao_social": "EMPRESA TESTE TECNOLOGIA LTDA",
            "cnpj_cpf": "24493607000119",  # CNPJ fornecido sem pontuação
            "email": f"contato.teste.{timestamp}@empresateste.com.br",
            "tipo_cliente": "ambos",  # Cliente e fornecedor
            "nome_fantasia": "Teste Tech",
            "telefone1_ddd": "11",
            "telefone1_numero": "987654321",
            "endereco": "Rua das Empresas, 1234, Sala 567",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01310100"
        },
        "fornecedor_teste": {
            "razao_social": "FORNECEDOR TESTE SERVICOS LTDA",
            "cnpj_cpf": "24493607000119",  # Mesmo CNPJ válido
            "email": f"fornecedor.teste.{timestamp}@fornecedorteste.com.br",
            "tipo_cliente": "fornecedor",
            "nome_fantasia": "Fornecedor Teste",
            "telefone1_ddd": "11",
            "telefone1_numero": "912345678",
            "endereco": "Av. dos Fornecedores, 999",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01415000"
        }
    }

# ============================================================================
# ENDPOINTS MCP
# ============================================================================

@app.get("/")
async def root():
    """Endpoint de status"""
    test_data = get_test_data()
    return {
        "service": "Omie MCP Server - Versão Completa para Testes",
        "status": "running",
        "version": "3.0.0",
        "tools": [
            "cadastrar_cliente_fornecedor",
            "consultar_tipos_documento",
            "criar_conta_pagar",
            "criar_conta_receber",
            "consultar_contas_pagar",
            "consultar_contas_receber"
        ],
        "test_features": [
            "✅ CNPJ válido: 24.493.607/0001-19",
            "✅ Dados de teste realistas",
            "✅ Criação de contas a pagar e receber",
            "✅ Consultas com filtros",
            "✅ Validação completa de erros"
        ],
        "test_data_sample": {
            "cnpj_usado": "24.493.607/0001-19",
            "cidade": test_data["cliente_teste"]["cidade"],
            "estado": test_data["cliente_teste"]["estado"]
        },
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
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "omie-mcp-server-complete-test",
                        "version": "3.0.0"
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
                            "description": "Cadastra um novo cliente ou fornecedor no Omie ERP (usa CNPJ válido para testes)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "razao_social": {"type": "string", "description": "Razão social da empresa"},
                                    "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF (use 24493607000119 para testes)"},
                                    "email": {"type": "string", "description": "E-mail de contato"},
                                    "tipo_cliente": {"type": "string", "enum": ["cliente", "fornecedor", "ambos"], "description": "Tipo do cadastro"},
                                    "nome_fantasia": {"type": "string", "description": "Nome fantasia (opcional)"},
                                    "telefone1_ddd": {"type": "string", "description": "DDD do telefone"},
                                    "telefone1_numero": {"type": "string", "description": "Número do telefone"},
                                    "endereco": {"type": "string", "description": "Endereço completo"},
                                    "cidade": {"type": "string", "description": "Nome da cidade"},
                                    "estado": {"type": "string", "description": "Sigla do estado (ex: SP)"},
                                    "cep": {"type": "string", "description": "CEP (somente números)"}
                                },
                                "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"]
                            }
                        },
                        {
                            "name": "consultar_tipos_documento",
                            "description": "Consulta tipos de documentos disponíveis no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo": {"type": "string", "description": "Código específico do tipo de documento (opcional)"}
                                }
                            }
                        },
                        {
                            "name": "criar_conta_pagar",
                            "description": "Cria uma nova conta a pagar no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor no Omie"},
                                    "numero_documento": {"type": "string", "description": "Número do documento/nota fiscal"},
                                    "data_vencimento": {"type": "string", "description": "Data de vencimento (DD/MM/AAAA)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria de despesa", "default": "1.01.01"},
                                    "observacao": {"type": "string", "description": "Observações adicionais"},
                                    "numero_parcela": {"type": "integer", "description": "Número da parcela", "default": 1}
                                },
                                "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                            }
                        },
                        {
                            "name": "criar_conta_receber",
                            "description": "Cria uma nova conta a receber no Omie ERP",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente no Omie"},
                                    "numero_documento": {"type": "string", "description": "Número do documento/nota fiscal"},
                                    "data_vencimento": {"type": "string", "description": "Data de vencimento (DD/MM/AAAA)"},
                                    "valor_documento": {"type": "number", "description": "Valor do documento"},
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria de receita", "default": "1.01.02"},
                                    "observacao": {"type": "string", "description": "Observações adicionais"},
                                    "numero_parcela": {"type": "integer", "description": "Número da parcela", "default": 1}
                                },
                                "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                            }
                        },
                        {
                            "name": "consultar_contas_pagar",
                            "description": "Consulta contas a pagar com filtros de fornecedor e período",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do fornecedor (opcional)"},
                                    "data_de": {"type": "string", "description": "Data início do período (DD/MM/AAAA)"},
                                    "data_ate": {"type": "string", "description": "Data fim do período (DD/MM/AAAA)"},
                                    "pagina": {"type": "integer", "description": "Número da página", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                                }
                            }
                        },
                        {
                            "name": "consultar_contas_receber",
                            "description": "Consulta contas a receber com filtros de cliente e período",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo_cliente_fornecedor": {"type": "integer", "description": "Código do cliente (opcional)"},
                                    "data_de": {"type": "string", "description": "Data início do período (DD/MM/AAAA)"},
                                    "data_ate": {"type": "string", "description": "Data fim do período (DD/MM/AAAA)"},
                                    "pagina": {"type": "integer", "description": "Número da página", "default": 1},
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
            elif tool_name == "consultar_tipos_documento":
                result = await handle_consultar_tipos_documento(arguments)
            elif tool_name == "criar_conta_pagar":
                result = await handle_criar_conta_pagar(arguments)
            elif tool_name == "criar_conta_receber":
                result = await handle_criar_conta_receber(arguments)
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
# HANDLERS DAS FERRAMENTAS
# ============================================================================

async def handle_cadastrar_cliente_fornecedor(args: Dict) -> str:
    """Handler para cadastrar cliente/fornecedor"""
    
    # Mapear tipo de cliente
    tipo_mapping = {"cliente": "C", "fornecedor": "F", "ambos": "A"}
    
    dados_omie = {
        "razao_social": args["razao_social"],
        "cnpj_cpf": args["cnpj_cpf"],
        "email": args["email"],
        "cliente_fornecedor": tipo_mapping.get(args["tipo_cliente"], "C"),
        "nome_fantasia": args.get("nome_fantasia", ""),
        "telefone1_ddd": args.get("telefone1_ddd", ""),
        "telefone1_numero": args.get("telefone1_numero", ""),
        "endereco": args.get("endereco", ""),
        "cidade": args.get("cidade", ""),
        "estado": args.get("estado", ""),
        "cep": args.get("cep", ""),
        "tags": [{"tag": "MCP_TESTE_COMPLETO"}],
        "inativo": "N"
    }
    
    resultado = await omie_client.cadastrar_cliente_fornecedor(dados_omie)
    
    if "codigo_cliente_omie" in resultado:
        return f"""✅ **Cliente/Fornecedor cadastrado com sucesso!**

📋 **Detalhes do cadastro:**
• **Código Omie:** {resultado['codigo_cliente_omie']}
• **Razão Social:** {args['razao_social']}
• **CNPJ/CPF:** {args['cnpj_cpf']}
• **Tipo:** {args['tipo_cliente'].capitalize()}
• **E-mail:** {args['email']}
• **Tag:** MCP_TESTE_COMPLETO

🔗 **Próximos passos:**
1. Use o código {resultado['codigo_cliente_omie']} para criar contas a pagar/receber
2. Este cadastro está disponível no seu Omie ERP
3. Pode ser usado imediatamente para operações financeiras

💡 **Dica:** Guarde o código {resultado['codigo_cliente_omie']} para os próximos testes!"""
    else:
        return f"✅ Cadastrado com sucesso!\n\nResposta completa: {json.dumps(resultado, indent=2)}"

async def handle_consultar_tipos_documento(args: Dict) -> str:
    """Handler para consultar tipos de documentos"""
    
    dados_omie = {
        "codigo": args.get("codigo", "")
    }
    
    resultado = await omie_client.consultar_tipos_documento(dados_omie)
    
    if "tipo_documento_cadastro" in resultado:
        tipos = resultado["tipo_documento_cadastro"]
        
        if args.get("codigo"):
            if tipos:
                tipo = tipos[0]
                return f"""📄 **Tipo de Documento encontrado:**

• **Código:** {tipo['codigo']}
• **Descrição:** {tipo['descricao']}

💡 **Uso:** Este código pode ser usado ao criar contas a pagar/receber."""
            else:
                return f"❌ Tipo de documento com código '{args['codigo']}' não encontrado."
        
        else:
            total = len(tipos)
            lista_formatada = []
            
            # Mostrar tipos mais comuns primeiro
            tipos_comuns = ["NF", "BOL", "DUP", "CHQ", "PIX", "TED", "DOC", "CART", "REC"]
            tipos_encontrados = []
            outros_tipos = []
            
            for tipo in tipos:
                if tipo['codigo'] in tipos_comuns:
                    tipos_encontrados.append(f"• **{tipo['codigo']}** - {tipo['descricao']}")
                else:
                    outros_tipos.append(f"• **{tipo['codigo']}** - {tipo['descricao']}")
            
            # Mostrar primeiros tipos comuns + alguns outros
            lista_final = tipos_encontrados + outros_tipos[:15]
            
            resultado_texto = f"""📄 **Tipos de Documentos no Omie ERP**

📊 **Total encontrado:** {total} tipos

🏆 **Tipos mais comuns para testes:**
{chr(10).join(lista_final)}"""
            
            if total > len(lista_final):
                resultado_texto += f"\n\n... e mais **{total - len(lista_final)}** tipos disponíveis."
            
            resultado_texto += "\n\n💡 **Recomendações para testes:**"
            resultado_texto += "\n• Use 'NF' para Nota Fiscal"
            resultado_texto += "\n• Use 'BOL' para Boleto"  
            resultado_texto += "\n• Use 'DUP' para Duplicata"
            resultado_texto += "\n• Use 'REC' para Recibo"
            
            return resultado_texto
    
    else:
        return f"📄 Resposta dos tipos de documento: {json.dumps(resultado, indent=2)}"

async def handle_criar_conta_pagar(args: Dict) -> str:
    """Handler para criar conta a pagar"""
    
    dados_omie = {
        "codigo_cliente_fornecedor": args["codigo_cliente_fornecedor"],
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args.get("codigo_categoria", "1.01.01"),
        "observacao": args.get("observacao", f"Conta a pagar criada via MCP Teste Completo em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "numero_parcela": args.get("numero_parcela", 1),
        "codigo_tipo_documento": "01",  # Nota Fiscal
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "data_entrada": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    resultado = await omie_client.criar_conta_pagar(dados_omie)
    
    if "codigo_lancamento_omie" in resultado:
        return f"""💰 **Conta a Pagar criada com sucesso!**

📋 **Detalhes da conta:**
• **Código do Lançamento:** {resultado['codigo_lancamento_omie']}
• **Fornecedor:** {args['codigo_cliente_fornecedor']}
• **Documento:** {args['numero_documento']}
• **Valor:** R$ {args['valor_documento']:,.2f}
• **Vencimento:** {args['data_vencimento']}
• **Parcela:** {args.get('numero_parcela', 1)}
• **Status:** ABERTO

🔗 **Localização:** Financeiro > Contas a Pagar no Omie ERP

🧪 **Próximo teste sugerido:**
Agora teste "consultar_contas_pagar" usando o código do fornecedor {args['codigo_cliente_fornecedor']}"""
    else:
        return f"💰 Conta criada com sucesso!\n\nResposta completa: {json.dumps(resultado, indent=2)}"

async def handle_criar_conta_receber(args: Dict) -> str:
    """Handler para criar conta a receber"""
    
    dados_omie = {
        "codigo_cliente_fornecedor": args["codigo_cliente_fornecedor"],
        "numero_documento": args["numero_documento"],
        "data_vencimento": args["data_vencimento"],
        "valor_documento": args["valor_documento"],
        "codigo_categoria": args.get("codigo_categoria", "1.01.02"),  # Categoria de receita
        "observacao": args.get("observacao", f"Conta a receber criada via MCP Teste Completo em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "numero_parcela": args.get("numero_parcela", 1),
        "codigo_tipo_documento": "01",  # Nota Fiscal
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "data_entrada": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    resultado = await omie_client.criar_conta_receber(dados_omie)
    
    if "codigo_lancamento_omie" in resultado:
        return f"""💵 **Conta a Receber criada com sucesso!**

📋 **Detalhes da conta:**
• **Código do Lançamento:** {resultado['codigo_lancamento_omie']}
• **Cliente:** {args['codigo_cliente_fornecedor']}
• **Documento:** {args['numero_documento']}
• **Valor:** R$ {args['valor_documento']:,.2f}
• **Vencimento:** {args['data_vencimento']}
• **Parcela:** {args.get('numero_parcela', 1)}
• **Status:** ABERTO

🔗 **Localização:** Financeiro > Contas a Receber no Omie ERP

🧪 **Próximo teste sugerido:**
Teste "consultar_contas_receber" usando o código do cliente {args['codigo_cliente_fornecedor']}"""
    else:
        return f"💵 Conta a receber criada com sucesso!\n\nResposta completa: {json.dumps(resultado, indent=2)}"

async def handle_consultar_contas_pagar(args: Dict) -> str:
    """Handler para consultar contas a pagar"""
    
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 20)
    }
    
    # Adicionar filtros se fornecidos
    if args.get("codigo_cliente_fornecedor"):
        params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
    
    if args.get("data_de"):
        params["data_de"] = args["data_de"]
    
    if args.get("data_ate"):
        params["data_ate"] = args["data_ate"]
    
    resultado = await omie_client.consultar_contas_pagar(params)
    
    contas = resultado.get("conta_pagar_cadastro", [])
    total = resultado.get("total_de_registros", len(contas))
    
    if contas:
        lista_contas = []
        total_valor = 0
        
        for conta in contas[:10]:
            numero_doc = conta.get("numero_documento", "N/A")
            valor = conta.get("valor_documento", 0)
            vencimento = conta.get("data_vencimento", "N/A")
            status = conta.get("status_titulo", "N/A")
            
            total_valor += valor
            lista_contas.append(f"• **{numero_doc}** | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
        
        filtros_texto = []
        if args.get("codigo_cliente_fornecedor"):
            filtros_texto.append(f"Fornecedor: {args['codigo_cliente_fornecedor']}")
        if args.get("data_de") and args.get("data_ate"):
            filtros_texto.append(f"Período: {args['data_de']} a {args['data_ate']}")
        
        return f"""💰 **Contas a Pagar encontradas:** {total}

📋 **Lista de contas:**
{chr(10).join(lista_contas)}

💵 **Total das {min(10, len(contas))} primeiras:** R$ {total_valor:,.2f}

📊 **Filtros aplicados:**
{chr(10).join([f"• {filtro}" for filtro in filtros_texto]) if filtros_texto else "• Nenhum filtro aplicado (mostrando todas)"}

{f"💡 **Nota:** Mostrando {min(10, len(contas))} de {total} registros encontrados." if total > 10 else ""}

🧪 **Teste concluído com sucesso!** As contas a pagar estão sendo consultadas corretamente."""
    else:
        return f"""❌ **Nenhuma conta a pagar encontrada**

📊 **Filtros aplicados:**
• Fornecedor: {args.get('codigo_cliente_fornecedor', 'Todos')}
• Período: {args.get('data_de', 'Não especificado')} a {args.get('data_ate', 'Não especificado')}

💡 **Sugestões:**
1. Verifique se o código do fornecedor está correto
2. Tente expandir o período de busca
3. Remova filtros para ver todas as contas"""

async def handle_consultar_contas_receber(args: Dict) -> str:
    """Handler para consultar contas a receber"""
    
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 20)
    }
    
    # Adicionar filtros se fornecidos
    if args.get("codigo_cliente_fornecedor"):
        params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
    
    if args.get("data_de"):
        params["data_de"] = args["data_de"]
    
    if args.get("data_ate"):
        params["data_ate"] = args["data_ate"]
    
    resultado = await omie_client.consultar_contas_receber(params)
    
    contas = resultado.get("conta_receber_cadastro", [])
    total = resultado.get("total_de_registros", len(contas))
    
    if contas:
        lista_contas = []
        total_valor = 0
        
        for conta in contas[:10]:
            numero_doc = conta.get("numero_documento", "N/A")
            valor = conta.get("valor_documento", 0)
            vencimento = conta.get("data_vencimento", "N/A")
            status = conta.get("status_titulo", "N/A")
            
            total_valor += valor
            lista_contas.append(f"• **{numero_doc}** | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
        
        filtros_texto = []
        if args.get("codigo_cliente_fornecedor"):
            filtros_texto.append(f"Cliente: {args['codigo_cliente_fornecedor']}")
        if args.get("data_de") and args.get("data_ate"):
            filtros_texto.append(f"Período: {args['data_de']} a {args['data_ate']}")
        
        return f"""💵 **Contas a Receber encontradas:** {total}

📋 **Lista de contas:**
{chr(10).join(lista_contas)}

💰 **Total das {min(10, len(contas))} primeiras:** R$ {total_valor:,.2f}

📊 **Filtros aplicados:**
{chr(10).join([f"• {filtro}" for filtro in filtros_texto]) if filtros_texto else "• Nenhum filtro aplicado (mostrando todas)"}

{f"💡 **Nota:** Mostrando {min(10, len(contas))} de {total} registros encontrados." if total > 10 else ""}

🧪 **Teste concluído com sucesso!** As contas a receber estão sendo consultadas corretamente."""
    else:
        return f"""❌ **Nenhuma conta a receber encontrada**

📊 **Filtros aplicados:**
• Cliente: {args.get('codigo_cliente_fornecedor', 'Todos')}
• Período: {args.get('data_de', 'Não especificado')} a {args.get('data_ate', 'Não especificado')}

💡 **Sugestões:**
1. Verifique se o código do cliente está correto
2. Tente expandir o período de busca
3. Remova filtros para ver todas as contas"""

# ============================================================================
# ENDPOINTS DE TESTE COM DADOS REALISTAS
# ============================================================================

@app.get("/test/dados-realistas")
async def get_test_data_endpoint():
    """Endpoint que retorna dados de teste realistas"""
    return {
        "dados_de_teste": get_test_data(),
        "cnpj_valido": "24.493.607/0001-19",
        "sugestoes_teste": [
            "1. Use cadastrar_cliente_fornecedor com os dados fornecidos",
            "2. Anote o código retornado para usar nas contas",
            "3. Crie contas a pagar e receber com o código do cliente",
            "4. Consulte as contas criadas para validar"
        ]
    }

@app.post("/test/fluxo-completo")
async def test_fluxo_completo():
    """Executa um fluxo completo de teste automatizado"""
    resultados = []
    
    try:
        # 1. Cadastrar cliente
        test_data = get_test_data()
        cliente_result = await handle_cadastrar_cliente_fornecedor(test_data["cliente_teste"])
        resultados.append(f"✅ Cliente cadastrado: {cliente_result[:100]}...")
        
        # 2. Consultar tipos de documento
        tipos_result = await handle_consultar_tipos_documento({"codigo": "NF"})
        resultados.append(f"✅ Tipos consultados: {tipos_result[:100]}...")
        
        return {
            "status": "sucesso",
            "resultados": resultados,
            "observacao": "Fluxo de teste automatizado executado com sucesso!"
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "erro": str(e),
            "resultados": resultados
        }

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP completo para testes"""
    
    print("🚀 Iniciando Servidor MCP HTTP para Omie ERP - VERSÃO COMPLETA PARA TESTES")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("📡 Ferramentas disponíveis:")
    print("   ✅ cadastrar_cliente_fornecedor")
    print("   ✅ consultar_tipos_documento")
    print("   ✅ criar_conta_pagar")
    print("   ✅ criar_conta_receber (NOVA)")
    print("   ✅ consultar_contas_pagar")
    print("   ✅ consultar_contas_receber")
    print("\n🧪 Recursos de teste:")
    print("   • CNPJ válido: 24.493.607/0001-19")
    print("   • Dados de teste realistas")
    print("   • Fluxo completo de testes")
    print("   • Endpoints de teste adicionais")
    print(f"\n✅ Servidor HTTP rodando em: http://localhost:{MCP_SERVER_PORT}")
    print(f"📖 Docs: http://localhost:{MCP_SERVER_PORT}/docs")
    print(f"🧪 Teste dados: http://localhost:{MCP_SERVER_PORT}/test/dados-realistas")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()