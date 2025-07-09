"""
Modelos Pydantic para validação de dados
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# ============================================================================
# MODELOS BASE
# ============================================================================

class BaseOmieModel(BaseModel):
    """Modelo base para todas as entidades Omie"""
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        allow_population_by_field_name = True

class PaginationModel(BaseModel):
    """Modelo para paginação"""
    pagina: int = Field(1, ge=1, description="Página atual")
    registros_por_pagina: int = Field(50, ge=1, le=500, description="Registros por página")
    total_de_registros: Optional[int] = Field(None, description="Total de registros")
    total_de_paginas: Optional[int] = Field(None, description="Total de páginas")

# ============================================================================
# MODELOS DE CONSULTA
# ============================================================================

class ConsultaCategoriaRequest(BaseOmieModel):
    """Request para consulta de categorias"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_codigo: Optional[str] = None
    filtrar_por_descricao: Optional[str] = None

class ConsultaDepartamentoRequest(BaseOmieModel):
    """Request para consulta de departamentos"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_codigo: Optional[str] = None
    filtrar_por_descricao: Optional[str] = None

class ConsultaTipoDocumentoRequest(BaseOmieModel):
    """Request para consulta de tipos de documento"""
    filtrar_por_codigo: Optional[str] = None
    filtrar_por_descricao: Optional[str] = None

class ConsultaContasPagarRequest(BaseOmieModel):
    """Request para consulta de contas a pagar"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_codigo_lancamento: Optional[str] = None
    filtrar_por_fornecedor: Optional[str] = None
    filtrar_por_data_inicial: Optional[str] = None
    filtrar_por_data_final: Optional[str] = None

class ConsultaContasReceberRequest(BaseOmieModel):
    """Request para consulta de contas a receber"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_codigo_lancamento: Optional[str] = None
    filtrar_por_cliente: Optional[str] = None
    filtrar_por_data_inicial: Optional[str] = None
    filtrar_por_data_final: Optional[str] = None

class ConsultaClienteRequest(BaseOmieModel):
    """Request para consulta de clientes"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_nome: Optional[str] = None
    cnpj_cpf: Optional[str] = None
    codigo_cliente_omie: Optional[str] = None

class ConsultaFornecedorRequest(BaseOmieModel):
    """Request para consulta de fornecedores"""
    pagina: int = Field(1, ge=1)
    registros_por_pagina: int = Field(50, ge=1, le=500)
    filtrar_por_nome: Optional[str] = None
    cnpj_cpf: Optional[str] = None
    codigo_fornecedor_omie: Optional[str] = None

# ============================================================================
# MODELOS DE ENTIDADES
# ============================================================================

class EnderecoModel(BaseModel):
    """Modelo para endereço"""
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    
    @validator('cep')
    def validar_cep(cls, v):
        if v:
            import re
            cep_limpo = re.sub(r'[^0-9]', '', v)
            if len(cep_limpo) != 8:
                raise ValueError('CEP deve ter 8 dígitos')
        return v

class ClienteModel(BaseOmieModel):
    """Modelo para cliente"""
    codigo_cliente_omie: Optional[str] = None
    codigo_cliente_integracao: Optional[str] = None
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF do cliente")
    razao_social: str = Field(..., description="Razão social do cliente")
    nome_fantasia: Optional[str] = None
    email: Optional[str] = None
    telefone1_numero: Optional[str] = None
    telefone2_numero: Optional[str] = None
    endereco: Optional[EnderecoModel] = None
    
    @validator('cnpj_cpf')
    def validar_cnpj_cpf(cls, v):
        if v:
            import re
            doc_limpo = re.sub(r'[^0-9]', '', v)
            if len(doc_limpo) not in [11, 14]:
                raise ValueError('CNPJ/CPF deve ter 11 ou 14 dígitos')
        return v

class FornecedorModel(BaseOmieModel):
    """Modelo para fornecedor"""
    codigo_fornecedor_omie: Optional[str] = None
    codigo_fornecedor_integracao: Optional[str] = None
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF do fornecedor")
    razao_social: str = Field(..., description="Razão social do fornecedor")
    nome_fantasia: Optional[str] = None
    email: Optional[str] = None
    telefone1_numero: Optional[str] = None
    telefone2_numero: Optional[str] = None
    endereco: Optional[EnderecoModel] = None
    
    @validator('cnpj_cpf')
    def validar_cnpj_cpf(cls, v):
        if v:
            import re
            doc_limpo = re.sub(r'[^0-9]', '', v)
            if len(doc_limpo) not in [11, 14]:
                raise ValueError('CNPJ/CPF deve ter 11 ou 14 dígitos')
        return v

class DistribuicaoModel(BaseModel):
    """Modelo para distribuição de departamentos"""
    cCodDep: str = Field(..., description="Código do departamento")
    nPerc: float = Field(100.0, ge=0, le=100, description="Percentual do departamento")
    nValor: Optional[float] = Field(None, ge=0, description="Valor do departamento")

class ContaPagarModel(BaseOmieModel):
    """Modelo para conta a pagar"""
    codigo_lancamento_omie: Optional[str] = None
    codigo_lancamento_integracao: Optional[str] = None
    codigo_fornecedor_omie: Optional[str] = None
    codigo_fornecedor_integracao: Optional[str] = None
    data_vencimento: str = Field(..., description="Data de vencimento (DD/MM/YYYY)")
    valor_documento: float = Field(..., gt=0, description="Valor do documento")
    codigo_categoria: str = Field(..., description="Código da categoria")
    observacao: Optional[str] = None
    numero_documento: Optional[str] = None
    distribuicao: Optional[List[DistribuicaoModel]] = None
    
    @validator('data_vencimento')
    def validar_data_vencimento(cls, v):
        if v:
            import re
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', v):
                raise ValueError('Data deve estar no formato DD/MM/YYYY')
        return v

class ContaReceberModel(BaseOmieModel):
    """Modelo para conta a receber"""
    codigo_lancamento_omie: Optional[str] = None
    codigo_lancamento_integracao: Optional[str] = None
    codigo_cliente_omie: Optional[str] = None
    codigo_cliente_integracao: Optional[str] = None
    data_vencimento: str = Field(..., description="Data de vencimento (DD/MM/YYYY)")
    valor_documento: float = Field(..., gt=0, description="Valor do documento")
    codigo_categoria: str = Field(..., description="Código da categoria")
    observacao: Optional[str] = None
    numero_documento: Optional[str] = None
    distribuicao: Optional[List[DistribuicaoModel]] = None
    
    @validator('data_vencimento')
    def validar_data_vencimento(cls, v):
        if v:
            import re
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', v):
                raise ValueError('Data deve estar no formato DD/MM/YYYY')
        return v

# ============================================================================
# MODELOS DE RESPOSTA
# ============================================================================

class CategoriaResponse(BaseModel):
    """Resposta para categoria"""
    codigo: str
    descricao: str
    codigo_pai: Optional[str] = None

class DepartamentoResponse(BaseModel):
    """Resposta para departamento"""
    codigo: str
    descricao: str
    inativo: Optional[str] = None

class TipoDocumentoResponse(BaseModel):
    """Resposta para tipo de documento"""
    codigo: str
    descricao: str
    tipo: Optional[str] = None

class ClienteResponse(BaseModel):
    """Resposta para cliente"""
    codigo_cliente_omie: str
    codigo_cliente_integracao: Optional[str] = None
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    email: Optional[str] = None
    telefone1_numero: Optional[str] = None

class FornecedorResponse(BaseModel):
    """Resposta para fornecedor"""
    codigo_fornecedor_omie: str
    codigo_fornecedor_integracao: Optional[str] = None
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    email: Optional[str] = None
    telefone1_numero: Optional[str] = None

class ContaPagarResponse(BaseModel):
    """Resposta para conta a pagar"""
    codigo_lancamento_omie: str
    codigo_lancamento_integracao: Optional[str] = None
    codigo_fornecedor_omie: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    observacao: Optional[str] = None
    numero_documento: Optional[str] = None

class ContaReceberResponse(BaseModel):
    """Resposta para conta a receber"""
    codigo_lancamento_omie: str
    codigo_lancamento_integracao: Optional[str] = None
    codigo_cliente_omie: str
    data_vencimento: str
    valor_documento: float
    codigo_categoria: str
    observacao: Optional[str] = None
    numero_documento: Optional[str] = None

# ============================================================================
# MODELOS MCP
# ============================================================================

class MCPToolRequest(BaseModel):
    """Request para ferramenta MCP"""
    arguments: Dict[str, Any] = Field(default_factory=dict)

class MCPToolResponse(BaseModel):
    """Resposta para ferramenta MCP"""
    content: List[Dict[str, Any]] = Field(default_factory=list)

class MCPError(BaseModel):
    """Erro MCP"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class MCPRequest(BaseModel):
    """Request MCP completa"""
    jsonrpc: str = Field("2.0", description="Versão JSON-RPC")
    method: str = Field(..., description="Método MCP")
    params: Optional[Dict[str, Any]] = None
    id: Union[str, int] = Field(..., description="ID da requisição")

class MCPResponse(BaseModel):
    """Resposta MCP completa"""
    jsonrpc: str = Field("2.0", description="Versão JSON-RPC")
    id: Union[str, int] = Field(..., description="ID da requisição")
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None