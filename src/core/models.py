#!/usr/bin/env python3
"""
Modelos Pydantic para o projeto Omie MCP
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """Modelo base para requisições MCP"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Dict[str, Any] = {}


class MCPResponse(BaseModel):
    """Modelo base para respostas MCP"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ClienteFornecedorInput(BaseModel):
    """Modelo para entrada de dados de cliente/fornecedor"""
    razao_social: str = Field(..., description="Razão social do cliente/fornecedor")
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF")
    email: str = Field(..., description="Email do cliente/fornecedor")
    tipo_cliente: str = Field(..., description="Tipo do cliente (ex: 'S' para Sim)")
    nome_fantasia: Optional[str] = Field("", description="Nome fantasia")
    telefone1_ddd: Optional[str] = Field("", description="DDD do telefone")
    telefone1_numero: Optional[str] = Field("", description="Número do telefone")
    endereco: Optional[str] = Field("", description="Endereço")
    cidade: Optional[str] = Field("", description="Cidade")
    estado: Optional[str] = Field("", description="Estado")
    cep: Optional[str] = Field("", description="CEP")


class ContaPagarInput(BaseModel):
    """Modelo para entrada de dados de conta a pagar"""
    codigo_cliente_fornecedor: int = Field(..., description="Código do cliente/fornecedor")
    data_vencimento: str = Field(..., description="Data de vencimento (DD/MM/YYYY)")
    valor_documento: float = Field(..., description="Valor do documento")
    numero_documento: str = Field(..., description="Número do documento")
    codigo_categoria: Optional[str] = Field("", description="Código da categoria")
    observacao: Optional[str] = Field("", description="Observação")


class ContaReceberInput(BaseModel):
    """Modelo para entrada de dados de conta a receber"""
    codigo_cliente: int = Field(..., description="Código do cliente")
    data_vencimento: str = Field(..., description="Data de vencimento (DD/MM/YYYY)")
    valor_documento: float = Field(..., description="Valor do documento")
    numero_documento: str = Field(..., description="Número do documento")
    codigo_categoria: Optional[str] = Field("", description="Código da categoria")
    observacao: Optional[str] = Field("", description="Observação")


class ConsultaContasRequest(BaseModel):
    """Modelo para consulta de contas"""
    data_inicial: Optional[str] = Field(None, description="Data inicial (DD/MM/YYYY)")
    data_final: Optional[str] = Field(None, description="Data final (DD/MM/YYYY)")
    codigo_cliente_fornecedor: Optional[int] = Field(None, description="Código do cliente/fornecedor")
    apenas_importado_api: Optional[str] = Field("N", description="Apenas importado via API")
    pagina: Optional[int] = Field(1, description="Página da consulta")
    registros_por_pagina: Optional[int] = Field(50, description="Registros por página")


class TipoDocumentoRequest(BaseModel):
    """Modelo para pesquisa de tipos de documento"""
    filtrar_apenas_ativo: Optional[str] = Field("S", description="Filtrar apenas ativos")
    filtrar_por_codigo: Optional[str] = Field("", description="Filtrar por código")


class CategoriaResponse(BaseModel):
    """Modelo para resposta de categoria"""
    codigo: str
    descricao: str
    tipo: str


class DepartamentoResponse(BaseModel):
    """Modelo para resposta de departamento"""
    codigo: str
    descricao: str


class ClienteResponse(BaseModel):
    """Modelo para resposta de cliente"""
    codigo_cliente_omie: int
    codigo_cliente_integracao: Optional[str] = None
    razao_social: str
    cnpj_cpf: str
    email: str


class ContaResponse(BaseModel):
    """Modelo para resposta de conta"""
    codigo_lancamento_omie: int
    codigo_cliente_fornecedor: int
    valor_documento: float
    data_vencimento: str
    numero_documento: str
    observacao: Optional[str] = None


class OmieError(BaseModel):
    """Modelo para erro da API Omie"""
    faultCode: str
    faultString: str