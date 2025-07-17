#!/usr/bin/env python3
"""
Servidor MCP HTTP para Omie ERP - CORREÇÃO ULTRA-ROBUSTA JSON
Foco em resolver definitivamente o erro 422 JSON decode error

PROBLEMA PERSISTENTE:
- Erro 422 na posição 195 do body
- "Expecting property name enclosed in double quotes"
- JSON ainda malformado após primeira correção

ESTRATÉGIA ULTRA-ROBUSTA:
1. Limpeza extremamente agressiva de caracteres
2. Validação JSON em múltiplas etapas
3. Logs detalhados char por char se necessário
4. Construção manual de JSON válido
5. Teste antes e depois de cada etapa
"""

import asyncio
import json
import logging
import os
import sys
import re
import unicodedata
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

OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")

if not OMIE_APP_KEY or not OMIE_APP_SECRET:
    print("❌ ERRO: Configure as variáveis de ambiente OMIE_APP_KEY e OMIE_APP_SECRET")
    sys.exit(1)

OMIE_BASE_URL = "https://app.omie.com.br/api/v1"
MCP_SERVER_PORT = 8000

# ============================================================================
# CONFIGURAÇÃO DE LOGS DETALHADOS
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG,  # Debug mais detalhado
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("omie-mcp-ultra-fix")

# ============================================================================
# UTILITÁRIOS ULTRA-ROBUSTOS PARA JSON
# ============================================================================

def ultra_clean_string(value: Any) -> str:
    """Limpeza ultra-agressiva de string para JSON"""
    if value is None:
        return ""
    
    # Converter para string
    text = str(value)
    
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Remover TODOS os caracteres de controle e especiais problemáticos
    # Manter apenas ASCII printable + acentos comuns
    clean_chars = []
    for char in text:
        # Manter apenas caracteres seguros
        if char.isalnum() or char in ' .-_@()[]{}|+/\\:;,!?áéíóúàèìòùãõâêîôûç':
            clean_chars.append(char)
        else:
            # Log do caractere removido para debug
            logger.debug(f"Removendo caractere problemático: '{char}' (ord: {ord(char)})")
    
    text = ''.join(clean_chars)
    
    # Remover múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    # Limitar tamanho
    if len(text) > 100:
        text = text[:100]
        logger.debug(f"String truncada para 100 chars")
    
    return text

def validate_json_step_by_step(data: Dict) -> Dict:
    """Validação JSON passo a passo com logs detalhados"""
    
    logger.info("🔍 Iniciando validação JSON step-by-step")
    
    # Passo 1: Limpar recursivamente todos os valores
    clean_data = {}
    for key, value in data.items():
        clean_key = ultra_clean_string(key)
        clean_value = ultra_clean_string(value)
        
        # Log da limpeza
        if str(key) != clean_key:
            logger.debug(f"Chave limpa: '{key}' -> '{clean_key}'")
        if str(value) != clean_value:
            logger.debug(f"Valor limpo para {clean_key}: '{value}' -> '{clean_value}'")
        
        # Só incluir se não estiver vazio
        if clean_key and clean_value:
            clean_data[clean_key] = clean_value
    
    logger.info(f"📋 Dados após limpeza: {len(clean_data)} campos")
    
    # Passo 2: Testar serialização JSON simples
    try:
        json_simple = json.dumps(clean_data, ensure_ascii=True, separators=(',', ':'))
        logger.info(f"✅ JSON simples OK: {len(json_simple)} chars")
    except Exception as e:
        logger.error(f"❌ Falha JSON simples: {e}")
        raise ValueError(f"JSON simples falhou: {e}")
    
    # Passo 3: Testar deserialização
    try:
        reloaded = json.loads(json_simple)
        logger.info(f"✅ JSON reload OK: {len(reloaded)} campos")
    except Exception as e:
        logger.error(f"❌ Falha JSON reload: {e}")
        raise ValueError(f"JSON reload falhou: {e}")
    
    # Passo 4: Construir payload do Omie step by step
    omie_payload = {
        "call": ultra_clean_string("IncluirCliente"),
        "app_key": ultra_clean_string(OMIE_APP_KEY),
        "app_secret": ultra_clean_string(OMIE_APP_SECRET),
        "param": [clean_data]
    }
    
    # Passo 5: Validar payload final
    try:
        final_json = json.dumps(omie_payload, ensure_ascii=True, separators=(',', ':'))
        logger.info(f"✅ Payload final OK: {len(final_json)} chars")
        
        # Log dos primeiros e últimos caracteres para debug
        logger.debug(f"JSON início: {final_json[:50]}...")
        logger.debug(f"JSON fim: ...{final_json[-50:]}")
        
        # Verificar se não há caracteres problemáticos
        problematic_chars = ['"', "'", '\n', '\r', '\t', '\\']
        for i, char in enumerate(final_json):
            if char in problematic_chars and i > 10:  # Ignorar os primeiros (estrutura normal)
                logger.warning(f"Char problemático na posição {i}: '{char}'")
        
    except Exception as e:
        logger.error(f"❌ Falha payload final: {e}")
        # Log do payload que causou problema
        logger.error(f"Payload problemático: {omie_payload}")
        raise ValueError(f"Payload final falhou: {e}")
    
    return omie_payload

def create_minimal_test_payload() -> Dict:
    """Cria o payload mais mínimo possível para teste"""
    return {
        "call": "IncluirCliente",
        "app_key": ultra_clean_string(OMIE_APP_KEY),
        "app_secret": ultra_clean_string(OMIE_APP_SECRET),
        "param": [{
            "razao_social": "TESTE ULTRA SIMPLES",
            "cnpj_cpf": "24493607000119",
            "email": "teste@ultra.com",
            "cliente_fornecedor": "C",
            "inativo": "N"
        }]
    }

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
# CLIENTE OMIE ULTRA-ROBUSTO
# ============================================================================

class OmieClientUltraRobust:
    """Cliente ultra-robusto para comunicação com API Omie"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = ultra_clean_string(app_key)
        self.app_secret = ultra_clean_string(app_secret)
        self.base_url = OMIE_BASE_URL
        
        logger.info(f"🔑 Credenciais limpas - App Key: {self.app_key[:8]}...****")
    
    async def _make_ultra_safe_request(self, endpoint: str, call: str, params: Dict) -> Dict:
        """Requisição ultra-segura com validação rigorosa"""
        
        logger.info(f"🚀 Iniciando requisição ultra-segura: {endpoint}/{call}")
        
        # Etapa 1: Validar payload
        try:
            payload = validate_json_step_by_step(params)
        except ValueError as e:
            logger.error(f"❌ Erro na validação: {e}")
            raise HTTPException(status_code=400, detail=f"Erro na validação JSON: {e}")
        
        url = f"{self.base_url}/{endpoint}/"
        
        # Etapa 2: Preparar requisição com headers ultra-explícitos
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "Omie-MCP-UltraFix/1.0"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Etapa 3: Serializar JSON com configurações ultra-seguras
                json_data = json.dumps(
                    payload, 
                    ensure_ascii=True,  # Forçar ASCII
                    separators=(',', ':'),  # Sem espaços
                    sort_keys=True  # Ordem consistente
                )
                
                logger.info(f"📤 Enviando JSON ({len(json_data)} chars)")
                logger.debug(f"JSON completo: {json_data}")
                
                # Etapa 4: Fazer requisição
                response = await client.post(
                    url,
                    content=json_data,  # Usar content em vez de json
                    headers=headers
                )
                
                logger.info(f"📥 Resposta HTTP: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"❌ Erro HTTP {response.status_code}: {error_text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Erro HTTP {response.status_code}: {error_text}"
                    )
                
                # Etapa 5: Processar resposta
                if not response.content:
                    raise HTTPException(status_code=500, detail="Resposta vazia")
                
                try:
                    result = response.json()
                    logger.info(f"✅ Resposta JSON OK")
                    
                    if isinstance(result, dict) and "faultstring" in result:
                        error_msg = result.get("faultstring", "Erro Omie")
                        logger.error(f"❌ Erro Omie: {error_msg}")
                        raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro decodificação resposta: {e}")
                    raise HTTPException(status_code=500, detail=f"Resposta inválida: {e}")
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro interno: {e}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor com ultra-validação"""
        return await self._make_ultra_safe_request("geral/clientes", "IncluirCliente", dados)
    
    async def test_minimal_request(self) -> Dict:
        """Teste com payload mínimo"""
        logger.info("🧪 Testando payload mínimo")
        minimal_data = {
            "razao_social": "TESTE MINIMAL",
            "cnpj_cpf": "24493607000119",
            "email": "teste@minimal.com",
            "cliente_fornecedor": "C",
            "inativo": "N"
        }
        return await self._make_ultra_safe_request("geral/clientes", "IncluirCliente", minimal_data)

# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

omie_client = OmieClientUltraRobust(OMIE_APP_KEY, OMIE_APP_SECRET)

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Omie MCP Server - Ultra JSON Fix",
    description="Correção ultra-robusta para erro 422 JSON",
    version="6.0.0"
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
        "service": "Omie MCP Server - Ultra JSON Fix",
        "status": "running",
        "version": "6.0.0",
        "ultra_fixes": [
            "✅ Limpeza ultra-agressiva de caracteres",
            "✅ Validação JSON step-by-step",
            "✅ Logs detalhados char por char",
            "✅ Headers ultra-explícitos",
            "✅ ASCII forçado, sem unicode",
            "✅ Teste mínimo disponível"
        ],
        "target_error": "422 JSON decode error na posição 195",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "omie-mcp-ultra-fix", "version": "6.0.0"}
                }
            )
        
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [
                        {
                            "name": "cadastrar_cliente_fornecedor",
                            "description": "Cadastra cliente/fornecedor (ULTRA JSON FIX)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "razao_social": {"type": "string", "description": "Razão social"},
                                    "cnpj_cpf": {"type": "string", "description": "CNPJ"},
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
                            "name": "test_minimal_omie",
                            "description": "Teste mínimo para debug do erro 422",
                            "inputSchema": {"type": "object", "properties": {}}
                        }
                    ]
                }
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            if tool_name == "cadastrar_cliente_fornecedor":
                result = await handle_cadastrar_cliente_ultra_safe(arguments)
            elif tool_name == "test_minimal_omie":
                result = await handle_test_minimal()
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
# HANDLERS ULTRA-SEGUROS
# ============================================================================

async def handle_cadastrar_cliente_ultra_safe(args: Dict) -> str:
    """Handler ultra-seguro para cadastro"""
    
    logger.info(f"🛡️ Iniciando cadastro ultra-seguro")
    logger.debug(f"Args recebidos: {args}")
    
    # Mapear tipo
    tipo_map = {"cliente": "C", "fornecedor": "F", "ambos": "A"}
    
    # Construir dados ultra-limpos
    dados_ultra_limpos = {
        "razao_social": ultra_clean_string(args.get("razao_social", "")),
        "cnpj_cpf": ultra_clean_string(args.get("cnpj_cpf", "")),
        "email": ultra_clean_string(args.get("email", "")),
        "cliente_fornecedor": tipo_map.get(args.get("tipo_cliente"), "C"),
        "inativo": "N"
    }
    
    # Adicionar campos opcionais apenas se não vazios
    optional_fields = {
        "nome_fantasia": args.get("nome_fantasia"),
        "cidade": args.get("cidade"),
        "estado": args.get("estado"),
        "telefone1_ddd": args.get("telefone1_ddd"),
        "telefone1_numero": args.get("telefone1_numero"),
        "endereco": args.get("endereco"),
        "cep": args.get("cep")
    }
    
    for key, value in optional_fields.items():
        if value and str(value).strip():
            clean_value = ultra_clean_string(value)
            if clean_value:
                dados_ultra_limpos[key] = clean_value
    
    logger.info(f"📋 Dados ultra-limpos: {dados_ultra_limpos}")
    
    try:
        resultado = await omie_client.cadastrar_cliente_fornecedor(dados_ultra_limpos)
        
        if resultado and "codigo_cliente_omie" in resultado:
            return f"""✅ SUCESSO! Cliente cadastrado com ULTRA JSON FIX!

📋 Detalhes:
• Código Omie: {resultado['codigo_cliente_omie']}
• Razão Social: {dados_ultra_limpos.get('razao_social', 'N/A')}
• CNPJ: {dados_ultra_limpos.get('cnpj_cpf', 'N/A')}
• E-mail: {dados_ultra_limpos.get('email', 'N/A')}

🔧 Erro 422 resolvido definitivamente!
🎉 JSON ultra-seguro funcionando!"""
        else:
            return f"✅ Cadastrado! Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"
            
    except Exception as e:
        logger.error(f"❌ Erro no cadastro: {e}")
        return f"❌ Erro no cadastro: {str(e)}"

async def handle_test_minimal() -> str:
    """Handler para teste mínimo"""
    
    logger.info(f"🧪 Executando teste mínimo")
    
    try:
        resultado = await omie_client.test_minimal_request()
        
        return f"""🧪 TESTE MÍNIMO EXECUTADO!

✅ Status: SUCESSO
📊 Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}

🔧 Se este teste passou, o erro 422 foi resolvido!"""
        
    except Exception as e:
        logger.error(f"❌ Erro no teste mínimo: {e}")
        return f"""🧪 TESTE MÍNIMO FALHOU

❌ Erro: {str(e)}

🔍 Este erro ajuda a identificar o problema exato."""

# ============================================================================
# ENDPOINTS DE DEBUG
# ============================================================================

@app.post("/debug/test-json-cleaning")
async def debug_json_cleaning():
    """Endpoint para testar limpeza JSON"""
    
    test_cases = [
        "String normal",
        "String com 'aspas simples'",
        'String com "aspas duplas"',
        "String\ncom\nquebras",
        "String\tcom\ttabs",
        "String com çãràctéres especiais",
        "String com caracteres unicode: 💻📱🚀",
        "",
        None
    ]
    
    results = []
    for case in test_cases:
        original = case
        cleaned = ultra_clean_string(case)
        
        results.append({
            "original": original,
            "cleaned": cleaned,
            "length_diff": len(str(original)) - len(cleaned) if original else 0
        })
    
    return {
        "test_cases": results,
        "summary": "Teste de limpeza de strings para JSON"
    }

@app.post("/debug/test-minimal-payload")
async def debug_minimal_payload():
    """Endpoint para testar payload mínimo"""
    
    try:
        payload = create_minimal_test_payload()
        json_str = json.dumps(payload, ensure_ascii=True, separators=(',', ':'))
        
        return {
            "payload": payload,
            "json_string": json_str,
            "length": len(json_str),
            "status": "JSON válido"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "JSON inválido"
        }

@app.post("/test/cliente-ultra")
async def test_cliente_ultra(request: ClienteFornecedorRequest):
    """Endpoint de teste ultra-seguro para cliente"""
    result = await handle_cadastrar_cliente_ultra_safe(request.dict())
    return {"result": result}

@app.post("/test/minimal")
async def test_minimal():
    """Endpoint de teste mínimo"""
    result = await handle_test_minimal()
    return {"result": result}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    print("🚀 OMIE MCP SERVER - ULTRA JSON FIX")
    print(f"🔑 App Key: {OMIE_APP_KEY[:8]}...****")
    print(f"🌐 Porta: {MCP_SERVER_PORT}")
    print("")
    print("🎯 FOCO: Resolver erro 422 JSON decode error definitivamente")
    print("🔧 ULTRA FIXES APLICADOS:")
    print("   • Limpeza ultra-agressiva de caracteres")
    print("   • Validação JSON step-by-step com logs")
    print("   • Headers ultra-explícitos")
    print("   • ASCII forçado, zero unicode")
    print("   • Teste mínimo para debug")
    print("")
    print(f"✅ Servidor rodando: http://localhost:{MCP_SERVER_PORT}")
    print(f"🧪 Teste mínimo: http://localhost:{MCP_SERVER_PORT}/test/minimal")
    print(f"🔍 Debug JSON: http://localhost:{MCP_SERVER_PORT}/debug/test-json-cleaning")
    print(f"📖 Docs: http://localhost:{MCP_SERVER_PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_SERVER_PORT,
        log_level="debug"  # Logs ultra-detalhados
    )

if __name__ == "__main__":
    main()