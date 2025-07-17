#!/usr/bin/env python3
"""
Script para verificar e atualizar configuração do Claude Desktop
"""

import json
import os
import sys
from pathlib import Path

def find_claude_config():
    """Encontra arquivo de configuração do Claude Desktop"""
    
    # Possíveis localizações do arquivo de configuração
    possible_paths = [
        "~/Library/Application Support/Claude/claude_desktop_config.json",
        "~/.config/claude/claude_desktop_config.json",
        "~/AppData/Roaming/Claude/claude_desktop_config.json"
    ]
    
    for path_str in possible_paths:
        path = Path(path_str).expanduser()
        if path.exists():
            print(f"✅ Arquivo de configuração encontrado: {path}")
            return path
    
    print("❌ Arquivo de configuração do Claude Desktop não encontrado")
    print("📋 Localizações verificadas:")
    for path_str in possible_paths:
        print(f"  - {Path(path_str).expanduser()}")
    
    return None

def read_claude_config(config_path):
    """Lê configuração atual do Claude Desktop"""
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"📄 Configuração atual:")
        print(json.dumps(config, indent=2))
        
        return config
        
    except Exception as e:
        print(f"❌ Erro ao ler configuração: {e}")
        return None

def check_mcp_servers(config):
    """Verifica servidores MCP configurados"""
    
    mcp_servers = config.get("mcpServers", {})
    
    print(f"\n🔧 Servidores MCP configurados: {len(mcp_servers)}")
    
    for server_name, server_config in mcp_servers.items():
        print(f"\n📋 Servidor: {server_name}")
        print(f"  Comando: {server_config.get('command', 'N/A')}")
        print(f"  Argumentos: {server_config.get('args', [])}")
        
        # Verificar se está usando arquivo antigo
        args = server_config.get('args', [])
        if args:
            script_path = args[0] if args else ""
            if script_path:
                print(f"  Script: {script_path}")
                
                # Verificar se arquivo existe
                if os.path.exists(script_path):
                    print(f"  ✅ Script existe")
                else:
                    print(f"  ❌ Script não encontrado")
    
    return mcp_servers

def suggest_new_config():
    """Sugere nova configuração com servidores híbridos"""
    
    # Caminhos dos servidores híbridos
    omie_hybrid = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    nibo_hybrid = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py"
    
    # Verificar se servidores híbridos existem
    omie_exists = os.path.exists(omie_hybrid)
    nibo_exists = os.path.exists(nibo_hybrid)
    
    print(f"\n🔧 Servidores híbridos disponíveis:")
    print(f"  Omie: {'✅' if omie_exists else '❌'} {omie_hybrid}")
    print(f"  Nibo: {'✅' if nibo_exists else '❌'} {nibo_hybrid}")
    
    # Configuração sugerida
    suggested_config = {
        "mcpServers": {}
    }
    
    if omie_exists:
        suggested_config["mcpServers"]["omie-erp"] = {
            "command": "python3",
            "args": [omie_hybrid, "--mode", "stdio"]
        }
    
    if nibo_exists:
        suggested_config["mcpServers"]["nibo-erp"] = {
            "command": "python3", 
            "args": [nibo_hybrid, "--mode", "stdio"]
        }
    
    print(f"\n📋 Configuração sugerida:")
    print(json.dumps(suggested_config, indent=2))
    
    return suggested_config

def update_claude_config(config_path, new_config):
    """Atualiza configuração do Claude Desktop"""
    
    try:
        # Fazer backup da configuração atual
        backup_path = f"{config_path}.backup"
        if os.path.exists(config_path):
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"📦 Backup salvo em: {backup_path}")
        
        # Escrever nova configuração
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print(f"✅ Configuração atualizada: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar configuração: {e}")
        return False

def main():
    """Função principal"""
    
    print("🔍 Verificador de Configuração do Claude Desktop")
    print("=" * 55)
    
    # Encontrar arquivo de configuração
    config_path = find_claude_config()
    if not config_path:
        print("\n❌ Não foi possível encontrar o arquivo de configuração")
        print("📋 Crie manualmente em: ~/Library/Application Support/Claude/claude_desktop_config.json")
        return
    
    # Ler configuração atual
    current_config = read_claude_config(config_path)
    if not current_config:
        return
    
    # Verificar servidores MCP
    mcp_servers = check_mcp_servers(current_config)
    
    # Sugerir nova configuração
    suggested_config = suggest_new_config()
    
    # Perguntar se deseja atualizar
    print("\n" + "="*55)
    response = input("\nDeseja atualizar a configuração do Claude Desktop? (y/n): ")
    
    if response.lower() == 'y':
        if update_claude_config(config_path, suggested_config):
            print("\n🎉 Configuração atualizada com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Reinicie o Claude Desktop")
            print("2. Teste os servidores MCP")
            print("3. Os erros de protocolo devem estar resolvidos")
        else:
            print("\n❌ Falha ao atualizar configuração")
    else:
        print("\n📋 Configuração não alterada")
        print("Para atualizar manualmente, substitua o conteúdo do arquivo por:")
        print(json.dumps(suggested_config, indent=2))

if __name__ == "__main__":
    main()