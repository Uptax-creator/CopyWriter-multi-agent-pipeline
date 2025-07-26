#!/usr/bin/env python3
"""
Teste de Integração N8N + Omie MCP Server
Simula requisições que o N8N faria ao servidor MCP
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List

class N8NIntegrationTester:
    """Testador de integração N8N"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        self.mcp_server_url = mcp_server_url
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_server_health(self) -> Dict[str, Any]:
        """Testa saúde do servidor"""
        print("🔍 Testando saúde do servidor...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.mcp_server_url}/") as response:
                    data = await response.json()
                    result = {
                        "test": "server_health",
                        "status": "success" if response.status == 200 else "failed",
                        "response_code": response.status,
                        "data": data,
                        "timestamp": time.time()
                    }
                    print(f"✅ Servidor funcionando: {data['name']} v{data['version']}")
                    return result
            
            except Exception as e:
                result = {
                    "test": "server_health",
                    "status": "failed",
                    "error": str(e),
                    "timestamp": time.time()
                }
                print(f"❌ Erro na saúde do servidor: {e}")
                return result
    
    async def test_tools_list(self) -> Dict[str, Any]:
        """Testa listagem de ferramentas"""
        print("📋 Testando listagem de ferramentas...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.mcp_server_url}/mcp/tools") as response:
                    data = await response.json()
                    tools = data.get('tools', [])
                    result = {
                        "test": "tools_list",
                        "status": "success" if response.status == 200 else "failed",
                        "tools_count": len(tools),
                        "tools": [tool['name'] for tool in tools],
                        "timestamp": time.time()
                    }
                    print(f"✅ {len(tools)} ferramentas encontradas: {[t['name'] for t in tools]}")
                    return result
            
            except Exception as e:
                result = {
                    "test": "tools_list",
                    "status": "failed", 
                    "error": str(e),
                    "timestamp": time.time()
                }
                print(f"❌ Erro na listagem de ferramentas: {e}")
                return result
    
    async def test_tool_execution(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Testa execução de uma ferramenta específica"""
        print(f"⚙️ Testando execução da ferramenta: {tool_name}")
        
        if arguments is None:
            arguments = {}
        
        payload = {"arguments": arguments}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_server_url}/mcp/tools/{tool_name}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    data = await response.json()
                    result = {
                        "test": f"tool_execution_{tool_name}",
                        "status": "success" if response.status == 200 else "failed",
                        "response_code": response.status,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "response": data,
                        "timestamp": time.time()
                    }
                    if response.status == 200:
                        print(f"✅ Ferramenta {tool_name} executada com sucesso")
                    else:
                        print(f"⚠️ Ferramenta {tool_name} retornou código {response.status}")
                    return result
            
            except Exception as e:
                result = {
                    "test": f"tool_execution_{tool_name}",
                    "status": "failed",
                    "error": str(e),
                    "tool_name": tool_name,
                    "timestamp": time.time()
                }
                print(f"❌ Erro na execução de {tool_name}: {e}")
                return result
    
    async def test_n8n_webhook_simulation(self) -> Dict[str, Any]:
        """Simula requisição que viria do N8N via webhook"""
        print("🔗 Simulando requisição N8N webhook...")
        
        # Simular dados que viriam do N8N
        webhook_data = {
            "tool_name": "consultar_categorias",
            "arguments": {
                "pagina": 1,
                "registros_por_pagina": 5
            },
            "source": "n8n_webhook",
            "workflow_id": "test_workflow_123"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_server_url}/mcp/tools/{webhook_data['tool_name']}",
                    json={"arguments": webhook_data['arguments']},
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "n8n-webhook/1.0",
                        "X-N8N-Workflow-ID": webhook_data['workflow_id']
                    }
                ) as response:
                    data = await response.json()
                    result = {
                        "test": "n8n_webhook_simulation",
                        "status": "success" if response.status == 200 else "failed",
                        "webhook_data": webhook_data,
                        "response": data,
                        "timestamp": time.time()
                    }
                    print("✅ Simulação N8N webhook funcionando")
                    return result
            
            except Exception as e:
                result = {
                    "test": "n8n_webhook_simulation",
                    "status": "failed",
                    "error": str(e),
                    "timestamp": time.time()
                }
                print(f"❌ Erro na simulação N8N: {e}")
                return result
    
    async def test_concurrent_requests(self) -> Dict[str, Any]:
        """Testa requisições concorrentes (simulando múltiplos workflows N8N)"""
        print("🔄 Testando requisições concorrentes...")
        
        tools_to_test = [
            ("testar_conexao", {}),
            ("consultar_categorias", {"pagina": 1, "registros_por_pagina": 3}),
            ("consultar_departamentos", {"pagina": 1, "registros_por_pagina": 3}),
            ("testar_conexao", {}),  # Duplicado para testar cache/performance
        ]
        
        start_time = time.time()
        tasks = [
            self.test_tool_execution(tool_name, args) 
            for tool_name, args in tools_to_test
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
            total_time = end_time - start_time
            
            result = {
                "test": "concurrent_requests",
                "status": "success" if successful == len(tools_to_test) else "partial",
                "total_requests": len(tools_to_test),
                "successful_requests": successful,
                "total_time_seconds": round(total_time, 2),
                "avg_time_per_request": round(total_time / len(tools_to_test), 2),
                "results": results,
                "timestamp": time.time()
            }
            
            print(f"✅ Testes concorrentes: {successful}/{len(tools_to_test)} sucessos em {total_time:.2f}s")
            return result
        
        except Exception as e:
            result = {
                "test": "concurrent_requests",
                "status": "failed",
                "error": str(e),
                "timestamp": time.time()
            }
            print(f"❌ Erro nos testes concorrentes: {e}")
            return result
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Executa suite completa de testes"""
        print("🧪 INICIANDO SUITE COMPLETA DE TESTES N8N + OMIE MCP")
        print("=" * 60)
        
        start_time = time.time()
        
        # Executar todos os testes
        tests = [
            self.test_server_health(),
            self.test_tools_list(),
            self.test_tool_execution("testar_conexao"),
            self.test_tool_execution("consultar_categorias", {"pagina": 1, "registros_por_pagina": 3}),
            self.test_n8n_webhook_simulation(),
            self.test_concurrent_requests()
        ]
        
        print("\n🔄 Executando testes...")
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Processar resultados
        successful_tests = sum(
            1 for r in results 
            if isinstance(r, dict) and r.get('status') in ['success', 'partial']
        )
        
        test_summary = {
            "test_suite": "n8n_omie_mcp_integration",
            "total_tests": len(tests),
            "successful_tests": successful_tests,
            "failed_tests": len(tests) - successful_tests,
            "success_rate": round((successful_tests / len(tests)) * 100, 1),
            "total_time_seconds": round(total_time, 2),
            "results": results,
            "timestamp": time.time(),
            "verdict": "PASSED" if successful_tests == len(tests) else "PARTIAL" if successful_tests > 0 else "FAILED"
        }
        
        # Imprimir resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        print(f"✅ Testes bem-sucedidos: {successful_tests}/{len(tests)}")
        print(f"📈 Taxa de sucesso: {test_summary['success_rate']}%")
        print(f"⏱️ Tempo total: {total_time:.2f} segundos")
        print(f"🎯 Veredicto: {test_summary['verdict']}")
        
        if test_summary['verdict'] == "PASSED":
            print("\n🎉 TODOS OS TESTES PASSARAM! N8N + OMIE MCP ESTÁ PRONTO!")
        elif test_summary['verdict'] == "PARTIAL":
            print("\n⚠️ ALGUNS TESTES FALHARAM - VERIFICAR LOGS ACIMA")
        else:
            print("\n❌ TESTES FALHARAM - VERIFICAR CONFIGURAÇÃO")
        
        return test_summary
    
    def save_results(self, results: Dict[str, Any], filename: str = "n8n_integration_test_results.json"):
        """Salva resultados dos testes"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Resultados salvos em: {filename}")

async def main():
    """Função principal"""
    tester = N8NIntegrationTester()
    results = await tester.run_full_test_suite()
    tester.save_results(results)
    
    # Sugestões baseadas nos resultados
    print("\n💡 PRÓXIMOS PASSOS:")
    if results['verdict'] == "PASSED":
        print("1. ✅ Importar workflow N8N: n8n_workflows_oficial/3_webhook_integration.json")
        print("2. ✅ Testar no N8N real com webhook")
        print("3. ✅ Configurar monitoramento automático")
    else:
        print("1. 🔧 Verificar logs de erro acima")
        print("2. 🔧 Reiniciar servidor MCP se necessário")
        print("3. 🔧 Testar endpoints individualmente")

if __name__ == "__main__":
    asyncio.run(main())