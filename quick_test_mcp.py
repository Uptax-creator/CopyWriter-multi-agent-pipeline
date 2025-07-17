#!/usr/bin/env python3
"""
Teste rápido dos servidores MCP híbridos
"""

import subprocess
import json
import sys
import time

def test_omie_server():
    """Testa servidor Omie híbrido"""
    print("🧪 Testando servidor Omie híbrido...")
    
    try:
        # Iniciar servidor
        process = subprocess.Popen(
            ["python3", "omie_mcp_server_hybrid.py", "--mode", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Testar initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize",
            "params": {}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Ler resposta
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            
            # Verificar se response tem estrutura correta
            if "jsonrpc" in response and "id" in response and "result" in response:
                print("  ✅ Servidor Omie: Protocolo JSON-RPC correto")
                print(f"  📋 ID da resposta: {response['id']}")
                print(f"  📋 Versão protocolo: {response['result'].get('protocolVersion', 'N/A')}")
                return True
            else:
                print("  ❌ Servidor Omie: Resposta malformada")
                print(f"  📋 Resposta: {response}")
                return False
        else:
            print("  ❌ Servidor Omie: Sem resposta")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao testar servidor Omie: {e}")
        return False
    
    finally:
        if process:
            process.terminate()

def test_nibo_server():
    """Testa servidor Nibo híbrido"""
    print("\n🧪 Testando servidor Nibo híbrido...")
    
    try:
        # Iniciar servidor
        process = subprocess.Popen(
            ["python3", "nibo-mcp/nibo_mcp_server_hybrid.py", "--mode", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Testar initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "initialize",
            "params": {}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Ler resposta
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            
            # Verificar se response tem estrutura correta
            if "jsonrpc" in response and "id" in response and "result" in response:
                print("  ✅ Servidor Nibo: Protocolo JSON-RPC correto")
                print(f"  📋 ID da resposta: {response['id']}")
                print(f"  📋 Versão protocolo: {response['result'].get('protocolVersion', 'N/A')}")
                return True
            else:
                print("  ❌ Servidor Nibo: Resposta malformada")
                print(f"  📋 Resposta: {response}")
                return False
        else:
            print("  ❌ Servidor Nibo: Sem resposta")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao testar servidor Nibo: {e}")
        return False
    
    finally:
        if process:
            process.terminate()

def check_claude_config():
    """Verifica configuração do Claude Desktop"""
    print("\n🔍 Verificando configuração do Claude Desktop...")
    
    config_path = "/Users/kleberdossantosribeiro/Library/Application Support/Claude/claude_desktop_config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        mcp_servers = config.get("mcpServers", {})
        
        print(f"  📋 Servidores MCP configurados: {len(mcp_servers)}")
        
        for server_name, server_config in mcp_servers.items():
            print(f"  🔧 {server_name}:")
            print(f"    Comando: {server_config.get('command', 'N/A')}")
            
            args = server_config.get('args', [])
            if args:
                script_path = args[0]
                print(f"    Script: {script_path}")
                
                # Verificar se é híbrido
                if "hybrid" in script_path:
                    print("    ✅ Usando servidor híbrido")
                else:
                    print("    ⚠️  Não está usando servidor híbrido")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao ler configuração: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste Rápido dos Servidores MCP Híbridos")
    print("=" * 50)
    
    # Testar servidores
    omie_ok = test_omie_server()
    nibo_ok = test_nibo_server()
    
    # Verificar configuração
    config_ok = check_claude_config()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DO TESTE:")
    
    if omie_ok and nibo_ok and config_ok:
        print("✅ Todos os testes passaram!")
        print("🎉 Os servidores híbridos estão funcionando corretamente!")
        print("\n📋 Próximos passos:")
        print("1. Reinicie o Claude Desktop")
        print("2. Teste as ferramentas MCP")
        print("3. Os erros de protocolo devem estar resolvidos")
        
    else:
        print("❌ Alguns testes falharam:")
        print(f"  Omie: {'✅' if omie_ok else '❌'}")
        print(f"  Nibo: {'✅' if nibo_ok else '❌'}")
        print(f"  Config: {'✅' if config_ok else '❌'}")
        
        if not omie_ok or not nibo_ok:
            print("\n🔧 Possíveis soluções:")
            print("1. Verifique se Python está instalado")
            print("2. Verifique se os arquivos híbridos existem")
            print("3. Execute os scripts de consolidação")

if __name__ == "__main__":
    main()