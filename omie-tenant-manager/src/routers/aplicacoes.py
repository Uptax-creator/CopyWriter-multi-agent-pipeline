"""
Router para gerenciamento de aplicações
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.database import Aplicacao, AplicacaoCliente, Empresa
from ..auth import create_app_credentials, rotate_app_secret

router = APIRouter()

class AplicacaoCreate(BaseModel):
    """Modelo para criação de aplicação do sistema"""
    descricao: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., description="Tipo da aplicação: 'claude', 'copilot', 'n8n', 'api'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "descricao": "Claude Desktop Integration",
                "tipo": "claude"
            }
        }

class AplicacaoUpdate(BaseModel):
    """Modelo para atualização de aplicação"""
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    tipo: Optional[str] = None
    ativo: Optional[bool] = None

class AplicacaoResponse(BaseModel):
    """Modelo para resposta de aplicação com APP_SECRET visível"""
    id_aplicacao: str
    descricao: str
    tipo: str
    app_key: str
    app_secret: Optional[str] = None  # Será mostrado apenas na criação
    criado_em: datetime
    ultimo_acesso_em: Optional[datetime]
    ativo: bool
    total_clientes: int = 0
    
    class Config:
        from_attributes = True

class AplicacaoClienteCreate(BaseModel):
    """Modelo para criação de aplicação do cliente"""
    id_empresa: str
    id_aplicacao: str
    nome_aplicacao: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    omie_app_key: str = Field(..., min_length=1)
    omie_app_secret: str = Field(..., min_length=1)
    config_omie: Optional[Dict[str, Any]] = None
    config_aplicacao: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_empresa": "123e4567-e89b-12d3-a456-426614174000",
                "id_aplicacao": "456e7890-e89b-12d3-a456-426614174000",
                "nome_aplicacao": "Claude para Contabilidade",
                "descricao": "Integração do Claude com sistema contábil",
                "omie_app_key": "1234567890123",
                "omie_app_secret": "abcdefghijklmnop",
                "config_omie": {
                    "departamento_padrao": "001",
                    "categoria_padrao": "1.01.01"
                },
                "config_aplicacao": {
                    "modo": "producao",
                    "timeout": 30
                }
            }
        }

class AplicacaoClienteUpdate(BaseModel):
    """Modelo para atualização de aplicação do cliente"""
    nome_aplicacao: Optional[str] = None
    descricao: Optional[str] = None
    omie_app_key: Optional[str] = None
    omie_app_secret: Optional[str] = None
    config_omie: Optional[Dict[str, Any]] = None
    config_aplicacao: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None

class AplicacaoClienteResponse(BaseModel):
    """Modelo para resposta de aplicação do cliente"""
    id_aplicacao_cliente: str
    id_empresa: str
    id_aplicacao: str
    nome_aplicacao: str
    descricao: Optional[str]
    omie_app_key: str
    config_omie: Optional[Dict[str, Any]]
    config_aplicacao: Optional[Dict[str, Any]]
    criado_em: datetime
    atualizado_em: datetime
    ativo: bool
    
    # Dados relacionados
    empresa_razao_social: Optional[str] = None
    empresa_cnpj: Optional[str] = None
    aplicacao_descricao: Optional[str] = None
    aplicacao_tipo: Optional[str] = None
    
    class Config:
        from_attributes = True

# Endpoints para Aplicações do Sistema

@router.post("/", response_model=AplicacaoResponse)
async def criar_aplicacao(
    aplicacao: AplicacaoCreate,
    db: Session = Depends(get_db)
):
    """Criar nova aplicação do sistema com credenciais automáticas"""
    try:
        # Criar credenciais
        credentials = create_app_credentials(aplicacao.descricao, db)
        
        # Buscar a aplicação criada para adicionar o tipo
        app = db.query(Aplicacao).filter(Aplicacao.app_key == credentials["app_key"]).first()
        if app:
            app.tipo = aplicacao.tipo
            app.app_secret_visible = credentials["app_secret"]  # Guardar temporariamente
            db.commit()
            db.refresh(app)
        
        return AplicacaoResponse(
            id_aplicacao=credentials["id_aplicacao"],
            descricao=aplicacao.descricao,
            tipo=aplicacao.tipo,
            app_key=credentials["app_key"],
            app_secret=credentials["app_secret"],  # Mostrar apenas na criação
            criado_em=app.criado_em,
            ultimo_acesso_em=app.ultimo_acesso_em,
            ativo=app.ativo,
            total_clientes=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar aplicação: {str(e)}"
        )

@router.get("/", response_model=List[AplicacaoResponse])
async def listar_aplicacoes(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar aplicações do sistema"""
    query = db.query(Aplicacao)
    
    if ativo is not None:
        query = query.filter(Aplicacao.ativo == ativo)
    
    if tipo:
        query = query.filter(Aplicacao.tipo == tipo)
    
    aplicacoes = query.offset(skip).limit(limit).all()
    
    result = []
    for app in aplicacoes:
        # Contar clientes vinculados
        total_clientes = db.query(AplicacaoCliente).filter(
            AplicacaoCliente.id_aplicacao == app.id_aplicacao,
            AplicacaoCliente.ativo == True
        ).count()
        
        result.append(AplicacaoResponse(
            id_aplicacao=str(app.id_aplicacao),
            descricao=app.descricao,
            tipo=app.tipo,
            app_key=app.app_key,
            app_secret=app.app_secret_visible,  # Mostrar se disponível
            criado_em=app.criado_em,
            ultimo_acesso_em=app.ultimo_acesso_em,
            ativo=app.ativo,
            total_clientes=total_clientes
        ))
    
    return result

@router.get("/{aplicacao_id}", response_model=AplicacaoResponse)
async def buscar_aplicacao(
    aplicacao_id: str,
    db: Session = Depends(get_db)
):
    """Buscar aplicação por ID"""
    aplicacao = db.query(Aplicacao).filter(Aplicacao.id_aplicacao == aplicacao_id).first()
    
    if not aplicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    # Contar clientes vinculados
    total_clientes = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_aplicacao == aplicacao_id,
        AplicacaoCliente.ativo == True
    ).count()
    
    return AplicacaoResponse(
        id_aplicacao=str(aplicacao.id_aplicacao),
        descricao=aplicacao.descricao,
        tipo=aplicacao.tipo,
        app_key=aplicacao.app_key,
        app_secret=aplicacao.app_secret_visible,
        criado_em=aplicacao.criado_em,
        ultimo_acesso_em=aplicacao.ultimo_acesso_em,
        ativo=aplicacao.ativo,
        total_clientes=total_clientes
    )

@router.put("/{aplicacao_id}", response_model=AplicacaoResponse)
async def atualizar_aplicacao(
    aplicacao_id: str,
    aplicacao_update: AplicacaoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar aplicação"""
    aplicacao = db.query(Aplicacao).filter(Aplicacao.id_aplicacao == aplicacao_id).first()
    
    if not aplicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    # Atualizar campos fornecidos
    update_data = aplicacao_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(aplicacao, field, value)
    
    db.commit()
    db.refresh(aplicacao)
    
    # Contar clientes vinculados
    total_clientes = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_aplicacao == aplicacao_id,
        AplicacaoCliente.ativo == True
    ).count()
    
    return AplicacaoResponse(
        id_aplicacao=str(aplicacao.id_aplicacao),
        descricao=aplicacao.descricao,
        tipo=aplicacao.tipo,
        app_key=aplicacao.app_key,
        app_secret=None,  # Não mostrar em atualizações
        criado_em=aplicacao.criado_em,
        ultimo_acesso_em=aplicacao.ultimo_acesso_em,
        ativo=aplicacao.ativo,
        total_clientes=total_clientes
    )

@router.post("/{aplicacao_id}/rotate-secret")
async def rotacionar_secret(
    aplicacao_id: str,
    db: Session = Depends(get_db)
):
    """Rotacionar APP_SECRET de uma aplicação"""
    aplicacao = db.query(Aplicacao).filter(Aplicacao.id_aplicacao == aplicacao_id).first()
    
    if not aplicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    try:
        new_secret = rotate_app_secret(aplicacao.app_key, db)
        
        # Atualizar o campo visível temporariamente
        aplicacao.app_secret_visible = new_secret
        db.commit()
        
        return {
            "message": "APP_SECRET rotacionado com sucesso",
            "new_app_secret": new_secret,
            "app_key": aplicacao.app_key,
            "warning": "Atualize todas as aplicações clientes com o novo SECRET"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{aplicacao_id}")
async def excluir_aplicacao(
    aplicacao_id: str,
    db: Session = Depends(get_db)
):
    """Excluir aplicação (soft delete)"""
    aplicacao = db.query(Aplicacao).filter(Aplicacao.id_aplicacao == aplicacao_id).first()
    
    if not aplicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    # Verificar se há clientes vinculados ativos
    clientes_ativos = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_aplicacao == aplicacao_id,
        AplicacaoCliente.ativo == True
    ).count()
    
    if clientes_ativos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir: aplicação possui {clientes_ativos} clientes vinculados"
        )
    
    # Soft delete
    aplicacao.ativo = False
    db.commit()
    
    return {"message": "Aplicação excluída com sucesso"}

# Endpoints para Aplicações dos Clientes

@router.post("/cliente", response_model=AplicacaoClienteResponse)
async def criar_aplicacao_cliente(
    aplicacao_cliente: AplicacaoClienteCreate,
    db: Session = Depends(get_db)
):
    """Criar aplicação específica do cliente"""
    
    # Verificar se empresa existe
    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == aplicacao_cliente.id_empresa,
        Empresa.ativo == True
    ).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Verificar se aplicação do sistema existe
    aplicacao = db.query(Aplicacao).filter(
        Aplicacao.id_aplicacao == aplicacao_cliente.id_aplicacao,
        Aplicacao.ativo == True
    ).first()
    
    if not aplicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    # Verificar se já existe vinculação
    vinculacao_existente = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_empresa == aplicacao_cliente.id_empresa,
        AplicacaoCliente.id_aplicacao == aplicacao_cliente.id_aplicacao
    ).first()
    
    if vinculacao_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma aplicação vinculada entre esta empresa e aplicação"
        )
    
    # Hash do secret do Omie
    from ..auth import hash_password
    omie_secret_hash = hash_password(aplicacao_cliente.omie_app_secret)
    
    # Criar aplicação do cliente
    nova_aplicacao_cliente = AplicacaoCliente(
        id_empresa=aplicacao_cliente.id_empresa,
        id_aplicacao=aplicacao_cliente.id_aplicacao,
        nome_aplicacao=aplicacao_cliente.nome_aplicacao,
        descricao=aplicacao_cliente.descricao,
        omie_app_key=aplicacao_cliente.omie_app_key,
        omie_app_secret_hash=omie_secret_hash,
        config_omie_json=aplicacao_cliente.config_omie,
        config_aplicacao_json=aplicacao_cliente.config_aplicacao
    )
    
    db.add(nova_aplicacao_cliente)
    db.commit()
    db.refresh(nova_aplicacao_cliente)
    
    return AplicacaoClienteResponse(
        id_aplicacao_cliente=str(nova_aplicacao_cliente.id_aplicacao_cliente),
        id_empresa=str(nova_aplicacao_cliente.id_empresa),
        id_aplicacao=str(nova_aplicacao_cliente.id_aplicacao),
        nome_aplicacao=nova_aplicacao_cliente.nome_aplicacao,
        descricao=nova_aplicacao_cliente.descricao,
        omie_app_key=nova_aplicacao_cliente.omie_app_key,
        config_omie=nova_aplicacao_cliente.config_omie_json,
        config_aplicacao=nova_aplicacao_cliente.config_aplicacao_json,
        criado_em=nova_aplicacao_cliente.criado_em,
        atualizado_em=nova_aplicacao_cliente.atualizado_em,
        ativo=nova_aplicacao_cliente.ativo,
        empresa_razao_social=empresa.razao_social,
        empresa_cnpj=empresa.cnpj,
        aplicacao_descricao=aplicacao.descricao,
        aplicacao_tipo=aplicacao.tipo
    )

@router.get("/cliente", response_model=List[AplicacaoClienteResponse])
async def listar_aplicacoes_cliente(
    skip: int = 0,
    limit: int = 100,
    id_empresa: Optional[str] = None,
    id_aplicacao: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar aplicações dos clientes"""
    query = db.query(AplicacaoCliente).join(Empresa).join(Aplicacao)
    
    if id_empresa:
        query = query.filter(AplicacaoCliente.id_empresa == id_empresa)
    
    if id_aplicacao:
        query = query.filter(AplicacaoCliente.id_aplicacao == id_aplicacao)
    
    if ativo is not None:
        query = query.filter(AplicacaoCliente.ativo == ativo)
    
    aplicacoes_cliente = query.offset(skip).limit(limit).all()
    
    return [
        AplicacaoClienteResponse(
            id_aplicacao_cliente=str(app.id_aplicacao_cliente),
            id_empresa=str(app.id_empresa),
            id_aplicacao=str(app.id_aplicacao),
            nome_aplicacao=app.nome_aplicacao,
            descricao=app.descricao,
            omie_app_key=app.omie_app_key,
            config_omie=app.config_omie_json,
            config_aplicacao=app.config_aplicacao_json,
            criado_em=app.criado_em,
            atualizado_em=app.atualizado_em,
            ativo=app.ativo,
            empresa_razao_social=app.empresa.razao_social,
            empresa_cnpj=app.empresa.cnpj,
            aplicacao_descricao=app.aplicacao.descricao,
            aplicacao_tipo=app.aplicacao.tipo
        )
        for app in aplicacoes_cliente
    ]

@router.put("/cliente/{aplicacao_cliente_id}", response_model=AplicacaoClienteResponse)
async def atualizar_aplicacao_cliente(
    aplicacao_cliente_id: str,
    aplicacao_update: AplicacaoClienteUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar aplicação do cliente"""
    aplicacao_cliente = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_aplicacao_cliente == aplicacao_cliente_id
    ).first()
    
    if not aplicacao_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação do cliente não encontrada"
        )
    
    # Atualizar campos fornecidos
    update_data = aplicacao_update.dict(exclude_unset=True)
    
    # Hash do novo secret se fornecido
    if 'omie_app_secret' in update_data:
        from ..auth import hash_password
        update_data['omie_app_secret_hash'] = hash_password(update_data.pop('omie_app_secret'))
    
    # Tratar campos JSON
    for field, value in update_data.items():
        if field == 'config_omie':
            setattr(aplicacao_cliente, 'config_omie_json', value)
        elif field == 'config_aplicacao':
            setattr(aplicacao_cliente, 'config_aplicacao_json', value)
        else:
            setattr(aplicacao_cliente, field, value)
    
    aplicacao_cliente.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(aplicacao_cliente)
    
    # Buscar dados relacionados
    empresa = db.query(Empresa).filter(Empresa.id_empresa == aplicacao_cliente.id_empresa).first()
    aplicacao = db.query(Aplicacao).filter(Aplicacao.id_aplicacao == aplicacao_cliente.id_aplicacao).first()
    
    return AplicacaoClienteResponse(
        id_aplicacao_cliente=str(aplicacao_cliente.id_aplicacao_cliente),
        id_empresa=str(aplicacao_cliente.id_empresa),
        id_aplicacao=str(aplicacao_cliente.id_aplicacao),
        nome_aplicacao=aplicacao_cliente.nome_aplicacao,
        descricao=aplicacao_cliente.descricao,
        omie_app_key=aplicacao_cliente.omie_app_key,
        config_omie=aplicacao_cliente.config_omie_json,
        config_aplicacao=aplicacao_cliente.config_aplicacao_json,
        criado_em=aplicacao_cliente.criado_em,
        atualizado_em=aplicacao_cliente.atualizado_em,
        ativo=aplicacao_cliente.ativo,
        empresa_razao_social=empresa.razao_social if empresa else None,
        empresa_cnpj=empresa.cnpj if empresa else None,
        aplicacao_descricao=aplicacao.descricao if aplicacao else None,
        aplicacao_tipo=aplicacao.tipo if aplicacao else None
    )

@router.get("/tipos")
async def listar_tipos_aplicacao():
    """Listar tipos de aplicação disponíveis"""
    return {
        "tipos": [
            {"valor": "claude", "nome": "Claude Desktop"},
            {"valor": "copilot", "nome": "Microsoft Copilot Studio"},
            {"valor": "n8n", "nome": "N8N Workflow"},
            {"valor": "api", "nome": "API Personalizada"}
        ]
    }