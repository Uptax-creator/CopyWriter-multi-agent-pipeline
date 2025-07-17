#!/usr/bin/env python3
"""
Monitor de Saúde do Nibo MCP Server
Monitora continuamente o status do serviço e detecta problemas
"""
import asyncio
import json
import sys
import os
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

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

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class HealthMonitor:
    def __init__(self, interval: int = 30):
        self.interval = interval
        self.running = True
        self.checks_performed = 0
        self.start_time = datetime.now()
        self.health_history = []
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Colors.YELLOW}🛑 Recebido sinal de interrupção. Finalizando monitor...{Colors.END}")
        self.running = False
        
    def setup_signal_handlers(self):
        """Configure signal handlers"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    async def check_api_health(self) -> Dict:
        """Verifica saúde da API"""
        try:
            from src.core.config import NiboConfig
            from src.core.nibo_client import NiboClient
            
            config = NiboConfig()
            client = NiboClient(config)
            
            start_time = time.time()
            result = await client.testar_conexao()
            response_time = (time.time() - start_time) * 1000
            
            if result.get('success'):
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "message": "API respondendo normalmente"
                }
            else:
                return {
                    "status": "unhealthy", 
                    "response_time_ms": response_time,
                    "message": result.get('message', 'API não respondeu')
                }
                
        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": 0,
                "message": f"Erro ao conectar: {e}"
            }

    async def check_tools_sample(self) -> Dict:
        """Verifica amostra de ferramentas"""
        try:
            from src.core.config import NiboConfig
            from src.core.nibo_client import NiboClient
            from src.tools.consultas import NiboConsultas
            
            config = NiboConfig()
            client = NiboClient(config)
            consultas = NiboConsultas(client)
            
            # Testar amostra de ferramentas
            tools_to_test = [
                ("categorias", consultas.consultar_categorias),
                ("fornecedores", consultas.consultar_fornecedores),
            ]
            
            results = {}
            for tool_name, tool_func in tools_to_test:
                try:
                    start_time = time.time()
                    result = await tool_func(registros_por_pagina=1)
                    response_time = (time.time() - start_time) * 1000
                    
                    if isinstance(result, dict) and ('items' in result or 'count' in result):
                        results[tool_name] = {
                            "status": "healthy",
                            "response_time_ms": response_time
                        }
                    else:
                        results[tool_name] = {
                            "status": "warning",
                            "response_time_ms": response_time,
                            "message": "Resposta inesperada"
                        }
                except Exception as e:
                    results[tool_name] = {
                        "status": "error",
                        "response_time_ms": 0,
                        "message": str(e)
                    }
            
            # Avaliar resultado geral
            healthy_count = len([r for r in results.values() if r['status'] == 'healthy'])
            total_count = len(results)
            
            if healthy_count == total_count:
                overall_status = "healthy"
            elif healthy_count > total_count / 2:
                overall_status = "warning"
            else:
                overall_status = "error"
            
            return {
                "status": overall_status,
                "tools_tested": total_count,
                "tools_healthy": healthy_count,
                "details": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao testar ferramentas: {e}"
            }

    def check_system_resources(self) -> Dict:
        """Verifica recursos do sistema"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Avaliar status
            warnings = []
            if cpu_percent > 80:
                warnings.append(f"CPU alta: {cpu_percent}%")
            if memory_percent > 80:
                warnings.append(f"Memória alta: {memory_percent}%")
            if disk_percent > 90:
                warnings.append(f"Disco cheio: {disk_percent}%")
            
            status = "error" if any("alta" in w or "cheio" in w for w in warnings) else "warning" if warnings else "healthy"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "warnings": warnings
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil não instalado - recursos não monitorados"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao verificar recursos: {e}"
            }

    def check_credentials_expiry(self) -> Dict:
        """Verifica expiração de credenciais"""
        try:
            from src.core.config import NiboConfig
            
            config = NiboConfig()
            company = config.current_company
            
            if not company:
                return {
                    "status": "error",
                    "message": "Empresa não configurada"
                }
            
            if company.token_expires_at:
                now = datetime.now()
                expires_at = company.token_expires_at
                time_left = expires_at - now
                
                if time_left.total_seconds() < 0:
                    return {
                        "status": "error",
                        "message": "Token expirado",
                        "expired_since": abs(time_left.total_seconds())
                    }
                elif time_left.total_seconds() < 3600:  # 1 hora
                    return {
                        "status": "warning",
                        "message": f"Token expira em {time_left.total_seconds()//60:.0f} minutos",
                        "expires_in_seconds": time_left.total_seconds()
                    }
                else:
                    return {
                        "status": "healthy",
                        "message": f"Token válido por {time_left.days} dia(s)",
                        "expires_in_seconds": time_left.total_seconds()
                    }
            else:
                return {
                    "status": "healthy", 
                    "message": "Token sem expiração configurada"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao verificar credenciais: {e}"
            }

    async def perform_health_check(self) -> Dict:
        """Executa verificação completa de saúde"""
        check_time = datetime.now()
        
        print(f"🔍 {Colors.BLUE}Verificação de saúde - {check_time.strftime('%H:%M:%S')}{Colors.END}")
        
        # Executar verificações
        api_health = await self.check_api_health()
        tools_health = await self.check_tools_sample()
        system_health = self.check_system_resources()
        credentials_health = self.check_credentials_expiry()
        
        # Determinar status geral
        all_checks = [api_health, tools_health, system_health, credentials_health]
        error_count = len([c for c in all_checks if c.get('status') == 'error'])
        warning_count = len([c for c in all_checks if c.get('status') == 'warning'])
        
        if error_count > 0:
            overall_status = "error"
            overall_message = f"{error_count} erro(s) crítico(s)"
        elif warning_count > 0:
            overall_status = "warning"
            overall_message = f"{warning_count} aviso(s)"
        else:
            overall_status = "healthy"
            overall_message = "Todos os sistemas operacionais"
        
        health_result = {
            "timestamp": check_time.isoformat(),
            "overall_status": overall_status,
            "overall_message": overall_message,
            "checks": {
                "api": api_health,
                "tools": tools_health,
                "system": system_health,
                "credentials": credentials_health
            }
        }
        
        # Mostrar resultado
        status_icon = "✅" if overall_status == "healthy" else "⚠️" if overall_status == "warning" else "❌"
        status_color = Colors.GREEN if overall_status == "healthy" else Colors.YELLOW if overall_status == "warning" else Colors.RED
        
        print(f"  {status_icon} {status_color}Status: {overall_message}{Colors.END}")
        
        # Mostrar detalhes de problemas
        for check_name, check_result in health_result["checks"].items():
            if check_result.get("status") != "healthy":
                icon = "⚠️" if check_result.get("status") == "warning" else "❌"
                print(f"    {icon} {check_name}: {check_result.get('message', 'Problema detectado')}")
        
        return health_result

    def save_health_log(self, health_result: Dict):
        """Salva log de saúde"""
        log_file = Path("health_monitor.log")
        
        log_entry = {
            "timestamp": health_result["timestamp"],
            "status": health_result["overall_status"],
            "message": health_result["overall_message"],
            "details": health_result["checks"]
        }
        
        # Append to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Manter histórico em memória (últimas 24 horas)
        self.health_history.append(health_result)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.health_history = [
            h for h in self.health_history 
            if datetime.fromisoformat(h["timestamp"]) > cutoff_time
        ]

    def print_statistics(self):
        """Imprime estatísticas do monitoramento"""
        uptime = datetime.now() - self.start_time
        
        if len(self.health_history) > 0:
            healthy_count = len([h for h in self.health_history if h["overall_status"] == "healthy"])
            uptime_percentage = (healthy_count / len(self.health_history)) * 100
        else:
            uptime_percentage = 0
        
        print(f"\n{Colors.CYAN}📊 Estatísticas do Monitor:{Colors.END}")
        print(f"  • Tempo ativo: {uptime}")
        print(f"  • Verificações realizadas: {self.checks_performed}")
        print(f"  • Uptime (24h): {uptime_percentage:.1f}%")
        print(f"  • Histórico: {len(self.health_history)} entradas")

    async def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              MONITOR DE SAÚDE - NIBO MCP SERVER             ║")
        print("║                        v2.0.0                                ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        print(f"🚀 {Colors.GREEN}Monitor iniciado - verificações a cada {self.interval}s{Colors.END}")
        print(f"💡 {Colors.YELLOW}Pressione Ctrl+C para parar{Colors.END}")
        
        self.setup_signal_handlers()
        
        while self.running:
            try:
                # Executar verificação de saúde
                health_result = await self.perform_health_check()
                self.save_health_log(health_result)
                self.checks_performed += 1
                
                # Aguardar próxima verificação
                for _ in range(self.interval):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"❌ {Colors.RED}Erro durante monitoramento: {e}{Colors.END}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
        
        # Mostrar estatísticas finais
        self.print_statistics()
        print(f"🛑 {Colors.YELLOW}Monitor finalizado{Colors.END}")

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de Saúde do Nibo MCP Server")
    parser.add_argument("--interval", "-i", type=int, default=30,
                       help="Intervalo entre verificações em segundos (padrão: 30)")
    parser.add_argument("--once", action="store_true",
                       help="Executar apenas uma verificação")
    
    args = parser.parse_args()
    
    try:
        monitor = HealthMonitor(interval=args.interval)
        
        if args.once:
            # Executar apenas uma verificação
            health_result = await monitor.perform_health_check()
            print(f"\n💾 {Colors.BLUE}Resultado salvo no log{Colors.END}")
            
            # Código de saída baseado no status
            if health_result["overall_status"] == "error":
                sys.exit(1)
            elif health_result["overall_status"] == "warning":
                sys.exit(2)
            else:
                sys.exit(0)
        else:
            # Monitoramento contínuo
            await monitor.run_continuous_monitoring()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Monitor interrompido pelo usuário{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}💥 Erro crítico no monitor: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())