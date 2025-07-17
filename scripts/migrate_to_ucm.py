#!/usr/bin/env python3
"""
🔄 Script de Migração Omie-MCP para Universal Credentials Manager
Migra credenciais locais para UCM e testa integração
"""

import asyncio
import sys
import json
import httpx
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

class OmieMCPMigrator:
    """Migrador do Omie-MCP para UCM"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.ucm_url = "http://localhost:8100"
        self.project_name = "omie-mcp"
        self.company_key = "empresa_principal"
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def check_ucm_available(self) -> bool:
        """Verificar se UCM está disponível"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ucm_url}/")
                result = response.json()
                self.log(f"✅ UCM disponível: {result.get('service', 'Unknown')}")
                return True
        except Exception as e:
            self.log(f"❌ UCM não disponível: {e}", "ERROR")
            self.log("💡 Inicie o UCM: cd universal-credentials-manager && python src/api/server.py", "INFO")
            return False
    
    def load_local_credentials(self) -> dict:
        """Carregar credenciais locais"""
        credentials_file = self.project_root / "credentials.json"
        
        if not credentials_file.exists():
            raise FileNotFoundError("Arquivo credentials.json não encontrado")
        
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        self.log(f"📄 Credenciais locais carregadas: {credentials_file}")
        return creds
    
    async def create_ucm_project_data(self, local_creds: dict) -> dict:
        """Criar dados do projeto para UCM"""
        
        project_data = {
            "version": "1.0",
            "project_name": self.project_name,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "credential_type": "omie",
                "encryption_enabled": True,
                "default_company": self.company_key,
                "migrated_from": "credentials.json",
                "migration_date": datetime.now().isoformat()
            },
            "companies": {
                self.company_key: {
                    "name": "Empresa Principal",
                    "app_key": local_creds["app_key"],
                    "app_secret": local_creds["app_secret"],
                    "base_url": local_creds.get("base_url", "https://app.omie.com.br/api/v1"),
                    "active": True,
                    "security_level": "standard",
                    "token_timeout_minutes": 60,
                    "credential_type": "omie"
                }
            },
            "security": {
                "auto_refresh_tokens": True,
                "log_access_attempts": True,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            }
        }
        
        return project_data
    
    async def save_to_ucm_storage(self, project_data: dict) -> bool:
        """Salvar dados diretamente no storage do UCM"""
        try:
            # Importar storage do UCM
            ucm_root = self.project_root / "universal-credentials-manager"
            sys.path.insert(0, str(ucm_root))
            
            from src.storage.cloud_storage import storage
            
            # Salvar projeto
            success = await storage.save_project_data(self.project_name, project_data)
            
            if success:
                self.log(f"✅ Projeto salvo no UCM storage")
                return True
            else:
                self.log(f"❌ Falha ao salvar no UCM storage", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao salvar no UCM: {e}", "ERROR")
            return False
    
    async def test_ucm_integration(self) -> bool:
        """Testar integração com UCM"""
        try:
            # Testar obtenção de credenciais via API
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{self.ucm_url}/api/v1/projects/{self.project_name}/credentials/{self.company_key}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Verificar se credenciais estão presentes
                    if result.get("app_key") and result.get("app_secret"):
                        self.log("✅ Credenciais UCM obtidas via API")
                        self.log(f"📋 Base URL: {result.get('base_url')}")
                        return True
                    else:
                        self.log("❌ Credenciais incompletas na resposta UCM", "ERROR")
                        return False
                else:
                    self.log(f"❌ Erro HTTP {response.status_code} do UCM", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Erro no teste de integração: {e}", "ERROR")
            return False
    
    async def test_omie_api_via_ucm(self) -> bool:
        """Testar chamada real para API Omie via UCM"""
        try:
            # Importar cliente UCM
            from src.client.omie_client_ucm import omie_client_ucm
            
            # Testar conexão UCM
            ucm_connected = await omie_client_ucm.test_ucm_connection()
            if not ucm_connected:
                self.log("❌ Falha na conexão com UCM", "ERROR")
                return False
            
            # Testar chamada simples para Omie
            self.log("🧪 Testando consulta de categorias via UCM...")
            
            result = await omie_client_ucm.consultar_categorias({
                "pagina": 1,
                "registros_por_pagina": 5
            })
            
            if result and "categoria_cadastro" in result:
                categorias = result["categoria_cadastro"]
                self.log(f"✅ API Omie funcionando via UCM: {len(categorias)} categorias")
                return True
            else:
                self.log("❌ Resposta inválida da API Omie", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro no teste Omie via UCM: {e}", "ERROR")
            return False
    
    async def create_backup(self):
        """Criar backup das credenciais locais"""
        try:
            backup_dir = self.project_root / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar credentials.json
            credentials_file = self.project_root / "credentials.json"
            if credentials_file.exists():
                import shutil
                backup_file = backup_dir / "credentials.json"
                shutil.copy2(credentials_file, backup_file)
                self.log(f"💾 Backup criado: {backup_file}")
            
        except Exception as e:
            self.log(f"⚠️ Erro ao criar backup: {e}", "WARN")
    
    async def migrate(self) -> bool:
        """Executar migração completa"""
        self.log("🚀 Iniciando migração Omie-MCP para UCM")
        
        try:
            # 1. Verificar UCM disponível
            if not await self.check_ucm_available():
                return False
            
            # 2. Carregar credenciais locais
            local_creds = self.load_local_credentials()
            
            # 3. Criar backup
            await self.create_backup()
            
            # 4. Preparar dados para UCM
            project_data = await self.create_ucm_project_data(local_creds)
            
            # 5. Salvar no UCM
            if not await self.save_to_ucm_storage(project_data):
                return False
            
            # 6. Testar integração
            if not await self.test_ucm_integration():
                return False
            
            # 7. Testar API Omie via UCM
            if not await self.test_omie_api_via_ucm():
                return False
            
            self.log("🎉 Migração concluída com sucesso!")
            self.log("💡 Agora o Omie-MCP usa Universal Credentials Manager")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro durante migração: {e}", "ERROR")
            return False
    
    async def show_migration_info(self):
        """Mostrar informações da migração"""
        print("\n" + "="*60)
        print("📋 INFORMAÇÕES DA MIGRAÇÃO")
        print("="*60)
        print(f"Projeto: {self.project_name}")
        print(f"Empresa: {self.company_key}")
        print(f"UCM URL: {self.ucm_url}")
        print(f"Credenciais: {self.project_root}/credentials.json")
        print("\n💡 Próximos passos:")
        print("1. Atualizar imports no código para usar omie_client_ucm")
        print("2. Configurar variáveis de ambiente UCM se necessário")
        print("3. Testar todas as ferramentas MCP")
        print("="*60)

async def main():
    """Função principal"""
    migrator = OmieMCPMigrator()
    
    try:
        await migrator.show_migration_info()
        
        # Confirmar migração
        response = input("\nProsseguir com a migração? (s/N): ").lower()
        if response != 's':
            print("❌ Migração cancelada pelo usuário")
            return 1
        
        # Executar migração
        success = await migrator.migrate()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Migração interrompida pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))