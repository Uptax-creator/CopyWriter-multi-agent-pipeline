#!/usr/bin/env python3
"""
Configuração parametrizada do Claude Desktop para Omie MCP
"""

import os
import json
import sys
from pathlib import Path

def create_parameterized_config():
    """Criar configuração parametrizada para Claude Desktop"""
    
    print("🚀 Configurando Claude Desktop com parâmetros...")
    
    # Obter credenciais do usuário
    print("\n🔐 Configuração de Credenciais:")
    print("Escolha o método de configuração:")
    print("1. Via arquivo credentials.json (atual)")
    print("2. Via variáveis de ambiente")
    print("3. Via parâmetros no claude_desktop_config.json")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    # Caminho para configuração do Claude
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Claude"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "claude_desktop_config.json"
    
    project_dir = Path(__file__).parent.parent
    python_path = str(project_dir / "venv" / "bin" / "python")
    
    if not Path(python_path).exists():
        python_path = "python3"
    
    if choice == "1":
        # Configuração atual (arquivo credentials.json)
        client_path = str(project_dir / "claude_http_client.py")
        config = {
            "mcpServers": {
                "omie-erp": {
                    "command": python_path,
                    "args": [client_path]
                }
            }
        }
        print("\n✅ Usando arquivo credentials.json")
        
    elif choice == "2":
        # Configuração via variáveis de ambiente
        print("\n📝 Configure as variáveis de ambiente:")
        print("export OMIE_APP_KEY='sua_app_key'")
        print("export OMIE_APP_SECRET='seu_app_secret'")
        
        client_path = str(project_dir / "claude_mcp_client_parameterized.py")
        config = {
            "mcpServers": {
                "omie-erp": {
                    "command": python_path,
                    "args": [client_path],
                    "env": {
                        "OMIE_APP_KEY": "${OMIE_APP_KEY}",
                        "OMIE_APP_SECRET": "${OMIE_APP_SECRET}"
                    }
                }
            }
        }
        print("\n✅ Configuração via variáveis de ambiente criada")
        
    elif choice == "3":
        # Configuração via parâmetros diretos
        app_key = input("\n🔑 Digite sua OMIE_APP_KEY: ").strip()
        app_secret = input("🔑 Digite sua OMIE_APP_SECRET: ").strip()
        
        if not app_key or not app_secret:
            print("❌ Credenciais são obrigatórias!")
            return False
        
        client_path = str(project_dir / "claude_mcp_client_parameterized.py")
        config = {
            "mcpServers": {
                "omie-erp": {
                    "command": python_path,
                    "args": [
                        client_path,
                        f"--omie-app-key={app_key}",
                        f"--omie-app-secret={app_secret}",
                        "--server-url=http://localhost:3000"
                    ]
                }
            }
        }
        print("\n✅ Configuração com credenciais diretas criada")
        
    else:
        print("❌ Opção inválida!")
        return False
    
    # Escrever configuração
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuração salva em: {config_file}")
        
        # Mostrar configuração (mascarando credenciais se presentes)
        display_config = json.loads(json.dumps(config))
        if "args" in display_config["mcpServers"]["omie-erp"]:
            args = display_config["mcpServers"]["omie-erp"]["args"]
            masked_args = []
            for arg in args:
                if "--omie-app-key=" in arg:
                    masked_args.append("--omie-app-key=***masked***")
                elif "--omie-app-secret=" in arg:
                    masked_args.append("--omie-app-secret=***masked***")
                else:
                    masked_args.append(arg)
            display_config["mcpServers"]["omie-erp"]["args"] = masked_args
        
        print("\n📋 Configuração criada:")
        print(json.dumps(display_config, indent=2))
        
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False
    
    # Instruções finais
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Certifique-se de que o servidor HTTP está rodando:")
    print("   python scripts/start_server.py")
    print("")
    print("2. Reinicie o Claude Desktop completamente")
    print("")
    print("3. Teste: 'Consulte as categorias do Omie ERP'")
    
    print("\n🔧 VANTAGENS DESTA CONFIGURAÇÃO:")
    if choice == "1":
        print("✅ Simples e segura para desenvolvimento")
        print("✅ Credenciais ficam no arquivo local")
    elif choice == "2":
        print("✅ Credenciais via variáveis de ambiente")
        print("✅ Mais seguro para produção")
        print("✅ Não expõe credenciais no arquivo de config")
    elif choice == "3":
        print("✅ Configuração autocontida")
        print("⚠️  Credenciais ficam no arquivo de config")
        print("⚠️  Menos seguro - use apenas para testes")
    
    return True

def main():
    """Função principal"""
    success = create_parameterized_config()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()