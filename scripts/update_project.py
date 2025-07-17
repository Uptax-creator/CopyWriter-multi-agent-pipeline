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
    
    def run_tests(self) -> bool:
        """Executa testes completos"""
        self.log("🧪 Executando testes...")
        
        # Teste básico
        success, output, error = self.run_command("python tests/test_basic.py")
        if not success:
            self.log(f"❌ Testes básicos falharam: {error}", "ERROR")
            return False
        
        # Teste de ferramentas
        success, output, error = self.run_command("python scripts/test_all_tools.py")
        if not success:
            self.log(f"❌ Testes de ferramentas falharam: {error}", "ERROR")
            return False
        
        self.log("✅ Todos os testes passaram")
        return True
    
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
        return "2.0.0"  # Default\n    \n    def bump_version(self, version_type: str) -> str:\n        \"\"\"Incrementa versão (major, minor, patch)\"\"\"\n        current = self.get_current_version()\n        major, minor, patch = map(int, current.split("."))\n        \n        if version_type == "major":\n            major += 1\n            minor = 0\n            patch = 0\n        elif version_type == "minor":\n            minor += 1\n            patch = 0\n        elif version_type == "patch":\n            patch += 1\n        else:\n            raise ValueError(f"Tipo de versão inválido: {version_type}")\n        \n        return f"{major}.{minor}.{patch}"\n    \n    def update_version_files(self, new_version: str):\n        \"\"\"Atualiza versão em todos os arquivos\"\"\"\n        files_to_update = [\n            ("README.md", r"version-\d+\.\d+\.\d+", f"version-{new_version}"),\n            ("src/config.py", r"VERSION = \".*?\"", f'VERSION = "{new_version}"'),\n        ]\n        \n        for file_path, pattern, replacement in files_to_update:\n            full_path = PROJECT_ROOT / file_path\n            if full_path.exists():\n                with open(full_path, "r") as f:\n                    content = f.read()\n                \n                new_content = re.sub(pattern, replacement, content)\n                \n                with open(full_path, "w") as f:\n                    f.write(new_content)\n                \n                self.log(f"📝 Atualizada versão em {file_path}")\n    \n    def create_backup(self) -> str:\n        \"\"\"Cria backup antes de mudanças importantes\"\"\"\n        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")\n        backup_dir = PROJECT_ROOT / "backup" / timestamp\n        backup_dir.mkdir(parents=True, exist_ok=True)\n        \n        # Backup de arquivos críticos\n        critical_files = [\n            "src/server.py",\n            "run_server.py",\n            "README.md",\n            "requirements.txt"\n        ]\n        \n        for file_path in critical_files:\n            full_path = PROJECT_ROOT / file_path\n            if full_path.exists():\n                success, _, error = self.run_command(\n                    f"cp {full_path} {backup_dir}/{full_path.name}"\n                )\n                if success:\n                    self.log(f"📦 Backup: {file_path}")\n        \n        return str(backup_dir)\n    \n    def interactive_commit(self):\n        \"\"\"Commit interativo com validações\"\"\"\n        if self.git_status["clean"]:\n            print("✅ Repositório limpo, nada para commitar")\n            return\n        \n        print("📋 Arquivos modificados:")\n        for file_info in self.git_status["files"]:\n            print(f"   {file_info['status']} {file_info['path']}")\n        \n        # Solicitar tipo de commit\n        print("\\n🏷️  Tipo de commit:")\n        commit_types = {\n            "1": "feat",\n            "2": "fix", \n            "3": "docs",\n            "4": "style",\n            "5": "refactor",\n            "6": "test",\n            "7": "chore"\n        }\n        \n        for key, value in commit_types.items():\n            print(f"   {key}. {value}")\n        \n        choice = input("\\nEscolha o tipo (1-7): ").strip()\n        if choice not in commit_types:\n            print("❌ Escolha inválida")\n            return\n        \n        commit_type = commit_types[choice]\n        \n        # Solicitar escopo e descrição\n        scope = input("Escopo (opcional, ex: tools, client, docs): ").strip()\n        description = input("Descrição breve: ").strip()\n        \n        if not description:\n            print("❌ Descrição é obrigatória")\n            return\n        \n        # Montar mensagem de commit\n        if scope:\n            commit_msg = f"{commit_type}({scope}): {description}"\n        else:\n            commit_msg = f"{commit_type}: {description}"\n        \n        # Executar testes antes do commit\n        if not self.run_tests():\n            response = input("❌ Testes falharam. Continuar mesmo assim? (y/N): ")\n            if response.lower() != 'y':\n                return\n        \n        # Fazer commit\n        success, output, error = self.run_command(f'git add -A && git commit -m "{commit_msg}"')\n        \n        if success:\n            self.log(f"✅ Commit realizado: {commit_msg}")\n        else:\n            self.log(f"❌ Erro no commit: {error}", "ERROR")\n    \n    def release(self, version_type: str):\n        \"\"\"Processo completo de release\"\"\"\n        self.log(f"🚀 Iniciando release {version_type}...")\n        \n        # Verificar se repo está limpo\n        if not self.git_status["clean"]:\n            print("❌ Repositório tem mudanças não commitadas")\n            return\n        \n        # Criar backup\n        backup_dir = self.create_backup()\n        self.log(f"📦 Backup criado em: {backup_dir}")\n        \n        # Executar testes\n        if not self.run_tests():\n            print("❌ Testes falharam, release abortado")\n            return\n        \n        # Atualizar versão\n        old_version = self.get_current_version()\n        new_version = self.bump_version(version_type)\n        self.update_version_files(new_version)\n        \n        self.log(f"📈 Versão: {old_version} → {new_version}")\n        \n        # Commit da nova versão\n        commit_msg = f"chore: bump version to {new_version}"\n        success, _, error = self.run_command(f'git add -A && git commit -m "{commit_msg}"')\n        \n        if not success:\n            self.log(f"❌ Erro no commit de versão: {error}", "ERROR")\n            return\n        \n        # Criar tag\n        tag_msg = f"Release v{new_version}"\n        success, _, error = self.run_command(f'git tag -a v{new_version} -m "{tag_msg}"')\n        \n        if success:\n            self.log(f"🏷️  Tag criada: v{new_version}")\n        else:\n            self.log(f"❌ Erro ao criar tag: {error}", "ERROR")\n            return\n        \n        # Push (opcional)\n        response = input(f"\\n📤 Push para origin? (y/N): ")\n        if response.lower() == 'y':\n            success, _, error = self.run_command("git push origin main --tags")\n            if success:\n                self.log("📤 Push realizado com sucesso")\n            else:\n                self.log(f"❌ Erro no push: {error}", "ERROR")\n        \n        self.log(f"🎉 Release v{new_version} concluído!")\n    \n    def show_status(self):\n        \"\"\"Mostra status detalhado do projeto\"\"\"\n        print("📊 STATUS DO PROJETO OMIE MCP SERVER")\n        print("=" * 50)\n        \n        # Git status\n        if self.git_status["clean"]:\n            print("✅ Git: Repositório limpo")\n        else:\n            print(f"⚠️  Git: {len(self.git_status['files'])} arquivos modificados")\n        \n        # Versão atual\n        version = self.get_current_version()\n        print(f"📦 Versão atual: {version}")\n        \n        # Status do servidor\n        success, output, error = self.run_command("python scripts/service_manager.py status")\n        if "Rodando" in output:\n            print("🟢 Servidor: Rodando")\n        else:\n            print("🔴 Servidor: Parado")\n        \n        # Último teste\n        log_files = list((PROJECT_ROOT / "logs").glob("test_report_*.json"))\n        if log_files:\n            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)\n            print(f"🧪 Último teste: {latest_log.name}")\n        else:\n            print("🧪 Último teste: Nenhum encontrado")\n\ndef main():\n    \"\"\"Função principal\"\"\"\n    if len(sys.argv) < 2:\n        print("🔄 Automação de Atualizações - Omie MCP Server")\n        print()\n        print("Uso: python update_project.py <comando>")\n        print()\n        print("Comandos:")\n        print("  status     - Mostra status do projeto")\n        print("  test       - Executa todos os testes")\n        print("  commit     - Commit interativo com validações")\n        print("  backup     - Cria backup dos arquivos críticos")\n        print("  release    - Release completo (patch|minor|major)")\n        print()\n        print("Exemplos:")\n        print("  python update_project.py status")\n        print("  python update_project.py test")\n        print("  python update_project.py commit")\n        print("  python update_project.py release patch")\n        print()\n        sys.exit(1)\n    \n    command = sys.argv[1].lower()\n    updater = ProjectUpdater()\n    \n    if command == "status":\n        updater.show_status()\n    \n    elif command == "test":\n        success = updater.run_tests()\n        sys.exit(0 if success else 1)\n    \n    elif command == "commit":\n        updater.interactive_commit()\n    \n    elif command == "backup":\n        backup_dir = updater.create_backup()\n        print(f"📦 Backup criado em: {backup_dir}")\n    \n    elif command == "release":\n        if len(sys.argv) < 3:\n            print("❌ Especifique o tipo de release: patch, minor ou major")\n            sys.exit(1)\n        \n        version_type = sys.argv[2].lower()\n        if version_type not in ["patch", "minor", "major"]:\n            print("❌ Tipo inválido. Use: patch, minor ou major")\n            sys.exit(1)\n        \n        updater.release(version_type)\n    \n    else:\n        print(f"❌ Comando desconhecido: {command}")\n        sys.exit(1)\n\nif __name__ == "__main__":\n    main()