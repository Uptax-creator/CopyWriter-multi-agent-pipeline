"""
Configuração unificada para o Omie MCP Server
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Classe de configuração unificada"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.load_config()
    
    def load_config(self):
        """Carregar configurações de múltiplas fontes"""
        
        # Configurações padrão
        self.server_host = os.getenv("MCP_SERVER_HOST", "localhost")
        self.server_port = int(os.getenv("MCP_SERVER_PORT", "3000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Credenciais Omie
        self.omie_app_key = os.getenv("OMIE_APP_KEY", "")
        self.omie_app_secret = os.getenv("OMIE_APP_SECRET", "")
        
        # Carregar credenciais do arquivo se não estiverem em env
        if not self.omie_app_key or not self.omie_app_secret:
            self._load_credentials_from_file()
        
        # URLs da API Omie
        self.omie_base_url = "https://app.omie.com.br/api/v1"
        self.omie_timeout = 30
        
        # Configurações de cache
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutos
        
        # Configurações de rate limiting
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Validar configurações obrigatórias
        self._validate_config()
    
    def _load_credentials_from_file(self):
        """Carregar credenciais do arquivo credentials.json"""
        credentials_path = self.project_root / "credentials.json"
        
        if credentials_path.exists():
            try:
                with open(credentials_path, 'r') as f:
                    credentials = json.load(f)
                    self.omie_app_key = self.omie_app_key or credentials.get("app_key", "")
                    self.omie_app_secret = self.omie_app_secret or credentials.get("app_secret", "")
            except Exception as e:
                print(f"Erro ao carregar credenciais: {e}")
    
    def _validate_config(self):
        """Validar configurações obrigatórias"""
        if not self.omie_app_key:
            raise ValueError("OMIE_APP_KEY é obrigatório")
        if not self.omie_app_secret:
            raise ValueError("OMIE_APP_SECRET é obrigatório")
    
    def get_omie_headers(self) -> Dict[str, str]:
        """Obter headers para requisições Omie"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_omie_auth(self) -> Dict[str, str]:
        """Obter dados de autenticação Omie"""
        return {
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter configuração para dicionário (sem credenciais)"""
        return {
            "server_host": self.server_host,
            "server_port": self.server_port,
            "debug": self.debug,
            "log_level": self.log_level,
            "omie_base_url": self.omie_base_url,
            "omie_timeout": self.omie_timeout,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
            "has_credentials": bool(self.omie_app_key and self.omie_app_secret)
        }

# Instância global de configuração
config = Config()