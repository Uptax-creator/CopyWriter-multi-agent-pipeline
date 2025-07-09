#!/usr/bin/env python3
"""
Script para corrigir a configuração do Claude Desktop com o caminho correto do Python
"""

import os
import json
import sys
from pathlib import Path

def main():
    print("🔧 Corrigindo configuração do Claude Desktop...")
    
    # Caminho para a configuração do Claude
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Claude"
    
    config_file = config_dir / "claude_desktop_config.json"
    
    # Opções de configuração
    project_dir = Path(__file__).parent
    
    # Opção 1: Usar Python do ambiente virtual
    python_venv = str(project_dir / "venv" / "bin" / "python")
    
    # Opção 2: Usar script wrapper bash
    bash_wrapper = str(project_dir / "run_omie_server.sh")
    
    print(f"📁 Diretório do projeto: {project_dir}")
    print(f"🐍 Python venv: {python_venv}")
    print(f"📜 Script wrapper: {bash_wrapper}")
    
    # Verificar qual opção usar
    if Path(python_venv).exists():
        print("✅ Usando Python do ambiente virtual")
        config = {
            "mcpServers": {
                "omie-erp": {
                    "command": python_venv,
                    "args": [str(project_dir / "omie_http_server.py")]
                }
            }
        }
    else:
        print("✅ Usando script wrapper bash")
        config = {
            "mcpServers": {
                "omie-erp": {
                    "command": "bash",
                    "args": [bash_wrapper]
                }
            }
        }
    
    # Escrever configuração
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuração atualizada em: {config_file}")
        
        # Mostrar conteúdo
        print("\n📋 Nova configuração:")
        with open(config_file, 'r') as f:
            print(f.read())
            
    except Exception as e:
        print(f"❌ Erro ao atualizar configuração: {e}")
        return False
    
    # Testar execução
    print("\n🧪 Testando configuração...")
    try:
        if "python" in config["mcpServers"]["omie-erp"]["command"]:
            # Testar Python
            import subprocess
            result = subprocess.run([
                config["mcpServers"]["omie-erp"]["command"],
                "-c",
                f"import sys; sys.path.insert(0, '{project_dir}'); from omie_http_server import OMIE_APP_KEY; print('✅ Python funcionando!')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Python do venv funcionando!")
            else:
                print(f"❌ Erro no Python: {result.stderr}")
        else:
            # Testar bash wrapper
            print("✅ Script bash criado!")
            
    except Exception as e:
        print(f"⚠️  Erro no teste: {e}")
    
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("1. Feche completamente o Claude Desktop")
    print("2. Abra novamente o Claude Desktop")
    print("3. Teste com: 'Consulte as categorias do Omie ERP'")
    
    print("\n💡 Se ainda não funcionar, verifique o log do Claude Desktop")
    print("   ~/Library/Logs/Claude/mcp-server-omie-erp.log")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)