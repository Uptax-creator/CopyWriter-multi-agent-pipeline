#!/usr/bin/env python3
"""
🧪 Testador de Ferramentas Omie MCP Server
Testa todas as ferramentas e gera relatório detalhado
"""

import asyncio
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import requests
import aiohttp

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.config import config

class ToolTester:
    """Testador de ferramentas MCP"""
    
    def __init__(self):
        self.server_url = f"http://{config.server_host}:{config.server_port}"
        self.results = {}
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_server_health(self) -> bool:
        """Testa se o servidor está rodando"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        self.log(f"Servidor saudável: {health_data.get('status', 'unknown')}")
                        return True
                    else:
                        self.log(f"Servidor não saudável: HTTP {response.status}", "ERROR")
                        return False
        except Exception as e:
            self.log(f"Servidor inacessível: {e}", "ERROR")
            return False
    
    async def get_available_tools(self) -> List[Dict]:
        """Obtém lista de ferramentas disponíveis"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/tools") as response:
                    if response.status == 200:
                        data = await response.json()
                        tools = data.get("tools", [])
                        self.log(f"Encontradas {len(tools)} ferramentas")
                        return tools
                    else:
                        self.log(f"Erro ao obter ferramentas: HTTP {response.status}", "ERROR")
                        return []
        except Exception as e:
            self.log(f"Erro ao conectar: {e}", "ERROR")
            return []
    
    async def test_tool(self, tool: Dict) -> Dict:
        """Testa uma ferramenta específica"""
        tool_name = tool.get("name", "unknown")
        self.log(f"Testando ferramenta: {tool_name}")
        
        result = {
            "name": tool_name,
            "description": tool.get("description", ""),
            "status": "unknown",
            "response_time": 0,
            "error": None,
            "response_data": None,
            "test_params": {}
        }
        
        try:
            # Determinar parâmetros de teste baseado no nome da ferramenta
            test_params = self.get_test_params(tool_name)
            result["test_params"] = test_params
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "name": tool_name,
                    "arguments": test_params
                }
                
                async with session.post(
                    f"{self.server_url}/tools/call",
                    json=payload,
                    timeout=30
                ) as response:
                    result["response_time"] = round((time.time() - start_time) * 1000, 2)  # ms
                    
                    if response.status == 200:
                        response_data = await response.json()
                        result["status"] = "success"
                        result["response_data"] = response_data
                        self.log(f"✅ {tool_name}: OK ({result['response_time']}ms)")
                    else:
                        result["status"] = "http_error"
                        result["error"] = f"HTTP {response.status}"
                        error_text = await response.text()
                        result["response_data"] = error_text
                        self.log(f"❌ {tool_name}: HTTP {response.status}", "ERROR")
                        
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error"] = "Timeout após 30s"
            result["response_time"] = 30000
            self.log(f"⏰ {tool_name}: Timeout", "WARN")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["response_time"] = round((time.time() - start_time) * 1000, 2) if 'start_time' in locals() else 0
            self.log(f"❌ {tool_name}: {e}", "ERROR")
        
        return result
    
    def get_test_params(self, tool_name: str) -> Dict:
        """Retorna parâmetros de teste para cada ferramenta"""
        
        # Parâmetros seguros para teste (apenas consultas)
        test_params = {
            # Consultas básicas
            "consultar_categorias": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_departamentos": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_tipos_documento": {},
            "consultar_contas_pagar": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_contas_receber": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_clientes": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_fornecedores": {"pagina": 1, "registros_por_pagina": 5},
            
            # Consultas específicas (teste apenas se fornecido código válido)
            "consultar_cliente_por_codigo": {"codigo_cliente_omie": 1},
            "consultar_fornecedor_por_codigo": {"codigo_cliente_omie": 1},
            "buscar_dados_contato_cliente": {"codigo_cliente_omie": 1},
            "buscar_dados_contato_fornecedor": {"codigo_cliente_omie": 1},
            
            # Relatórios (apenas com parâmetros mínimos)
            "relatorio_contas_receber_detalhado": {"pagina": 1, "registros_por_pagina": 5},
            "relatorio_contas_pagar_detalhado": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_contas_receber_com_cliente_detalhado": {"pagina": 1, "registros_por_pagina": 5},
            "consultar_contas_pagar_com_fornecedor_detalhado": {"pagina": 1, "registros_por_pagina": 5},
        }\n        \n        # NOTA: Ferramentas de CRUD (incluir, alterar, excluir) são PULADAS nos testes\n        # para evitar modificações acidentais no sistema de produção\n        \n        return test_params.get(tool_name, {})\n    \n    def is_safe_to_test(self, tool_name: str) -> bool:\n        \"\"\"Verifica se é seguro testar a ferramenta (apenas consultas)\"\"\"\n        \n        unsafe_operations = [\n            \"incluir_\", \"alterar_\", \"excluir_\", \"criar_\", \"atualizar_\",\n            \"cadastrar_\", \"deletar_\", \"remover_\"\n        ]\n        \n        for unsafe in unsafe_operations:\n            if unsafe in tool_name.lower():\n                return False\n        \n        return True\n    \n    async def run_tests(self) -> Dict:\n        \"\"\"Executa todos os testes\"\"\"\n        self.log(\"🚀 Iniciando testes das ferramentas Omie MCP\")\n        \n        # Verificar se servidor está rodando\n        if not await self.test_server_health():\n            return {\n                \"success\": False,\n                \"error\": \"Servidor inacessível\",\n                \"timestamp\": self.start_time.isoformat()\n            }\n        \n        # Obter ferramentas disponíveis\n        tools = await self.get_available_tools()\n        if not tools:\n            return {\n                \"success\": False,\n                \"error\": \"Nenhuma ferramenta encontrada\",\n                \"timestamp\": self.start_time.isoformat()\n            }\n        \n        # Testar cada ferramenta\n        results = []\n        safe_tools = [tool for tool in tools if self.is_safe_to_test(tool.get(\"name\", \"\"))]\n        unsafe_tools = [tool for tool in tools if not self.is_safe_to_test(tool.get(\"name\", \"\"))]\n        \n        self.log(f\"Testando {len(safe_tools)} ferramentas seguras\")\n        self.log(f\"Pulando {len(unsafe_tools)} ferramentas de modificação\")\n        \n        for tool in safe_tools:\n            result = await self.test_tool(tool)\n            results.append(result)\n            \n            # Pequeno delay entre testes\n            await asyncio.sleep(0.5)\n        \n        # Adicionar ferramentas não testadas\n        for tool in unsafe_tools:\n            results.append({\n                \"name\": tool.get(\"name\", \"unknown\"),\n                \"description\": tool.get(\"description\", \"\"),\n                \"status\": \"skipped\",\n                \"reason\": \"Operação de modificação - pulada por segurança\",\n                \"response_time\": 0\n            })\n        \n        # Compilar relatório final\n        end_time = datetime.now()\n        duration = (end_time - self.start_time).total_seconds()\n        \n        success_count = len([r for r in results if r[\"status\"] == \"success\"])\n        error_count = len([r for r in results if r[\"status\"] in [\"error\", \"http_error\", \"timeout\"]])\n        skipped_count = len([r for r in results if r[\"status\"] == \"skipped\"])\n        \n        report = {\n            \"success\": True,\n            \"timestamp\": self.start_time.isoformat(),\n            \"duration_seconds\": round(duration, 2),\n            \"server_url\": self.server_url,\n            \"summary\": {\n                \"total_tools\": len(tools),\n                \"tested_tools\": len(safe_tools),\n                \"skipped_tools\": len(unsafe_tools),\n                \"successful_tests\": success_count,\n                \"failed_tests\": error_count,\n                \"success_rate\": round((success_count / len(safe_tools)) * 100, 1) if safe_tools else 0\n            },\n            \"results\": results,\n            \"skipped_tools\": [tool.get(\"name\") for tool in unsafe_tools]\n        }\n        \n        return report\n    \n    def save_report(self, report: Dict, filename: str = None):\n        \"\"\"Salva relatório em arquivo JSON\"\"\"\n        if not filename:\n            timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n            filename = f\"test_report_{timestamp}.json\"\n        \n        report_path = PROJECT_ROOT / \"logs\" / filename\n        report_path.parent.mkdir(exist_ok=True)\n        \n        with open(report_path, \"w\", encoding=\"utf-8\") as f:\n            json.dump(report, f, indent=2, ensure_ascii=False)\n        \n        self.log(f\"Relatório salvo em: {report_path}\")\n        return report_path\n    \n    def print_summary(self, report: Dict):\n        \"\"\"Exibe resumo dos testes\"\"\"\n        if not report.get(\"success\"):\n            print(f\"❌ Testes falharam: {report.get('error')}\")\n            return\n        \n        summary = report[\"summary\"]\n        \n        print(\"\\n📊 RESUMO DOS TESTES\")\n        print(\"=\" * 50)\n        print(f\"🕐 Duração: {report['duration_seconds']}s\")\n        print(f\"🔧 Total de ferramentas: {summary['total_tools']}\")\n        print(f\"🧪 Ferramentas testadas: {summary['tested_tools']}\")\n        print(f\"⏭️  Ferramentas puladas: {summary['skipped_tools']}\")\n        print(f\"✅ Testes bem-sucedidos: {summary['successful_tests']}\")\n        print(f\"❌ Testes falharam: {summary['failed_tests']}\")\n        print(f\"📈 Taxa de sucesso: {summary['success_rate']}%\")\n        \n        # Mostrar detalhes dos testes falhados\n        failed_tests = [r for r in report[\"results\"] if r[\"status\"] in [\"error\", \"http_error\", \"timeout\"]]\n        if failed_tests:\n            print(\"\\n❌ TESTES FALHADOS:\")\n            for test in failed_tests:\n                print(f\"   • {test['name']}: {test.get('error', 'Erro desconhecido')}\")\n        \n        # Mostrar ferramentas puladas\n        if report.get(\"skipped_tools\"):\n            print(\"\\n⏭️  FERRAMENTAS PULADAS (Operações de Modificação):\")\n            for tool in report[\"skipped_tools\"]:\n                print(f\"   • {tool}\")\n\nasync def main():\n    \"\"\"Função principal\"\"\"\n    tester = ToolTester()\n    \n    try:\n        report = await tester.run_tests()\n        report_path = tester.save_report(report)\n        tester.print_summary(report)\n        \n        print(f\"\\n📋 Relatório completo: {report_path}\")\n        \n        # Retornar código de saída baseado no sucesso\n        if report.get(\"success\") and report[\"summary\"][\"failed_tests\"] == 0:\n            print(\"\\n🎉 Todos os testes passaram!\")\n            return 0\n        else:\n            print(\"\\n⚠️  Alguns testes falharam\")\n            return 1\n            \n    except KeyboardInterrupt:\n        print(\"\\n⚠️  Testes interrompidos pelo usuário\")\n        return 130\n    except Exception as e:\n        print(f\"\\n❌ Erro durante os testes: {e}\")\n        traceback.print_exc()\n        return 1\n\nif __name__ == \"__main__\":\n    sys.exit(asyncio.run(main()))