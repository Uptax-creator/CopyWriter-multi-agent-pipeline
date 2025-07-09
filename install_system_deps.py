#!/usr/bin/env python3
"""
Script para instalar dependências no Python do sistema
Isso permite usar 'python3' na configuração do Claude sem problemas
"""

import subprocess
import sys
import os

def main():
    print("📦 Instalando dependências no Python do sistema...")
    
    # Dependências necessárias
    dependencies = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic"
    ]
    
    # Usar pip3 para instalar no Python do sistema
    try:
        for dep in dependencies:
            print(f"📥 Instalando {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {dep} instalado com sucesso!")
            else:
                print(f"❌ Erro ao instalar {dep}: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    # Testar importações
    print("\n🧪 Testando importações...")
    try:
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        print("✅ Todas as dependências funcionando!")
        
        # Testar servidor
        print("\n🧪 Testando servidor...")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        from omie_http_server import OMIE_APP_KEY
        print(f"✅ Servidor funcionando! Credenciais: {OMIE_APP_KEY[:8]}...****")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    
    # Criar configuração simplificada
    print("\n⚙️  Criando configuração simplificada...")
    config_content = """{
  "mcpServers": {
    "omie-erp": {
      "command": "python3",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}"""
    
    config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Configuração criada em: {config_path}")
    print("\n📋 Nova configuração:")
    print(config_content)
    
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("1. Feche completamente o Claude Desktop")
    print("2. Abra novamente o Claude Desktop")
    print("3. Teste com: 'Consulte as categorias do Omie ERP'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)