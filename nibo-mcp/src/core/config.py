"""
Configurações para o Nibo MCP Server com suporte multi-empresa
"""
import os
import json
from typing import Optional
from .credentials_manager import CredentialsManager, CompanyCredentials

class NiboConfig:
    def __init__(self, company_key: Optional[str] = None, credentials_file: Optional[str] = None):
        self.credentials_manager = CredentialsManager(credentials_file or "credentials.json")
        self.current_company_key = company_key
        self.current_company: Optional[CompanyCredentials] = None
        self._load_company_credentials()
    
    def _load_company_credentials(self):
        """Carrega credenciais da empresa selecionada"""
        try:
            self.current_company = self.credentials_manager.get_company_credentials(
                self.current_company_key
            )
            if self.current_company_key is None:
                self.current_company_key = self.credentials_manager.default_company
        except Exception as e:
            self.current_company = None
            raise ValueError(f"Erro ao carregar credenciais: {e}")
    
    def set_company(self, company_key: str):
        """Define a empresa ativa"""
        self.current_company_key = company_key
        self._load_company_credentials()
    
    def is_configured(self) -> bool:
        """Verifica se as credenciais estão configuradas"""
        return self.current_company is not None and self.current_company.is_valid()
    
    def get_auth_headers(self) -> dict:
        """Retorna headers de autenticação"""
        if not self.current_company or not self.current_company.nibo_api_token:
            raise ValueError("API Token não configurado")
        return {"ApiToken": self.current_company.nibo_api_token}
    
    def get_api_url(self, endpoint: str) -> str:
        """Monta URL completa da API"""
        if not self.current_company:
            raise ValueError("Empresa não configurada")
        endpoint = endpoint.lstrip("/")
        return f"{self.current_company.base_url}/empresas/v1/{endpoint}"
    
    def get_company_list(self) -> list:
        """Retorna lista de empresas disponíveis"""
        return self.credentials_manager.get_company_list()
    
    def get_current_company_info(self) -> dict:
        """Retorna informações da empresa atual"""
        if not self.current_company:
            return {"error": "Nenhuma empresa selecionada"}
        
        return {
            "key": self.current_company_key,
            "name": self.current_company.name,
            "company_id": self.current_company.company_id,
            "token_expired": self.current_company.is_token_expired(),
            "active": self.current_company.active
        }
    
    @property
    def api_token(self) -> Optional[str]:
        """Propriedade para compatibilidade"""
        return self.current_company.nibo_api_token if self.current_company else None
    
    @property
    def company_id(self) -> Optional[str]:
        """Propriedade para compatibilidade"""
        return self.current_company.company_id if self.current_company else None