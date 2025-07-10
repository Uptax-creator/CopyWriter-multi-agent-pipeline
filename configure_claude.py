#!/usr/bin/env python3
"""
Script Python para configurar o Omie MCP Server no Claude Desktop
"""

import os
import json
import sys
from pathlib import Path

def main():
    print("🚀 Configurando Omie MCP Server no Claude Desktop...")
    
    # Caminho para a configuração do Claude
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Claude"
    
    # Criar diretório se não existir
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Diretório de configuração: {config_dir}")
    
    # Caminho do arquivo de configuração
    config_file = config_dir / "claude_desktop_config.json"
    
    # Configuração MCP
    config = {
        "mcpServers": {
            "omie-erp": {
                "command": "python",
                "args": [str(Path(__file__).parent / "omie_mcp_server.py")]
            }
        }
    }
    
    # Escrever configuração
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuração criada em: {config_file}")
        
        # Mostrar conteúdo
        print("\n📋 Conteúdo da configuração:")
        with open(config_file, 'r') as f:
            print(f.read())
            
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False
    
    # Verificar credentials.json
    credentials_file = Path(__file__).parent / "credentials.json"
    if credentials_file.exists():
        print("✅ Arquivo credentials.json encontrado")
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
                app_key = creds.get("app_key", "")
                print(f"✅ Credenciais carregadas: {app_key[:8]}...****")
        except Exception as e:
            print(f"⚠️  Erro ao ler credentials.json: {e}")
    else:
        print("⚠️  Arquivo credentials.json não encontrado!")
        print("   Crie o arquivo com suas credenciais Omie:")
        print('   {"app_key": "sua_app_key", "app_secret": "seu_app_secret"}')
    
    # Testar importação do servidor
    print("\n🧪 Testando servidor Python...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from omie_http_server import OMIE_APP_KEY
        print("✅ Servidor Python funcionando!")
        print(f"✅ Credenciais carregadas: {OMIE_APP_KEY[:8]}...****")
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        return False
    
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("1. Feche completamente o Claude Desktop")
    print("2. Abra novamente o Claude Desktop")
    print("3. Teste com: 'Consulte as categorias do Omie ERP'")
    
    print("\n🎯 COMANDOS DE TESTE SUGERIDOS:")
    print("• 'Liste as categorias do Omie ERP'")
    print("• 'Mostre os departamentos disponíveis'")
    print("• 'Consulte os tipos de documento'")
    print("• 'Crie uma conta a pagar para o fornecedor X'")
    
    print("\n💡 NOTA: As credenciais são carregadas automaticamente do arquivo credentials.json")
    print("🎉 Configuração concluída! Reinicie o Claude Desktop para ativar.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)