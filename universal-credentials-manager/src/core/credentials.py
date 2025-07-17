"""
🏢 Modelos de Credenciais Universais
Classes para diferentes tipos de credenciais (Omie, Nibo, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("credentials")

@dataclass
class BaseCredentials(ABC):
    """Classe base para credenciais"""
    name: str
    active: bool = True
    security_level: str = "standard"
    token_timeout_minutes: int = 60
    token_expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @abstractmethod
    def get_sensitive_fields(self) -> list:
        """Retorna lista de campos sensíveis para criptografia"""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Verifica se as credenciais são válidas"""
        pass
    
    def is_token_expired(self) -> bool:
        """Verifica se o token expirou"""
        if not self.token_expires_at:
            return False
        return datetime.now() > self.token_expires_at
    
    def refresh_token_expiration(self):
        """Atualiza a expiração do token"""
        self.token_expires_at = datetime.now() + timedelta(minutes=self.token_timeout_minutes)
        self.updated_at = datetime.now()
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        
        # Converter datetime para string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        if not include_sensitive:
            sensitive_fields = self.get_sensitive_fields()
            for field in sensitive_fields:
                if field in data:
                    data[field] = "***HIDDEN***"
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Cria instância a partir de dicionário"""
        # Converter strings de data para datetime
        for date_field in ['token_expires_at', 'created_at', 'updated_at']:
            if date_field in data and data[date_field]:
                if isinstance(data[date_field], str):
                    try:
                        data[date_field] = datetime.fromisoformat(data[date_field])
                    except ValueError:
                        data[date_field] = None
        
        return cls(**data)

@dataclass
class OmieCredentials(BaseCredentials):
    """Credenciais específicas do Omie ERP"""
    app_key: str = ""
    app_secret: str = ""
    base_url: str = "https://app.omie.com.br/api/v1/"
    company_id: Optional[str] = None
    
    def get_sensitive_fields(self) -> list:
        """Campos sensíveis do Omie"""
        return ["app_key", "app_secret"]
    
    def is_valid(self) -> bool:
        """Valida credenciais do Omie"""
        return bool(
            self.app_key and 
            self.app_secret and 
            self.active and
            self.base_url
        )
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação para requisições"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Universal-Credentials-Manager/1.0"
        }
    
    def get_auth_payload(self, call: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna payload de autenticação do Omie"""
        return {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param]
        }

@dataclass
class NiboCredentials(BaseCredentials):
    """Credenciais específicas do Nibo"""
    api_token: str = ""
    company_id: str = ""
    base_url: str = "https://api.nibo.com.br"
    
    def get_sensitive_fields(self) -> list:
        """Campos sensíveis do Nibo"""
        return ["api_token"]
    
    def is_valid(self) -> bool:
        """Valida credenciais do Nibo"""
        return bool(
            self.api_token and 
            self.company_id and 
            self.active and
            self.base_url
        )
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação para requisições"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Universal-Credentials-Manager/1.0"
        }

@dataclass
class GenericAPICredentials(BaseCredentials):
    """Credenciais genéricas para APIs"""
    api_key: str = ""
    api_secret: str = ""
    base_url: str = ""
    auth_type: str = "bearer"  # bearer, basic, api_key
    
    def get_sensitive_fields(self) -> list:
        """Campos sensíveis genéricos"""
        return ["api_key", "api_secret"]
    
    def is_valid(self) -> bool:
        """Valida credenciais genéricas"""
        return bool(
            self.api_key and 
            self.active and
            self.base_url
        )
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação baseado no tipo"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Universal-Credentials-Manager/1.0"
        }
        
        if self.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.auth_type == "api_key":
            headers["X-API-Key"] = self.api_key
        elif self.auth_type == "basic" and self.api_secret:
            import base64
            credentials = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        return headers

class CredentialsFactory:
    """Factory para criar diferentes tipos de credenciais"""
    
    CREDENTIAL_TYPES = {
        "omie": OmieCredentials,
        "nibo": NiboCredentials,
        "generic": GenericAPICredentials
    }
    
    @classmethod
    def create_credentials(cls, credential_type: str, data: Dict[str, Any]) -> BaseCredentials:
        """Cria credenciais do tipo especificado"""
        if credential_type not in cls.CREDENTIAL_TYPES:
            raise ValueError(f"Tipo de credencial não suportado: {credential_type}")
        
        credential_class = cls.CREDENTIAL_TYPES[credential_type]
        return credential_class.from_dict(data)
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Retorna tipos de credenciais suportados"""
        return list(cls.CREDENTIAL_TYPES.keys())
    
    @classmethod
    def detect_credential_type(cls, data: Dict[str, Any]) -> str:
        """Detecta automaticamente o tipo de credencial"""
        if "app_key" in data and "app_secret" in data:
            return "omie"
        elif "api_token" in data and "company_id" in data:
            return "nibo"
        else:
            return "generic"