#!/usr/bin/env python3
"""
Script para iniciar o servidor HTTP do Omie MCP
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Iniciando servidor HTTP do Omie MCP...")
    
    # Verificar se estamos no diretório correto
    if not Path("run_server.py").exists():
        print("❌ Erro: Execute este script no diretório do projeto")
        print("   cd /Users/kleberdossantosribeiro/omie-mcp")
        return False
    
    # Verificar credenciais
    if not Path("credentials.json").exists():
        print("❌ Erro: Arquivo credentials.json não encontrado")
        print("   Crie o arquivo com suas credenciais Omie")
        return False
    
    # Verificar ambiente virtual
    venv_python = Path("venv/bin/python")
    if venv_python.exists():
        python_cmd = str(venv_python)
        print(f"🐍 Usando Python do ambiente virtual: {python_cmd}")
    else:
        python_cmd = "python3"
        print(f"🐍 Usando Python do sistema: {python_cmd}")
    
    # Verificar dependências
    try:
        result = subprocess.run([
            python_cmd, "-c", 
            "import fastapi, uvicorn, httpx; print('✅ Dependências OK')"
        ], capture_output=True, text=True, check=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("❌ Erro: Dependências não encontradas")
        print("   Execute: pip install fastapi uvicorn httpx")
        print(f"   Erro: {e.stderr}")
        return False
    
    # Configurar porta
    port = os.getenv("MCP_SERVER_PORT", "3000")
    
    print(f"\n📋 INFORMAÇÕES DO SERVIDOR:")
    print(f"• Porta: {port}")
    print(f"• URL: http://localhost:{port}")
    print(f"• Docs: http://localhost:{port}/docs")
    print(f"• Teste: http://localhost:{port}/test/categorias")
    
    print(f"\n🎯 COMO USAR NO CLAUDE DESKTOP:")
    print("1. Execute em outro terminal: python configure_claude_http.py")
    print("2. Reinicie o Claude Desktop")
    print("3. Use normalmente: 'Consulte as categorias do Omie'")
    
    print(f"\n🔄 Iniciando servidor na porta {port}...")
    print("   Pressione Ctrl+C para parar")
    
    # Definir variável de ambiente para a porta
    env = os.environ.copy()
    env["MCP_SERVER_PORT"] = port
    
    try:
        # Iniciar servidor
        subprocess.run([python_cmd, "run_server.py"], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)