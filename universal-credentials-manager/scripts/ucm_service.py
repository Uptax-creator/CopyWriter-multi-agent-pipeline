#!/usr/bin/env python3
"""
🚀 Universal Credentials Manager - Service Manager
Arquivo de ativação/desativação universal para todos os serviços
"""

import os
import sys
import json
import time
import signal
import psutil
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configurações
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_CONFIG = {
    "ucm-api": {
        "name": "Universal Credentials Manager API",
        "command": [sys.executable, "src/api/server.py"],
        "port": 8100,
        "health_url": "http://localhost:8100/",
        "pid_file": "ucm-api.pid",
        "log_file": "logs/ucm-api.log"
    },
    "omie-mcp": {
        "name": "Omie MCP Server", 
        "command": [sys.executable, "../src/server.py"],
        "port": 3000,
        "health_url": None,
        "pid_file": "omie-mcp.pid",
        "log_file": "logs/omie-mcp.log"
    },
    "nibo-mcp": {
        "name": "Nibo MCP Server",
        "command": [sys.executable, "../nibo-mcp/nibo_mcp_server.py"],
        "port": 3001,
        "health_url": None,
        "pid_file": "nibo-mcp.pid", 
        "log_file": "logs/nibo-mcp.log"
    }
}

class ServiceManager:
    """Gerenciador universal de serviços"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.pids_dir = self.project_root / "pids"
        self.logs_dir = self.project_root / "logs"
        
        # Criar diretórios
        self.pids_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def get_pid_file(self, service_name: str) -> Path:
        """Caminho do arquivo PID"""
        return self.pids_dir / SERVICES_CONFIG[service_name]["pid_file"]
    
    def get_log_file(self, service_name: str) -> Path:
        """Caminho do arquivo de log"""
        return self.logs_dir / SERVICES_CONFIG[service_name]["log_file"]
    
    def is_service_running(self, service_name: str) -> bool:
        """Verifica se serviço está rodando"""
        pid_file = self.get_pid_file(service_name)
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificar se processo existe
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                # Verificar se é o processo correto
                cmdline = ' '.join(process.cmdline())
                if any(part in cmdline for part in SERVICES_CONFIG[service_name]["command"]):
                    return True
            
            # PID file inválido, remover
            pid_file.unlink()
            return False
            
        except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def start_service(self, service_name: str) -> bool:
        """Iniciar serviço"""
        if service_name not in SERVICES_CONFIG:
            self.log(f"❌ Serviço desconhecido: {service_name}", "ERROR")
            return False
        
        if self.is_service_running(service_name):
            self.log(f"⚠️ Serviço {service_name} já está rodando")
            return True
        
        config = SERVICES_CONFIG[service_name]
        self.log(f"🚀 Iniciando {config['name']}...")
        
        try:
            # Preparar ambiente
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"
            
            # Criar arquivo de log
            log_file = self.get_log_file(service_name)
            log_file.parent.mkdir(exist_ok=True)
            
            # Iniciar processo
            import subprocess
            
            with open(log_file, 'a') as log_f:
                log_f.write(f"\n=== Iniciado em {datetime.now().isoformat()} ===\n")
                
                process = subprocess.Popen(
                    config["command"],
                    cwd=PROJECT_ROOT,
                    env=env,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
            
            # Salvar PID
            pid_file = self.get_pid_file(service_name)
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Aguardar inicialização
            time.sleep(2)
            
            if self.is_service_running(service_name):
                self.log(f"✅ {config['name']} iniciado (PID: {process.pid})")
                
                # Verificar porta se configurada
                if config.get("port"):
                    if self.check_port(config["port"]):
                        self.log(f"🌐 Porta {config['port']} ativa")
                    else:
                        self.log(f"⚠️ Porta {config['port']} não responde ainda")
                
                return True
            else:
                self.log(f"❌ Falha ao iniciar {config['name']}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao iniciar {service_name}: {e}", "ERROR")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Parar serviço"""
        if service_name not in SERVICES_CONFIG:
            self.log(f"❌ Serviço desconhecido: {service_name}", "ERROR")
            return False
        
        if not self.is_service_running(service_name):
            self.log(f"⚠️ Serviço {service_name} não está rodando")
            return True
        
        config = SERVICES_CONFIG[service_name]
        self.log(f"🛑 Parando {config['name']}...")
        
        try:
            pid_file = self.get_pid_file(service_name)
            
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            
            # Tentar parar graciosamente
            process.terminate()
            
            # Aguardar até 10 segundos
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                self.log(f"⚠️ Forçando parada de {service_name}...")
                process.kill()
                process.wait(timeout=5)
            
            # Remover PID file
            if pid_file.exists():
                pid_file.unlink()
            
            self.log(f"✅ {config['name']} parado")
            return True
            
        except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
            # Processo já não existe, limpar PID file
            pid_file = self.get_pid_file(service_name)
            if pid_file.exists():
                pid_file.unlink()
            self.log(f"✅ {config['name']} parado")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao parar {service_name}: {e}", "ERROR")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Reiniciar serviço"""
        self.log(f"🔄 Reiniciando {service_name}...")
        
        if not self.stop_service(service_name):
            return False
        
        time.sleep(1)
        return self.start_service(service_name)
    
    def check_port(self, port: int) -> bool:
        """Verificar se porta está ativa"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def health_check(self, service_name: str) -> Dict:
        """Health check de serviço"""
        config = SERVICES_CONFIG[service_name]
        
        result = {
            "service": service_name,
            "name": config["name"],
            "running": self.is_service_running(service_name),
            "port_active": False,
            "health_url_ok": False,
            "uptime": None,
            "memory_mb": None,
            "cpu_percent": None
        }
        
        if not result["running"]:
            return result
        
        try:
            # Verificar porta
            if config.get("port"):
                result["port_active"] = self.check_port(config["port"])
            
            # Verificar health URL
            if config.get("health_url"):
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=5) as client:
                        response = await client.get(config["health_url"])
                        result["health_url_ok"] = response.status_code == 200
                except:
                    result["health_url_ok"] = False
            
            # Estatísticas do processo
            pid_file = self.get_pid_file(service_name)
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                process = psutil.Process(pid)
                result["uptime"] = time.time() - process.create_time()
                result["memory_mb"] = round(process.memory_info().rss / 1024 / 1024, 1)
                result["cpu_percent"] = round(process.cpu_percent(), 1)
                
        except Exception as e:
            self.log(f"⚠️ Erro no health check de {service_name}: {e}", "WARN")
        
        return result
    
    async def status_all(self) -> List[Dict]:
        """Status de todos os serviços"""
        results = []
        
        for service_name in SERVICES_CONFIG.keys():
            health = await self.health_check(service_name)
            results.append(health)
        
        return results
    
    def start_all(self) -> bool:
        """Iniciar todos os serviços"""
        self.log("🚀 Iniciando todos os serviços...")
        
        # Ordem de inicialização: UCM primeiro
        order = ["ucm-api", "omie-mcp", "nibo-mcp"]
        success = True
        
        for service_name in order:
            if service_name in SERVICES_CONFIG:
                if not self.start_service(service_name):
                    success = False
                time.sleep(1)  # Delay entre serviços
        
        return success
    
    def stop_all(self) -> bool:
        """Parar todos os serviços"""
        self.log("🛑 Parando todos os serviços...")
        
        # Ordem inversa de parada
        order = ["nibo-mcp", "omie-mcp", "ucm-api"]
        success = True
        
        for service_name in order:
            if service_name in SERVICES_CONFIG:
                if not self.stop_service(service_name):
                    success = False
        
        return success
    
    async def show_status(self):
        """Mostrar status formatado"""
        print("\n🔍 STATUS DOS SERVIÇOS")
        print("=" * 80)
        
        statuses = await self.status_all()
        
        for status in statuses:
            name = status["name"]
            running = "🟢 RODANDO" if status["running"] else "🔴 PARADO"
            
            print(f"\n📦 {name}")
            print(f"   Status: {running}")
            
            if status["running"]:
                if status.get("port_active"):
                    port = next(config["port"] for config in SERVICES_CONFIG.values() 
                              if config["name"] == name and config.get("port"))
                    print(f"   Porta: 🌐 {port} ativa")
                
                if status["uptime"]:
                    uptime_str = f"{int(status['uptime']//60)}m {int(status['uptime']%60)}s"
                    print(f"   Uptime: ⏱️ {uptime_str}")
                
                if status["memory_mb"]:
                    print(f"   Memória: 💾 {status['memory_mb']} MB")
                
                if status["cpu_percent"]:
                    print(f"   CPU: ⚡ {status['cpu_percent']}%")
        
        print("\n" + "=" * 80)
    
    def show_logs(self, service_name: str, lines: int = 50):
        """Mostrar logs de serviço"""
        if service_name not in SERVICES_CONFIG:
            self.log(f"❌ Serviço desconhecido: {service_name}", "ERROR")
            return
        
        log_file = self.get_log_file(service_name)
        
        if not log_file.exists():
            self.log(f"📋 Nenhum log encontrado para {service_name}")
            return
        
        self.log(f"📋 Últimas {lines} linhas de {service_name}:")
        print("-" * 60)
        
        try:
            # Ler últimas linhas
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]
                
                for line in recent_lines:
                    print(line.rstrip())
                    
        except Exception as e:
            self.log(f"❌ Erro ao ler logs: {e}", "ERROR")
        
        print("-" * 60)

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Universal Credentials Manager - Service Manager")
    parser.add_argument("action", choices=[
        "start", "stop", "restart", "status", "logs", 
        "start-all", "stop-all", "health"
    ], help="Ação a executar")
    parser.add_argument("service", nargs="?", choices=list(SERVICES_CONFIG.keys()),
                       help="Nome do serviço (obrigatório para start/stop/restart/logs)")
    parser.add_argument("--lines", type=int, default=50,
                       help="Número de linhas de log para mostrar (padrão: 50)")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    try:
        if args.action == "start":
            if not args.service:
                print("❌ Especifique o serviço para iniciar")
                sys.exit(1)
            success = manager.start_service(args.service)
            sys.exit(0 if success else 1)
            
        elif args.action == "stop":
            if not args.service:
                print("❌ Especifique o serviço para parar")
                sys.exit(1)
            success = manager.stop_service(args.service)
            sys.exit(0 if success else 1)
            
        elif args.action == "restart":
            if not args.service:
                print("❌ Especifique o serviço para reiniciar")
                sys.exit(1)
            success = manager.restart_service(args.service)
            sys.exit(0 if success else 1)
            
        elif args.action == "logs":
            if not args.service:
                print("❌ Especifique o serviço para ver logs")
                sys.exit(1)
            manager.show_logs(args.service, args.lines)
            
        elif args.action == "start-all":
            success = manager.start_all()
            sys.exit(0 if success else 1)
            
        elif args.action == "stop-all":
            success = manager.stop_all()
            sys.exit(0 if success else 1)
            
        elif args.action == "status":
            await manager.show_status()
            
        elif args.action == "health":
            statuses = await manager.status_all()
            
            # JSON output para scripts
            print(json.dumps(statuses, indent=2))
            
            # Exit code baseado na saúde
            all_healthy = all(s["running"] for s in statuses)
            sys.exit(0 if all_healthy else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())