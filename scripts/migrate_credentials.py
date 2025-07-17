#!/usr/bin/env python3
"""
🔄 Script de Migração de Credenciais
Migra do formato antigo (credentials.json) para o novo formato seguro
"""

import json
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.security.secure_credentials import SecureCredentialsManager

class CredentialsMigrator:
    """Migrador de credenciais"""
    
    def __init__(self):
        self.old_file = PROJECT_ROOT / "credentials.json"
        self.new_file = PROJECT_ROOT / "credentials_secure.json"
        self.backup_dir = PROJECT_ROOT / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def create_backup(self):
        """Cria backup do arquivo antigo"""
        try:
            if not self.old_file.exists():
                self.log("❌ Arquivo credentials.json não encontrado", "ERROR")
                return False
            
            # Criar diretório de backup
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivo original
            backup_file = self.backup_dir / "credentials.json"
            shutil.copy2(self.old_file, backup_file)
            
            self.log(f"✅ Backup criado: {backup_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao criar backup: {e}", "ERROR")
            return False
    
    def load_old_credentials(self) -> dict:
        """Carrega credenciais do formato antigo"""
        try:
            with open(self.old_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.log("📖 Credenciais antigas carregadas")
            return data
            
        except Exception as e:
            self.log(f"❌ Erro ao carregar credenciais antigas: {e}", "ERROR")
            return {}
    
    def convert_to_new_format(self, old_data: dict) -> dict:
        """Converte dados para o novo formato"""
        
        # Se já está no formato multi-empresa
        if "companies" in old_data:
            self.log("📋 Dados já estão em formato multi-empresa")
            return old_data
        
        # Converter formato simples para multi-empresa
        company_data = {
            "name": old_data.get("company_name", "Empresa Principal"),
            "app_key": old_data.get("app_key", ""),
            "app_secret": old_data.get("app_secret", ""),
            "base_url": old_data.get("base_url", "https://app.omie.com.br/api/v1/"),
            "active": True,
            "security_level": "standard",
            "token_timeout_minutes": 60
        }
        
        new_data = {
            "companies": {
                "empresa_principal": company_data
            },
            "default_company": "empresa_principal",
            "security": {
                "auto_refresh_tokens": True,
                "log_access_attempts": True,
                "max_failed_attempts": 3,
                "lockout_duration_minutes": 15,
                "require_company_selection": False
            }
        }
        
        self.log("🔄 Dados convertidos para formato multi-empresa")
        return new_data
    
    def migrate(self) -> bool:
        """Executa a migração completa"""
        self.log("🚀 Iniciando migração de credenciais")
        
        # 1. Verificar se já existe arquivo novo
        if self.new_file.exists():
            self.log("⚠️ Arquivo credentials_secure.json já existe")
            response = input("Deseja sobrescrever? (s/N): ").lower()
            if response != 's':
                self.log("❌ Migração cancelada pelo usuário")
                return False
        
        # 2. Criar backup
        if not self.create_backup():
            return False
        
        # 3. Carregar dados antigos
        old_data = self.load_old_credentials()
        if not old_data:
            return False
        
        # 4. Converter para novo formato
        new_data = self.convert_to_new_format(old_data)
        
        # 5. Criar novo gerenciador e adicionar empresas
        try:
            manager = SecureCredentialsManager(str(self.new_file))
            
            # Adicionar empresas
            for company_key, company_data in new_data["companies"].items():
                manager.add_company(company_key, company_data)
            
            # Definir empresa padrão
            if new_data.get("default_company"):
                manager.set_default_company(new_data["default_company"])
            
            # Configurações de segurança
            manager.security_config = new_data.get("security", {})
            manager._save_credentials()
            
            self.log("✅ Migração concluída com sucesso!")
            self.log(f"📁 Novo arquivo: {self.new_file}")
            self.log(f"📦 Backup: {self.backup_dir}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro durante migração: {e}", "ERROR")
            return False
    
    def verify_migration(self) -> bool:
        """Verifica se a migração foi bem-sucedida"""
        try:
            manager = SecureCredentialsManager(str(self.new_file))
            companies = manager.get_company_list()
            
            self.log("🔍 Verificando migração...")
            self.log(f"📊 Empresas encontradas: {len(companies)}")
            
            for company in companies:
                status = "✅" if company["has_credentials"] else "❌"
                self.log(f"  {status} {company['name']} ({company['key']})")
            
            return len(companies) > 0
            
        except Exception as e:
            self.log(f"❌ Erro na verificação: {e}", "ERROR")
            return False

def main():
    """Função principal"""
    print("🔒 MIGRADOR DE CREDENCIAIS OMIE-MCP")
    print("="*50)
    
    migrator = CredentialsMigrator()
    
    try:
        # Executar migração
        if migrator.migrate():
            # Verificar resultado
            if migrator.verify_migration():
                print("\n🎉 MIGRAÇÃO REALIZADA COM SUCESSO!")
                print(f"👉 Configure a variável de ambiente:")
                print(f"   export OMIE_MASTER_PASSWORD='sua-senha-segura'")
                print(f"👉 Use o novo arquivo: credentials_secure.json")
                return 0
            else:
                print("\n❌ Falha na verificação da migração")
                return 1
        else:
            print("\n❌ Falha na migração")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Migração interrompida pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())