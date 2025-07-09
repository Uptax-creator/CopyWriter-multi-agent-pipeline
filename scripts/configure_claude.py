#!/usr/bin/env python3
"""
Configuração do Claude Desktop para usar o servidor HTTP do Omie MCP
"""

import os
import json
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Configurando Claude Desktop para usar servidor HTTP v2.0.0...")
    
    # Caminho para a configuração do Claude
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Claude"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "claude_desktop_config.json"
    
    # Configuração usando cliente HTTP
    project_dir = Path(__file__).parent.parent
    python_path = str(project_dir / "venv" / "bin" / "python")
    client_path = str(project_dir / "claude_http_client.py")
    
    # Verificar se o ambiente virtual existe
    if not Path(python_path).exists():
        python_path = "python3"
    
    config = {
        "mcpServers": {
            "omie-erp": {
                "command": python_path,
                "args": [client_path]
            }
        }
    }
    
    # Escrever configuração
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuração criada em: {config_file}")
        
        # Mostrar configuração
        print("\\n📋 Configuração do Claude Desktop:")
        with open(config_file, 'r') as f:
            print(f.read())
            
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False
    
    # Verificar se o servidor HTTP pode ser iniciado
    print("\\n🧪 Verificando servidor HTTP...")
    try:
        # Testar se as dependências estão disponíveis
        subprocess.run([python_path, "-c", "import fastapi, uvicorn, httpx, pydantic"], 
                      check=True, capture_output=True)
        print("✅ Dependências do servidor HTTP disponíveis")
        
    except subprocess.CalledProcessError:
        print("❌ Erro: Dependências não encontradas")
        print("   Execute: pip install fastapi uvicorn httpx pydantic")
        return False
    
    # Instruções de uso
    print("\\n📋 INSTRUÇÕES DE USO:")
    print("1. Inicie o servidor HTTP em um terminal:")
    print("   python scripts/start_server.py")
    print("")
    print("2. Feche e reabra o Claude Desktop")
    print("")
    print("3. Teste com: 'Consulte as categorias do Omie ERP'")
    
    print("\\n💡 VANTAGENS DA ARQUITETURA HÍBRIDA:")
    print("✅ Estrutura modular e organizada")
    print("✅ Código limpo e manutenível")
    print("✅ Testes unitários estruturados")
    print("✅ Validação robusta de dados")
    print("✅ Logs centralizados e claros")
    print("✅ Documentação automática")
    print("✅ Configuração unificada")
    
    print("\\n🔧 ENDPOINTS DISPONÍVEIS:")
    print("• http://localhost:3000/mcp/tools - Lista ferramentas")
    print("• http://localhost:3000/mcp/tools/consultar_categorias - Executar ferramenta")
    print("• http://localhost:3000/docs - Documentação automática")
    print("• http://localhost:3000/test/categorias - Teste rápido")
    print("• http://localhost:3000/health - Health check")
    
    print("\\n🛠️ FERRAMENTAS DISPONÍVEIS:")
    print("• Consultas: categorias, departamentos, tipos de documento")
    print("• Clientes: incluir, alterar, consultar")
    print("• Fornecedores: incluir, alterar, consultar")
    print("• Contas a pagar: incluir, alterar, excluir, consultar")
    print("• Contas a receber: incluir, alterar, excluir, consultar")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)