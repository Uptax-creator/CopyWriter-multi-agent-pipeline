#!/usr/bin/env python3
"""
🚀 Gerenciador de Serviço Omie MCP Server
Controla start/stop/restart/status do servidor
"""

import os
import sys
import time
import signal
import subprocess
import json
from pathlib import Path
from datetime import datetime
import requests
import psutil

# Configurações
PROJECT_ROOT = Path(__file__).parent.parent
PID_FILE = PROJECT_ROOT / "server.pid"
LOG_FILE = PROJECT_ROOT / "logs" / "service.log"
SERVER_URL = "http://localhost:3001"
SERVER_SCRIPT = PROJECT_ROOT / "omie_http_server_fastapi.py"

class ServiceManager:
    """Gerenciador do serviço Omie MCP"""
    
    def __init__(self):
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Garante que o diretório de logs existe"""
        LOG_FILE.parent.mkdir(exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Adiciona entrada no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # Escrever no arquivo
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Exibir no console
        print(f"🔧 {log_entry.strip()}")
    
    def is_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        if not PID_FILE.exists():
            return False
        
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            
            # Verificar se o processo existe
            if psutil.pid_exists(pid):
                return True
            else:
                # PID file órfão, remover
                PID_FILE.unlink()
                return False
                
        except (ValueError, FileNotFoundError):
            return False
    
    def get_status(self) -> dict:
        """Obtém status detalhado do serviço"""
        status = {
            "running": self.is_running(),
            "pid": None,
            "uptime": None,
            "health": "unknown",
            "last_check": datetime.now().isoformat()
        }
        
        if status["running"]:
            try:
                with open(PID_FILE, "r") as f:
                    status["pid"] = int(f.read().strip())
                
                # Verificar saúde via HTTP
                try:
                    response = requests.get(f"{SERVER_URL}/", timeout=5)
                    if response.status_code == 200:
                        status["health"] = "healthy"
                        health_data = response.json()
                        status["uptime"] = health_data.get("uptime", "active")
                    else:
                        status["health"] = "unhealthy"
                except:
                    status["health"] = "unreachable"
                    
            except Exception as e:
                self.log(f"Erro ao obter status: {e}", "ERROR")
        
        return status
    
    def start(self) -> bool:
        """Inicia o servidor"""
        if self.is_running():
            self.log("Servidor já está rodando")
            return True
        
        self.log("Iniciando servidor Omie MCP...")
        
        try:
            # Iniciar processo em background
            process = subprocess.Popen(
                [sys.executable, str(SERVER_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=PROJECT_ROOT
            )
            
            # Salvar PID
            with open(PID_FILE, "w") as f:
                f.write(str(process.pid))
            
            # Aguardar um pouco para verificar se iniciou
            time.sleep(3)
            
            if self.is_running():
                self.log(f"Servidor iniciado com sucesso (PID: {process.pid})")
                return True
            else:
                self.log("Falha ao iniciar servidor", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Erro ao iniciar servidor: {e}", "ERROR")
            return False
    
    def stop(self) -> bool:
        """Para o servidor"""
        if not self.is_running():
            self.log("Servidor não está rodando")
            return True
        
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            
            self.log(f"Parando servidor (PID: {pid})...")
            
            # Tentar parada graceful
            os.kill(pid, signal.SIGTERM)
            
            # Aguardar até 10 segundos
            for _ in range(10):
                if not psutil.pid_exists(pid):
                    break
                time.sleep(1)
            
            # Se ainda estiver rodando, forçar
            if psutil.pid_exists(pid):
                self.log("Forçando parada do servidor", "WARN")
                os.kill(pid, signal.SIGKILL)
                time.sleep(2)
            
            # Remover PID file
            if PID_FILE.exists():
                PID_FILE.unlink()
            
            self.log("Servidor parado com sucesso")
            return True
            
        except Exception as e:
            self.log(f"Erro ao parar servidor: {e}", "ERROR")
            return False
    
    def restart(self) -> bool:
        """Reinicia o servidor"""
        self.log("Reiniciando servidor...")
        
        if self.is_running():
            if not self.stop():
                return False
        
        time.sleep(2)
        return self.start()
    
    def show_status(self):
        """Exibe status detalhado"""
        status = self.get_status()
        
        print("🔍 Status do Omie MCP Server:")
        print(f"   Estado: {'🟢 Rodando' if status['running'] else '🔴 Parado'}")
        
        if status['running']:
            print(f"   PID: {status['pid']}")
            print(f"   Saúde: {status['health']}")
            if status['uptime']:
                print(f"   Uptime: {status['uptime']}")
        
        print(f"   Última verificação: {status['last_check']}")
        print(f"   URL: {SERVER_URL}")
        print(f"   Logs: {LOG_FILE}")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("🚀 Gerenciador de Serviço Omie MCP Server")
        print()
        print("Uso: python service_manager.py <comando>")
        print()
        print("Comandos:")
        print("  start    - Inicia o servidor")
        print("  stop     - Para o servidor")
        print("  restart  - Reinicia o servidor")
        print("  status   - Mostra status detalhado")
        print("  logs     - Mostra logs recentes")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = ServiceManager()
    
    if command == "start":
        success = manager.start()
        sys.exit(0 if success else 1)
    
    elif command == "stop":
        success = manager.stop()
        sys.exit(0 if success else 1)
    
    elif command == "restart":
        success = manager.restart()
        sys.exit(0 if success else 1)
    
    elif command == "status":
        manager.show_status()
    
    elif command == "logs":
        if LOG_FILE.exists():
            print("📋 Logs recentes:")
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-20:]:  # Últimas 20 linhas
                    print(f"   {line.strip()}")
        else:
            print("📋 Nenhum log encontrado")
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()