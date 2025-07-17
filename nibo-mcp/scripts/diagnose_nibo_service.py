#!/usr/bin/env python3
"""
Script de Diagnóstico Completo do Nibo MCP Server
Executa testes abrangentes e gera relatório detalhado de saúde do serviço
"""
import asyncio
import json
import os
import sys
import platform
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

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

class DiagnosticResult:
    def __init__(self, name: str, status: str, message: str, details: Dict = None):
        self.name = name
        self.status = status  # 'success', 'warning', 'error'
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class NiboDiagnostic:
    def __init__(self):
        self.results: List[DiagnosticResult] = []
        self.start_time = datetime.now()
        
        # Adicionar diretório raiz ao path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def add_result(self, name: str, status: str, message: str, details: Dict = None):
        """Adiciona resultado de diagnóstico"""
        result = DiagnosticResult(name, status, message, details)
        self.results.append(result)
        
        # Print em tempo real
        icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        color = Colors.GREEN if status == "success" else Colors.YELLOW if status == "warning" else Colors.RED
        print(f"  {icon} {color}{name}: {message}{Colors.END}")
        
        if details and status != "success":
            for key, value in details.items():
                print(f"     • {key}: {value}")

    def print_section(self, title: str):
        """Imprime cabeçalho de seção"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
        print(f"🔍 {title.upper()}")
        print(f"{'='*60}{Colors.END}")

    async def diagnose_system_info(self):
        """Diagnóstico de informações do sistema"""
        self.print_section("Informações do Sistema")
        
        try:
            system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture()[0],
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "working_directory": os.getcwd(),
                "timestamp": datetime.now().isoformat()
            }
            
            self.add_result(
                "Sistema Operacional",
                "success",
                f"{system_info['os']} {system_info['architecture']}",
                {"version": system_info['os_version']}
            )
            
            # Verificar versão do Python
            if sys.version_info >= (3, 8):
                self.add_result("Versão Python", "success", system_info['python_version'])
            else:
                self.add_result(
                    "Versão Python", 
                    "error", 
                    f"{system_info['python_version']} (mínimo: 3.8)"
                )
            
            # Verificar espaço em disco
            try:
                disk_usage = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
                if disk_usage.returncode == 0:
                    self.add_result("Espaço em Disco", "success", "Verificado")
                else:
                    self.add_result("Espaço em Disco", "warning", "Não foi possível verificar")
            except:
                self.add_result("Espaço em Disco", "warning", "Não disponível no Windows")
                
        except Exception as e:
            self.add_result("Informações do Sistema", "error", f"Erro: {e}")

    async def diagnose_dependencies(self):
        """Diagnóstico de dependências"""
        self.print_section("Dependências")
        
        required_packages = {
            'mcp': '1.0.0',
            'aiohttp': '3.8.0', 
            'pydantic': '2.0.0',
            'requests': '2.28.0',
            'python-dateutil': '2.8.0',
            'asyncio': None,  # Built-in
            'typing-extensions': '4.0.0'
        }
        
        missing_packages = []
        
        for package, min_version in required_packages.items():
            try:
                if package == 'asyncio':
                    # Built-in module
                    import asyncio
                    self.add_result(f"Pacote {package}", "success", "Built-in do Python")
                else:
                    imported_module = __import__(package.replace('-', '_'))
                    version = getattr(imported_module, '__version__', 'unknown')
                    self.add_result(f"Pacote {package}", "success", f"v{version}")
                    
            except ImportError:
                missing_packages.append(package)
                self.add_result(f"Pacote {package}", "error", "Não instalado")
        
        if missing_packages:
            self.add_result(
                "Dependências Faltantes", 
                "error", 
                f"{len(missing_packages)} pacote(s)",
                {"pacotes": missing_packages}
            )
        else:
            self.add_result("Todas as Dependências", "success", "Instaladas")

    async def diagnose_project_structure(self):
        """Diagnóstico da estrutura do projeto"""
        self.print_section("Estrutura do Projeto")
        
        required_files = [
            "nibo_mcp_server.py",
            "credentials.json",
            "requirements.txt",
            "src/core/config.py",
            "src/core/nibo_client.py",
            "src/tools/consultas.py",
            "src/tools/clientes_fornecedores.py",
            "src/tools/financeiro.py",
            "src/tools/socios.py"
        ]
        
        missing_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                self.add_result(f"Arquivo {file_path}", "success", "Encontrado")
            else:
                missing_files.append(file_path)
                self.add_result(f"Arquivo {file_path}", "error", "Não encontrado")
        
        if not missing_files:
            self.add_result("Estrutura do Projeto", "success", "Completa")

    async def diagnose_credentials(self):
        """Diagnóstico das credenciais"""
        self.print_section("Credenciais")
        
        try:
            credentials_file = Path("credentials.json")
            
            if not credentials_file.exists():
                self.add_result("Arquivo credentials.json", "error", "Não encontrado")
                return
            
            with open(credentials_file, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            # Verificar estrutura básica
            companies = creds.get('companies', {})
            if not companies:
                self.add_result("Empresas Configuradas", "error", "Nenhuma empresa encontrada")
                return
            
            self.add_result("Arquivo credentials.json", "success", "Válido")
            self.add_result("Empresas Configuradas", "success", f"{len(companies)} empresa(s)")
            
            # Verificar empresa padrão
            default_company = creds.get('default_company')
            if default_company and default_company in companies:
                company_data = companies[default_company]
                
                self.add_result("Empresa Padrão", "success", company_data.get('name', default_company))
                
                # Verificar campos obrigatórios
                required_fields = ['nibo_api_token', 'company_id', 'name']
                for field in required_fields:
                    if company_data.get(field):
                        if field == 'nibo_api_token':
                            masked_token = f"{'*' * 20}{company_data[field][-4:]}"
                            self.add_result(f"Campo {field}", "success", masked_token)
                        else:
                            self.add_result(f"Campo {field}", "success", str(company_data[field])[:50])
                    else:
                        self.add_result(f"Campo {field}", "error", "Não configurado")
                
                # Verificar timeout de token
                token_expires = company_data.get('token_expires_at')
                if token_expires:
                    try:
                        expires_dt = datetime.fromisoformat(token_expires)
                        if expires_dt > datetime.now():
                            self.add_result("Token Expiry", "success", f"Válido até {expires_dt.strftime('%d/%m/%Y %H:%M')}")
                        else:
                            self.add_result("Token Expiry", "warning", "Token expirado")
                    except:
                        self.add_result("Token Expiry", "warning", "Data inválida")
                else:
                    self.add_result("Token Expiry", "success", "Sem expiração configurada")
            else:
                self.add_result("Empresa Padrão", "error", f"'{default_company}' não encontrada")
                
        except json.JSONDecodeError:
            self.add_result("Arquivo credentials.json", "error", "JSON inválido")
        except Exception as e:
            self.add_result("Credenciais", "error", f"Erro: {e}")

    async def diagnose_api_connectivity(self):
        """Diagnóstico de conectividade com API"""
        self.print_section("Conectividade API")
        
        try:
            from src.core.config import NiboConfig
            from src.core.nibo_client import NiboClient
            
            config = NiboConfig()
            if not config.is_configured():
                self.add_result("Configuração", "error", "Credenciais não configuradas")
                return
            
            self.add_result("Configuração", "success", "Carregada com sucesso")
            
            # Teste de conectividade
            client = NiboClient(config)
            start_time = time.time()
            result = await client.testar_conexao()
            response_time = (time.time() - start_time) * 1000
            
            if result.get('success'):
                self.add_result(
                    "Conexão API", 
                    "success", 
                    f"Conectado ({response_time:.0f}ms)",
                    {"empresa": config.current_company.name}
                )
            else:
                self.add_result("Conexão API", "error", result.get('message', 'Falha desconhecida'))
                
        except Exception as e:
            self.add_result("Conectividade API", "error", f"Erro: {e}")

    async def diagnose_tools_functionality(self):
        """Diagnóstico das ferramentas do MCP"""
        self.print_section("Funcionalidades das Ferramentas")
        
        try:
            from src.core.config import NiboConfig
            from src.core.nibo_client import NiboClient
            from src.tools.consultas import NiboConsultas
            from src.tools.clientes_fornecedores import NiboClientesFornecedores
            from src.tools.financeiro import NiboFinanceiro
            from src.tools.socios import NiboSocios
            
            config = NiboConfig()
            client = NiboClient(config)
            
            # Teste básico de cada ferramenta
            tools_tests = [
                ("Consultas", NiboConsultas(client).consultar_categorias, {"registros_por_pagina": 1}),
                ("Clientes/Fornecedores", NiboConsultas(client).consultar_fornecedores, {"registros_por_pagina": 1}),
                ("Financeiro", NiboConsultas(client).consultar_contas_pagar, {"registros_por_pagina": 1}),
                ("Sócios", NiboSocios(client).consultar_socios, {"registros_por_pagina": 1}),
            ]
            
            for tool_name, tool_func, params in tools_tests:
                try:
                    start_time = time.time()
                    result = await tool_func(**params)
                    response_time = (time.time() - start_time) * 1000
                    
                    if isinstance(result, dict) and ('items' in result or 'count' in result):
                        count = len(result.get('items', [])) if 'items' in result else result.get('count', 0)
                        self.add_result(
                            f"Ferramenta {tool_name}", 
                            "success", 
                            f"Funcionando ({response_time:.0f}ms)",
                            {"registros": count}
                        )
                    else:
                        self.add_result(f"Ferramenta {tool_name}", "warning", "Resposta inesperada")
                        
                except Exception as e:
                    self.add_result(f"Ferramenta {tool_name}", "error", f"Erro: {e}")
                    
        except Exception as e:
            self.add_result("Ferramentas", "error", f"Erro de inicialização: {e}")

    async def diagnose_performance(self):
        """Diagnóstico de performance"""
        self.print_section("Performance")
        
        try:
            # Teste de importação
            start_time = time.time()
            from src.core.config import NiboConfig
            from src.core.nibo_client import NiboClient
            import_time = (time.time() - start_time) * 1000
            
            if import_time < 1000:
                self.add_result("Tempo de Importação", "success", f"{import_time:.0f}ms")
            elif import_time < 3000:
                self.add_result("Tempo de Importação", "warning", f"{import_time:.0f}ms")
            else:
                self.add_result("Tempo de Importação", "error", f"{import_time:.0f}ms (muito lento)")
            
            # Teste de inicialização
            start_time = time.time()
            config = NiboConfig()
            client = NiboClient(config)
            init_time = (time.time() - start_time) * 1000
            
            if init_time < 500:
                self.add_result("Tempo de Inicialização", "success", f"{init_time:.0f}ms")
            elif init_time < 1500:
                self.add_result("Tempo de Inicialização", "warning", f"{init_time:.0f}ms")
            else:
                self.add_result("Tempo de Inicialização", "error", f"{init_time:.0f}ms (muito lento)")
                
        except Exception as e:
            self.add_result("Performance", "error", f"Erro: {e}")

    def generate_report(self) -> Dict:
        """Gera relatório final"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Estatísticas
        total_tests = len(self.results)
        success_count = len([r for r in self.results if r.status == "success"])
        warning_count = len([r for r in self.results if r.status == "warning"])
        error_count = len([r for r in self.results if r.status == "error"])
        
        # Status geral
        if error_count > 0:
            overall_status = "error"
            overall_message = f"{error_count} erro(s) crítico(s) encontrado(s)"
        elif warning_count > 0:
            overall_status = "warning" 
            overall_message = f"{warning_count} aviso(s) encontrado(s)"
        else:
            overall_status = "success"
            overall_message = "Todos os testes passaram"
        
        report = {
            "diagnostic_info": {
                "version": "2.0.0",
                "service": "nibo-mcp-server",
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "platform": platform.system()
            },
            "summary": {
                "overall_status": overall_status,
                "overall_message": overall_message,
                "total_tests": total_tests,
                "success_count": success_count,
                "warning_count": warning_count,
                "error_count": error_count,
                "success_rate": round((success_count / total_tests) * 100, 1) if total_tests > 0 else 0
            },
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }
        
        return report

    def print_summary(self, report: Dict):
        """Imprime resumo final"""
        summary = report['summary']
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
        print(f"📊 RESUMO DO DIAGNÓSTICO")
        print(f"{'='*60}{Colors.END}")
        
        # Status geral
        status_color = Colors.GREEN if summary['overall_status'] == 'success' else Colors.YELLOW if summary['overall_status'] == 'warning' else Colors.RED
        status_icon = "✅" if summary['overall_status'] == 'success' else "⚠️" if summary['overall_status'] == 'warning' else "❌"
        
        print(f"\n{status_icon} {status_color}{Colors.BOLD}Status Geral: {summary['overall_message']}{Colors.END}")
        
        # Estatísticas
        print(f"\n📈 {Colors.BOLD}Estatísticas:{Colors.END}")
        print(f"  • Total de testes: {summary['total_tests']}")
        print(f"  • {Colors.GREEN}Sucessos: {summary['success_count']}{Colors.END}")
        print(f"  • {Colors.YELLOW}Avisos: {summary['warning_count']}{Colors.END}")
        print(f"  • {Colors.RED}Erros: {summary['error_count']}{Colors.END}")
        print(f"  • Taxa de sucesso: {summary['success_rate']}%")
        
        # Duração
        duration = report['diagnostic_info']['duration_seconds']
        print(f"  • Tempo de execução: {duration:.2f}s")

    async def run_full_diagnostic(self):
        """Executa diagnóstico completo"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           DIAGNÓSTICO COMPLETO - NIBO MCP SERVER            ║")
        print("║                        v2.0.0                                ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        # Executar todos os diagnósticos
        await self.diagnose_system_info()
        await self.diagnose_dependencies()
        await self.diagnose_project_structure()
        await self.diagnose_credentials()
        await self.diagnose_api_connectivity()
        await self.diagnose_tools_functionality()
        await self.diagnose_performance()
        
        # Gerar e salvar relatório
        report = self.generate_report()
        
        report_filename = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Imprimir resumo
        self.print_summary(report)
        
        print(f"\n💾 {Colors.BLUE}Relatório completo salvo em: {report_filename}{Colors.END}")
        
        return report

async def main():
    """Função principal"""
    try:
        diagnostic = NiboDiagnostic()
        report = await diagnostic.run_full_diagnostic()
        
        # Determinar código de saída
        if report['summary']['overall_status'] == 'error':
            sys.exit(1)
        elif report['summary']['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Diagnóstico interrompido pelo usuário{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}💥 Erro crítico durante diagnóstico: {e}{Colors.END}")
        print(f"{Colors.RED}Stack trace: {traceback.format_exc()}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())