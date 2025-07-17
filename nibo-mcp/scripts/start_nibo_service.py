#!/usr/bin/env python3
"""
Script para inicializar o Nibo MCP Server
Inclui verificações de pré-requisitos, configuração e ativação
"""
import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Imprime banner do Nibo MCP Server"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    NIBO MCP SERVER v2.0                     ║
║              Servidor MCP para Integração Nibo              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def check_python_version():
    """Verifica versão do Python"""
    print(f"{Colors.BLUE}🐍 Verificando versão do Python...{Colors.END}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.RED}❌ Python 3.8+ requerido. Versão atual: {version.major}.{version.minor}{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} - OK{Colors.END}")
    return True

def check_dependencies():
    """Verifica dependências instaladas"""
    print(f"{Colors.BLUE}📦 Verificando dependências...{Colors.END}")
    
    required_packages = [
        'mcp', 'aiohttp', 'pydantic', 'requests', 
        'python-dateutil', 'asyncio', 'typing-extensions'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{Colors.YELLOW}⚠️  Pacotes faltantes: {', '.join(missing_packages)}{Colors.END}")
        print(f"{Colors.BLUE}🔧 Instalando dependências...{Colors.END}")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                         check=True, capture_output=True)
            print(f"{Colors.GREEN}✅ Dependências instaladas com sucesso{Colors.END}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Erro ao instalar dependências: {e}{Colors.END}")
            return False
    
    return True

def check_credentials():
    """Verifica se as credenciais estão configuradas"""
    print(f"{Colors.BLUE}🔐 Verificando credenciais...{Colors.END}")
    
    credentials_file = Path("credentials.json")
    
    if not credentials_file.exists():
        print(f"{Colors.RED}❌ Arquivo credentials.json não encontrado{Colors.END}")
        return False
    
    try:
        with open(credentials_file, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        companies = creds.get('companies', {})
        if not companies:
            print(f"{Colors.RED}❌ Nenhuma empresa configurada em credentials.json{Colors.END}")
            return False
        
        default_company = creds.get('default_company')
        if default_company not in companies:
            print(f"{Colors.RED}❌ Empresa padrão '{default_company}' não encontrada{Colors.END}")
            return False
        
        company_data = companies[default_company]
        required_fields = ['nibo_api_token', 'company_id', 'name']
        
        for field in required_fields:
            if not company_data.get(field):
                print(f"{Colors.RED}❌ Campo obrigatório '{field}' não configurado{Colors.END}")
                return False
        
        print(f"  ✅ Empresa: {company_data['name']}")
        print(f"  ✅ API Token: {'*' * 20}{company_data['nibo_api_token'][-4:]}")
        print(f"  ✅ Company ID: {company_data['company_id'][:8]}...")
        print(f"{Colors.GREEN}✅ Credenciais configuradas corretamente{Colors.END}")
        return True
        
    except json.JSONDecodeError:
        print(f"{Colors.RED}❌ Arquivo credentials.json com formato inválido{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao verificar credenciais: {e}{Colors.END}")
        return False

def test_api_connection():
    """Testa conexão com a API do Nibo"""
    print(f"{Colors.BLUE}🌐 Testando conexão com API do Nibo...{Colors.END}")
    
    try:
        # Importar e testar conexão
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from src.core.config import NiboConfig
        from src.core.nibo_client import NiboClient
        
        config = NiboConfig()
        client = NiboClient(config)
        
        # Executar teste assíncrono
        import asyncio
        result = asyncio.run(client.testar_conexao())
        
        if result.get('success'):
            print(f"{Colors.GREEN}✅ Conexão com API estabelecida com sucesso{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Falha na conexão: {result.get('message')}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao testar conexão: {e}{Colors.END}")
        return False

def start_server():
    """Inicia o servidor MCP"""
    print(f"{Colors.BLUE}🚀 Iniciando Nibo MCP Server...{Colors.END}")
    
    server_file = Path("nibo_mcp_server.py")
    if not server_file.exists():
        print(f"{Colors.RED}❌ Arquivo nibo_mcp_server.py não encontrado{Colors.END}")
        return False
    
    try:
        print(f"{Colors.CYAN}📡 Servidor MCP rodando em modo stdio...{Colors.END}")
        print(f"{Colors.YELLOW}💡 Para parar o servidor, pressione Ctrl+C{Colors.END}")
        print(f"{Colors.WHITE}{'='*60}{Colors.END}")
        
        # Executar servidor
        subprocess.run([sys.executable, "nibo_mcp_server.py"], check=True)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Servidor interrompido pelo usuário{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erro ao executar servidor: {e}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.END}")
        return False

def create_status_file():
    """Cria arquivo de status do serviço"""
    status = {
        "service": "nibo-mcp-server",
        "version": "2.0.0",
        "started_at": datetime.now().isoformat(),
        "platform": platform.system(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "status": "running"
    }
    
    with open("service_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def main():
    """Função principal"""
    print_banner()
    
    print(f"{Colors.PURPLE}🔍 Executando verificações de pré-requisitos...{Colors.END}\n")
    
    # Verificações de pré-requisitos
    checks = [
        ("Versão do Python", check_python_version),
        ("Dependências", check_dependencies), 
        ("Credenciais", check_credentials),
        ("Conexão API", test_api_connection)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            break
        print()
    
    if not all_passed:
        print(f"{Colors.RED}❌ Falha nas verificações. Corrija os problemas antes de continuar.{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}🎉 Todas as verificações passaram!{Colors.END}\n")
    
    # Criar arquivo de status
    create_status_file()
    
    # Iniciar servidor
    if start_server():
        print(f"{Colors.GREEN}✅ Servidor finalizado com sucesso{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Servidor finalizado com erro{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Script interrompido pelo usuário{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}💥 Erro crítico: {e}{Colors.END}")
        sys.exit(1)