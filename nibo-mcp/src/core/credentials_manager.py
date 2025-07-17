"""
Gerenciador de credenciais multi-empresa com timeout de tokens
"""
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger("credentials-manager")

class CompanyCredentials:
    def __init__(self, company_data: Dict):
        self.name = company_data.get("name", "")
        self.nibo_api_token = company_data.get("nibo_api_token", "")
        self.company_id = company_data.get("company_id", "")
        self.base_url = company_data.get("base_url", "https://api.nibo.com.br")
        self.token_timeout_minutes = company_data.get("token_timeout_minutes", 60)
        self.active = company_data.get("active", True)
        
        # Parse token expiration
        expires_str = company_data.get("token_expires_at")
        if expires_str:
            try:
                self.token_expires_at = datetime.fromisoformat(expires_str)
            except ValueError:
                self.token_expires_at = None
        else:
            self.token_expires_at = None
    
    def is_valid(self) -> bool:
        """Verifica se as credenciais são válidas"""
        return bool(
            self.nibo_api_token and 
            self.company_id and 
            self.active
        )
    
    def is_token_expired(self) -> bool:
        """Verifica se o token expirou"""
        if not self.token_expires_at:
            return False
        return datetime.now() > self.token_expires_at
    
    def refresh_token_expiration(self):
        """Atualiza a expiração do token"""
        self.token_expires_at = datetime.now() + timedelta(minutes=self.token_timeout_minutes)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "name": self.name,
            "nibo_api_token": self.nibo_api_token,
            "company_id": self.company_id,
            "base_url": self.base_url,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "token_timeout_minutes": self.token_timeout_minutes,
            "active": self.active
        }

class CredentialsManager:
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = Path(credentials_file)
        self.companies: Dict[str, CompanyCredentials] = {}
        self.default_company: Optional[str] = None
        self.security_config: Dict = {}
        self._load_credentials()
    
    def _load_credentials(self):
        """Carrega credenciais do arquivo"""
        try:
            if not self.credentials_file.exists():
                logger.warning(f"Arquivo de credenciais não encontrado: {self.credentials_file}")
                return
            
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Carregar empresas
            companies_data = data.get("companies", {})
            for company_key, company_data in companies_data.items():
                self.companies[company_key] = CompanyCredentials(company_data)
            
            # Configurações gerais
            self.default_company = data.get("default_company")
            self.security_config = data.get("security", {})
            
            logger.info(f"Carregadas {len(self.companies)} empresas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            raise
    
    def _save_credentials(self):
        """Salva credenciais no arquivo"""
        try:
            data = {
                "companies": {
                    key: company.to_dict() 
                    for key, company in self.companies.items()
                },
                "default_company": self.default_company,
                "security": self.security_config
            }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar credenciais: {e}")
            raise
    
    def get_company_list(self) -> List[Dict]:
        """Retorna lista de empresas disponíveis"""
        return [
            {
                "key": key,
                "name": company.name,
                "active": company.active,
                "token_expired": company.is_token_expired()
            }
            for key, company in self.companies.items()
        ]
    
    def get_company_credentials(self, company_key: Optional[str] = None) -> CompanyCredentials:
        """Obtém credenciais de uma empresa"""
        # Se não especificado, usa empresa padrão
        if not company_key:
            company_key = self.default_company
        
        if not company_key:
            raise ValueError("Nenhuma empresa especificada e nenhuma empresa padrão configurada")
        
        if company_key not in self.companies:
            raise ValueError(f"Empresa '{company_key}' não encontrada")
        
        company = self.companies[company_key]
        
        if not company.is_valid():
            raise ValueError(f"Credenciais inválidas para empresa '{company_key}'")
        
        if company.is_token_expired():
            logger.warning(f"Token expirado para empresa '{company_key}'")
            if self.security_config.get("auto_refresh_tokens", True):
                company.refresh_token_expiration()
                self._save_credentials()
                logger.info(f"Token renovado para empresa '{company_key}'")
            else:
                raise ValueError(f"Token expirado para empresa '{company_key}'. Renovação necessária.")
        
        # Log de acesso se habilitado
        if self.security_config.get("log_access_attempts", True):
            logger.info(f"Acesso às credenciais da empresa '{company_key}' ({company.name})")
        
        return company
    
    def add_company(self, company_key: str, company_data: Dict):
        """Adiciona uma nova empresa"""
        self.companies[company_key] = CompanyCredentials(company_data)
        self._save_credentials()
        logger.info(f"Empresa '{company_key}' adicionada")
    
    def update_company(self, company_key: str, company_data: Dict):
        """Atualiza dados de uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"Empresa '{company_key}' não encontrada")
        
        self.companies[company_key] = CompanyCredentials(company_data)
        self._save_credentials()
        logger.info(f"Empresa '{company_key}' atualizada")
    
    def deactivate_company(self, company_key: str):
        """Desativa uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"Empresa '{company_key}' não encontrada")
        
        company = self.companies[company_key]
        company.active = False
        self._save_credentials()
        logger.info(f"Empresa '{company_key}' desativada")
    
    def refresh_company_token(self, company_key: str):
        """Renova o token de uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"Empresa '{company_key}' não encontrada")
        
        company = self.companies[company_key]
        company.refresh_token_expiration()
        self._save_credentials()
        logger.info(f"Token renovado para empresa '{company_key}'")
    
    def is_multi_company_mode(self) -> bool:
        """Verifica se está em modo multi-empresa"""
        return self.security_config.get("require_company_selection", True)
    
    def get_company_count(self) -> int:
        """Retorna número de empresas ativas"""
        return len([c for c in self.companies.values() if c.active])