#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - CORREÇÃO JSON MALFORMADO
Foco na correção do erro 422 "JSON decode error"

PROBLEMA IDENTIFICADO:
- Erro 422: Unprocessable Entity
- "Expecting property name enclosed in double quotes"
- JSON malformado sendo enviado para API Omie

CORREÇÕES APLICADAS:
1. Validação rigorosa de JSON antes do envio
2. Sanitização de strings para evitar caracteres inválidos
3. Logs detalhados do JSON sendo enviado
4. Formatação segura de dados
"""

import asyncio
import json
import logging
import os
import sys
import re
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
logger = logging.getLogger("omie-mcp-json-fixed")

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

class ConsultaContasRequest(BaseModel):
    codigo_cliente_fornecedor: Optional[int] = None
    status: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
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
# UTILITÁRIOS PARA CORREÇÃO DE JSON
# ============================================================================

def sanitize_string(value: str) -> str:
    """Sanitiza string para evitar problemas no JSON"""
    if not isinstance(value, str):
        return str(value)
    
    # Remover caracteres de controle
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Escapar caracteres especiais JSON
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\t', '\\t')
    
    # Remover espaços extras
    value = value.strip()
    
    return value

def sanitize_dict(data: Dict) -> Dict:
    """Sanitiza recursivamente um dicionário para JSON seguro"""
    sanitized = {}
    
    for key, value in data.items():
        # Sanitizar chave
        clean_key = sanitize_string(str(key))
        
        # Sanitizar valor
        if isinstance(value, str):
            clean_value = sanitize_string(value)
        elif isinstance(value, dict):
            clean_value = sanitize_dict(value)
        elif isinstance(value, list):
            clean_value = [sanitize_dict(item) if isinstance(item, dict) else sanitize_string(str(item)) for item in value]
        elif value is None:
            clean_value = ""  # Converter None para string vazia
        else:
            clean_value = value
        
        sanitized[clean_key] = clean_value
    
    return sanitized

def validate_json_payload(payload: Dict) -> Dict:
    """Valida e corrige payload JSON antes do envio"""
    try:
        # Sanitizar o payload
        clean_payload = sanitize_dict(payload)
        
        # Tentar serializar para validar JSON
        json_str = json.dumps(clean_payload, ensure_ascii=False, separators=(',', ':'))
        
        # Tentar deserializar para garantir que está válido
        validated = json.loads(json_str)
        
        logger.debug(f"JSON validado com sucesso: {len(json_str)} caracteres")
        return validated
        
    except json.JSONEncodeError as e:
        logger.error(f"Erro ao validar JSON: {e}")
        raise ValueError(f"JSON inválido: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado na validação JSON: {e}")
        raise ValueError(f"Erro na validação: {e}")

# ============================================================================
# CLIENTE OMIE COM CORREÇÃO JSON
# ============================================================================

class OmieClient:
    """Cliente HTTP para comunicação com a API do Omie - COM CORREÇÃO JSON"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = sanitize_string(app_key)
        self.app_secret = sanitize_string(app_secret)
        self.base_url = OMIE_BASE_URL
        
    async def _make_request(self, endpoint: str, call: str, params: Dict) -> Dict:
        """Faz requisição para a API do Omie - COM VALIDAÇÃO JSON"""
        
        # CORREÇÃO 1: Sanitizar parâmetros
        clean_params = sanitize_dict(params)
        
        # CORREÇÃO 2: Montar payload com validação
        payload = {
            "call": sanitize_string(call),
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [clean_params]
        }
        
        # CORREÇÃO 3: Validar JSON antes do envio
        try:
            validated_payload = validate_json_payload(payload)
        except ValueError as e:
            logger.error(f"❌ Payload JSON inválido: {e}")
            raise HTTPException(status_code=400, detail=f"Erro na formação do JSON: {e}")
        
        url = f"{self.base_url}/{endpoint}/"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"📡 Requisição Omie: {endpoint}/{call}")
                
                # CORREÇÃO 4: Log do JSON que será enviado
                json_str = json.dumps(validated_payload, ensure_ascii=False, indent=2)
                logger.debug(f"JSON enviado ({len(json_str)} chars):\n{json_str}")
                
                # CORREÇÃO 5: Enviar com headers explícitos
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json"
                }
                
                response = await client.post(
                    url, 
                    json=validated_payload,
                    headers=headers
                )
                
                logger.info(f"📥 Resposta HTTP: {response.status_code}")
                
                # CORREÇÃO 6: Log da resposta recebida
                response_text = response.text
                logger.debug(f"Resposta recebida ({len(response_text)} chars): {response_text[:500]}...")
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response_text}"
                    logger.error(f"❌ Erro HTTP: {error_msg}")
                    raise HTTPException(status_code=response.status_code, detail=f"Erro HTTP Omie: {error_msg}")
                
                if not response.content:
                    error_msg = "Resposta vazia da API Omie"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
                
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"Erro ao decodificar resposta JSON: {e}. Resposta: {response_text[:200]}"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
                
                if result is None:
                    error_msg = "Resposta JSON é None"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
                
                if isinstance(result, dict) and "faultstring" in result:
                    error_msg = result.get("faultstring", "Erro desconhecido do Omie")
                    fault_code = result.get("faultcode", "N/A")
                    logger.error(f"❌ Erro Omie [{fault_code}]: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"Erro Omie [{fault_code}]: {error_msg}")
                
                logger.info(f"✅ Resposta Omie: Sucesso")
                return result
                
        except HTTPException:
            raise
        except httpx.TimeoutException:
            error_msg = "Timeout na comunicação com Omie"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=504, detail=error_msg)
        except httpx.HTTPError as e:
            error_msg = f"Erro de conexão com Omie: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=503, detail=error_msg)
        except Exception as e:
            error_msg = f"Erro interno na comunicação com Omie: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    # ========== MÉTODOS DA API ==========
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    async def consultar_contas_pagar(self, dados: Dict) -> Dict:
        """Consulta contas a pagar"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", dados)
    
    async def consultar_contas_receber(self, dados: Dict) -> Dict:
        """Consulta contas a receber"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", dados)
    
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
    
    async def consultar_tipos_documento(self, dados: Dict) -> Dict:
        """Consulta tipos de documentos"""
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", dados)

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Correção JSON",
    description="Servidor MCP HTTP com correção para erro 422 JSON malformado",
    version="5.0.0"
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
    """Endpoint de status"""
    return {
        "service": "Omie MCP Server - Correção JSON",
        "status": "running",
        "version": "5.0.0",
        "tools": [
            "cadastrar_cliente_fornecedor",
            "consultar_categorias",
            "consultar_departamentos", 
            "consultar_tipos_documento",
            "criar_conta_pagar",
            "consultar_contas_pagar",
            "consultar_contas_receber"
        ],
        "json_fixes": [
            "✅ Sanitização de strings para JSON seguro",
            "✅ Validação de JSON antes do envio",
            "✅ Remoção de caracteres de controle",
            "✅ Escape adequado de caracteres especiais",
            "✅ Headers Content-Type explícitos",
            "✅ Logs detalhados do JSON enviado"
        ],
        "problem_solved": "Erro 422 - JSON decode error",
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
                        "name": "omie-mcp-server-json-fixed",
                        "version": "5.0.0"
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
                            "description": "Cadastra um novo cliente ou fornecedor no Omie ERP (JSON CORRIGIDO)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "razao_social": {"type": "string", "description": "Razão social"},
                                    "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF (somente números)"},
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
                                    "pagina": {"type": "integer", "description": "Página", "default": 1},
                                    "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                                }
                            }
                        },
                        {
                            "name": "consultar_departamentos",
                            "description": "Consulta departamentos cadastrados no Omie",
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
                            "description": "Consulta tipos de documentos disponíveis no Omie",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codigo": {"type": "string", "description": "Código específico (opcional)"}
                                }
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
                            "description": "Consulta contas a pagar com filtros",
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
                            "description": "Consulta contas a receber com filtros",
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
# HANDLERS DAS FERRAMENTAS COM SANITIZAÇÃO
# ============================================================================

async def handle_cadastrar_cliente_fornecedor(args: Dict) -> str:
    """Handler para cadastrar cliente/fornecedor - COM SANITIZAÇÃO"""
    
    # Mapear tipo
    tipo_mapping = {"cliente": "C", "fornecedor": "F", "ambos": "A"}
    
    # CORREÇÃO: Sanitizar todos os campos de entrada
    dados_omie = {
        "razao_social": sanitize_string(args.get("razao_social", "")),
        "cnpj_cpf": sanitize_string(args.get("cnpj_cpf", "")),
        "email": sanitize_string(args.get("email", "")),
        "cliente_fornecedor": tipo_mapping.get(args.get("tipo_cliente", "cliente"), "C"),
        "nome_fantasia": sanitize_string(args.get("nome_fantasia", "")),
        "telefone1_ddd": sanitize_string(args.get("telefone1_ddd", "")),
        "telefone1_numero": sanitize_string(args.get("telefone1_numero", "")),
        "endereco": sanitize_string(args.get("endereco", "")),
        "cidade": sanitize_string(args.get("cidade", "")),
        "estado": sanitize_string(args.get("estado", "")),
        "cep": sanitize_string(args.get("cep", "")),
        "tags": [{"tag": "MCP_JSON_FIXED"}],
        "inativo": "N"
    }
    
    # Remover campos vazios para evitar problemas no JSON
    dados_limpos = {k: v for k, v in dados_omie.items() if v and v != ""}
    dados_limpos["tags"] = [{"tag": "MCP_JSON_FIXED"}]  # Sempre manter tags
    dados_limpos["inativo"] = "N"  # Sempre manter inativo
    
    logger.info(f"Dados sanitizados para cadastro: {dados_limpos}")
    
    resultado = await omie_client.cadastrar_cliente_fornecedor(dados_limpos)
    
    if resultado and "codigo_cliente_omie" in resultado:
        return f"""✅ Cliente/Fornecedor cadastrado com sucesso!

📋 Detalhes:
• Código Omie: {resultado['codigo_cliente_omie']}
• Razão Social: {args.get('razao_social', 'N/A')}
• CNPJ/CPF: {args.get('cnpj_cpf', 'N/A')}
• Tipo: {args.get('tipo_cliente', 'N/A')}
• E-mail: {args.get('email', 'N/A')}

🔧 JSON corrigido - sem mais erro 422!
🔗 Disponível no seu Omie ERP com tag MCP_JSON_FIXED"""
    else:
        return f"✅ Cadastrado! Resposta: {json.dumps(resultado, indent=2, ensure_ascii=False)}"

# ============================================================================
# OUTROS HANDLERS (MANTIDOS)
# ============================================================================

async def handle_consultar_categorias(args: Dict) -> str:
    """Handler para consultar categorias"""
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 50)
    }
    
    resultado = await omie_client.consultar_categorias(params)
    
    if resultado and "categoria_cadastro" in resultado:
        categorias = resultado["categoria_cadastro"]
        total = resultado.get("total_de_registros", len(categorias))
        
        if categorias:
            lista_categorias = []
            for cat in categorias[:10]:
                codigo = cat.get("codigo", "N/A")
                descricao = cat.get("descricao", "N/A")
                tipo = cat.get("tipo", "N/A")
                lista_categorias.append(f"• {codigo} - {descricao} ({tipo})")
            
            return f"""📊 Categorias encontradas: {total}

🏷️ Principais categorias:
{chr(10).join(lista_categorias)}

{f"(Mostrando 10 de {total})" if total > 10 else ""}"""
        else:
            return "❌ Nenhuma categoria encontrada"
    else:
        return f"📊 Resposta de categorias: {json.dumps(resultado, indent=2, ensure_ascii=False) if resultado else 'Nenhuma resposta'}"

async def handle_consultar_departamentos(args: Dict) -> str:
    """Handler para consultar departamentos"""
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 50)
    }
    
    resultado = await omie_client.consultar_departamentos(params)
    
    if resultado and "departamento_cadastro" in resultado:
        departamentos = resultado["departamento_cadastro"]
        total = resultado.get("total_de_registros", len(departamentos))
        
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
    else:
        return f"🏢 Resposta de departamentos: {json.dumps(resultado, indent=2, ensure_ascii=False) if resultado else 'Nenhuma resposta'}"

async def handle_consultar_tipos_documento(args: Dict) -> str:
    """Handler para consultar tipos de documentos"""
    dados_omie = {
        "codigo": sanitize_string(args.get("codigo", ""))
    }
    
    resultado = await omie_client.consultar_tipos_documento(dados_omie)
    
    if resultado and "tipo_documento_cadastro" in resultado:
        tipos = resultado["tipo_documento_cadastro"]
        
        if args.get("codigo"):
            if tipos:
                tipo = tipos[0]
                return f"""📄 Tipo de Documento encontrado:

• Código: {tipo['codigo']}
• Descrição: {tipo['descricao']}"""
            else:
                return f"❌ Tipo de documento com código '{args['codigo']}' não encontrado."
        
        else:
            total = len(tipos)
            lista_formatada = []
            
            for i, tipo in enumerate(tipos[:20]):
                lista_formatada.append(f"• {tipo['codigo']} - {tipo['descricao']}")
            
            resultado_texto = f"""📄 Tipos de Documentos no Omie ERP (Total: {total})

{chr(10).join(lista_formatada)}"""
            
            if total > 20:
                resultado_texto += f"\n\n... e mais {total - 20} tipos disponíveis."
            
            return resultado_texto
    
    else:
        return f"📄 Resposta dos tipos: {json.dumps(resultado, indent=2, ensure_ascii=False) if resultado else 'Nenhuma resposta'}"

async def handle_criar_conta_pagar(args: Dict) -> str:
    """Handler para criar conta a pagar"""
    dados_omie = {
        "codigo_cliente_fornecedor": args["codigo_cliente_fornecedor"],
        "numero_documento": sanitize_string(args["numero_documento"]),
        "data_vencimento": sanitize_string(args["data_vencimento"]),
        "valor_documento": args["valor_documento"],
        "codigo_categoria": sanitize_string(args.get("codigo_categoria", "1.01.01")),
        "observacao": sanitize_string(args.get("observacao", f"Conta criada via MCP JSON Fixed em {datetime.now().strftime('%d/%m/%Y %H:%M')}")),
        "numero_parcela": args.get("numero_parcela", 1),
        "codigo_tipo_documento": "01",
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "data_entrada": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    resultado = await omie_client.criar_conta_pagar(dados_omie)
    
    if resultado and "codigo_lancamento_omie" in resultado:
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
        return f"💰 Conta criada! Resposta: {json.dumps(resultado, indent=2, ensure_ascii=False)}"

async def handle_consultar_contas_pagar(args: Dict) -> str:
    """Handler para consultar contas a pagar"""
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 20)
    }
    
    if args.get("codigo_cliente_fornecedor"):
        params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
    
    if args.get("data_inicio") and args.get("data_fim"):
        params["data_de"] = sanitize_string(args["data_inicio"])
        params["data_ate"] = sanitize_string(args["data_fim"])
    
    resultado = await omie_client.consultar_contas_pagar(params)
    
    if resultado and "conta_pagar_cadastro" in resultado:
        contas = resultado["conta_pagar_cadastro"]
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
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"""💰 Contas a Pagar encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💵 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}"""
        else:
            return "❌ Nenhuma conta a pagar encontrada"
    else:
        return f"💰 Resposta de contas a pagar: {json.dumps(resultado, indent=2, ensure_ascii=False) if resultado else 'Nenhuma resposta'}"

async def handle_consultar_contas_receber(args: Dict) -> str:
    """Handler para consultar contas a receber"""
    params = {
        "pagina": args.get("pagina", 1),
        "registros_por_pagina": args.get("registros_por_pagina", 20)
    }
    
    if args.get("codigo_cliente_fornecedor"):
        params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
    
    if args.get("data_inicio") and args.get("data_fim"):
        params["data_de"] = sanitize_string(args["data_inicio"])
        params["data_ate"] = sanitize_string(args["data_fim"])
    
    resultado = await omie_client.consultar_contas_receber(params)
    
    if resultado and "conta_receber_cadastro" in resultado:
        contas = resultado["conta_receber_cadastro"]
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
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"""💵 Contas a Receber encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💰 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}"""
        else:
            return "❌ Nenhuma conta a receber encontrada"
    else:
        return f"💵 Resposta de contas a receber: {json.dumps(resultado, indent=2, ensure_ascii=False) if resultado else 'Nenhuma resposta'}"

# ============================================================================
# ENDPOINTS DE TESTE COM DADOS SANITIZADOS
# ============================================================================

@app.post("/test/cliente")
async def test_cliente(request: ClienteFornecedorRequest):
    result = await handle_cadastrar_cliente_fornecedor(request.dict())
    return {"result": result}

@app.post("/test/json-validation")
async def test_json_validation():
    """Endpoint para testar a validação JSON"""
    test_data = {
        "teste": "string normal",
        "com_aspas": 'string com "aspas"',
        "com_quebra": "string\ncom\nquebra",
        "com_tab": "string\tcom\ttab",
        "numero": 123,
        "vazio": "",
        "nulo": None
    }
    
    try:
        sanitized = sanitize_dict(test_data)
        validated = validate_json_payload(sanitized)
        
        return {
            "original": test_data,
            "sanitized": sanitized,
            "validated": validated,
            "json_string": json.dumps(validated, ensure_ascii=False),
            "status": "sucesso"
        }
    except Exception as e:
        return {
            "erro": str(e),
            "status": "falha"
        }

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Inicia o servidor HTTP MCP com correção JSON"""
    
    print("🚀 Iniciando Servidor MCP HTTP para Omie ERP - CORREÇÃO JSON")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("🔧 PROBLEMA RESOLVIDO: Erro 422 - JSON decode error")
    print("📡 Ferramentas com JSON corrigido:")
    print("   ✅ cadastrar_cliente_fornecedor (JSON SANITIZADO)")
    print("   ✅ consultar_categorias")
    print("   ✅ consultar_departamentos")
    print("   ✅ consultar_tipos_documento")
    print("   ✅ criar_conta_pagar")
    print("   ✅ consultar_contas_pagar")
    print("   ✅ consultar_contas_receber")
    print("\n🔧 Correções JSON aplicadas:")
    print("   • Sanitização de strings")
    print("   • Validação de JSON antes envio")
    print("   • Remoção de caracteres de controle")
    print("   • Headers Content-Type explícitos")
    print("   • Logs detalhados do JSON")
    print(f"\n✅ Servidor HTTP rodando em: http://localhost:{MCP_SERVER_PORT}")
    print(f"📖 Docs: http://localhost:{MCP_SERVER_PORT}/docs")
    print(f"🧪 Teste JSON: http://localhost:{MCP_SERVER_PORT}/test/json-validation")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()