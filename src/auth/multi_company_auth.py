#!/usr/bin/env python3
"""
🏢 SISTEMA DE AUTENTICAÇÃO MULTI-EMPRESAS
Gerenciador de múltiplas empresas Omie com isolamento de credenciais
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import uuid

@dataclass
class CompanyCredentials:
    """Credenciais de uma empresa"""
    company_id: str
    company_name: str
    app_key: str
    app_secret: str
    created_at: str
    last_used: Optional[str] = None
    is_active: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ServiceConfig:
    """Configuração de um serviço MCP"""
    service_name: str
    service_id: str
    default_company_id: Optional[str] = None
    allowed_companies: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.allowed_companies is None:
            self.allowed_companies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class MultiCompanyAuthManager:
    """Gerenciador de autenticação multi-empresas"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or "config")
        self.companies_file = self.config_dir / "companies.json"
        self.services_file = self.config_dir / "services.json"
        self.audit_file = self.config_dir / "auth_audit.log"
        
        # Criar diretório se não existir
        self.config_dir.mkdir(exist_ok=True)
        
        # Carregar dados
        self.companies = self._load_companies()
        self.services = self._load_services()
    
    def _load_companies(self) -> Dict[str, CompanyCredentials]:
        """Carrega empresas do arquivo"""
        if not self.companies_file.exists():
            return {}
        
        try:
            with open(self.companies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            companies = {}
            for company_id, company_data in data.items():
                companies[company_id] = CompanyCredentials(**company_data)
            
            return companies
        except Exception as e:
            self._log_audit("error", f"Erro ao carregar empresas: {str(e)}")
            return {}
    
    def _load_services(self) -> Dict[str, ServiceConfig]:
        """Carrega serviços do arquivo"""
        if not self.services_file.exists():
            return {}
        
        try:
            with open(self.services_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            services = {}
            for service_id, service_data in data.items():
                services[service_id] = ServiceConfig(**service_data)
            
            return services
        except Exception as e:
            self._log_audit("error", f"Erro ao carregar serviços: {str(e)}")
            return {}
    
    def _save_companies(self):
        """Salva empresas no arquivo"""
        try:
            data = {}
            for company_id, company in self.companies.items():
                data[company_id] = asdict(company)
            
            with open(self.companies_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self._log_audit("error", f"Erro ao salvar empresas: {str(e)}")
            raise
    
    def _save_services(self):
        """Salva serviços no arquivo"""
        try:
            data = {}
            for service_id, service in self.services.items():
                data[service_id] = asdict(service)
            
            with open(self.services_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self._log_audit("error", f"Erro ao salvar serviços: {str(e)}")
            raise
    
    def _log_audit(self, level: str, message: str, company_id: str = None, service_id: str = None):
        """Log de auditoria"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "company_id": company_id,
            "service_id": service_id
        }
        
        try:
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except:
            pass  # Não falhar se não conseguir logar
    
    # ========================================================================
    # GERENCIAMENTO DE EMPRESAS
    # ========================================================================
    
    def add_company(self, company_name: str, app_key: str, app_secret: str, 
                   tags: List[str] = None) -> str:
        """Adiciona nova empresa"""
        company_id = str(uuid.uuid4())
        
        company = CompanyCredentials(
            company_id=company_id,
            company_name=company_name,
            app_key=app_key,
            app_secret=app_secret,
            created_at=datetime.now().isoformat(),
            tags=tags or []
        )
        
        self.companies[company_id] = company
        self._save_companies()
        
        self._log_audit("info", f"Empresa adicionada: {company_name}", company_id)
        return company_id
    
    def update_company(self, company_id: str, **kwargs) -> bool:
        """Atualiza dados da empresa"""
        if company_id not in self.companies:
            return False
        
        company = self.companies[company_id]
        
        # Campos atualizáveis
        updatable_fields = ['company_name', 'app_key', 'app_secret', 'is_active', 'tags']
        
        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(company, field, value)
        
        self._save_companies()
        self._log_audit("info", f"Empresa atualizada: {company.company_name}", company_id)
        return True
    
    def remove_company(self, company_id: str) -> bool:
        """Remove empresa"""
        if company_id not in self.companies:
            return False
        
        company_name = self.companies[company_id].company_name
        
        # Remover de todos os serviços
        for service in self.services.values():
            if company_id in service.allowed_companies:
                service.allowed_companies.remove(company_id)
            if service.default_company_id == company_id:
                service.default_company_id = None
        
        self._save_services()
        
        # Remover empresa
        del self.companies[company_id]
        self._save_companies()
        
        self._log_audit("warning", f"Empresa removida: {company_name}", company_id)
        return True
    
    def list_companies(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Lista empresas"""
        companies = []
        
        for company in self.companies.values():
            if active_only and not company.is_active:
                continue
                
            companies.append({
                "company_id": company.company_id,
                "company_name": company.company_name,
                "is_active": company.is_active,
                "tags": company.tags,
                "created_at": company.created_at,
                "last_used": company.last_used
            })
        
        return companies
    
    # ========================================================================
    # GERENCIAMENTO DE SERVIÇOS
    # ========================================================================
    
    def register_service(self, service_name: str, default_company_id: str = None,
                        allowed_companies: List[str] = None) -> str:
        """Registra novo serviço MCP"""
        service_id = f"{service_name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
        
        service = ServiceConfig(
            service_name=service_name,
            service_id=service_id,
            default_company_id=default_company_id,
            allowed_companies=allowed_companies or []
        )
        
        self.services[service_id] = service
        self._save_services()
        
        self._log_audit("info", f"Serviço registrado: {service_name}", service_id=service_id)
        return service_id
    
    def update_service(self, service_id: str, **kwargs) -> bool:
        """Atualiza configuração do serviço"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        updatable_fields = ['service_name', 'default_company_id', 'allowed_companies']
        
        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(service, field, value)
        
        self._save_services()
        self._log_audit("info", f"Serviço atualizado: {service.service_name}", service_id=service_id)
        return True
    
    def get_service_auth(self, service_id: str, company_id: str = None) -> Optional[Dict[str, str]]:
        """Obtém credenciais de autenticação para um serviço"""
        if service_id not in self.services:
            self._log_audit("error", f"Serviço não encontrado: {service_id}", service_id=service_id)
            return None
        
        service = self.services[service_id]
        
        # Determinar qual empresa usar
        target_company_id = company_id or service.default_company_id
        
        if not target_company_id:
            self._log_audit("error", f"Nenhuma empresa especificada para o serviço", service_id=service_id)
            return None
        
        # Verificar se empresa existe e está ativa
        if target_company_id not in self.companies:
            self._log_audit("error", f"Empresa não encontrada: {target_company_id}", 
                          company_id=target_company_id, service_id=service_id)
            return None
        
        company = self.companies[target_company_id]
        
        if not company.is_active:
            self._log_audit("warning", f"Empresa inativa: {company.company_name}", 
                          company_id=target_company_id, service_id=service_id)
            return None
        
        # Verificar permissões do serviço
        if service.allowed_companies and target_company_id not in service.allowed_companies:
            self._log_audit("warning", f"Empresa não autorizada para o serviço", 
                          company_id=target_company_id, service_id=service_id)
            return None
        
        # Atualizar último uso
        company.last_used = datetime.now().isoformat()
        self._save_companies()
        
        self._log_audit("info", f"Credenciais fornecidas para {service.service_name}", 
                      company_id=target_company_id, service_id=service_id)
        
        return {
            "app_key": company.app_key,
            "app_secret": company.app_secret,
            "company_name": company.company_name,
            "company_id": company.company_id
        }
    
    # ========================================================================
    # UTILITÁRIOS
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        active_companies = len([c for c in self.companies.values() if c.is_active])
        total_companies = len(self.companies)
        
        return {
            "total_companies": total_companies,
            "active_companies": active_companies,
            "total_services": len(self.services),
            "config_dir": str(self.config_dir),
            "files": {
                "companies": self.companies_file.exists(),
                "services": self.services_file.exists(),
                "audit": self.audit_file.exists()
            }
        }
    
    def export_config(self) -> Dict[str, Any]:
        """Exporta configuração completa (sem credenciais sensíveis)"""
        companies_export = []
        for company in self.companies.values():
            companies_export.append({
                "company_id": company.company_id,
                "company_name": company.company_name,
                "is_active": company.is_active,
                "tags": company.tags,
                "created_at": company.created_at,
                "last_used": company.last_used,
                "has_credentials": bool(company.app_key and company.app_secret)
            })
        
        services_export = []
        for service in self.services.values():
            services_export.append(asdict(service))
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "companies": companies_export,
            "services": services_export,
            "status": self.get_status()
        }

# ============================================================================
# INTEGRAÇÃO COM OMIE MCP
# ============================================================================

class OmieMCPAuthIntegration:
    """Integração do sistema de auth com Omie MCP"""
    
    def __init__(self, auth_manager: MultiCompanyAuthManager):
        self.auth_manager = auth_manager
        self.current_service_id = None
    
    def setup_omie_mcp_service(self) -> str:
        """Configura o serviço omie-mcp"""
        service_id = self.auth_manager.register_service(
            service_name="omie-mcp",
            default_company_id=None,
            allowed_companies=[]
        )
        
        self.current_service_id = service_id
        return service_id
    
    def get_omie_client_auth(self, company_id: str = None) -> Optional[Dict[str, str]]:
        """Obtém credenciais para OmieClient"""
        if not self.current_service_id:
            self.setup_omie_mcp_service()
        
        return self.auth_manager.get_service_auth(self.current_service_id, company_id)
    
    def list_available_companies(self) -> List[Dict[str, Any]]:
        """Lista empresas disponíveis para omie-mcp"""
        return self.auth_manager.list_companies(active_only=True)

# ============================================================================
# CLI PARA GERENCIAMENTO
# ============================================================================

def main():
    """Interface CLI para gerenciamento"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador Multi-Company Auth")
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Adicionar empresa
    add_parser = subparsers.add_parser('add-company', help='Adicionar empresa')
    add_parser.add_argument('name', help='Nome da empresa')
    add_parser.add_argument('app_key', help='App Key Omie')
    add_parser.add_argument('app_secret', help='App Secret Omie')
    add_parser.add_argument('--tags', nargs='*', help='Tags da empresa')
    
    # Listar empresas
    subparsers.add_parser('list-companies', help='Listar empresas')
    
    # Registrar serviço
    service_parser = subparsers.add_parser('add-service', help='Registrar serviço')
    service_parser.add_argument('name', help='Nome do serviço')
    service_parser.add_argument('--default-company', help='Empresa padrão')
    
    # Status
    subparsers.add_parser('status', help='Status do sistema')
    
    args = parser.parse_args()
    
    auth_manager = MultiCompanyAuthManager()
    
    if args.command == 'add-company':
        company_id = auth_manager.add_company(
            args.name, args.app_key, args.app_secret, args.tags
        )
        print(f"✅ Empresa adicionada: {company_id}")
    
    elif args.command == 'list-companies':
        companies = auth_manager.list_companies()
        print("🏢 Empresas cadastradas:")
        for company in companies:
            print(f"  • {company['company_name']} ({company['company_id']})")
    
    elif args.command == 'add-service':
        service_id = auth_manager.register_service(args.name)
        print(f"✅ Serviço registrado: {service_id}")
    
    elif args.command == 'status':
        status = auth_manager.get_status()
        print("📊 Status do sistema:")
        print(f"  • Empresas: {status['active_companies']}/{status['total_companies']}")
        print(f"  • Serviços: {status['total_services']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()