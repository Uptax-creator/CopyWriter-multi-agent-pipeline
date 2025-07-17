"""
Router para gerenciamento de empresas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import re

from ..database import get_db
from ..models.database import Empresa, Usuario, AplicacaoCliente
from ..auth import verify_token

router = APIRouter()

class EmpresaCreate(BaseModel):
    """Modelo para criação de empresa"""
    razao_social: str = Field(..., min_length=1, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=14)
    email_contato: Optional[str] = Field(None, max_length=255)
    telefone_contato: Optional[str] = Field(None, max_length=20)
    
    class Config:
        schema_extra = {
            "example": {
                "razao_social": "Empresa Exemplo LTDA",
                "cnpj": "12345678000195",
                "email_contato": "contato@empresa.com",
                "telefone_contato": "(11) 99999-9999"
            }
        }

class EmpresaUpdate(BaseModel):
    """Modelo para atualização de empresa"""
    razao_social: Optional[str] = Field(None, min_length=1, max_length=255)
    email_contato: Optional[str] = Field(None, max_length=255)
    telefone_contato: Optional[str] = Field(None, max_length=20)
    ativo: Optional[bool] = None

class EmpresaResponse(BaseModel):
    """Modelo para resposta de empresa"""
    id_empresa: str
    razao_social: str
    cnpj: str
    email_contato: Optional[str]
    telefone_contato: Optional[str]
    criado_em: datetime
    atualizado_em: datetime
    ativo: bool
    
    class Config:
        from_attributes = True

def validar_cnpj(cnpj: str) -> bool:
    """Validar CNPJ"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    if cnpj == cnpj[0] * 14:
        return False
    
    # Cálculo do primeiro dígito verificador
    soma = 0
    multiplicador = 5
    for i in range(12):
        soma += int(cnpj[i]) * multiplicador
        multiplicador = multiplicador - 1 if multiplicador > 2 else 9
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        return False
    
    # Cálculo do segundo dígito verificador
    soma = 0
    multiplicador = 6
    for i in range(13):
        soma += int(cnpj[i]) * multiplicador
        multiplicador = multiplicador - 1 if multiplicador > 2 else 9
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cnpj[13]) == digito2

@router.post("/", response_model=EmpresaResponse)
async def criar_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db)
):
    """Criar nova empresa"""
    
    # Validar CNPJ
    cnpj_limpo = re.sub(r'[^0-9]', '', empresa.cnpj)
    if not validar_cnpj(cnpj_limpo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido"
        )
    
    # Verificar se CNPJ já existe
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == cnpj_limpo).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    
    # Criar empresa
    nova_empresa = Empresa(
        razao_social=empresa.razao_social,
        cnpj=cnpj_limpo,
        email_contato=empresa.email_contato,
        telefone_contato=empresa.telefone_contato
    )
    
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    
    return EmpresaResponse(
        id_empresa=str(nova_empresa.id_empresa),
        razao_social=nova_empresa.razao_social,
        cnpj=nova_empresa.cnpj,
        email_contato=nova_empresa.email_contato,
        telefone_contato=nova_empresa.telefone_contato,
        criado_em=nova_empresa.criado_em,
        atualizado_em=nova_empresa.atualizado_em,
        ativo=nova_empresa.ativo
    )

@router.get("/", response_model=List[EmpresaResponse])
async def listar_empresas(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar empresas"""
    query = db.query(Empresa)
    
    if ativo is not None:
        query = query.filter(Empresa.ativo == ativo)
    
    empresas = query.offset(skip).limit(limit).all()
    
    return [
        EmpresaResponse(
            id_empresa=str(empresa.id_empresa),
            razao_social=empresa.razao_social,
            cnpj=empresa.cnpj,
            email_contato=empresa.email_contato,
            telefone_contato=empresa.telefone_contato,
            criado_em=empresa.criado_em,
            atualizado_em=empresa.atualizado_em,
            ativo=empresa.ativo
        )
        for empresa in empresas
    ]

@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def buscar_empresa(
    empresa_id: str,
    db: Session = Depends(get_db)
):
    """Buscar empresa por ID"""
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return EmpresaResponse(
        id_empresa=str(empresa.id_empresa),
        razao_social=empresa.razao_social,
        cnpj=empresa.cnpj,
        email_contato=empresa.email_contato,
        telefone_contato=empresa.telefone_contato,
        criado_em=empresa.criado_em,
        atualizado_em=empresa.atualizado_em,
        ativo=empresa.ativo
    )

@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(
    empresa_id: str,
    empresa_update: EmpresaUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar empresa"""
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Atualizar campos fornecidos
    update_data = empresa_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(empresa, field, value)
    
    empresa.atualizado_em = datetime.utcnow()
    
    db.commit()
    db.refresh(empresa)
    
    return EmpresaResponse(
        id_empresa=str(empresa.id_empresa),
        razao_social=empresa.razao_social,
        cnpj=empresa.cnpj,
        email_contato=empresa.email_contato,
        telefone_contato=empresa.telefone_contato,
        criado_em=empresa.criado_em,
        atualizado_em=empresa.atualizado_em,
        ativo=empresa.ativo
    )

@router.delete("/{empresa_id}")
async def excluir_empresa(
    empresa_id: str,
    db: Session = Depends(get_db)
):
    """Excluir empresa (soft delete)"""
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Verificar se há usuários ou aplicações vinculadas
    usuarios_count = db.query(Usuario).filter(
        and_(Usuario.id_empresa == empresa_id, Usuario.ativo == True)
    ).count()
    
    aplicacoes_count = db.query(AplicacaoCliente).filter(
        and_(AplicacaoCliente.id_empresa == empresa_id, AplicacaoCliente.ativo == True)
    ).count()
    
    if usuarios_count > 0 or aplicacoes_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir: empresa possui {usuarios_count} usuários e {aplicacoes_count} aplicações ativas"
        )
    
    # Soft delete
    empresa.ativo = False
    empresa.atualizado_em = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Empresa excluída com sucesso"}

@router.get("/{empresa_id}/usuarios")
async def listar_usuarios_empresa(
    empresa_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar usuários de uma empresa"""
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    usuarios = db.query(Usuario).filter(
        Usuario.id_empresa == empresa_id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id_usuario": str(usuario.id_usuario),
            "nome": usuario.nome,
            "sobrenome": usuario.sobrenome,
            "email": usuario.email,
            "telefone": usuario.telefone,
            "criado_em": usuario.criado_em,
            "ativo": usuario.ativo
        }
        for usuario in usuarios
    ]

@router.get("/{empresa_id}/aplicacoes")
async def listar_aplicacoes_empresa(
    empresa_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar aplicações vinculadas a uma empresa"""
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    aplicacoes = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_empresa == empresa_id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id_aplicacao_cliente": str(app.id_aplicacao_cliente),
            "id_aplicacao": str(app.id_aplicacao),
            "nome_aplicacao": app.nome_aplicacao,
            "omie_app_key": app.omie_app_key,
            "config_omie": app.config_omie_json,
            "config_aplicacao": app.config_aplicacao_json,
            "criado_em": app.criado_em,
            "ativo": app.ativo
        }
        for app in aplicacoes
    ]