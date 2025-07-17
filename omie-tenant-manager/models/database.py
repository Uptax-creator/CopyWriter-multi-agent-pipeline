"""
Modelos de banco de dados para o Omie Tenant Manager
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import String as UUID_String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Empresa(Base):
    """Modelo para empresas/clientes"""
    __tablename__ = 'empresa'
    
    id_empresa = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    razao_social = Column(String(255), nullable=False)
    cnpj = Column(String(14), nullable=False, unique=True)
    email_contato = Column(String(255))
    telefone_contato = Column(String(20))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    usuarios = relationship("Usuario", back_populates="empresa")
    aplicacoes = relationship("ClienteAplicacao", back_populates="empresa")
    
    def __repr__(self):
        return f"<Empresa(cnpj='{self.cnpj}', razao_social='{self.razao_social}')>"

class Usuario(Base):
    """Modelo para usuários"""
    __tablename__ = 'usuario'
    
    id_usuario = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    sobrenome = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefone = Column(String(20))
    id_empresa = Column(String(36), ForeignKey('empresa.id_empresa'), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="usuarios")
    
    def __repr__(self):
        return f"<Usuario(email='{self.email}', nome='{self.nome} {self.sobrenome}')>"

class Aplicacao(Base):
    """Modelo para aplicações"""
    __tablename__ = 'aplicacao'
    
    id_aplicacao = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    descricao = Column(String(255), nullable=False)
    app_key = Column(String(32), nullable=False, unique=True)
    app_secret_hash = Column(String(60), nullable=False)  # BCrypt hash
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_acesso_em = Column(DateTime(timezone=True))
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    clientes = relationship("ClienteAplicacao", back_populates="aplicacao")
    
    def __repr__(self):
        return f"<Aplicacao(app_key='{self.app_key}', descricao='{self.descricao}')>"

class ClienteAplicacao(Base):
    """Modelo para vinculação cliente × aplicação"""
    __tablename__ = 'cliente_aplicacao'
    
    id_cliente_aplicacao = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_empresa = Column(String(36), ForeignKey('empresa.id_empresa'), nullable=False)
    id_aplicacao = Column(String(36), ForeignKey('aplicacao.id_aplicacao'), nullable=False)
    config_especifica_json = Column(JSON)  # Configurações específicas
    omie_app_key = Column(String(255))  # Credenciais Omie específicas do cliente
    omie_app_secret_hash = Column(String(60))  # Hash das credenciais Omie
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="aplicacoes")
    aplicacao = relationship("Aplicacao", back_populates="clientes")
    
    # Índices
    __table_args__ = (
        Index('idx_cliente_aplicacao_empresa', 'id_empresa'),
        Index('idx_cliente_aplicacao_app', 'id_aplicacao'),
    )
    
    def __repr__(self):
        return f"<ClienteAplicacao(empresa_id='{self.id_empresa}', app_id='{self.id_aplicacao}')>"

class Auditoria(Base):
    """Modelo para auditoria de operações"""
    __tablename__ = 'auditoria'
    
    id_auditoria = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tabela = Column(String(50), nullable=False)
    operacao = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    registro_id = Column(String(36), nullable=False)
    usuario_id = Column(String(36))
    dados_anteriores = Column(JSON)
    dados_novos = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_origem = Column(String(45))
    user_agent = Column(Text)
    
    def __repr__(self):
        return f"<Auditoria(tabela='{self.tabela}', operacao='{self.operacao}')>"

class Token(Base):
    """Modelo para tokens de acesso"""
    __tablename__ = 'token'
    
    id_token = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    app_key = Column(String(32), nullable=False)
    token_hash = Column(String(60), nullable=False)  # Hash do JWT
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    expira_em = Column(DateTime(timezone=True), nullable=False)
    revogado = Column(Boolean, default=False)
    ip_origem = Column(String(45))
    
    def __repr__(self):
        return f"<Token(app_key='{self.app_key}', expira_em='{self.expira_em}')>"