#!/usr/bin/env python3
"""
🚀 SETUP SERVIDOR UNIFICADO - OMIE MCP
Script para configurar Claude Desktop com servidor unificado (11 ferramentas)
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def print_step(step: str):
    """Imprime passo formatado"""
    print(f"\n🔧 {step}")
    print("-" * 50)

def print_result(success: bool, message: str):
    """Imprime resultado formatado"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def find_claude_config_path():
    """Encontra o caminho da configuração do Claude Desktop"""
    return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")

def backup_existing_config(config_path: str):
    """Faz backup da configuração existente"""
    if os.path.exists(config_path):
        backup_path = f"{config_path}.backup.unified.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_path, backup_path)
        print_result(True, f"Backup criado: {backup_path}")
        return backup_path
    return None

def create_unified_config():
    """Cria configuração do Claude Desktop com servidor unificado"""
    print_step("Configurando Claude Desktop - Servidor Unificado")
    
    config_path = find_claude_config_path()
    print(f"📁 Caminho da configuração: {config_path}")
    
    # Criar diretório se não existir
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    # Fazer backup
    backup_path = backup_existing_config(config_path)
    
    # Carregar configuração existente
    existing_config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print_result(True, "Configuração existente carregada")
        except Exception as e:
            print_result(False, f"Erro ao carregar configuração: {e}")
    
    # Configuração do servidor unificado
    project_path = os.path.dirname(os.path.abspath(__file__))
    python_path = f"{project_path}/venv/bin/python3"
    
    unified_config = {
        "omie-unified-server": {
            "command": python_path,
            "args": [
                f"{project_path}/omie_fastmcp_unified.py"
            ],
            "env": {
                "PYTHONPATH": project_path
            }
        }
    }
    
    # Limpar servidores antigos e adicionar unificado
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Remover servidores antigos do Omie
    servers_to_remove = ["omie-conjunto-1-enhanced", "omie-conjunto-2-complete", "omie-optimized"]
    for server in servers_to_remove:
        if server in existing_config["mcpServers"]:
            del existing_config["mcpServers"][server]
            print_result(True, f"Servidor antigo removido: {server}")
    
    # Adicionar servidor unificado
    existing_config["mcpServers"].update(unified_config)
    
    # Salvar configuração
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        
        print_result(True, f"Configuração unificada salva em: {config_path}")
        
        # Mostrar configuração
        print("\n📋 CONFIGURAÇÃO SERVIDOR UNIFICADO:")
        print(json.dumps(unified_config, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao salvar configuração: {e}")
        return False

def verify_unified_setup():
    """Verifica se o setup unificado está correto"""
    print_step("Verificando setup unificado")
    
    required_files = [
        "omie_fastmcp_unified.py",
        "credentials.json",
        "src/client/omie_client.py"
    ]
    
    all_files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print_result(True, f"Arquivo encontrado: {file}")
        else:
            print_result(False, f"Arquivo não encontrado: {file}")
            all_files_ok = False
    
    return all_files_ok

def main():
    """Execução principal"""
    print("=" * 60)
    print("🚀 SETUP SERVIDOR UNIFICADO - OMIE MCP")
    print("=" * 60)
    print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = True
    
    # Etapa 1: Verificar setup
    if not verify_unified_setup():
        print_result(False, "Setup incompleto - verifique os arquivos")
        success = False
    
    # Etapa 2: Configurar Claude Desktop
    if success:
        if not create_unified_config():
            print_result(False, "Falha na configuração do Claude Desktop")
            success = False
    
    # Resultado final
    print("\n" + "=" * 60)
    print("🎯 RESULTADO FINAL")
    print("=" * 60)
    
    if success:
        print("✅ SERVIDOR UNIFICADO CONFIGURADO COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reinicie o Claude Desktop")
        print("2. Verifique se o servidor 'omie-unified-server' aparece")
        print("3. Teste com: 'Liste as categorias disponíveis'")
        print("4. Valide todas as 11 ferramentas")
        
        print("\n🎯 SERVIDOR DISPONÍVEL:")
        print("   - omie-unified-server (11 ferramentas)")
        print("     ├── Conjunto 1: consultar_categorias, listar_clientes, consultar_contas_pagar")
        print("     └── Conjunto 2: projetos, lançamentos, contas correntes (8 tools)")
        
        print("\n⚡ BENEFÍCIOS DA UNIFICAÇÃO:")
        print("   - Redução de recursos (3 → 1 servidor)")
        print("   - Performance otimizada")
        print("   - Manutenção simplificada")
        print("   - Deploy mais fácil")
        
    else:
        print("❌ Falha na configuração")
        print("🔍 Verifique os erros acima")
    
    print(f"\n🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        exit(1)