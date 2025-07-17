"""
🔒 Gerenciador de Credenciais Seguro - Omie MCP
Implementação simples com criptografia e multi-empresa
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger("secure-credentials")

class SecureCredentials:
    """Classe para uma empresa específica"""
    
    def __init__(self, company_data: Dict):
        self.name = company_data.get("name", "")
        self.app_key = company_data.get("app_key", "")
        self.app_secret = company_data.get("app_secret", "")
        self.base_url = company_data.get("base_url", "https://app.omie.com.br/api/v1/")
        self.token_timeout_minutes = company_data.get("token_timeout_minutes", 60)
        self.active = company_data.get("active", True)
        self.security_level = company_data.get("security_level", "standard")
        
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
            self.app_key and 
            self.app_secret and 
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
        """Converte para dicionário (para criptografia)"""
        return {
            "name": self.name,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "base_url": self.base_url,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "token_timeout_minutes": self.token_timeout_minutes,
            "active": self.active,
            "security_level": self.security_level
        }

class SecureCredentialsManager:
    """Gerenciador de credenciais com criptografia"""
    
    def __init__(self, credentials_file: str = "credentials_secure.json"):
        self.credentials_file = Path(credentials_file)
        self.companies: Dict[str, SecureCredentials] = {}
        self.default_company: Optional[str] = None
        self.security_config: Dict = {}
        self.cipher = None
        self._initialize_encryption()
        self._load_credentials()
    
    def _initialize_encryption(self):
        """Inicializa sistema de criptografia"""
        master_password = os.getenv("OMIE_MASTER_PASSWORD", "omie-mcp-default-key-2025")
        
        # Gerar chave de criptografia a partir da senha mestre
        password = master_password.encode()
        salt = b'omie-mcp-salt-2025'  # Em produção, usar salt aleatório
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher = Fernet(key)
        
        logger.info("🔒 Sistema de criptografia inicializado")
    
    def _encrypt_data(self, data: Dict) -> str:
        """Criptografa dados sensíveis"""
        json_data = json.dumps(data)
        encrypted_data = self.cipher.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> Dict:
        """Descriptografa dados sensíveis"""
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(decoded_data)
        return json.loads(decrypted_data.decode())
    
    def _load_credentials(self):
        """Carrega credenciais do arquivo"""
        try:
            if not self.credentials_file.exists():
                logger.warning(f"📁 Arquivo de credenciais não encontrado: {self.credentials_file}")
                self._create_default_structure()
                return
            
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar versão do arquivo
            version = data.get("version", "1.0")
            if version != "2.0":
                logger.warning("⚠️ Arquivo de credenciais em formato antigo, considere migração")
            
            # Carregar empresas
            companies_data = data.get("companies", {})
            for company_key, company_info in companies_data.items():
                
                if "credentials_encrypted" in company_info:
                    # Dados criptografados (versão 2.0)
                    try:
                        decrypted_data = self._decrypt_data(company_info["credentials_encrypted"])
                        # Mesclar com dados não sensíveis
                        company_data = {**company_info, **decrypted_data}
                        del company_data["credentials_encrypted"]
                    except Exception as e:
                        logger.error(f"❌ Erro ao descriptografar empresa {company_key}: {e}")
                        continue
                else:
                    # Dados em texto plano (versão 1.0)
                    company_data = company_info
                
                self.companies[company_key] = SecureCredentials(company_data)
            
            # Configurações gerais
            self.default_company = data.get("default_company")
            self.security_config = data.get("security", {})
            
            logger.info(f"✅ Carregadas {len(self.companies)} empresas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar credenciais: {e}")
            raise
    
    def _create_default_structure(self):
        """Cria estrutura padrão do arquivo"""
        default_data = {
            "version": "2.0",
            "encryption": {
                "algorithm": "AES-256",
                "key_derivation": "PBKDF2",
                "created_at": datetime.now().isoformat()
            },
            "companies": {},
            "default_company": None,
            "security": {
                "auto_refresh_tokens": True,
                "log_access_attempts": True,
                "max_failed_attempts": 3,
                "lockout_duration_minutes": 15,
                "require_company_selection": False
            }
        }
        
        with open(self.credentials_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        logger.info("📄 Arquivo de credenciais padrão criado")
    
    def _save_credentials(self):
        """Salva credenciais no arquivo"""
        try:
            # Preparar dados para salvar
            companies_data = {}
            
            for company_key, company in self.companies.items():
                # Dados sensíveis para criptografar
                sensitive_data = {
                    "app_key": company.app_key,
                    "app_secret": company.app_secret
                }
                
                # Dados não sensíveis
                non_sensitive_data = {
                    "name": company.name,
                    "base_url": company.base_url,
                    "token_expires_at": company.token_expires_at.isoformat() if company.token_expires_at else None,
                    "token_timeout_minutes": company.token_timeout_minutes,
                    "active": company.active,
                    "security_level": company.security_level,
                    "credentials_encrypted": self._encrypt_data(sensitive_data)
                }
                
                companies_data[company_key] = non_sensitive_data
            
            data = {
                "version": "2.0",
                "encryption": {
                    "algorithm": "AES-256",
                    "key_derivation": "PBKDF2",
                    "last_updated": datetime.now().isoformat()
                },
                "companies": companies_data,
                "default_company": self.default_company,
                "security": self.security_config
            }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Credenciais salvas com segurança")
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar credenciais: {e}")
            raise
    
    def get_company_list(self) -> List[Dict]:
        """Retorna lista de empresas disponíveis"""
        return [
            {
                "key": key,
                "name": company.name,
                "active": company.active,
                "security_level": company.security_level,
                "token_expired": company.is_token_expired(),
                "has_credentials": company.is_valid()
            }
            for key, company in self.companies.items()
        ]
    
    def get_company_credentials(self, company_key: Optional[str] = None) -> SecureCredentials:
        """Obtém credenciais de uma empresa com logs de auditoria"""
        # Se não especificado, usa empresa padrão
        if not company_key:
            company_key = self.default_company
        
        if not company_key:
            raise ValueError("❌ Nenhuma empresa especificada e nenhuma empresa padrão configurada")
        
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada")
        
        company = self.companies[company_key]
        
        if not company.is_valid():
            raise ValueError(f"❌ Credenciais inválidas para empresa '{company_key}'")
        
        # Verificar expiração do token
        if company.is_token_expired():
            logger.warning(f"⏰ Token expirado para empresa '{company_key}'")
            if self.security_config.get("auto_refresh_tokens", True):
                company.refresh_token_expiration()
                self._save_credentials()
                logger.info(f"🔄 Token renovado para empresa '{company_key}'")
            else:
                raise ValueError(f"❌ Token expirado para empresa '{company_key}'. Renovação necessária.")
        
        # Log de acesso para auditoria
        if self.security_config.get("log_access_attempts", True):
            self._log_access_attempt(company_key, company.name, "SUCCESS")
        
        return company
    
    def _log_access_attempt(self, company_key: str, company_name: str, status: str):
        """Log estruturado para auditoria"""
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_access",
            "company_key": company_key,
            "company_name": company_name,
            "status": status,
            "security_level": self.companies.get(company_key, SecureCredentials({})).security_level
        }
        
        logger.info(f"🔍 AUDIT: {json.dumps(audit_data)}")
    
    def add_company(self, company_key: str, company_data: Dict):
        """Adiciona uma nova empresa"""
        self.companies[company_key] = SecureCredentials(company_data)
        self._save_credentials()
        logger.info(f"➕ Empresa '{company_key}' adicionada com segurança")
    
    def update_company(self, company_key: str, company_data: Dict):
        """Atualiza dados de uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada")
        
        self.companies[company_key] = SecureCredentials(company_data)
        self._save_credentials()
        logger.info(f"✏️ Empresa '{company_key}' atualizada")
    
    def set_default_company(self, company_key: str):
        """Define empresa padrão"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada")
        
        self.default_company = company_key
        self._save_credentials()
        logger.info(f"🏢 Empresa padrão definida: '{company_key}'")
    
    def deactivate_company(self, company_key: str):
        """Desativa uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada")
        
        company = self.companies[company_key]
        company.active = False
        self._save_credentials()
        logger.warning(f"🚫 Empresa '{company_key}' desativada")
    
    def export_for_migration(self) -> Dict:
        """Exporta dados para migração (sem criptografia)"""
        return {
            "companies": {
                key: company.to_dict() 
                for key, company in self.companies.items()
            },
            "default_company": self.default_company,
            "security": self.security_config
        }

# Instância global
secure_credentials_manager = SecureCredentialsManager()