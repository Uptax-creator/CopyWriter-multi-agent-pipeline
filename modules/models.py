"""
Modelos Pydantic para o Omie MCP Server
"""

from typing import Optional, Dict
from pydantic import BaseModel


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