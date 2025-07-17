#!/usr/bin/env python3
"""
Script para testar os servidores MCP corrigidos
"""

import asyncio
import json
import subprocess
import sys
import time
import signal
import os

class MCPTester:
    """Classe para testar servidores MCP"""
    
    def __init__(self):
        self.servers = {}
        
    def start_server(self, name: str, script_path: str) -> subprocess.Popen:
        """Inicia um servidor MCP"""
        print(f"🚀 Iniciando servidor {name}...")
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        self.servers[name] = process
        time.sleep(2)  # Aguardar inicialização
        
        return process
    
    def stop_server(self, name: str):
        """Para um servidor MCP"""
        if name in self.servers:
            print(f"🛑 Parando servidor {name}...")
            process = self.servers[name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.servers[name]
    
    def send_request(self, process: subprocess.Popen, request: dict) -> dict:
        """Envia requisição para servidor MCP"""
        request_json = json.dumps(request) + "\n"
        
        try:
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Aguardar resposta
            response_line = process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response received"}
        
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    def test_server(self, name: str, process: subprocess.Popen) -> dict:
        """Testa um servidor MCP"""
        print(f"\n🧪 Testando servidor {name}...")
        
        results = {
            "server": name,
            "tests": [],
            "success": True
        }
        
        # Teste 1: Initialize
        print("  📋 Teste 1: Initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": "test-init",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = self.send_request(process, init_request)
        test_result = {
            "name": "initialize",
            "request": init_request,
            "response": response,
            "passed": "result" in response and "error" not in response
        }
        results["tests"].append(test_result)
        
        if not test_result["passed"]:
            print(f"    ❌ Falhou: {response}")
            results["success"] = False
        else:
            print(f"    ✅ Passou")
        
        # Teste 2: Tools List
        print("  📋 Teste 2: Tools List...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": "test-tools",
            "method": "tools/list"
        }
        
        response = self.send_request(process, tools_request)
        test_result = {
            "name": "tools/list",
            "request": tools_request,
            "response": response,
            "passed": "result" in response and "tools" in response.get("result", {})
        }
        results["tests"].append(test_result)
        
        if not test_result["passed"]:
            print(f"    ❌ Falhou: {response}")
            results["success"] = False
        else:
            tools_count = len(response["result"]["tools"])
            print(f"    ✅ Passou - {tools_count} ferramentas disponíveis")
        
        # Teste 3: Tool Call (testar_conexao)
        print("  📋 Teste 3: Tool Call (testar_conexao)...")
        call_request = {
            "jsonrpc": "2.0",
            "id": "test-call",
            "method": "tools/call",
            "params": {
                "name": "testar_conexao",
                "arguments": {}
            }
        }
        
        response = self.send_request(process, call_request)
        test_result = {
            "name": "tools/call",
            "request": call_request,
            "response": response,
            "passed": "result" in response and "content" in response.get("result", {})
        }
        results["tests"].append(test_result)
        
        if not test_result["passed"]:
            print(f"    ❌ Falhou: {response}")
            results["success"] = False
        else:
            print(f"    ✅ Passou")
        
        # Teste 4: Invalid Method
        print("  📋 Teste 4: Invalid Method...")
        invalid_request = {
            "jsonrpc": "2.0",
            "id": "test-invalid",
            "method": "invalid/method"
        }
        
        response = self.send_request(process, invalid_request)
        test_result = {
            "name": "invalid_method",
            "request": invalid_request,
            "response": response,
            "passed": "error" in response and response.get("error", {}).get("code") == -32601
        }
        results["tests"].append(test_result)
        
        if not test_result["passed"]:
            print(f"    ❌ Falhou: {response}")
            results["success"] = False
        else:
            print(f"    ✅ Passou - Erro tratado corretamente")
        
        return results
    
    def run_tests(self):
        """Executa todos os testes"""
        print("🧪 Iniciando testes dos servidores MCP...")
        print("=" * 60)
        
        # Configurar caminhos
        omie_script = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_fixed.py"
        nibo_script = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_fixed.py"
        
        results = {}
        
        # Testar Omie MCP
        if os.path.exists(omie_script):
            try:
                omie_process = self.start_server("Omie", omie_script)
                results["omie"] = self.test_server("Omie", omie_process)
                self.stop_server("Omie")
            except Exception as e:
                results["omie"] = {"error": f"Failed to test Omie server: {str(e)}"}
        else:
            results["omie"] = {"error": "Omie server script not found"}
        
        # Testar Nibo MCP
        if os.path.exists(nibo_script):
            try:
                nibo_process = self.start_server("Nibo", nibo_script)
                results["nibo"] = self.test_server("Nibo", nibo_process)
                self.stop_server("Nibo")
            except Exception as e:
                results["nibo"] = {"error": f"Failed to test Nibo server: {str(e)}"}
        else:
            results["nibo"] = {"error": "Nibo server script not found"}
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)
        
        for server_name, result in results.items():
            print(f"\n🔧 Servidor {server_name.upper()}:")
            
            if "error" in result:
                print(f"  ❌ Erro: {result['error']}")
                continue
            
            if result.get("success"):
                print(f"  ✅ Todos os testes passaram")
            else:
                print(f"  ❌ Alguns testes falharam")
            
            for test in result.get("tests", []):
                status = "✅" if test["passed"] else "❌"
                print(f"    {status} {test['name']}")
        
        # Salvar relatório
        report_file = f"/Users/kleberdossantosribeiro/omie-mcp/test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Relatório salvo em: {report_file}")
        
        return results

def main():
    """Função principal"""
    tester = MCPTester()
    
    # Configurar handler para Ctrl+C
    def signal_handler(sig, frame):
        print("\n🛑 Interrompido pelo usuário")
        for name in list(tester.servers.keys()):
            tester.stop_server(name)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        results = tester.run_tests()
        
        # Verificar se todos os testes passaram
        all_passed = all(
            result.get("success", False) for result in results.values()
            if "error" not in result
        )
        
        if all_passed:
            print("\n🎉 Todos os testes passaram! Os servidores MCP estão funcionando corretamente.")
            sys.exit(0)
        else:
            print("\n⚠️  Alguns testes falharam. Verifique os servidores MCP.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)
    
    finally:
        # Limpar servidores
        for name in list(tester.servers.keys()):
            tester.stop_server(name)

if __name__ == "__main__":
    main()