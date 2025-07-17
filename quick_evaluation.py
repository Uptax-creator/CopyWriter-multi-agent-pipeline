#!/usr/bin/env python3
"""
Script de avaliação rápida dos serviços MCP
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path

def check_files_exist():
    """Verifica se os arquivos de script existem"""
    print("🔍 Verificando arquivos de script...")
    
    files_to_check = [
        "scripts/service_toggle.py",
        "scripts/comprehensive_test_all_tools.py", 
        "scripts/extract_all_tools.py",
        "omie_mcp_server_hybrid.py",
        "nibo-mcp/nibo_mcp_server_hybrid.py"
    ]
    
    results = {}
    for file_path in files_to_check:
        full_path = os.path.join("/Users/kleberdossantosribeiro/omie-mcp", file_path)
        exists = os.path.exists(full_path)
        results[file_path] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    return results

def test_http_servers():
    """Testa se servidores HTTP estão respondendo"""
    print("\n🌐 Testando servidores HTTP...")
    
    servers = {
        "Omie MCP": "http://localhost:3001",
        "Nibo MCP": "http://localhost:3002"
    }
    
    results = {}
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results[name] = {"status": "online", "url": url}
                print(f"  ✅ {name}: Online ({url})")
            else:
                results[name] = {"status": "error", "error": f"HTTP {response.status_code}"}
                print(f"  ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            results[name] = {"status": "offline", "error": str(e)}
            print(f"  ❌ {name}: Offline - {e}")
    
    return results

def test_single_tool_stdio():
    """Testa uma ferramenta via STDIO"""
    print("\n📡 Testando ferramenta via STDIO...")
    
    script_path = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    
    if not os.path.exists(script_path):
        print(f"  ❌ Script não encontrado: {script_path}")
        return False
    
    try:
        # Testar comando simples
        process = subprocess.Popen([
            sys.executable, script_path, "--mode", "stdio"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Enviar inicialização
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-init",
            "method": "initialize",
            "params": {}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Ler resposta com timeout
        try:
            response_line = process.stdout.readline()
            process.terminate()
            
            if response_line and "jsonrpc" in response_line:
                print(f"  ✅ STDIO funcionando - resposta recebida")
                return True
            else:
                print(f"  ❌ STDIO não respondeu corretamente")
                return False
                
        except Exception as e:
            process.terminate()
            print(f"  ❌ Erro no STDIO: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao executar STDIO: {e}")
        return False

def test_claude_config():
    """Verifica configuração do Claude Desktop"""
    print("\n🔧 Verificando configuração do Claude Desktop...")
    
    config_path = "/Users/kleberdossantosribeiro/Library/Application Support/Claude/claude_desktop_config.json"
    
    if not os.path.exists(config_path):
        print(f"  ❌ Arquivo de configuração não encontrado: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        mcp_servers = config.get("mcpServers", {})
        print(f"  📋 Servidores MCP configurados: {len(mcp_servers)}")
        
        for server_name, server_config in mcp_servers.items():
            args = server_config.get("args", [])
            if args:
                script_path = args[0]
                script_exists = os.path.exists(script_path)
                status = "✅" if script_exists else "❌"
                print(f"  {status} {server_name}: {script_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao ler configuração: {e}")
        return False

def discover_tools_simple():
    """Descobre ferramentas de forma simples"""
    print("\n🔍 Descobrindo ferramentas disponíveis...")
    
    tools_found = {"omie": [], "nibo": []}
    
    # Tentar via HTTP se estiver rodando
    for service, port in [("omie", 3001), ("nibo", 3002)]:
        try:
            url = f"http://localhost:{port}/mcp/tools"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tools = [tool["name"] for tool in data.get("tools", [])]
                tools_found[service] = tools
                print(f"  ✅ {service.upper()}: {len(tools)} ferramentas via HTTP")
            else:
                print(f"  ❌ {service.upper()}: HTTP não disponível")
        except:
            print(f"  ❌ {service.upper()}: Não foi possível conectar via HTTP")
    
    return tools_found

def run_quick_evaluation():
    """Executa avaliação rápida completa"""
    print("🚀 AVALIAÇÃO RÁPIDA DOS SERVIÇOS MCP")
    print("=" * 50)
    
    results = {
        "files": check_files_exist(),
        "http_servers": test_http_servers(),
        "stdio_test": test_single_tool_stdio(),
        "claude_config": test_claude_config(),
        "tools_discovered": discover_tools_simple()
    }
    
    # Resumo
    print("\n📊 RESUMO DA AVALIAÇÃO")
    print("-" * 30)
    
    files_ok = sum(1 for exists in results["files"].values() if exists)
    total_files = len(results["files"])
    print(f"Arquivos: {files_ok}/{total_files} OK")
    
    servers_online = sum(1 for server in results["http_servers"].values() if server["status"] == "online")
    total_servers = len(results["http_servers"])
    print(f"Servidores HTTP: {servers_online}/{total_servers} online")
    
    stdio_status = "✅" if results["stdio_test"] else "❌"
    print(f"STDIO: {stdio_status}")
    
    config_status = "✅" if results["claude_config"] else "❌"
    print(f"Claude Desktop Config: {config_status}")
    
    omie_tools = len(results["tools_discovered"]["omie"])
    nibo_tools = len(results["tools_discovered"]["nibo"])
    print(f"Ferramentas descobertas: Omie={omie_tools}, Nibo={nibo_tools}")
    
    # Salvar resultados
    output_file = "/Users/kleberdossantosribeiro/omie-mcp/quick_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    return results

if __name__ == "__main__":
    results = run_quick_evaluation()
    
    # Recomendações baseadas nos resultados
    print("\n💡 RECOMENDAÇÕES")
    print("-" * 20)
    
    if not all(results["files"].values()):
        print("1. Alguns arquivos de script estão ausentes")
    
    if not any(server["status"] == "online" for server in results["http_servers"].values()):
        print("2. Nenhum servidor HTTP está rodando - execute 'python scripts/service_toggle.py start-all'")
    
    if not results["stdio_test"]:
        print("3. Servidor STDIO não está funcionando corretamente")
    
    if not results["claude_config"]:
        print("4. Configuração do Claude Desktop precisa ser ajustada")
    
    total_tools = len(results["tools_discovered"]["omie"]) + len(results["tools_discovered"]["nibo"])
    if total_tools < 40:  # Esperado: 20 + 31 = 51
        print(f"5. Apenas {total_tools} ferramentas descobertas, menos que o esperado (51)")
    
    if all([
        all(results["files"].values()),
        any(server["status"] == "online" for server in results["http_servers"].values()),
        results["stdio_test"],
        results["claude_config"]
    ]):
        print("✅ Todos os componentes principais estão funcionando!")
    
    print(f"\n🎉 Avaliação concluída!")