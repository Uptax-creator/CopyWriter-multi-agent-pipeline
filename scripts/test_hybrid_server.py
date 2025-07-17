#!/usr/bin/env python3
"""
Script para testar servidor híbrido Omie MCP
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
import signal
import os

class HybridServerTester:
    """Classe para testar servidor híbrido"""
    
    def __init__(self):
        self.processes = {}
        
    def start_stdio_server(self) -> subprocess.Popen:
        """Inicia servidor no modo STDIO"""
        print("🚀 Iniciando servidor STDIO...")
        
        process = subprocess.Popen(
            [sys.executable, "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py", "--mode", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        self.processes["stdio"] = process
        time.sleep(2)  # Aguardar inicialização
        
        return process
    
    def start_http_server(self) -> subprocess.Popen:
        """Inicia servidor no modo HTTP"""
        print("🚀 Iniciando servidor HTTP...")
        
        process = subprocess.Popen(
            [sys.executable, "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py", "--mode", "http", "--port", "3001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes["http"] = process
        time.sleep(5)  # Aguardar inicialização HTTP
        
        return process
    
    def stop_server(self, name: str):
        """Para um servidor"""
        if name in self.processes:
            print(f"🛑 Parando servidor {name}...")
            process = self.processes[name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes[name]
    
    def test_stdio_server(self, process: subprocess.Popen) -> dict:
        """Testa servidor STDIO"""
        print("\n🧪 Testando servidor STDIO...")
        
        results = {
            "server": "STDIO",
            "tests": [],
            "success": True
        }
        
        # Teste 1: Initialize
        print("  📋 Teste 1: Initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-init",
            "method": "initialize",
            "params": {}
        }
        
        try:
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                test_passed = "result" in response and "error" not in response
                results["tests"].append({
                    "name": "initialize",
                    "passed": test_passed,
                    "response": response
                })
                print(f"    {'✅' if test_passed else '❌'} Initialize")
                if not test_passed:
                    results["success"] = False
            else:
                results["tests"].append({
                    "name": "initialize",
                    "passed": False,
                    "error": "No response received"
                })
                results["success"] = False
                print("    ❌ Initialize - No response")
        except Exception as e:
            results["tests"].append({
                "name": "initialize",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ Initialize - Error: {e}")
        
        # Teste 2: Tools List
        print("  📋 Teste 2: Tools List...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": "test-tools",
            "method": "tools/list"
        }
        
        try:
            request_json = json.dumps(tools_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                test_passed = "result" in response and "tools" in response.get("result", {})
                results["tests"].append({
                    "name": "tools/list",
                    "passed": test_passed,
                    "response": response
                })
                if test_passed:
                    tools_count = len(response["result"]["tools"])
                    print(f"    ✅ Tools List - {tools_count} ferramentas")
                else:
                    print("    ❌ Tools List")
                    results["success"] = False
            else:
                results["tests"].append({
                    "name": "tools/list",
                    "passed": False,
                    "error": "No response received"
                })
                results["success"] = False
                print("    ❌ Tools List - No response")
        except Exception as e:
            results["tests"].append({
                "name": "tools/list",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ Tools List - Error: {e}")
        
        # Teste 3: Tool Call
        print("  📋 Teste 3: Tool Call...")
        call_request = {
            "jsonrpc": "2.0",
            "id": "test-call",
            "method": "tools/call",
            "params": {
                "name": "testar_conexao",
                "arguments": {}
            }
        }
        
        try:
            request_json = json.dumps(call_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                test_passed = "result" in response and "content" in response.get("result", {})
                results["tests"].append({
                    "name": "tools/call",
                    "passed": test_passed,
                    "response": response
                })
                print(f"    {'✅' if test_passed else '❌'} Tool Call")
                if not test_passed:
                    results["success"] = False
            else:
                results["tests"].append({
                    "name": "tools/call",
                    "passed": False,
                    "error": "No response received"
                })
                results["success"] = False
                print("    ❌ Tool Call - No response")
        except Exception as e:
            results["tests"].append({
                "name": "tools/call",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ Tool Call - Error: {e}")
        
        return results
    
    def test_http_server(self) -> dict:
        """Testa servidor HTTP"""
        print("\n🧪 Testando servidor HTTP...")
        
        results = {
            "server": "HTTP",
            "tests": [],
            "success": True
        }
        
        base_url = "http://localhost:3001"
        
        # Teste 1: Health Check
        print("  📋 Teste 1: Health Check...")
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            test_passed = response.status_code == 200
            results["tests"].append({
                "name": "health_check",
                "passed": test_passed,
                "status_code": response.status_code,
                "response": response.json() if test_passed else None
            })
            print(f"    {'✅' if test_passed else '❌'} Health Check")
            if not test_passed:
                results["success"] = False
        except Exception as e:
            results["tests"].append({
                "name": "health_check",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ Health Check - Error: {e}")
        
        # Teste 2: MCP Initialize
        print("  📋 Teste 2: MCP Initialize...")
        try:
            response = requests.post(f"{base_url}/mcp/initialize", timeout=5)
            test_passed = response.status_code == 200
            results["tests"].append({
                "name": "mcp_initialize",
                "passed": test_passed,
                "status_code": response.status_code,
                "response": response.json() if test_passed else None
            })
            print(f"    {'✅' if test_passed else '❌'} MCP Initialize")
            if not test_passed:
                results["success"] = False
        except Exception as e:
            results["tests"].append({
                "name": "mcp_initialize",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ MCP Initialize - Error: {e}")
        
        # Teste 3: MCP Tools List
        print("  📋 Teste 3: MCP Tools List...")
        try:
            response = requests.get(f"{base_url}/mcp/tools", timeout=5)
            test_passed = response.status_code == 200
            if test_passed:
                data = response.json()
                tools_count = len(data.get("tools", []))
                print(f"    ✅ MCP Tools List - {tools_count} ferramentas")
            else:
                print("    ❌ MCP Tools List")
                results["success"] = False
            
            results["tests"].append({
                "name": "mcp_tools_list",
                "passed": test_passed,
                "status_code": response.status_code,
                "response": response.json() if test_passed else None
            })
        except Exception as e:
            results["tests"].append({
                "name": "mcp_tools_list",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ MCP Tools List - Error: {e}")
        
        # Teste 4: Tool Call
        print("  📋 Teste 4: Tool Call...")
        try:
            payload = {"arguments": {}}
            response = requests.post(f"{base_url}/mcp/tools/testar_conexao", json=payload, timeout=5)
            test_passed = response.status_code == 200
            results["tests"].append({
                "name": "mcp_tool_call",
                "passed": test_passed,
                "status_code": response.status_code,
                "response": response.json() if test_passed else None
            })
            print(f"    {'✅' if test_passed else '❌'} Tool Call")
            if not test_passed:
                results["success"] = False
        except Exception as e:
            results["tests"].append({
                "name": "mcp_tool_call",
                "passed": False,
                "error": str(e)
            })
            results["success"] = False
            print(f"    ❌ Tool Call - Error: {e}")
        
        return results
    
    def run_tests(self):
        """Executa todos os testes"""
        print("🧪 Iniciando testes do servidor híbrido...")
        print("=" * 60)
        
        results = {
            "stdio": None,
            "http": None
        }
        
        # Testar STDIO
        try:
            stdio_process = self.start_stdio_server()
            results["stdio"] = self.test_stdio_server(stdio_process)
            self.stop_server("stdio")
        except Exception as e:
            results["stdio"] = {"error": f"Failed to test STDIO server: {str(e)}"}
        
        # Testar HTTP
        try:
            http_process = self.start_http_server()
            results["http"] = self.test_http_server()
            self.stop_server("http")
        except Exception as e:
            results["http"] = {"error": f"Failed to test HTTP server: {str(e)}"}
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL - SERVIDOR HÍBRIDO")
        print("=" * 60)
        
        for mode, result in results.items():
            print(f"\n🔧 Modo {mode.upper()}:")
            
            if result is None:
                print("  ❌ Não testado")
                continue
            
            if "error" in result:
                print(f"  ❌ Erro: {result['error']}")
                continue
            
            if result.get("success"):
                print("  ✅ Todos os testes passaram")
            else:
                print("  ❌ Alguns testes falharam")
            
            for test in result.get("tests", []):
                status = "✅" if test["passed"] else "❌"
                print(f"    {status} {test['name']}")
        
        # Salvar relatório
        report_file = f"/Users/kleberdossantosribeiro/omie-mcp/hybrid_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Relatório salvo em: {report_file}")
        
        return results

def main():
    """Função principal"""
    tester = HybridServerTester()
    
    # Configurar handler para Ctrl+C
    def signal_handler(sig, frame):
        print("\n🛑 Interrompido pelo usuário")
        for name in list(tester.processes.keys()):
            tester.stop_server(name)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        results = tester.run_tests()
        
        # Verificar se todos os testes passaram
        all_passed = all(
            result.get("success", False) for result in results.values()
            if result is not None and "error" not in result
        )
        
        if all_passed:
            print("\n🎉 Todos os testes passaram! O servidor híbrido está funcionando corretamente.")
            print("\n📋 Próximos passos:")
            print("1. Configure Claude Desktop para usar: python omie_mcp_server_hybrid.py --mode stdio")
            print("2. Use integrações web com: python omie_mcp_server_hybrid.py --mode http")
            sys.exit(0)
        else:
            print("\n⚠️  Alguns testes falharam. Verifique a configuração do servidor.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)
    
    finally:
        # Limpar processos
        for name in list(tester.processes.keys()):
            tester.stop_server(name)

if __name__ == "__main__":
    main()