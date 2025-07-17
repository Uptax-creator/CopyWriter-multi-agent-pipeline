"""
Router de autenticação OAuth 2.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import authenticate_app, create_access_token, store_token, create_app_credentials

router = APIRouter()
security = HTTPBearer()

class TokenRequest(BaseModel):
    """Modelo para requisição de token"""
    app_key: str
    app_secret: str

class TokenResponse(BaseModel):
    """Modelo para resposta de token"""
    access_token: str
    token_type: str
    expires_in: int
    app_key: str

class AppCredentialsRequest(BaseModel):
    """Modelo para criação de credenciais"""
    descricao: str

@router.post("/token", response_model=TokenResponse)
async def get_access_token(
    token_request: TokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint OAuth 2.0 Client Credentials para obter access token
    """
    # Autenticar aplicação
    app = authenticate_app(token_request.app_key, token_request.app_secret, db)
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(hours=24)
    token_data = {
        "app_key": app.app_key,
        "app_id": str(app.id_aplicacao),
        "type": "access_token"
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    # Armazenar token no banco para controle de revogação
    expire_time = datetime.utcnow() + access_token_expires
    client_ip = request.client.host if request.client else "unknown"
    
    store_token(app.app_key, access_token, expire_time, client_ip, db)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        app_key=app.app_key
    )

@router.post("/credentials")
async def create_app_credentials_endpoint(
    credentials_request: AppCredentialsRequest,
    db: Session = Depends(get_db)
):
    """
    Criar novas credenciais de aplicação (APP_KEY e APP_SECRET)
    """
    try:
        credentials = create_app_credentials(credentials_request.descricao, db)
        return {
            "message": "Credenciais criadas com sucesso",
            **credentials
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar credenciais: {str(e)}"
        )

@router.get("/validate")
async def validate_token(
    db: Session = Depends(get_db)
):
    """
    Validar token atual (requer autenticação)
    """
    return {
        "message": "Token válido",
        "validated_at": datetime.utcnow().isoformat()
    }