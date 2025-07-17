"""
Módulo de autenticação OAuth 2.0
"""

import jwt
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .models.database import Aplicacao, Token

# Configurações JWT
SECRET_KEY = "your-secret-key-change-in-production"  # Em produção, use variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def generate_app_key() -> str:
    """Gerar APP_KEY único"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def generate_app_secret() -> str:
    """Gerar APP_SECRET único"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(64))

def hash_password(password: str) -> str:
    """Hash de senha com BCrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verificar senha com hash BCrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session) -> Dict:
    """Verificar e decodificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        app_key = payload.get("app_key")
        
        if app_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Verificar se o token não foi revogado
        token_hash = hash_password(token)
        db_token = db.query(Token).filter(
            Token.app_key == app_key,
            Token.token_hash == token_hash,
            Token.revogado == False,
            Token.expira_em > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revogado ou expirado"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def authenticate_app(app_key: str, app_secret: str, db: Session) -> Optional[Aplicacao]:
    """Autenticar aplicação com APP_KEY e APP_SECRET"""
    app = db.query(Aplicacao).filter(
        Aplicacao.app_key == app_key,
        Aplicacao.ativo == True
    ).first()
    
    if not app:
        return None
    
    if not verify_password(app_secret, app.app_secret_hash):
        return None
    
    # Atualizar último acesso
    app.ultimo_acesso_em = datetime.utcnow()
    db.commit()
    
    return app

def create_app_credentials(descricao: str, db: Session) -> Dict[str, str]:
    """Criar credenciais para nova aplicação"""
    app_key = generate_app_key()
    app_secret = generate_app_secret()
    app_secret_hash = hash_password(app_secret)
    
    # Verificar se APP_KEY é único
    while db.query(Aplicacao).filter(Aplicacao.app_key == app_key).first():
        app_key = generate_app_key()
    
    nova_app = Aplicacao(
        descricao=descricao,
        app_key=app_key,
        app_secret_hash=app_secret_hash
    )
    
    db.add(nova_app)
    db.commit()
    db.refresh(nova_app)
    
    return {
        "app_key": app_key,
        "app_secret": app_secret,  # Retorna apenas na criação
        "id_aplicacao": str(nova_app.id_aplicacao)
    }

def rotate_app_secret(app_key: str, db: Session) -> str:
    """Rotacionar APP_SECRET de uma aplicação"""
    app = db.query(Aplicacao).filter(
        Aplicacao.app_key == app_key,
        Aplicacao.ativo == True
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicação não encontrada"
        )
    
    new_app_secret = generate_app_secret()
    app.app_secret_hash = hash_password(new_app_secret)
    
    # Revogar todos os tokens existentes
    db.query(Token).filter(Token.app_key == app_key).update({"revogado": True})
    
    db.commit()
    
    return new_app_secret

def store_token(app_key: str, token: str, expire_time: datetime, ip_origem: str, db: Session):
    """Armazenar token no banco para controle de revogação"""
    token_hash = hash_password(token)
    
    db_token = Token(
        app_key=app_key,
        token_hash=token_hash,
        expira_em=expire_time,
        ip_origem=ip_origem
    )
    
    db.add(db_token)
    db.commit()

def revoke_token(token: str, db: Session):
    """Revogar token específico"""
    token_hash = hash_password(token)
    
    db.query(Token).filter(Token.token_hash == token_hash).update({"revogado": True})
    db.commit()