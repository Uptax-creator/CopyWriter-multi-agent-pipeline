#!/usr/bin/env python3
"""
Servidor MCP para Omie ERP - Compatível com MCP 1.10.1
Ferramentas: Cadastrar Cliente/Fornecedor e Criar Contas a Pagar

Versão otimizada para MCP SDK 1.10.1
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel, Field, ValidationError, field_validator
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Credenciais do Omie via variáveis de ambiente
OMIE_APP_KEY = os.getenv("OMIE_APP_KEY")
OMIE_APP_SECRET = os.getenv("OMIE_APP_SECRET")
OMIE_BASE_URL = "https://app.omie.com.br/api/v1"

# Configurações do servidor
SERVER_NAME = "omie-mcp-server"
SERVER_VERSION = "1.0.0"
REQUEST_TIMEOUT = 30.0

# ============================================================================
# VALIDAÇÃO DE CONFIGURAÇÕES
# ============================================================================

def validate_environment():
    """Valida se todas as variáveis de ambiente necessárias estão configuradas"""
    if not OMIE_APP_KEY or not OMIE_APP_SECRET:
        print("❌ ERRO: Credenciais do Omie não encontradas!", file=sys.stderr)
        print("📝 Configure as variáveis de ambiente:", file=sys.stderr)
        print("   export OMIE_APP_KEY='sua_app_key'", file=sys.stderr)
        print("   export OMIE_APP_SECRET='seu_app_secret'", file=sys.stderr)
        print("🔗 Obtenha suas credenciais em: https://app.omie.com.br/", file=sys.stderr)
        sys.exit(1)

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    return logging.getLogger(SERVER_NAME)

# ============================================================================
# MODELOS PYDANTIC v2 (MCP 1.10.1)
# ============================================================================

class ClienteFornecedorInput(BaseModel):
    """Modelo para validação de dados de cliente/fornecedor"""
    razao_social: str = Field(..., min_length=1, max_length=100, description="Razão social")
    nome_fantasia: Optional[str] = Field(None, max_length=100, description="Nome fantasia")
    cnpj_cpf: str = Field(..., min_length=11, max_length=14, description="CNPJ ou CPF")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="E-mail válido")
    telefone1_ddd: Optional[str] = Field(None, min_length=2, max_length=2, description="DDD")
    telefone1_numero: Optional[str] = Field(None, min_length=8, max_length=9, description="Telefone")
    endereco: Optional[str] = Field(None, max_length=200, description="Endereço")
    cidade: Optional[str] = Field(None, max_length=50, description="Cidade")
    estado: Optional[str] = Field(None, min_length=2, max_length=2, description="Estado")
    cep: Optional[str] = Field(None, min_length=8, max_length=8, description="CEP")
    tipo_cliente: str = Field(..., pattern=r'^(cliente|fornecedor|ambos)$', description="Tipo")

    @field_validator('cnpj_cpf')
    @classmethod
    def validate_cnpj_cpf(cls, v):
        """Valida se CNPJ/CPF contém apenas números"""
        if not v.isdigit():
            raise ValueError('CNPJ/CPF deve conter apenas números')
        return v

    @field_validator('cep')
    @classmethod
    def validate_cep(cls, v):
        """Valida se CEP contém apenas números"""
        if v and not v.isdigit():
            raise ValueError('CEP deve conter apenas números')
        return v

class ContaPagarInput(BaseModel):
    """Modelo para validação de dados de conta a pagar"""
    codigo_cliente_fornecedor: int = Field(..., gt=0, description="Código do fornecedor")
    numero_documento: str = Field(..., min_length=1, max_length=50, description="Número do documento")
    data_vencimento: str = Field(..., pattern=r'^\d{2}/\d{2}/\d{4}$', description="Data DD/MM/AAAA")
    valor_documento: float = Field(..., gt=0, description="Valor do documento")
    codigo_categoria: Optional[str] = Field("1.01.01", description="Código da categoria")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações")
    numero_parcela: Optional[int] = Field(1, ge=1, description="Número da parcela")
    codigo_tipo_documento: Optional[str] = Field("01", description="Tipo do documento")

    @field_validator('data_vencimento')
    @classmethod
    def validate_data_vencimento(cls, v):
        """Valida se a data está no formato correto e é válida"""
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError('Data deve estar no formato DD/MM/AAAA e ser válida')
        return v

# ============================================================================
# CLIENTE OMIE
# ============================================================================

class OmieClient:
    """Cliente para comunicação com a API do Omie"""
    
    def __init__(self, app_key: str, app_secret: str, logger: logging.Logger):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = OMIE_BASE_URL
        self.logger = logger
        
    async def _make_request(self, endpoint: str, call: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma requisição para a API do Omie"""
        
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        url = f"{self.base_url}/{endpoint}/"
        
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                self.logger.info(f"Enviando requisição para: {url}")
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Verificar se houve erro na resposta do Omie
                if isinstance(result, dict) and "faultstring" in result:
                    error_msg = result.get("faultstring", "Erro desconhecido do Omie")
                    self.logger.error(f"Erro retornado pelo Omie: {error_msg}")
                    raise Exception(f"Erro Omie: {error_msg}")
                
                self.logger.info("Requisição executada com sucesso")
                return result
                
        except httpx.TimeoutException:
            error_msg = "Timeout na comunicação com Omie"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Erro HTTP {e.response.status_code}: {e.response.text}"
            self.logger.error(error_msg)
            raise Exception(f"Erro na comunicação com Omie: {error_msg}")
            
        except Exception as e:
            error_msg = f"Erro inesperado na comunicação com Omie: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    async def cadastrar_cliente_fornecedor(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra um cliente ou fornecedor no Omie"""
        return await self._make_request(
            endpoint="geral/clientes",
            call="IncluirCliente",
            params=dados
        )
    
    async def criar_conta_pagar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma conta a pagar no Omie"""
        return await self._make_request(
            endpoint="financas/contapagar",
            call="IncluirContaPagar",
            params=dados
        )

# ============================================================================
# SERVIDOR MCP
# ============================================================================

def create_server(omie_client: OmieClient, logger: logging.Logger) -> Server:
    """Cria e configura o servidor MCP"""
    
    server = Server(SERVER_NAME)

    @server.list_tools()
    async def list_tools() -> ListToolsResult:
        """Lista as ferramentas disponíveis no servidor MCP"""
        
        tools = [
            Tool(
                name="cadastrar_cliente_fornecedor",
                description="Cadastra um novo cliente ou fornecedor no Omie ERP com validação completa",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "razao_social": {
                            "type": "string",
                            "description": "Nome/Razão social do cliente ou fornecedor",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "nome_fantasia": {
                            "type": "string",
                            "description": "Nome fantasia (opcional)",
                            "maxLength": 100
                        },
                        "cnpj_cpf": {
                            "type": "string",
                            "description": "CNPJ ou CPF (somente números, 11 ou 14 dígitos)",
                            "pattern": "^[0-9]{11,14}$"
                        },
                        "email": {
                            "type": "string",
                            "description": "E-mail de contato válido",
                            "format": "email"
                        },
                        "telefone1_ddd": {
                            "type": "string",
                            "description": "DDD do telefone principal (2 dígitos)",
                            "pattern": "^[0-9]{2}$"
                        },
                        "telefone1_numero": {
                            "type": "string",
                            "description": "Número do telefone principal (8 ou 9 dígitos)",
                            "pattern": "^[0-9]{8,9}$"
                        },
                        "endereco": {
                            "type": "string",
                            "description": "Endereço completo",
                            "maxLength": 200
                        },
                        "cidade": {
                            "type": "string",
                            "description": "Nome da cidade",
                            "maxLength": 50
                        },
                        "estado": {
                            "type": "string",
                            "description": "Sigla do estado (ex: SP, RJ)",
                            "pattern": "^[A-Z]{2}$"
                        },
                        "cep": {
                            "type": "string",
                            "description": "CEP (8 dígitos, somente números)",
                            "pattern": "^[0-9]{8}$"
                        },
                        "tipo_cliente": {
                            "type": "string",
                            "enum": ["cliente", "fornecedor", "ambos"],
                            "description": "Tipo: cliente, fornecedor ou ambos"
                        }
                    },
                    "required": ["razao_social", "cnpj_cpf", "email", "tipo_cliente"],
                    "additionalProperties": False
                }
            ),
            
            Tool(
                name="criar_conta_pagar",
                description="Cria uma nova conta a pagar no Omie ERP com validação de dados",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {
                            "type": "integer",
                            "description": "Código do fornecedor no Omie (obrigatório)",
                            "minimum": 1
                        },
                        "numero_documento": {
                            "type": "string",
                            "description": "Número do documento/nota fiscal",
                            "minLength": 1,
                            "maxLength": 50
                        },
                        "data_vencimento": {
                            "type": "string",
                            "description": "Data de vencimento (formato: DD/MM/AAAA)",
                            "pattern": "^[0-9]{2}/[0-9]{2}/[0-9]{4}$"
                        },
                        "valor_documento": {
                            "type": "number",
                            "description": "Valor do documento",
                            "minimum": 0.01
                        },
                        "codigo_categoria": {
                            "type": "string",
                            "description": "Código da categoria de despesa (ex: 1.01.01)",
                            "default": "1.01.01"
                        },
                        "observacao": {
                            "type": "string",
                            "description": "Observações sobre a conta a pagar",
                            "maxLength": 500
                        },
                        "numero_parcela": {
                            "type": "integer",
                            "description": "Número da parcela (padrão: 1)",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": [
                        "codigo_cliente_fornecedor", 
                        "numero_documento", 
                        "data_vencimento", 
                        "valor_documento"
                    ],
                    "additionalProperties": False
                }
            )
        ]
        
        return ListToolsResult(tools=tools)

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Executa as ferramentas do servidor MCP"""
        
        try:
            if name == "cadastrar_cliente_fornecedor":
                return await handle_cadastrar_cliente_fornecedor(arguments, omie_client, logger)
            elif name == "criar_conta_pagar":
                return await handle_criar_conta_pagar(arguments, omie_client, logger)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Ferramenta não encontrada: {name}")],
                    isError=True
                )
                
        except Exception as e:
            error_msg = f"❌ Erro ao executar {name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )

    return server

# ============================================================================
# HANDLERS DAS FERRAMENTAS
# ============================================================================

async def handle_cadastrar_cliente_fornecedor(
    arguments: Dict[str, Any], 
    omie_client: OmieClient, 
    logger: logging.Logger
) -> CallToolResult:
    """Handler para cadastro de cliente/fornecedor com validação Pydantic"""
    
    try:
        # Validar dados usando Pydantic
        dados_validados = ClienteFornecedorInput(**arguments)
        
        # Mapear tipo de cliente
        tipo_mapping = {
            "cliente": "C",
            "fornecedor": "F", 
            "ambos": "A"
        }
        
        # Preparar dados para o Omie
        dados_omie = {
            "razao_social": dados_validados.razao_social,
            "cnpj_cpf": dados_validados.cnpj_cpf,
            "email": dados_validados.email,
            "cliente_fornecedor": tipo_mapping[dados_validados.tipo_cliente],
            
            # Campos opcionais
            "nome_fantasia": dados_validados.nome_fantasia or "",
            "telefone1_ddd": dados_validados.telefone1_ddd or "",
            "telefone1_numero": dados_validados.telefone1_numero or "",
            "endereco": dados_validados.endereco or "",
            "cidade": dados_validados.cidade or "",
            "estado": dados_validados.estado or "",
            "cep": dados_validados.cep or "",
            
            # Campos padrão
            "tags": [{"tag": "MCP_CRIADO"}],
            "inativo": "N"
        }
        
        logger.info(f"Iniciando cadastro de {dados_validados.tipo_cliente}: {dados_validados.razao_social}")
        
        # Executar o cadastro
        resultado = await omie_client.cadastrar_cliente_fornecedor(dados_omie)
        
        # Preparar resposta
        if "codigo_cliente_omie" in resultado:
            sucesso_msg = f"""✅ **Cliente/Fornecedor cadastrado com sucesso!**

📋 **Detalhes do Cadastro:**
• **Código Omie:** {resultado['codigo_cliente_omie']}
• **Razão Social:** {dados_validados.razao_social}
• **CNPJ/CPF:** {dados_validados.cnpj_cpf}
• **Tipo:** {dados_validados.tipo_cliente.capitalize()}
• **E-mail:** {dados_validados.email}

🔗 O cadastro está disponível no seu Omie ERP e pode ser usado para criar contas a pagar."""
            
            logger.info(f"Cliente/Fornecedor cadastrado com sucesso. Código: {resultado['codigo_cliente_omie']}")
        else:
            sucesso_msg = f"✅ Cliente/Fornecedor cadastrado com sucesso!\n\nResposta: {json.dumps(resultado, indent=2)}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=sucesso_msg)]
        )
        
    except ValidationError as e:
        error_msg = f"❌ Dados inválidos: {'; '.join([f'{err[\"loc\"][0]}: {err[\"msg\"]}' for err in e.errors()])}"
        logger.error(f"Erro de validação: {error_msg}")
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )
        
    except Exception as e:
        error_msg = f"❌ Erro ao cadastrar cliente/fornecedor: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def handle_criar_conta_pagar(
    arguments: Dict[str, Any], 
    omie_client: OmieClient, 
    logger: logging.Logger
) -> CallToolResult:
    """Handler para criação de conta a pagar com validação Pydantic"""
    
    try:
        # Validar dados usando Pydantic
        dados_validados = ContaPagarInput(**arguments)
        
        # Preparar dados para o Omie
        dados_omie = {
            "codigo_cliente_fornecedor": dados_validados.codigo_cliente_fornecedor,
            "numero_documento": dados_validados.numero_documento,
            "data_vencimento": dados_validados.data_vencimento,
            "valor_documento": dados_validados.valor_documento,
            
            # Campos opcionais
            "codigo_categoria": dados_validados.codigo_categoria,
            "observacao": dados_validados.observacao or f"Conta criada via MCP em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "numero_parcela": dados_validados.numero_parcela,
            "codigo_tipo_documento": dados_validados.codigo_tipo_documento,
            
            # Campos padrão
            "data_emissao": datetime.now().strftime("%d/%m/%Y"),
            "data_entrada": datetime.now().strftime("%d/%m/%Y"),
            "status_titulo": "ABERTO"
        }
        
        logger.info(f"Iniciando criação de conta a pagar - Documento: {dados_validados.numero_documento}")
        
        # Executar a criação
        resultado = await omie_client.criar_conta_pagar(dados_omie)
        
        # Preparar resposta
        if "codigo_lancamento_omie" in resultado:
            sucesso_msg = f"""💰 **Conta a Pagar criada com sucesso!**

📋 **Detalhes da Conta:**
• **Código Lançamento:** {resultado['codigo_lancamento_omie']}
• **Código Fornecedor:** {dados_validados.codigo_cliente_fornecedor}
• **Documento:** {dados_validados.numero_documento}
• **Valor:** R$ {dados_validados.valor_documento:,.2f}
• **Vencimento:** {dados_validados.data_vencimento}
• **Parcela:** {dados_validados.numero_parcela}
• **Status:** ABERTO

🔗 A conta está disponível no módulo Financeiro do seu Omie ERP."""
            
            logger.info(f"Conta a pagar criada com sucesso. Código: {resultado['codigo_lancamento_omie']}")
        else:
            sucesso_msg = f"💰 Conta a Pagar criada com sucesso!\n\nResposta: {json.dumps(resultado, indent=2)}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=sucesso_msg)]
        )
        
    except ValidationError as e:
        error_msg = f"❌ Dados inválidos: {'; '.join([f'{err[\"loc\"][0]}: {err[\"msg\"]}' for err in e.errors()])}"
        logger.error(f"Erro de validação: {error_msg}")
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )
        
    except Exception as e:
        error_msg = f"❌ Erro ao criar conta a pagar: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

async def main():
    """Função principal que inicia o servidor MCP"""
    
    # Validar ambiente
    validate_environment()
    
    # Configurar logging
    logger = setup_logging()
    
    logger.info(f"🚀 Iniciando {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"🔑 App Key configurada: {OMIE_APP_KEY[:8]}...****")
    logger.info("📡 Ferramentas disponíveis:")
    logger.info("   • cadastrar_cliente_fornecedor")
    logger.info("   • criar_conta_pagar")
    
    # Criar cliente Omie
    omie_client = OmieClient(OMIE_APP_KEY, OMIE_APP_SECRET, logger)
    
    # Criar servidor MCP
    server = create_server(omie_client, logger)
    
    logger.info("✅ Servidor configurado! Aguardando conexões MCP...")
    
    # Iniciar o servidor usando stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor interrompido pelo usuário", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}", file=sys.stderr)
        sys.exit(1)