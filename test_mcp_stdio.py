#!/usr/bin/env python3
"""
Teste do MCP Server em modo STDIO
"""

import json
import subprocess
import os

def test_mcp_stdio():
    """Testa o servidor MCP em modo STDIO"""
    
    print("🧪 Testando Omie MCP Server em modo STDIO...")
    
    # Caminho para o servidor
    server_path = os.path.join(os.path.dirname(__file__), "omie_mcp_server_hybrid.py")
    
    try:
        # Iniciar servidor
        process = subprocess.Popen(
            ["python3", server_path, "--mode", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Teste 1: Initialize
        print("📡 Enviando comando initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Ler resposta
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"✅ Initialize Response: {response}")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar resposta: {e}")
                print(f"Resposta bruta: {response_line}")
        
        # Teste 2: Tools List
        print("\n📋 Enviando comando tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        request_json = json.dumps(tools_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Ler resposta
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"✅ Tools List Response: {response}")
                
                # Listar ferramentas disponíveis
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"\n🔧 Ferramentas disponíveis ({len(tools)}):")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool.get('description', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar resposta: {e}")
                print(f"Resposta bruta: {response_line}")
        
        # Fechar processo
        process.stdin.close()
        process.terminate()
        process.wait(timeout=5)
        
        print("\n🎉 Teste MCP STDIO concluído!")
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - processo ainda está rodando (isso é normal)")
        process.kill()
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    test_mcp_stdio()