#!/usr/bin/env python3
"""
Script para iniciar servidores HTTP puros MCP
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_omie_server():
    """Inicia servidor HTTP Omie"""
    print("🚀 Iniciando servidor HTTP Omie...")
    
    script_path = "/Users/kleberdossantosribeiro/omie-mcp/omie_http_server_pure.py"
    
    if not os.path.exists(script_path):
        print(f"❌ Script não encontrado: {script_path}")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, script_path,
            "--port", "3001",
            "--host", "localhost"
        ])
        
        print(f"✅ Servidor Omie iniciado!")
        print(f"📋 PID: {process.pid}")
        print(f"🔗 URL: http://localhost:3001")
        print(f"🔗 Ferramentas: http://localhost:3001/mcp/tools")
        
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor Omie: {e}")
        return None

def start_nibo_server():
    """Inicia servidor HTTP Nibo"""
    print(f"\n🚀 Iniciando servidor HTTP Nibo...")
    
    script_path = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_http_server_pure.py"
    
    if not os.path.exists(script_path):
        print(f"❌ Script não encontrado: {script_path}")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, script_path,
            "--port", "3002",
            "--host", "localhost"
        ])
        
        print(f"✅ Servidor Nibo iniciado!")
        print(f"📋 PID: {process.pid}")
        print(f"🔗 URL: http://localhost:3002")
        print(f"🔗 Ferramentas: http://localhost:3002/mcp/tools")
        
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor Nibo: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 INICIADOR DE SERVIDORES HTTP MCP")
    print("=" * 45)
    
    # Iniciar servidores
    omie_process = start_omie_server()
    nibo_process = start_nibo_server()
    
    if not omie_process and not nibo_process:
        print(f"\n❌ Nenhum servidor foi iniciado")
        return
    
    # Aguardar um pouco para inicialização
    print(f"\n⏳ Aguardando inicialização dos servidores...")
    time.sleep(3)
    
    # Resumo
    print(f"\n🎉 SERVIDORES INICIADOS!")
    print("-" * 30)
    
    if omie_process:
        print(f"✅ Omie MCP: http://localhost:3001 (PID: {omie_process.pid})")
    
    if nibo_process:
        print(f"✅ Nibo MCP: http://localhost:3002 (PID: {nibo_process.pid})")
    
    print(f"\n📋 CONFIGURAÇÃO CLAUDE DESKTOP:")
    print("Os servidores estão configurados para usar HTTP via cliente parameterizado.")
    print("Reinicie o Claude Desktop para aplicar as mudanças.")
    
    print(f"\n💡 COMANDOS ÚTEIS:")
    print("# Testar Omie")
    print("curl http://localhost:3001/mcp/tools")
    print("")
    print("# Testar Nibo") 
    print("curl http://localhost:3002/mcp/tools")
    print("")
    print("# Testar ferramenta Omie")
    print('curl -X POST http://localhost:3001/mcp/tools/testar_conexao -H "Content-Type: application/json" -d \'{"arguments": {}}\'')
    print("")
    print("# Testar ferramenta Nibo")
    print('curl -X POST http://localhost:3002/mcp/tools/testar_conexao -H "Content-Type: application/json" -d \'{"arguments": {}}\'')
    
    print(f"\n⚠️  IMPORTANTE: Mantenha este terminal aberto para os servidores continuarem rodando!")
    
    # Aguardar entrada do usuário
    try:
        input(f"\n⌨️  Pressione Enter para parar os servidores...")
    except KeyboardInterrupt:
        pass
    
    # Parar servidores
    print(f"\n🛑 Parando servidores...")
    
    if omie_process:
        omie_process.terminate()
        print("  ✅ Servidor Omie parado")
    
    if nibo_process:
        nibo_process.terminate()
        print("  ✅ Servidor Nibo parado")
    
    print(f"\n🎉 Todos os servidores foram parados!")

if __name__ == "__main__":
    main()