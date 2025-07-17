#!/usr/bin/env python3
"""
Script para ativar/desativar serviços MCP (Omie e Nibo)
"""

import os
import sys
import json
import subprocess
import signal
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional

class MCPServiceManager:
    def __init__(self):
        self.project_root = "/Users/kleberdossantosribeiro/omie-mcp"
        self.claude_config_path = "/Users/kleberdossantosribeiro/Library/Application Support/Claude/claude_desktop_config.json"
        self.pid_file = os.path.join(self.project_root, "services.pid")
        
        self.services = {
            "omie-mcp": {
                "script": os.path.join(self.project_root, "omie_mcp_server_hybrid.py"),
                "port_stdio": None,
                "port_http": 3001,
                "name": "Omie MCP Server"
            },
            "nibo-mcp": {
                "script": os.path.join(self.project_root, "nibo-mcp", "nibo_mcp_server_hybrid.py"),
                "port_stdio": None,
                "port_http": 3002,
                "name": "Nibo MCP Server"
            }
        }

    def check_service_status(self, service_name: str) -> Dict:
        """Verifica status de um serviço"""
        service = self.services.get(service_name)
        if not service:
            return {"error": f"Serviço {service_name} não encontrado"}
        
        status = {
            "name": service["name"],
            "script_exists": os.path.exists(service["script"]),
            "stdio_configured": False,
            "http_running": False,
            "pid": None,
            "port": service["port_http"]
        }
        
        # Verificar se está configurado no Claude Desktop
        try:
            with open(self.claude_config_path, 'r') as f:
                config = json.load(f)
                mcp_servers = config.get("mcpServers", {})
                for server_name, server_config in mcp_servers.items():
                    args = server_config.get("args", [])
                    if args and service["script"] in args[0]:
                        status["stdio_configured"] = True
                        break
        except Exception:
            pass
        
        # Verificar se processo HTTP está rodando
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any(service["script"] in cmd for cmd in cmdline):
                    if "--mode" in cmdline and "http" in cmdline:
                        status["http_running"] = True
                        status["pid"] = proc.info['pid']
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return status

    def get_all_status(self) -> Dict:
        """Obtém status de todos os serviços"""
        return {
            service_name: self.check_service_status(service_name) 
            for service_name in self.services.keys()
        }

    def start_service_http(self, service_name: str) -> bool:
        """Inicia serviço em modo HTTP"""
        service = self.services.get(service_name)
        if not service:
            print(f"❌ Serviço {service_name} não encontrado")
            return False
        
        if not os.path.exists(service["script"]):
            print(f"❌ Script não encontrado: {service['script']}")
            return False
        
        # Verificar se já está rodando
        status = self.check_service_status(service_name)
        if status["http_running"]:
            print(f"✅ {service['name']} já está rodando (PID: {status['pid']})")
            return True
        
        print(f"🚀 Iniciando {service['name']} em modo HTTP...")
        
        try:
            # Iniciar processo
            process = subprocess.Popen([
                sys.executable, service["script"],
                "--mode", "http",
                "--port", str(service["port_http"]),
                "--host", "0.0.0.0"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Aguardar inicialização
            time.sleep(3)
            
            # Verificar se iniciou corretamente
            if process.poll() is None:
                # Salvar PID
                self._save_pid(service_name, process.pid)
                print(f"✅ {service['name']} iniciado com sucesso!")
                print(f"📋 PID: {process.pid}")
                print(f"📋 URL: http://localhost:{service['port_http']}")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Falha ao iniciar {service['name']}")
                print(f"Erro: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar {service['name']}: {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Para serviço"""
        service = self.services.get(service_name)
        if not service:
            print(f"❌ Serviço {service_name} não encontrado")
            return False
        
        status = self.check_service_status(service_name)
        if not status["http_running"]:
            print(f"📋 {service['name']} não está rodando")
            return True
        
        print(f"🛑 Parando {service['name']}...")
        
        try:
            # Tentar parar pelo PID
            if status["pid"]:
                os.kill(status["pid"], signal.SIGTERM)
                time.sleep(2)
                
                # Verificar se parou
                try:
                    os.kill(status["pid"], 0)
                    # Ainda está rodando, forçar
                    os.kill(status["pid"], signal.SIGKILL)
                    time.sleep(1)
                except ProcessLookupError:
                    pass
            
            # Remover PID salvo
            self._remove_pid(service_name)
            print(f"✅ {service['name']} parado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao parar {service['name']}: {e}")
            return False

    def configure_claude_desktop(self, services_to_enable: List[str]) -> bool:
        """Configura Claude Desktop com serviços especificados"""
        print("🔧 Configurando Claude Desktop...")
        
        # Fazer backup
        backup_path = f"{self.claude_config_path}.backup"
        if os.path.exists(self.claude_config_path):
            import shutil
            shutil.copy2(self.claude_config_path, backup_path)
            print(f"📦 Backup salvo: {backup_path}")
        
        # Criar nova configuração
        config = {"mcpServers": {}}
        
        for service_name in services_to_enable:
            service = self.services.get(service_name)
            if service and os.path.exists(service["script"]):
                config_name = service_name.replace("-", "-erp")
                config["mcpServers"][config_name] = {
                    "command": "python3",
                    "args": [service["script"], "--mode", "stdio"]
                }
        
        # Salvar configuração
        try:
            os.makedirs(os.path.dirname(self.claude_config_path), exist_ok=True)
            with open(self.claude_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuração salva: {self.claude_config_path}")
            print("📋 Serviços configurados:")
            for service_name in services_to_enable:
                service = self.services[service_name]
                print(f"  • {service['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False

    def _save_pid(self, service_name: str, pid: int):
        """Salva PID de um serviço"""
        pids = {}
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pids = json.load(f)
            except:
                pass
        
        pids[service_name] = pid
        with open(self.pid_file, 'w') as f:
            json.dump(pids, f)

    def _remove_pid(self, service_name: str):
        """Remove PID de um serviço"""
        if not os.path.exists(self.pid_file):
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            if service_name in pids:
                del pids[service_name]
                
            with open(self.pid_file, 'w') as f:
                json.dump(pids, f)
        except:
            pass

    def print_status(self):
        """Imprime status detalhado dos serviços"""
        print("📊 STATUS DOS SERVIÇOS MCP")
        print("=" * 50)
        
        for service_name, status in self.get_all_status().items():
            service = self.services[service_name]
            print(f"\n🔧 {status['name']}")
            print(f"  Script: {'✅' if status['script_exists'] else '❌'} {service['script']}")
            print(f"  Claude Desktop: {'✅ Configurado' if status['stdio_configured'] else '❌ Não configurado'}")
            print(f"  HTTP Server: {'✅ Rodando' if status['http_running'] else '❌ Parado'}")
            
            if status['http_running'] and status['pid']:
                print(f"    PID: {status['pid']}")
                print(f"    URL: http://localhost:{status['port']}")

def main():
    manager = MCPServiceManager()
    
    if len(sys.argv) < 2:
        print("🔧 Gerenciador de Serviços MCP")
        print("=" * 30)
        print("\nUso:")
        print("  python service_toggle.py status              # Ver status dos serviços")
        print("  python service_toggle.py start <serviço>     # Iniciar serviço HTTP")
        print("  python service_toggle.py stop <serviço>      # Parar serviço")
        print("  python service_toggle.py configure <serviços># Configurar Claude Desktop")
        print("  python service_toggle.py start-all          # Iniciar todos os serviços")
        print("  python service_toggle.py stop-all           # Parar todos os serviços")
        print("\nServiços disponíveis: omie-mcp, nibo-mcp")
        print("\nExemplos:")
        print("  python service_toggle.py start omie-mcp")
        print("  python service_toggle.py configure omie-mcp nibo-mcp")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        manager.print_status()
    
    elif command == "start":
        if len(sys.argv) < 3:
            print("❌ Especifique o serviço: omie-mcp ou nibo-mcp")
            return
        service_name = sys.argv[2]
        manager.start_service_http(service_name)
    
    elif command == "stop":
        if len(sys.argv) < 3:
            print("❌ Especifique o serviço: omie-mcp ou nibo-mcp")
            return
        service_name = sys.argv[2]
        manager.stop_service(service_name)
    
    elif command == "configure":
        services = sys.argv[2:] if len(sys.argv) > 2 else ["omie-mcp", "nibo-mcp"]
        manager.configure_claude_desktop(services)
        print("\n📋 IMPORTANTE: Reinicie o Claude Desktop para aplicar as mudanças!")
    
    elif command == "start-all":
        print("🚀 Iniciando todos os serviços...")
        for service_name in manager.services.keys():
            manager.start_service_http(service_name)
            print()
    
    elif command == "stop-all":
        print("🛑 Parando todos os serviços...")
        for service_name in manager.services.keys():
            manager.stop_service(service_name)
            print()
    
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()