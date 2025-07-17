#!/usr/bin/env python3
"""
Script para configurar repositório GitHub com estrutura completa
"""

import os
import subprocess
import json
import sys
from pathlib import Path

def run_command(command, check=True):
    """Executa comando no terminal"""
    print(f"🔧 Executando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Erro: {result.stderr}")
        sys.exit(1)
    
    return result

def check_git_status():
    """Verifica status do git"""
    print("📊 Verificando status do Git...")
    
    # Verificar se está em um repositório git
    result = run_command("git status", check=False)
    if result.returncode != 0:
        print("❌ Não está em um repositório Git")
        return False
    
    # Verificar se há arquivos não commitados
    result = run_command("git status --porcelain")
    if result.stdout.strip():
        print("⚠️  Há arquivos não commitados:")
        print(result.stdout)
        return False
    
    print("✅ Git status OK")
    return True

def setup_github_repo():
    """Configura repositório GitHub"""
    print("🐙 Configurando repositório GitHub...")
    
    # Verificar se já existe remote
    result = run_command("git remote -v", check=False)
    if "origin" in result.stdout:
        print("✅ Remote origin já configurado")
        return True
    
    # Configurar remote (será necessário criar o repo no GitHub primeiro)
    repo_url = "https://github.com/kleberdossantosribeiro/omie-mcp-ecosystem.git"
    print(f"📝 Para continuar, crie o repositório no GitHub: {repo_url}")
    print("📝 Depois execute: git remote add origin {repo_url}")
    
    return False

def create_labels():
    """Cria labels no GitHub"""
    print("🏷️  Criando labels no GitHub...")
    
    labels = [
        {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
        {"name": "enhancement", "color": "a2eeef", "description": "New feature or request"},
        {"name": "erp-integration", "color": "0e8a16", "description": "ERP integration related"},
        {"name": "documentation", "color": "0075ca", "description": "Improvements or additions to documentation"},
        {"name": "security", "color": "b60205", "description": "Security related issues"},
        {"name": "omie", "color": "fbca04", "description": "Omie ERP specific"},
        {"name": "nibo", "color": "fef2c0", "description": "Nibo ERP specific"},
        {"name": "sap", "color": "1d76db", "description": "SAP ERP specific"},
        {"name": "oracle", "color": "ff7518", "description": "Oracle ERP specific"},
        {"name": "dynamics", "color": "0052cc", "description": "Dynamics ERP specific"},
        {"name": "quickbooks", "color": "2cbe4e", "description": "QuickBooks ERP specific"},
    ]
    
    for label in labels:
        command = f"gh label create {label['name']} --color {label['color']} --description '{label['description']}'"
        run_command(command, check=False)
    
    print("✅ Labels criados")

def create_milestones():
    """Cria milestones no GitHub"""
    print("🎯 Criando milestones no GitHub...")
    
    milestones = [
        {
            "title": "v2.1.0 - Common Library",
            "description": "Implementation of common library for all ERP servers",
            "due_date": "2024-08-15"
        },
        {
            "title": "v2.2.0 - Independent Architecture",
            "description": "Migration to independent server architecture",
            "due_date": "2024-09-01"
        },
        {
            "title": "v2.3.0 - SAP Integration",
            "description": "Add SAP ERP integration",
            "due_date": "2024-10-01"
        }
    ]
    
    for milestone in milestones:
        command = f"gh milestone create --title '{milestone['title']}' --description '{milestone['description']}' --due-date {milestone['due_date']}"
        run_command(command, check=False)
    
    print("✅ Milestones criados")

def setup_github_pages():
    """Configura GitHub Pages"""
    print("📄 Configurando GitHub Pages...")
    
    # Habilitar GitHub Pages
    command = "gh pages enable --source docs --branch main"
    run_command(command, check=False)
    
    print("✅ GitHub Pages configurado")

def create_initial_commit():
    """Cria commit inicial com estrutura GitHub"""
    print("📝 Criando commit inicial...")
    
    # Adicionar arquivos
    run_command("git add .github/")
    run_command("git add docs/README.md")
    run_command("git add docs/GITHUB_STRUCTURE_PROPOSAL.md")
    
    # Commit
    commit_message = """feat: Add GitHub structure and documentation

- Add issue templates for bugs, features, and ERP integrations
- Add PR template with comprehensive checklist
- Add GitHub Actions for CI/CD and documentation
- Add security policy and code owners
- Reorganize documentation structure
- Add comprehensive GitHub structure proposal

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    run_command(f'git commit -m "{commit_message}"')
    
    print("✅ Commit inicial criado")

def validate_structure():
    """Valida estrutura criada"""
    print("✅ Validando estrutura...")
    
    required_files = [
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/ISSUE_TEMPLATE/erp_integration.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/ci.yml",
        ".github/workflows/docs.yml",
        ".github/SECURITY.md",
        ".github/CODEOWNERS",
        "docs/README.md",
        "docs/GITHUB_STRUCTURE_PROPOSAL.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Arquivos faltando:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ Estrutura validada com sucesso")
    return True

def main():
    """Função principal"""
    print("🚀 Configurando estrutura GitHub para Omie MCP Ecosystem")
    print("=" * 60)
    
    # Verificar pré-requisitos
    if not check_git_status():
        print("❌ Pré-requisitos não atendidos")
        sys.exit(1)
    
    # Validar estrutura
    if not validate_structure():
        print("❌ Estrutura inválida")
        sys.exit(1)
    
    # Criar commit inicial
    create_initial_commit()
    
    # Instruções para próximos passos
    print("\n🎉 Estrutura GitHub configurada com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Crie o repositório no GitHub: https://github.com/new")
    print("2. Nome: omie-mcp-ecosystem")
    print("3. Descrição: Ecosystem of MCP servers for ERP integration")
    print("4. Execute: git remote add origin https://github.com/kleberdossantosribeiro/omie-mcp-ecosystem.git")
    print("5. Execute: git push -u origin main")
    print("6. Configure secrets no GitHub Actions")
    print("7. Habilite GitHub Pages")
    
    print("\n🔐 Secrets necessários:")
    print("- OMIE_APP_KEY_TEST")
    print("- OMIE_APP_SECRET_TEST")
    print("- NIBO_TOKEN_TEST")
    print("- NIBO_COMPANY_ID_TEST")
    
    print("\n✅ Estrutura pronta para uso!")

if __name__ == "__main__":
    main()