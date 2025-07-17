#!/usr/bin/env python3
"""
🔄 Automação de Atualizações do Projeto Omie MCP Server
Facilita commits, testes, versionamento e deploy
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent

class ProjectUpdater:
    """Automatiza tarefas de atualização do projeto"""
    
    def __init__(self):
        self.git_status = self.get_git_status()
    
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: str, cwd: Path = None) -> tuple:
        """Executa comando e retorna (success, output, error)"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def get_git_status(self) -> dict:
        """Obtém status do Git"""
        success, output, error = self.run_command("git status --porcelain")
        
        if not success:
            return {"clean": False, "files": [], "error": error}
        
        files = []
        for line in output.strip().split("\n"):
            if line.strip():
                status = line[:2]
                file_path = line[3:]
                files.append({"status": status, "path": file_path})
        
        return {
            "clean": len(files) == 0,
            "files": files,
            "error": None
        }
    
    def get_current_version(self) -> str:
        """Obtém versão atual do projeto"""
        try:
            with open(PROJECT_ROOT / "README.md", "r") as f:
                content = f.read()
                match = re.search(r"version-(\d+\.\d+\.\d+)", content)
                if match:
                    return match.group(1)
        except:
            pass
        return "2.0.0"  # Default
    
    def show_status(self):
        """Mostra status detalhado do projeto"""
        print("📊 STATUS DO PROJETO OMIE MCP SERVER")
        print("=" * 50)
        
        # Git status
        if self.git_status["clean"]:
            print("✅ Git: Repositório limpo")
        else:
            print(f"⚠️  Git: {len(self.git_status['files'])} arquivos modificados")
        
        # Versão atual
        version = self.get_current_version()
        print(f"📦 Versão atual: {version}")
        
        # Status do servidor
        success, output, error = self.run_command("python scripts/service_manager.py status")
        if "Rodando" in output:
            print("🟢 Servidor: Rodando")
        else:
            print("🔴 Servidor: Parado")
        
        # Último teste
        try:
            log_files = list((PROJECT_ROOT / "logs").glob("test_report_*.json"))
            if log_files:
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                print(f"🧪 Último teste: {latest_log.name}")
            else:
                print("🧪 Último teste: Nenhum encontrado")
        except:
            print("🧪 Último teste: Nenhum encontrado")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("🔄 Automação de Atualizações - Omie MCP Server")
        print()
        print("Uso: python update_project_fixed.py <comando>")
        print()
        print("Comandos:")
        print("  status     - Mostra status do projeto")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    updater = ProjectUpdater()
    
    if command == "status":
        updater.show_status()
    else:
        print(f"❌ Comando desconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()