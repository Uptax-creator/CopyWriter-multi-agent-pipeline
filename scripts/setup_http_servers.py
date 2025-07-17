#!/usr/bin/env python3
"""
Script para configurar servidores HTTP MCP
"""

import subprocess
import sys
import time
import requests
import json
import os
from pathlib import Path

def start_omie_http_server():
    """Inicia servidor HTTP Omie"""
    
    print("🚀 Iniciando servidor HTTP Omie...")
    
    try:
        # Verificar se servidor híbrido existe
        omie_hybrid = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
        if not os.path.exists(omie_hybrid):
            print(f"❌ Servidor híbrido não encontrado: {omie_hybrid}")
            return None
        
        # Iniciar servidor HTTP
        process = subprocess.Popen([
            sys.executable, omie_hybrid, 
            "--mode", "http", 
            "--port", "3001",
            "--host", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ Aguardando inicialização do servidor...")
        time.sleep(5)
        
        # Verificar se servidor está rodando
        try:
            response = requests.get("http://localhost:3001", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor HTTP Omie iniciado com sucesso!")
                print(f"📋 URL: http://localhost:3001")
                print(f"📋 Documentação: http://localhost:3001/docs")
                return process
            else:
                print(f"❌ Servidor retornou status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro ao conectar com servidor: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def start_nibo_http_server():
    """Inicia servidor HTTP Nibo"""
    
    print("🚀 Iniciando servidor HTTP Nibo...")
    
    try:
        # Verificar se servidor híbrido existe
        nibo_hybrid = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py"
        if not os.path.exists(nibo_hybrid):
            print(f"❌ Servidor híbrido não encontrado: {nibo_hybrid}")
            return None
        
        # Iniciar servidor HTTP
        process = subprocess.Popen([
            sys.executable, nibo_hybrid, 
            "--mode", "http", 
            "--port", "3002",
            "--host", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ Aguardando inicialização do servidor...")
        time.sleep(5)
        
        # Verificar se servidor está rodando
        try:
            response = requests.get("http://localhost:3002", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor HTTP Nibo iniciado com sucesso!")
                print(f"📋 URL: http://localhost:3002")
                print(f"📋 Documentação: http://localhost:3002/docs")
                return process
            else:
                print(f"❌ Servidor retornou status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro ao conectar com servidor: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def test_http_servers():
    """Testa servidores HTTP"""
    
    print("\n🧪 Testando servidores HTTP...")
    
    # Testar Omie
    print("\n📋 Testando servidor Omie...")
    try:
        # Testar endpoint básico
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("  ✅ Endpoint raiz OK")
        
        # Testar MCP tools
        response = requests.get("http://localhost:3001/mcp/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools_count = len(data.get("tools", []))
            print(f"  ✅ MCP tools OK - {tools_count} ferramentas")
        
        # Testar tool call
        payload = {"arguments": {}}
        response = requests.post("http://localhost:3001/mcp/tools/testar_conexao", json=payload, timeout=5)
        if response.status_code == 200:
            print("  ✅ Tool call OK")
        
        print("  🎉 Servidor Omie HTTP funcionando!")
        
    except Exception as e:
        print(f"  ❌ Erro no servidor Omie: {e}")
    
    # Testar Nibo
    print("\n📋 Testando servidor Nibo...")
    try:
        # Testar endpoint básico
        response = requests.get("http://localhost:3002", timeout=5)
        if response.status_code == 200:
            print("  ✅ Endpoint raiz OK")
        
        # Testar MCP tools
        response = requests.get("http://localhost:3002/mcp/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools_count = len(data.get("tools", []))
            print(f"  ✅ MCP tools OK - {tools_count} ferramentas")
        
        # Testar tool call
        payload = {"arguments": {}}
        response = requests.post("http://localhost:3002/mcp/tools/testar_conexao", json=payload, timeout=5)
        if response.status_code == 200:
            print("  ✅ Tool call OK")
        
        # Testar ferramenta específica do Nibo
        response = requests.post("http://localhost:3002/mcp/tools/consultar_socios", json=payload, timeout=5)
        if response.status_code == 200:
            print("  ✅ Ferramenta específica Nibo OK")
        
        print("  🎉 Servidor Nibo HTTP funcionando!")
        
    except Exception as e:
        print(f"  ❌ Erro no servidor Nibo: {e}")

def create_http_client_config():
    """Cria configuração para cliente HTTP MCP"""
    
    print("\n📝 Criando configuração para cliente HTTP...")
    
    # Configuração para Claude Desktop com cliente HTTP
    http_config = {
        "mcpServers": {
            "omie-erp-http": {
                "command": "python3",
                "args": [
                    "/Users/kleberdossantosribeiro/omie-mcp/claude_mcp_client_parameterized.py",
                    "--server-url", "http://localhost:3001",
                    "--server-name", "omie-erp"
                ]
            },
            "nibo-erp-http": {
                "command": "python3",
                "args": [
                    "/Users/kleberdossantosribeiro/omie-mcp/claude_mcp_client_parameterized.py",
                    "--server-url", "http://localhost:3002",
                    "--server-name", "nibo-erp"
                ]
            }
        }
    }
    
    # Salvar configuração
    config_file = "/Users/kleberdossantosribeiro/omie-mcp/claude_desktop_config_http.json"
    with open(config_file, 'w') as f:
        json.dump(http_config, f, indent=2)
    
    print(f"✅ Configuração HTTP salva em: {config_file}")
    print("\n📋 Para usar esta configuração:")
    print("1. Copie o conteúdo para: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("2. Mantenha os servidores HTTP rodando")
    print("3. Reinicie o Claude Desktop")
    
    return config_file

def main():
    """Função principal"""
    
    print("🔧 Configurador de Servidores HTTP MCP")
    print("=" * 45)
    
    # Iniciar servidores HTTP
    omie_process = start_omie_http_server()
    nibo_process = start_nibo_http_server()
    
    if not omie_process and not nibo_process:
        print("\n❌ Nenhum servidor HTTP foi iniciado")
        return
    
    # Testar servidores
    test_http_servers()
    
    # Criar configuração
    config_file = create_http_client_config()
    
    print("\n" + "="*45)
    print("🎉 Servidores HTTP configurados!")
    print("\n📋 Servidores rodando:")
    if omie_process:
        print("  ✅ Omie HTTP: http://localhost:3001")
    if nibo_process:
        print("  ✅ Nibo HTTP: http://localhost:3002")
    
    print(f"\n📋 Configuração salva em: {config_file}")
    print("\n⚠️  IMPORTANTE: Mantenha este terminal aberto para os servidores continuarem rodando!")
    
    # Aguardar entrada do usuário
    try:
        input("\n Pressione Enter para parar os servidores...")
    except KeyboardInterrupt:
        pass
    
    # Parar servidores
    print("\n🛑 Parando servidores...")
    if omie_process:
        omie_process.terminate()
        print("  ✅ Servidor Omie parado")
    if nibo_process:
        nibo_process.terminate()
        print("  ✅ Servidor Nibo parado")

if __name__ == "__main__":
    main()