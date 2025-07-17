#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - CORREÇÃO DA ESTRUTURA DO PAYLOAD
Corrige o erro 500 SOAP "Bad Request" ajustando a estrutura correta do payload

PROBLEMA IDENTIFICADO:
- Estrutura dupla do payload causando erro SOAP
- Função de validação criando payload dentro de payload
- API Omie espera estrutura específica

SOLUÇÃO:
1. Separar limpeza de dados da criação do payload
2. Criar payload Omie apenas uma vez com estrutura correta
3. Manter validação JSON mas sem duplicar estrutura
"""

import asyncio
import json
import logging
import os
import sys
import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")

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
logger = logging.getLogger("omie-mcp-fixed")

# ============================================================================
# UTILITÁRIOS DE LIMPEZA
# ============================================================================

def clean_string(value: Any) -> str:
    """Limpa string removendo caracteres problemáticos"""
    if value is None:
        return ""
    
    text = str(value).strip()
    
    # Remover caracteres de controle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Normalizar espaços
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def clean_data_recursive(data: Any) -> Any:
    """Limpa dados recursivamente"""
    if isinstance(data, dict):
        return {k: clean_data_recursive(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_data_recursive(item) for item in data]
    elif isinstance(data, str):
        return clean_string(data)
    else:
        return data

# ============================================================================
# MODELOS PYDANTIC
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
# CLIENTE OMIE CORRIGIDO
# ============================================================================

class OmieClient:
    """Cliente para comunicação com API Omie com estrutura correta"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = OMIE_BASE_URL
    
    async def _make_request(self, endpoint: str, call: str, params: Dict) -> Dict:
        """Faz requisição para API Omie com estrutura correta"""
        
        # Limpar dados do parâmetro
        clean_params = clean_data_recursive(params)
        
        # Criar payload com estrutura correta do Omie
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [clean_params]  # param é sempre um array
        }
        
        url = f"{self.base_url}/{endpoint}/"
        
        logger.info(f"📡 Requisição Omie: {endpoint}/{call}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                logger.info(f"📥 Status HTTP: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"❌ Erro HTTP {response.status_code}: {error_text}")
                    
                    # Tentar extrair mensagem de erro SOAP se existir
                    if "soap-envelope" in error_text.lower():
                        raise HTTPException(
                            status_code=400,
                            detail="Erro na estrutura da requisição. Verifique os dados enviados."
                        )
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro na API Omie: {error_text[:200]}"
                    )
                
                result = response.json()
                
                # Verificar erro no formato Omie
                if isinstance(result, dict) and "faultstring" in result:
                    error_msg = result.get("faultstring", "Erro desconhecido")
                    logger.error(f"❌ Erro Omie: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                
                logger.info("✅ Requisição bem-sucedida")
                return result
                
        except httpx.TimeoutException:
            logger.error("❌ Timeout na requisição")
            raise HTTPException(status_code=504, detail="Timeout na comunicação com Omie")
        except httpx.HTTPError as e:
            logger.error(f"❌ Erro HTTP: {e}")
            raise HTTPException(status_code=500, detail=f"Erro de comunicação: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    async def pesquisar_tipos_documento(self, codigo: str = "") -> Dict:
        """Pesquisa tipos de documento no Omie"""
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", {"codigo": codigo})

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Correção Estrutura",
    description="Servidor MCP com estrutura correta de payload",
    version="7.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Omie MCP Server",
        "status": "running",
        "version": "7.0.0",
        "tools": [
            "cadastrar_cliente_fornecedor",
            "criar_conta_pagar",
            "pesquisar_tipos_documento"
        ],
        "fixes": [
            "✅ Estrutura correta do payload Omie",
            "✅ Limpeza de dados sem duplicação",
            "✅ Tratamento de erros SOAP",
            "✅ Validação JSON apropriada"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
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
                    "serverInfo": {"name": "omie-mcp-server", "version": "7.0.0"}
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
                                    "estado": {"type": "string", "description": "Estado (UF)"},
                                    "cep": {"type": "string", "description": "CEP"}
                                },
                                "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"]
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
                                    "codigo_categoria": {"type": "string", "description": "Código da categoria"},
                                    "observacao": {"type": "string", "description": "Observações"},
                                    "numero_parcela": {"type": "integer", "description": "Número da parcela"}
                                },
                                "required": ["codigo_cliente_fornecedor", "numero_documento", "data_vencimento", "valor_documento"]
                            }
                        },
                        {
                            "name": "pesquisar_tipos_documento",
                            "description": "Pesquisa tipos de documento disponíveis no Omie",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo": {"type": "string", "description": "Código do tipo (vazio para listar todos)"}
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
                result = await handle_cadastrar_cliente(arguments)
            elif tool_name == "criar_conta_pagar":
                result = await handle_criar_conta_pagar(arguments)
            elif tool_name == "pesquisar_tipos_documento":
                result = await handle_pesquisar_tipos_documento(arguments)
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
# HANDLERS
# ============================================================================

async def handle_cadastrar_cliente(args: Dict) -> str:
    """Handler para cadastrar cliente/fornecedor"""
    
    # Mapear tipo
    tipo_map = {"cliente": "C", "fornecedor": "F", "ambos": "A"}
    
    # Preparar dados do cliente
    dados_cliente = {
        "razao_social": args.get("razao_social", ""),
        "cnpj_cpf": args.get("cnpj_cpf", ""),
        "email": args.get("email", ""),
        "cliente_fornecedor": tipo_map.get(args.get("tipo_cliente", "cliente"), "C"),
        "nome_fantasia": args.get("nome_fantasia", ""),
        "telefone1_ddd": args.get("telefone1_ddd", ""),
        "telefone1_numero": args.get("telefone1_numero", ""),
        "endereco": args.get("endereco", ""),
        "cidade": args.get("cidade", ""),
        "estado": args.get("estado", ""),
        "cep": args.get("cep", ""),
        "tags": [{"tag": "MCP_CRIADO"}],
        "inativo": "N"
    }
    
    # Remover campos vazios
    dados_cliente = {k: v for k, v in dados_cliente.items() if v}
    
    logger.info(f"📋 Cadastrando cliente: {dados_cliente.get('razao_social')}")
    
    try:
        resultado = await omie_client.cadastrar_cliente_fornecedor(dados_cliente)
        
        if "codigo_cliente_omie" in resultado:
            return f"""✅ Cliente/Fornecedor cadastrado com sucesso!

📋 Detalhes:
• Código Omie: {resultado['codigo_cliente_omie']}
• Código Integração: {resultado.get('codigo_cliente_integracao', 'N/A')}
• Razão Social: {args.get('razao_social')}
• CNPJ/CPF: {args.get('cnpj_cpf')}
• Tipo: {args.get('tipo_cliente')}
• E-mail: {args.get('email')}

🔗 Disponível no Omie ERP com a tag MCP_CRIADO"""
        else:
            return f"✅ Operação concluída. Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"
            
    except HTTPException as e:
        return f"❌ Erro: {e.detail}"
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return f"❌ Erro inesperado: {str(e)}"

async def handle_criar_conta_pagar(args: Dict) -> str:
    """Handler para criar conta a pagar"""
    
    # Preparar dados da conta
    dados_conta = {
        "codigo_cliente_fornecedor": args.get("codigo_cliente_fornecedor"),
        "numero_documento": args.get("numero_documento"),
        "data_vencimento": args.get("data_vencimento"),
        "valor_documento": args.get("valor_documento"),
        "codigo_categoria": args.get("codigo_categoria", "1.01.01"),
        "observacao": args.get("observacao", f"Criado via MCP em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        "numero_parcela": args.get("numero_parcela", 1),
        "codigo_tipo_documento": "99999",  # Outros
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "data_entrada": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    logger.info(f"💰 Criando conta a pagar: {dados_conta.get('numero_documento')}")
    
    try:
        resultado = await omie_client.criar_conta_pagar(dados_conta)
        
        if "codigo_lancamento_omie" in resultado:
            return f"""💰 Conta a Pagar criada com sucesso!

📋 Detalhes:
• Código Lançamento: {resultado['codigo_lancamento_omie']}
• Código Fornecedor: {args.get('codigo_cliente_fornecedor')}
• Documento: {args.get('numero_documento')}
• Valor: R$ {args.get('valor_documento'):,.2f}
• Vencimento: {args.get('data_vencimento')}
• Categoria: {args.get('codigo_categoria', '1.01.01')}

🔗 Disponível no módulo Financeiro do Omie"""
        else:
            return f"💰 Operação concluída. Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"
            
    except HTTPException as e:
        return f"❌ Erro: {e.detail}"
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return f"❌ Erro inesperado: {str(e)}"

async def handle_pesquisar_tipos_documento(args: Dict) -> str:
    """Handler para pesquisar tipos de documento"""
    
    codigo = args.get("codigo", "")
    
    logger.info(f"🔍 Pesquisando tipos de documento: {codigo or 'todos'}")
    
    try:
        resultado = await omie_client.pesquisar_tipos_documento(codigo)
        
        if "tipo_documento_cadastro" in resultado:
            tipos = resultado["tipo_documento_cadastro"]
            
            if not tipos:
                return "📄 Nenhum tipo de documento encontrado."
            
            # Formatar lista de tipos
            lista_tipos = []
            for tipo in tipos[:20]:  # Limitar a 20 para não ficar muito longo
                lista_tipos.append(f"• {tipo['codigo']} - {tipo['descricao']}")
            
            resposta = f"""📄 Tipos de Documento encontrados: {len(tipos)}

{chr(10).join(lista_tipos)}"""
            
            if len(tipos) > 20:
                resposta += f"\n\n... e mais {len(tipos) - 20} tipos."
            
            return resposta
        else:
            return f"📄 Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"
            
    except HTTPException as e:
        return f"❌ Erro: {e.detail}"
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return f"❌ Erro inesperado: {str(e)}"

# ============================================================================
# ENDPOINTS DE TESTE
# ============================================================================

@app.post("/test/cliente")
async def test_cliente(request: ClienteFornecedorRequest):
    """Endpoint de teste para cadastro de cliente"""
    result = await handle_cadastrar_cliente(request.dict())
    return {"result": result}

@app.post("/test/conta-pagar")
async def test_conta_pagar(request: ContaPagarRequest):
    """Endpoint de teste para conta a pagar"""
    result = await handle_criar_conta_pagar(request.dict())
    return {"result": result}

@app.post("/test/tipos-documento")
async def test_tipos_documento(request: TipoDocumentoRequest):
    """Endpoint de teste para tipos de documento"""
    result = await handle_pesquisar_tipos_documento(request.dict())
    return {"result": result}

@app.get("/test/minimal")
async def test_minimal():
    """Teste mínimo de funcionamento"""
    
    try:
        # Testar com pesquisa de tipos (mais simples)
        resultado = await omie_client.pesquisar_tipos_documento("")
        
        return {
            "status": "success",
            "message": "API Omie respondendo corretamente",
            "sample_response": str(resultado)[:200] + "..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP"""
    
    print("🚀 Iniciando Servidor MCP HTTP para Omie ERP")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("\n📡 Ferramentas disponíveis:")
    print("   • cadastrar_cliente_fornecedor")
    print("   • criar_conta_pagar")
    print("   • pesquisar_tipos_documento")
    print("\n✅ Correções aplicadas:")
    print("   • Estrutura correta do payload Omie")
    print("   • Tratamento de erros SOAP")
    print("   • Validação apropriada de dados")
    print(f"\n✅ Servidor rodando em: http://localhost:{MCP_SERVER_PORT}")
    print(f"📖 Documentação: http://localhost:{MCP_SERVER_PORT}/docs")
    print(f"🧪 Teste mínimo: http://localhost:{MCP_SERVER_PORT}/test/minimal")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()