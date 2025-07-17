"""
Aplicação principal do Omie Tenant Manager
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn

from .database import get_db, engine
from .auth import verify_token
from .routers import empresas, usuarios, aplicacoes, auth
from .models.database import Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="Omie Tenant Manager",
    description="Sistema de gerenciamento multi-tenant para Omie MCP Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema de segurança
security = HTTPBearer()

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(aplicacoes.router, prefix="/aplicacoes", tags=["Aplicações"])

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Omie Tenant Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "omie-tenant-manager",
        "version": "1.0.0"
    }

@app.get("/protected")
async def protected_route(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Rota protegida para teste de autenticação"""
    token_data = verify_token(credentials.credentials, db)
    return {
        "message": "Acesso autorizado",
        "app_key": token_data["app_key"],
        "expires_at": token_data["exp"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )