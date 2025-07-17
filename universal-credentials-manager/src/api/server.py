"""
🌐 Universal Credentials Manager - API Server
FastAPI server with Auth0 integration and cloud storage
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx
import json
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ucm-api")

# Configuração do Auth0
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE", "")
AUTH0_ALGORITHMS = ["RS256"]

# Configuração da aplicação
app = FastAPI(
    title="Universal Credentials Manager",
    description="Secure credential management for multiple ERP systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Modelos Pydantic
class CredentialRequest(BaseModel):
    name: str = Field(..., description="Nome da empresa")
    credential_type: str = Field(..., description="Tipo de credencial (omie, nibo, generic)")
    active: bool = Field(default=True, description="Status ativo")
    security_level: str = Field(default="standard", description="Nível de segurança")
    
    # Campos específicos por tipo
    app_key: Optional[str] = Field(None, description="App Key (Omie)")
    app_secret: Optional[str] = Field(None, description="App Secret (Omie)")
    api_token: Optional[str] = Field(None, description="API Token (Nibo)")
    company_id: Optional[str] = Field(None, description="Company ID (Nibo)")
    api_key: Optional[str] = Field(None, description="API Key (Generic)")
    base_url: Optional[str] = Field(None, description="Base URL")

class CredentialResponse(BaseModel):
    key: str
    name: str
    credential_type: str
    active: bool
    security_level: str
    token_expired: bool
    has_credentials: bool
    created_at: Optional[str]
    updated_at: Optional[str]

class ProjectResponse(BaseModel):
    name: str
    companies_count: int
    created_at: Optional[str]
    last_updated: Optional[str]

class AuditLogResponse(BaseModel):
    timestamp: str
    event: str
    project: str
    company_key: str
    company_name: str
    status: str
    user_email: Optional[str] = None

# Cache para chaves públicas do Auth0
auth0_public_keys_cache = {}

async def get_auth0_public_keys():
    """Obtém chaves públicas do Auth0 para validação JWT"""
    global auth0_public_keys_cache
    
    if not auth0_public_keys_cache:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
                auth0_public_keys_cache = response.json()
        except Exception as e:
            logger.error(f"Erro ao obter chaves Auth0: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de autenticação indisponível"
            )
    
    return auth0_public_keys_cache

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifica token JWT do Auth0"""
    if not AUTH0_DOMAIN or not AUTH0_API_AUDIENCE:
        # Modo desenvolvimento - pular validação
        logger.warning("🚫 AUTH0 não configurado - modo desenvolvimento")
        return {"sub": "dev-user", "email": "dev@example.com", "permissions": ["admin"]}
    
    try:
        import jwt
        from jwt.algorithms import RSAAlgorithm
        
        # Decodificar header do token
        unverified_header = jwt.get_unverified_header(credentials.credentials)
        
        # Obter chaves públicas
        jwks = await get_auth0_public_keys()
        
        # Encontrar chave correspondente
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chave de validação não encontrada"
            )
        
        # Validar token
        public_key = RSAAlgorithm.from_jwk(rsa_key)
        payload = jwt.decode(
            credentials.credentials,
            public_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Claims inválidos do token"
        )
    except Exception as e:
        logger.error(f"Erro na validação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def check_permissions(required_permission: str):
    """Decorator para verificar permissões do usuário"""
    def permission_checker(current_user: dict = Depends(verify_token)):
        user_permissions = current_user.get("permissions", [])
        
        if "admin" in user_permissions or required_permission in user_permissions:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissão necessária: {required_permission}"
        )
    
    return permission_checker

# Simulação do storage (será substituído pela implementação real)
class MockStorage:
    def __init__(self):
        self.projects = {}
    
    def list_projects(self) -> List[Dict]:
        return [
            {
                "name": "omie-mcp",
                "companies_count": 2,
                "created_at": "2025-07-15T10:00:00",
                "last_updated": "2025-07-15T14:30:00"
            },
            {
                "name": "nibo-mcp", 
                "companies_count": 1,
                "created_at": "2025-07-15T11:00:00",
                "last_updated": "2025-07-15T13:30:00"
            }
        ]
    
    def get_project_companies(self, project_name: str) -> List[Dict]:
        if project_name == "omie-mcp":
            return [
                {
                    "key": "empresa1",
                    "name": "Empresa Principal LTDA",
                    "credential_type": "omie",
                    "active": True,
                    "security_level": "high",
                    "token_expired": False,
                    "has_credentials": True,
                    "created_at": "2025-07-15T10:00:00",
                    "updated_at": "2025-07-15T14:30:00"
                },
                {
                    "key": "empresa2",
                    "name": "Filial Norte SA",
                    "credential_type": "omie",
                    "active": True,
                    "security_level": "standard",
                    "token_expired": True,
                    "has_credentials": True,
                    "created_at": "2025-07-15T10:15:00",
                    "updated_at": "2025-07-15T12:00:00"
                }
            ]
        elif project_name == "nibo-mcp":
            return [
                {
                    "key": "company1",
                    "name": "Tech Company Inc",
                    "credential_type": "nibo",
                    "active": True,
                    "security_level": "high",
                    "token_expired": False,
                    "has_credentials": True,
                    "created_at": "2025-07-15T11:00:00",
                    "updated_at": "2025-07-15T13:30:00"
                }
            ]
        return []

# Instância mock do storage
mock_storage = MockStorage()

# Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Universal Credentials Manager",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/projects", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(check_permissions("read:projects"))
):
    """Lista todos os projetos disponíveis"""
    try:
        projects = mock_storage.list_projects()
        return [ProjectResponse(**project) for project in projects]
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.get("/api/v1/projects/{project_name}/companies", response_model=List[CredentialResponse])
async def list_project_companies(
    project_name: str,
    current_user: dict = Depends(check_permissions("read:credentials"))
):
    """Lista empresas de um projeto específico"""
    try:
        companies = mock_storage.get_project_companies(project_name)
        return [CredentialResponse(**company) for company in companies]
    except Exception as e:
        logger.error(f"Erro ao listar empresas do projeto {project_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.get("/api/v1/projects/{project_name}/credentials/{company_key}")
async def get_credentials(
    project_name: str,
    company_key: str,
    current_user: dict = Depends(check_permissions("read:credentials"))
):
    """Obtém credenciais específicas de uma empresa"""
    try:
        # Log de auditoria
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_access",
            "project": project_name,
            "company_key": company_key,
            "user_email": current_user.get("email", "unknown"),
            "status": "SUCCESS"
        }
        logger.info(f"🔍 AUDIT: {json.dumps(audit_log)}")
        
        # Simulação de credenciais (sem dados sensíveis no log)
        return {
            "project": project_name,
            "company_key": company_key,
            "app_key": "***ENCRYPTED***",
            "app_secret": "***ENCRYPTED***",
            "base_url": "https://app.omie.com.br/api/v1/",
            "expires_at": "2025-07-15T15:30:00",
            "last_accessed": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter credenciais {project_name}/{company_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.post("/api/v1/projects/{project_name}/credentials")
async def create_credentials(
    project_name: str,
    request: CredentialRequest,
    current_user: dict = Depends(check_permissions("write:credentials"))
):
    """Cria novas credenciais para uma empresa"""
    try:
        # Log de auditoria
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_create",
            "project": project_name,
            "company_name": request.name,
            "user_email": current_user.get("email", "unknown"),
            "status": "SUCCESS"
        }
        logger.info(f"🔍 AUDIT: {json.dumps(audit_log)}")
        
        return {
            "message": "Credenciais criadas com sucesso",
            "project": project_name,
            "company_name": request.name,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar credenciais para {project_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.put("/api/v1/projects/{project_name}/credentials/{company_key}")
async def update_credentials(
    project_name: str,
    company_key: str,
    request: CredentialRequest,
    current_user: dict = Depends(check_permissions("write:credentials"))
):
    """Atualiza credenciais existentes"""
    try:
        # Log de auditoria
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_update",
            "project": project_name,
            "company_key": company_key,
            "user_email": current_user.get("email", "unknown"),
            "status": "SUCCESS"
        }
        logger.info(f"🔍 AUDIT: {json.dumps(audit_log)}")
        
        return {
            "message": "Credenciais atualizadas com sucesso",
            "project": project_name,
            "company_key": company_key,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar credenciais {project_name}/{company_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.delete("/api/v1/projects/{project_name}/credentials/{company_key}")
async def delete_credentials(
    project_name: str,
    company_key: str,
    current_user: dict = Depends(check_permissions("delete:credentials"))
):
    """Remove credenciais de uma empresa"""
    try:
        # Log de auditoria
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_delete",
            "project": project_name,
            "company_key": company_key,
            "user_email": current_user.get("email", "unknown"),
            "status": "SUCCESS"
        }
        logger.info(f"🔍 AUDIT: {json.dumps(audit_log)}")
        
        return {
            "message": "Credenciais removidas com sucesso",
            "project": project_name,
            "company_key": company_key,
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover credenciais {project_name}/{company_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@app.get("/api/v1/audit/logs")
async def get_audit_logs(
    project: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(check_permissions("read:audit"))
):
    """Obtém logs de auditoria"""
    try:
        # Simulação de logs de auditoria
        logs = [
            {
                "timestamp": "2025-07-15T14:30:00",
                "event": "credential_access",
                "project": "omie-mcp",
                "company_key": "empresa1",
                "company_name": "Empresa Principal LTDA",
                "status": "SUCCESS",
                "user_email": "admin@company.com"
            },
            {
                "timestamp": "2025-07-15T14:25:00",
                "event": "credential_update",
                "project": "omie-mcp",
                "company_key": "empresa2",
                "company_name": "Filial Norte SA",
                "status": "SUCCESS",
                "user_email": "manager@company.com"
            }
        ]
        
        # Filtrar por projeto se especificado
        if project:
            logs = [log for log in logs if log["project"] == project]
        
        # Limitar resultados
        logs = logs[:limit]
        
        return [AuditLogResponse(**log) for log in logs]
        
    except Exception as e:
        logger.error(f"Erro ao obter logs de auditoria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8100))
    
    logger.info(f"🚀 Iniciando Universal Credentials Manager na porta {port}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )