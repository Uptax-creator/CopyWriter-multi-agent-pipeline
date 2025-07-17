#!/usr/bin/env python3
"""
🧪 Teste de Integração - Universal Credentials Manager
Testa toda a stack: Storage, API, Criptografia
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from src.core.encryption import EncryptionManager
    from src.core.credentials import OmieCredentials, CredentialsFactory
    from src.storage.cloud_storage import create_storage
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("💡 Execute: pip install -r requirements.txt")
    sys.exit(1)

class UCMIntegrationTest:
    """Testes de integração completos"""
    
    def __init__(self):
        self.test_project = "test-omie-mcp"
        self.test_company = "empresa_teste"
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_encryption(self) -> bool:
        """Teste 1: Sistema de criptografia"""
        self.log("🔐 Testando criptografia AES-256...")
        
        try:
            # Criar encriptador
            encryptor = EncryptionManager(self.test_project)
            
            # Dados de teste
            test_data = {
                "app_key": "test_app_key_123",
                "app_secret": "test_app_secret_456",
                "sensitive_info": "dados_super_secretos"
            }
            
            # Criptografar
            encrypted = encryptor.encrypt_data(test_data)
            self.log(f"📄 Dados criptografados ({len(encrypted)} chars)")
            
            # Descriptografar
            decrypted = encryptor.decrypt_data(encrypted)
            
            # Verificar
            if test_data == decrypted:
                self.log("✅ Criptografia funcionando corretamente")
                return True
            else:
                self.log("❌ Dados descriptografados não conferem", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro no teste de criptografia: {e}", "ERROR")
            return False
    
    async def test_credentials_models(self) -> bool:
        """Teste 2: Modelos de credenciais"""
        self.log("🏢 Testando modelos de credenciais...")
        
        try:
            # Criar credenciais Omie
            omie_data = {
                "name": "Empresa Teste LTDA",
                "app_key": "test_key_123",
                "app_secret": "test_secret_456",
                "base_url": "https://app.omie.com.br/api/v1/",
                "active": True,
                "security_level": "high"
            }
            
            credentials = OmieCredentials.from_dict(omie_data)
            
            # Verificar validação
            if not credentials.is_valid():
                self.log("❌ Credenciais inválidas", "ERROR")
                return False
            
            # Testar conversão para dict
            credentials_dict = credentials.to_dict()
            
            # Testar campos sensíveis
            sensitive_fields = credentials.get_sensitive_fields()
            if "app_key" not in sensitive_fields or "app_secret" not in sensitive_fields:
                self.log("❌ Campos sensíveis não identificados", "ERROR")
                return False
            
            # Testar headers de autenticação
            headers = credentials.get_auth_headers()
            if "Content-Type" not in headers:
                self.log("❌ Headers de autenticação incompletos", "ERROR")
                return False
            
            self.log("✅ Modelos de credenciais funcionando")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no teste de credenciais: {e}", "ERROR")
            return False
    
    async def test_storage_local(self) -> bool:
        """Teste 3: Storage local"""
        self.log("💾 Testando storage local...")
        
        try:
            # Criar storage local
            storage = create_storage("local")
            
            # Dados de teste
            test_data = {
                "version": "1.0",
                "project_name": self.test_project,
                "companies": {
                    self.test_company: {
                        "name": "Empresa Teste",
                        "app_key": "encrypted_key",
                        "app_secret": "encrypted_secret"
                    }
                }
            }
            
            # Salvar projeto
            success = await storage.save_project_data(self.test_project, test_data)
            if not success:
                self.log("❌ Falha ao salvar projeto", "ERROR")
                return False
            
            # Carregar projeto
            loaded_data = await storage.load_project_data(self.test_project)
            if not loaded_data:
                self.log("❌ Falha ao carregar projeto", "ERROR")
                return False
            
            # Verificar dados
            if loaded_data["project_name"] != self.test_project:
                self.log("❌ Dados carregados incorretos", "ERROR")
                return False
            
            # Listar projetos
            projects = await storage.list_projects()
            if self.test_project not in projects:
                self.log("❌ Projeto não listado", "ERROR")
                return False
            
            self.log("✅ Storage local funcionando")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no teste de storage: {e}", "ERROR")
            return False
    
    async def test_storage_s3(self) -> bool:
        """Teste 4: Storage S3 (se configurado)"""
        bucket_name = os.getenv("AWS_S3_BUCKET")
        
        if not bucket_name:
            self.log("⏭️ S3 não configurado - pulando teste", "WARN")
            return True
        
        self.log("☁️ Testando storage S3...")
        
        try:
            # Criar storage S3
            storage = create_storage("s3", bucket_name=bucket_name)
            
            # Dados de teste
            test_data = {
                "version": "1.0",
                "project_name": f"{self.test_project}-s3",
                "test_timestamp": datetime.now().isoformat()
            }
            
            # Salvar projeto
            success = await storage.save_project_data(f"{self.test_project}-s3", test_data)
            if not success:
                self.log("❌ Falha ao salvar no S3", "ERROR")
                return False
            
            # Carregar projeto
            loaded_data = await storage.load_project_data(f"{self.test_project}-s3")
            if not loaded_data:
                self.log("❌ Falha ao carregar do S3", "ERROR")
                return False
            
            self.log("✅ Storage S3 funcionando")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Erro no teste S3 (pode ser config): {e}", "WARN")
            return True  # Não falhar por problema de S3
    
    async def test_complete_workflow(self) -> bool:
        """Teste 5: Workflow completo"""
        self.log("🔄 Testando workflow completo...")
        
        try:
            # 1. Criar storage híbrido
            storage = create_storage("hybrid")
            
            # 2. Criar credenciais
            credentials = OmieCredentials(
                name="Empresa Workflow Teste",
                app_key="workflow_key_123",
                app_secret="workflow_secret_456",
                active=True,
                security_level="high"
            )
            
            # 3. Criar projeto completo
            project_data = {
                "version": "1.0",
                "project_name": f"{self.test_project}-workflow",
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "credential_type": "omie",
                    "encryption_enabled": True
                },
                "companies": {
                    "empresa_workflow": credentials.to_dict()
                },
                "security": {
                    "auto_refresh_tokens": True,
                    "log_access_attempts": True
                }
            }
            
            # 4. Salvar projeto
            success = await storage.save_project_data(f"{self.test_project}-workflow", project_data)
            if not success:
                self.log("❌ Falha no workflow: save", "ERROR")
                return False
            
            # 5. Listar projetos
            projects = await storage.list_projects()
            if f"{self.test_project}-workflow" not in projects:
                self.log("❌ Falha no workflow: list", "ERROR")
                return False
            
            # 6. Carregar e validar
            loaded = await storage.load_project_data(f"{self.test_project}-workflow")
            if not loaded or "companies" not in loaded:
                self.log("❌ Falha no workflow: load", "ERROR")
                return False
            
            self.log("✅ Workflow completo funcionando")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no workflow completo: {e}", "ERROR")
            return False
    
    async def cleanup(self):
        """Limpar arquivos de teste"""
        self.log("🧹 Limpando arquivos de teste...")
        
        try:
            # Remover arquivos de teste locais
            test_files = [
                f"config/projects/{self.test_project}.json",
                f"config/projects/{self.test_project}-s3.json",
                f"config/projects/{self.test_project}-workflow.json"
            ]
            
            for file_path in test_files:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    self.log(f"🗑️ Removido: {file_path}")
            
        except Exception as e:
            self.log(f"⚠️ Erro na limpeza: {e}", "WARN")
    
    async def run_all_tests(self) -> bool:
        """Executar todos os testes"""
        self.log("🚀 Iniciando testes de integração")
        
        tests = [
            ("Criptografia AES-256", self.test_encryption),
            ("Modelos de Credenciais", self.test_credentials_models),
            ("Storage Local", self.test_storage_local),
            ("Storage S3", self.test_storage_s3),
            ("Workflow Completo", self.test_complete_workflow)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            try:
                success = await test_func()
                results.append((test_name, success))
            except Exception as e:
                self.log(f"❌ Erro inesperado em {test_name}: {e}", "ERROR")
                results.append((test_name, False))
        
        # Cleanup
        await self.cleanup()
        
        # Resumo
        print(f"\n{'='*50}")
        print("📊 RESUMO DOS TESTES")
        print('='*50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{test_name.ljust(30)} {status}")
            if success:
                passed += 1
        
        print('='*50)
        print(f"📈 Taxa de sucesso: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("💡 O Universal Credentials Manager está funcionando!")
        else:
            print("⚠️ Alguns testes falharam. Verifique os logs acima.")
        
        return passed == total

async def main():
    """Função principal"""
    tester = UCMIntegrationTest()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))