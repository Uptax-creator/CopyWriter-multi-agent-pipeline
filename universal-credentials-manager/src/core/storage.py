"""
💾 Sistema de Armazenamento Universal
Persistência JSON segura para múltiplos projetos
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from .encryption import multi_project_encryption
from .credentials import BaseCredentials, CredentialsFactory

logger = logging.getLogger("storage")

class ProjectStorage:
    """Armazenamento para um projeto específico"""
    
    def __init__(self, project_name: str, config_dir: str = "config/projects"):
        self.project_name = project_name
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / f"{project_name}.json"
        self.encryptor = multi_project_encryption.get_encryptor(project_name)
        self.companies: Dict[str, BaseCredentials] = {}
        self.metadata: Dict[str, Any] = {}
        
        # Criar diretório se não existir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar dados existentes
        self._load_project_data()
    
    def _load_project_data(self):
        """Carrega dados do projeto"""
        try:
            if not self.config_file.exists():
                logger.info(f"📁 Arquivo de projeto não encontrado: {self.config_file}")
                self._create_default_structure()
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Carregar metadados
            self.metadata = data.get("metadata", {})
            
            # Carregar empresas
            companies_data = data.get("companies", {})
            
            for company_key, company_info in companies_data.items():
                try:
                    # Descriptografar dados sensíveis
                    if "credentials_encrypted" in company_info:
                        sensitive_data = self.encryptor.decrypt_data(
                            company_info["credentials_encrypted"]
                        )
                        
                        # Mesclar dados sensíveis com não sensíveis
                        complete_data = {**company_info, **sensitive_data}
                        del complete_data["credentials_encrypted"]
                    else:
                        # Formato antigo sem criptografia
                        complete_data = company_info
                    
                    # Detectar tipo de credencial e criar instância
                    credential_type = complete_data.get(
                        "credential_type", 
                        CredentialsFactory.detect_credential_type(complete_data)
                    )
                    
                    credentials = CredentialsFactory.create_credentials(
                        credential_type, complete_data
                    )
                    
                    self.companies[company_key] = credentials
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao carregar empresa {company_key}: {e}")
                    continue
            
            logger.info(f"✅ Projeto {self.project_name} carregado: {len(self.companies)} empresas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar projeto {self.project_name}: {e}")
            raise
    
    def _create_default_structure(self):
        """Cria estrutura padrão do projeto"""
        default_data = {
            "version": "1.0",
            "project_name": self.project_name,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "credential_type": "auto-detect",
                "encryption_enabled": True,
                "default_company": None
            },
            "companies": {},
            "security": {
                "auto_refresh_tokens": True,
                "log_access_attempts": True,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        self.metadata = default_data["metadata"]
        
        logger.info(f"📄 Estrutura padrão criada para projeto: {self.project_name}")
    
    def _save_project_data(self):
        """Salva dados do projeto"""
        try:
            companies_data = {}
            
            for company_key, credentials in self.companies.items():
                # Separar dados sensíveis dos não sensíveis
                complete_data = credentials.to_dict()
                sensitive_fields = credentials.get_sensitive_fields()
                
                # Dados sensíveis para criptografar
                sensitive_data = {
                    field: complete_data[field] 
                    for field in sensitive_fields 
                    if field in complete_data
                }
                
                # Dados não sensíveis
                non_sensitive_data = {
                    key: value 
                    for key, value in complete_data.items() 
                    if key not in sensitive_fields
                }
                
                # Adicionar tipo de credencial para facilitar carregamento
                non_sensitive_data["credential_type"] = credentials.__class__.__name__.replace("Credentials", "").lower()
                
                # Criptografar dados sensíveis
                if sensitive_data:
                    non_sensitive_data["credentials_encrypted"] = self.encryptor.encrypt_data(sensitive_data)
                
                companies_data[company_key] = non_sensitive_data
            
            # Estrutura completa do arquivo
            project_data = {
                "version": "1.0",
                "project_name": self.project_name,
                "metadata": {
                    **self.metadata,
                    "last_updated": datetime.now().isoformat(),
                    "companies_count": len(self.companies)
                },
                "companies": companies_data,
                "security": {
                    "auto_refresh_tokens": True,
                    "log_access_attempts": True,
                    "max_failed_attempts": 5,
                    "lockout_duration_minutes": 30
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Projeto {self.project_name} salvo com segurança")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar projeto {self.project_name}: {e}")
            raise
    
    def get_company_list(self) -> List[Dict[str, Any]]:
        """Lista empresas do projeto"""
        return [
            {
                "key": company_key,
                "name": credentials.name,
                "active": credentials.active,
                "security_level": credentials.security_level,
                "token_expired": credentials.is_token_expired(),
                "has_credentials": credentials.is_valid(),
                "credential_type": credentials.__class__.__name__.replace("Credentials", "").lower(),
                "created_at": credentials.created_at.isoformat() if credentials.created_at else None,
                "updated_at": credentials.updated_at.isoformat() if credentials.updated_at else None
            }
            for company_key, credentials in self.companies.items()
        ]
    
    def get_credentials(self, company_key: str) -> BaseCredentials:
        """Obtém credenciais de uma empresa"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada no projeto '{self.project_name}'")
        
        credentials = self.companies[company_key]
        
        if not credentials.is_valid():
            raise ValueError(f"❌ Credenciais inválidas para empresa '{company_key}'")
        
        if not credentials.active:
            raise ValueError(f"❌ Empresa '{company_key}' está desativada")
        
        # Verificar expiração do token
        if credentials.is_token_expired():
            logger.warning(f"⏰ Token expirado para empresa '{company_key}'")
            credentials.refresh_token_expiration()
            self._save_project_data()
            logger.info(f"🔄 Token renovado para empresa '{company_key}'")
        
        # Log de acesso
        self._log_access_attempt(company_key, credentials.name, "SUCCESS")
        
        return credentials
    
    def add_company(self, company_key: str, credentials: BaseCredentials):
        """Adiciona nova empresa"""
        if company_key in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' já existe no projeto '{self.project_name}'")
        
        self.companies[company_key] = credentials
        self._save_project_data()
        
        logger.info(f"➕ Empresa '{company_key}' adicionada ao projeto '{self.project_name}'")
    
    def update_company(self, company_key: str, credentials: BaseCredentials):
        """Atualiza empresa existente"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada no projeto '{self.project_name}'")
        
        self.companies[company_key] = credentials
        self._save_project_data()
        
        logger.info(f"✏️ Empresa '{company_key}' atualizada no projeto '{self.project_name}'")
    
    def delete_company(self, company_key: str):
        """Remove empresa"""
        if company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada no projeto '{self.project_name}'")
        
        del self.companies[company_key]
        self._save_project_data()
        
        logger.warning(f"🗑️ Empresa '{company_key}' removida do projeto '{self.project_name}'")
    
    def set_default_company(self, company_key: Optional[str]):
        """Define empresa padrão"""
        if company_key and company_key not in self.companies:
            raise ValueError(f"❌ Empresa '{company_key}' não encontrada")
        
        self.metadata["default_company"] = company_key
        self._save_project_data()
        
        logger.info(f"🏢 Empresa padrão do projeto '{self.project_name}': {company_key}")
    
    def get_default_company(self) -> Optional[str]:
        """Obtém empresa padrão"""
        return self.metadata.get("default_company")
    
    def _log_access_attempt(self, company_key: str, company_name: str, status: str):
        """Log estruturado para auditoria"""
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "event": "credential_access",
            "project": self.project_name,
            "company_key": company_key,
            "company_name": company_name,
            "status": status
        }
        
        logger.info(f"🔍 AUDIT: {json.dumps(audit_data)}")

class UniversalStorage:
    """Gerenciador de armazenamento para múltiplos projetos"""
    
    def __init__(self, config_dir: str = "config/projects"):
        self.config_dir = Path(config_dir)
        self.projects: Dict[str, ProjectStorage] = {}
        
        # Criar diretório se não existir
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_project(self, project_name: str) -> ProjectStorage:
        """Obtém ou cria projeto"""
        if project_name not in self.projects:
            self.projects[project_name] = ProjectStorage(project_name, str(self.config_dir))
        
        return self.projects[project_name]
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos os projetos"""
        projects = []
        
        # Buscar arquivos de projeto existentes
        for config_file in self.config_dir.glob("*.json"):
            project_name = config_file.stem
            
            try:
                project = self.get_project(project_name)
                
                projects.append({
                    "name": project_name,
                    "companies_count": len(project.companies),
                    "config_file": str(config_file),
                    "created_at": project.metadata.get("created_at"),
                    "last_updated": project.metadata.get("last_updated")
                })
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar projeto {project_name}: {e}")
                continue
        
        return projects
    
    def delete_project(self, project_name: str):
        """Remove projeto completamente"""
        if project_name in self.projects:
            del self.projects[project_name]
        
        config_file = self.config_dir / f"{project_name}.json"
        if config_file.exists():
            config_file.unlink()
            logger.warning(f"🗑️ Projeto '{project_name}' removido")

# Instância global
universal_storage = UniversalStorage()