#!/usr/bin/env python3
"""
🚀 Setup Universal Credentials Manager
Script de configuração inicial rápida
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def print_banner():
    """Banner do setup"""
    print("=" * 60)
    print("🔒 UNIVERSAL CREDENTIALS MANAGER - SETUP")
    print("=" * 60)
    print()

def create_env_file():
    """Criar arquivo .env a partir do template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  Arquivo .env já existe")
        response = input("Deseja sobrescrever? (s/N): ").lower()
        if response != 's':
            print("📋 Mantendo .env existente")
            return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Arquivo .env criado a partir do template")
    else:
        print("❌ Template .env.example não encontrado")

def create_directories():
    """Criar diretórios necessários"""
    directories = [
        "config/projects",
        "logs",
        "backups",
        "frontend/public",
        "scripts/migrations"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Diretório criado: {directory}")

def create_sample_project():
    """Criar projeto de exemplo"""
    sample_project = {
        "version": "1.0",
        "project_name": "omie-mcp",
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "credential_type": "omie",
            "encryption_enabled": True,
            "default_company": "empresa_exemplo"
        },
        "companies": {
            "empresa_exemplo": {
                "name": "Empresa Exemplo LTDA",
                "credential_type": "omie",
                "base_url": "https://app.omie.com.br/api/v1/",
                "active": True,
                "security_level": "standard",
                "token_timeout_minutes": 60,
                "credentials_encrypted": "EXEMPLO_DADOS_CRIPTOGRAFADOS"
            }
        },
        "security": {
            "auto_refresh_tokens": True,
            "log_access_attempts": True,
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 30
        }
    }
    
    project_file = Path("config/projects/omie-mcp.json")
    
    if project_file.exists():
        print("⚠️  Projeto omie-mcp já existe")
        return
    
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(sample_project, f, indent=2, ensure_ascii=False)
    
    print("✅ Projeto de exemplo criado: omie-mcp")

def setup_aws_s3():
    """Configurar AWS S3 (opcional)"""
    print("\n🌐 CONFIGURAÇÃO AWS S3 (Opcional)")
    print("-" * 40)
    
    response = input("Deseja configurar AWS S3? (s/N): ").lower()
    if response != 's':
        print("📋 Configuração S3 pulada - usando storage local")
        return
    
    bucket_name = input("Nome do bucket S3: ").strip()
    if not bucket_name:
        print("❌ Nome do bucket é obrigatório")
        return
    
    aws_region = input("Região AWS (padrão: us-east-1): ").strip() or "us-east-1"
    
    # Atualizar .env
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Substituir valores
        content = content.replace("STORAGE_TYPE=hybrid", "STORAGE_TYPE=s3")
        content = content.replace("AWS_S3_BUCKET=ucm-credentials-bucket", f"AWS_S3_BUCKET={bucket_name}")
        content = content.replace("AWS_REGION=us-east-1", f"AWS_REGION={aws_region}")
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Configuração S3 salva: {bucket_name} ({aws_region})")
    
    print("\n💡 Próximos passos para S3:")
    print("1. Configure as credenciais AWS:")
    print("   aws configure")
    print("2. Ou defina as variáveis:")
    print("   export AWS_ACCESS_KEY_ID=seu-access-key")
    print("   export AWS_SECRET_ACCESS_KEY=seu-secret-key")

def setup_auth0():
    """Configurar Auth0 (opcional)"""
    print("\n🔐 CONFIGURAÇÃO AUTH0 (Opcional)")
    print("-" * 40)
    
    response = input("Deseja configurar Auth0? (s/N): ").lower()
    if response != 's':
        print("📋 Auth0 pulado - usando modo desenvolvimento")
        return
    
    print("\n📋 Para configurar Auth0:")
    print("1. Crie uma conta gratuita em https://auth0.com")
    print("2. Crie uma Application (Single Page Application)")
    print("3. Crie uma API com identifier: https://ucm-api")
    print("4. Anote os valores e configure no .env")
    
    auth0_domain = input("Auth0 Domain (ex: myapp.auth0.com): ").strip()
    client_id = input("Client ID: ").strip()
    
    if auth0_domain and client_id:
        # Atualizar .env
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            
            content = content.replace("AUTH0_DOMAIN=your-domain.auth0.com", f"AUTH0_DOMAIN={auth0_domain}")
            content = content.replace("AUTH0_CLIENT_ID=your-client-id", f"AUTH0_CLIENT_ID={client_id}")
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Configuração Auth0 salva")

def check_dependencies():
    """Verificar dependências"""
    print("\n🔧 VERIFICANDO DEPENDÊNCIAS")
    print("-" * 40)
    
    # Python
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (mínimo: 3.8)")
        return False
    
    # Docker
    if shutil.which("docker"):
        print("✅ Docker encontrado")
    else:
        print("⚠️  Docker não encontrado (opcional)")
    
    # Docker Compose
    if shutil.which("docker-compose"):
        print("✅ Docker Compose encontrado")
    else:
        print("⚠️  Docker Compose não encontrado (opcional)")
    
    # Node.js (para frontend)
    if shutil.which("node"):
        print("✅ Node.js encontrado")
    else:
        print("⚠️  Node.js não encontrado (necessário para frontend)")
    
    return True

def show_next_steps():
    """Mostrar próximos passos"""
    print("\n🚀 PRÓXIMOS PASSOS")
    print("=" * 60)
    print()
    print("1. 📦 Instalar dependências Python:")
    print("   pip install -r requirements.txt")
    print()
    print("2. 🐳 Iniciar com Docker (recomendado):")
    print("   docker-compose up -d")
    print()
    print("3. 🔧 Ou iniciar manualmente:")
    print("   # API Backend")
    print("   python src/api/server.py")
    print("   ")
    print("   # Frontend (em outro terminal)")
    print("   cd frontend && npm install && npm run dev")
    print()
    print("4. 🌐 Acessar aplicação:")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8100")
    print("   Docs: http://localhost:8100/docs")
    print()
    print("5. 🧪 Testar integração:")
    print("   python scripts/test_integration.py")
    print()
    print("6. 📚 Documentação completa:")
    print("   cat README.md")

def main():
    """Função principal do setup"""
    print_banner()
    
    # Verificar se estamos no diretório correto
    if not Path("requirements.txt").exists():
        print("❌ Execute este script a partir do diretório raiz do projeto")
        sys.exit(1)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências faltando. Verifique a instalação.")
        sys.exit(1)
    
    # Setup básico
    print("\n📋 CONFIGURAÇÃO BÁSICA")
    print("-" * 40)
    
    create_env_file()
    create_directories()
    create_sample_project()
    
    # Configurações opcionais
    setup_aws_s3()
    setup_auth0()
    
    # Próximos passos
    show_next_steps()
    
    print("\n🎉 Setup concluído com sucesso!")
    print("💡 Consulte o README.md para mais detalhes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        sys.exit(1)