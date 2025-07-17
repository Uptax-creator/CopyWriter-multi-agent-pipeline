"""
Router para gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re

from ..database import get_db
from ..models.database import Usuario, Empresa

router = APIRouter()

class UsuarioCreate(BaseModel):
    """Modelo para criação de usuário"""
    nome: str = Field(..., min_length=1, max_length=100)
    sobrenome: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    id_empresa: str
    
    @validator('email')
    def validar_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Email inválido')
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "nome": "João",
                "sobrenome": "Silva",
                "email": "joao.silva@empresa.com",
                "telefone": "(11) 99999-9999",
                "id_empresa": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

class UsuarioUpdate(BaseModel):
    """Modelo para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    sobrenome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    ativo: Optional[bool] = None
    
    @validator('email')
    def validar_email(cls, v):
        if v is not None:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Email inválido')
            return v.lower()
        return v

class UsuarioResponse(BaseModel):
    """Modelo para resposta de usuário"""
    id_usuario: str
    nome: str
    sobrenome: str
    email: str
    telefone: Optional[str]
    id_empresa: str
    criado_em: datetime
    atualizado_em: datetime
    ativo: bool
    
    # Dados da empresa
    empresa_razao_social: Optional[str] = None
    empresa_cnpj: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Criar novo usuário"""
    
    # Verificar se empresa existe
    empresa = db.query(Empresa).filter(
        Empresa.id_empresa == usuario.id_empresa,
        Empresa.ativo == True
    ).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada ou inativa"
        )
    
    # Verificar se email já existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    novo_usuario = Usuario(
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        telefone=usuario.telefone,
        id_empresa=usuario.id_empresa
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return UsuarioResponse(
        id_usuario=str(novo_usuario.id_usuario),
        nome=novo_usuario.nome,
        sobrenome=novo_usuario.sobrenome,
        email=novo_usuario.email,
        telefone=novo_usuario.telefone,
        id_empresa=str(novo_usuario.id_empresa),
        criado_em=novo_usuario.criado_em,
        atualizado_em=novo_usuario.atualizado_em,
        ativo=novo_usuario.ativo,
        empresa_razao_social=empresa.razao_social,
        empresa_cnpj=empresa.cnpj
    )

@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    id_empresa: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar usuários"""
    query = db.query(Usuario).join(Empresa)
    
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    if id_empresa:
        query = query.filter(Usuario.id_empresa == id_empresa)
    
    usuarios = query.offset(skip).limit(limit).all()
    
    return [
        UsuarioResponse(
            id_usuario=str(usuario.id_usuario),
            nome=usuario.nome,
            sobrenome=usuario.sobrenome,
            email=usuario.email,
            telefone=usuario.telefone,
            id_empresa=str(usuario.id_empresa),
            criado_em=usuario.criado_em,
            atualizado_em=usuario.atualizado_em,
            ativo=usuario.ativo,
            empresa_razao_social=usuario.empresa.razao_social,
            empresa_cnpj=usuario.empresa.cnpj
        )
        for usuario in usuarios
    ]

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def buscar_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    """Buscar usuário por ID"""
    usuario = db.query(Usuario).join(Empresa).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UsuarioResponse(
        id_usuario=str(usuario.id_usuario),
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        telefone=usuario.telefone,
        id_empresa=str(usuario.id_empresa),
        criado_em=usuario.criado_em,
        atualizado_em=usuario.atualizado_em,
        ativo=usuario.ativo,
        empresa_razao_social=usuario.empresa.razao_social,
        empresa_cnpj=usuario.empresa.cnpj
    )

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: str,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar usuário"""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar email único se estiver sendo alterado
    if usuario_update.email and usuario_update.email != usuario.email:
        email_existente = db.query(Usuario).filter(
            Usuario.email == usuario_update.email,
            Usuario.id_usuario != usuario_id
        ).first()
        
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado para outro usuário"
            )
    
    # Atualizar campos fornecidos
    update_data = usuario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    usuario.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(usuario)
    
    # Buscar dados da empresa para retorno
    empresa = db.query(Empresa).filter(Empresa.id_empresa == usuario.id_empresa).first()
    
    return UsuarioResponse(
        id_usuario=str(usuario.id_usuario),
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        telefone=usuario.telefone,
        id_empresa=str(usuario.id_empresa),
        criado_em=usuario.criado_em,
        atualizado_em=usuario.atualizado_em,
        ativo=usuario.ativo,
        empresa_razao_social=empresa.razao_social if empresa else None,
        empresa_cnpj=empresa.cnpj if empresa else None
    )

@router.delete("/{usuario_id}")
async def excluir_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    """Excluir usuário (soft delete)"""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Soft delete
    usuario.ativo = False
    usuario.atualizado_em = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Usuário excluído com sucesso"}

@router.get("/empresa/{empresa_id}/count")
async def contar_usuarios_empresa(
    empresa_id: str,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Contar usuários de uma empresa"""
    query = db.query(Usuario).filter(Usuario.id_empresa == empresa_id)
    
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    total = query.count()
    
    return {"empresa_id": empresa_id, "total_usuarios": total}

@router.get("/search/email/{email}")
async def buscar_por_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Buscar usuário por email"""
    usuario = db.query(Usuario).join(Empresa).filter(
        Usuario.email == email.lower()
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UsuarioResponse(
        id_usuario=str(usuario.id_usuario),
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        telefone=usuario.telefone,
        id_empresa=str(usuario.id_empresa),
        criado_em=usuario.criado_em,
        atualizado_em=usuario.atualizado_em,
        ativo=usuario.ativo,
        empresa_razao_social=usuario.empresa.razao_social,
        empresa_cnpj=usuario.empresa.cnpj
    )