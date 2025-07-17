#!/usr/bin/env python3
"""
Script de teste completo para todas as ferramentas MCP
Gera relatório detalhado do status de cada funcionalidade
"""

import os
import sys
import json
import asyncio
import subprocess
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class MCPToolsTester:
    def __init__(self):
        self.project_root = "/Users/kleberdossantosribeiro/omie-mcp"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "omie-mcp": {"server_status": {}, "tools": {}},
            "nibo-mcp": {"server_status": {}, "tools": {}}
        }
        
        # Definir ferramentas para cada serviço
        self.tools_definition = {
            "omie-mcp": {
                "testar_conexao": {"args": {}, "description": "Teste de conexão básica"},
                "consultar_categorias": {"args": {}, "description": "Listar categorias disponíveis"},
                "consultar_departamentos": {"args": {}, "description": "Listar departamentos"},
                "consultar_tipos_documento": {"args": {}, "description": "Listar tipos de documento"},
                "consultar_contas_pagar": {"args": {"pagina": 1, "registros_por_pagina": 10}, "description": "Consultar contas a pagar"},
                "consultar_contas_receber": {"args": {"pagina": 1, "registros_por_pagina": 10}, "description": "Consultar contas a receber"},
                "cadastrar_cliente_fornecedor": {
                    "args": {
                        "razao_social": "Teste Cliente MCP",
                        "nome_fantasia": "Teste MCP",
                        "cnpj_cpf": "12345678000195",
                        "telefone1_ddd": "11",
                        "telefone1_numero": "999999999",
                        "email": "teste@mcp.com"
                    },
                    "description": "Cadastrar cliente/fornecedor"
                },
                "criar_conta_pagar": {
                    "args": {
                        "codigo_cliente_fornecedor": "12345",
                        "valor_documento": 100.00,
                        "data_vencimento": "31/12/2024",
                        "observacao": "Teste MCP conta pagar"
                    },
                    "description": "Criar conta a pagar"
                },
                "criar_conta_receber": {
                    "args": {
                        "codigo_cliente": "12345",
                        "valor_documento": 150.00,
                        "data_vencimento": "31/12/2024",
                        "observacao": "Teste MCP conta receber"
                    },
                    "description": "Criar conta a receber"
                }
            },
            "nibo-mcp": {
                "testar_conexao": {"args": {}, "description": "Teste de conexão básica"},
                "consultar_socios": {"args": {}, "description": "Consultar sócios da empresa"},
                "consultar_centros_custo": {"args": {}, "description": "Consultar centros de custo"},
                "incluir_socio": {
                    "args": {
                        "nome": "Teste Sócio MCP",
                        "cpf": "12345678900",
                        "percentual_participacao": 100.0
                    },
                    "description": "Incluir novo sócio"
                },
                "incluir_multiplos_clientes": {
                    "args": {
                        "clientes": [
                            {
                                "nome": "Cliente Teste MCP 1",
                                "documento": "12345678000195",
                                "email": "cliente1@mcp.com"
                            }
                        ]
                    },
                    "description": "Incluir múltiplos clientes"
                }
            }
        }

    def test_server_availability(self, service_name: str) -> Dict:
        """Testa disponibilidade do servidor"""
        print(f"🔍 Testando servidor {service_name}...")
        
        result = {
            "stdio_server": {"available": False, "error": None},
            "http_server": {"available": False, "error": None, "url": None},
            "script_exists": False
        }
        
        # Verificar se script existe
        if service_name == "omie-mcp":
            script_path = os.path.join(self.project_root, "omie_mcp_server_hybrid.py")
            http_port = 3001
        else:  # nibo-mcp
            script_path = os.path.join(self.project_root, "nibo-mcp", "nibo_mcp_server_hybrid.py")
            http_port = 3002
        
        result["script_exists"] = os.path.exists(script_path)
        
        if not result["script_exists"]:
            result["stdio_server"]["error"] = f"Script não encontrado: {script_path}"
            result["http_server"]["error"] = f"Script não encontrado: {script_path}"
            return result
        
        # Testar servidor STDIO
        try:
            process = subprocess.Popen([
                sys.executable, script_path, "--mode", "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Enviar requisição de inicialização
            init_request = {
                "jsonrpc": "2.0",
                "id": "test-init",
                "method": "initialize",
                "params": {}
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Aguardar resposta (timeout de 5 segundos)
            process.wait(timeout=5)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0 or "jsonrpc" in stdout:
                result["stdio_server"]["available"] = True
            else:
                result["stdio_server"]["error"] = stderr or "Servidor não respondeu corretamente"
                
        except subprocess.TimeoutExpired:
            result["stdio_server"]["available"] = True  # Timeout é normal para servidor persistente
            process.terminate()
        except Exception as e:
            result["stdio_server"]["error"] = str(e)
        
        # Testar servidor HTTP
        http_url = f"http://localhost:{http_port}"
        result["http_server"]["url"] = http_url
        
        try:
            # Verificar se já está rodando
            response = requests.get(http_url, timeout=5)
            if response.status_code == 200:
                result["http_server"]["available"] = True
            else:
                result["http_server"]["error"] = f"Status code: {response.status_code}"
        except requests.RequestException:
            # Tentar iniciar servidor HTTP
            try:
                subprocess.Popen([
                    sys.executable, script_path, "--mode", "http", 
                    "--port", str(http_port), "--host", "0.0.0.0"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Aguardar inicialização
                time.sleep(3)
                
                response = requests.get(http_url, timeout=5)
                if response.status_code == 200:
                    result["http_server"]["available"] = True
                else:
                    result["http_server"]["error"] = f"Status code após inicialização: {response.status_code}"
                    
            except Exception as e:
                result["http_server"]["error"] = f"Erro ao iniciar servidor HTTP: {e}"
        
        return result

    def test_tool_stdio(self, service_name: str, tool_name: str, tool_config: Dict) -> Dict:
        """Testa ferramenta via STDIO"""
        result = {
            "method": "stdio",
            "success": False,
            "response": None,
            "error": None,
            "execution_time": 0
        }
        
        # Determinar script
        if service_name == "omie-mcp":
            script_path = os.path.join(self.project_root, "omie_mcp_server_hybrid.py")
        else:
            script_path = os.path.join(self.project_root, "nibo-mcp", "nibo_mcp_server_hybrid.py")
        
        try:
            start_time = time.time()
            
            process = subprocess.Popen([
                sys.executable, script_path, "--mode", "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Inicializar
            init_request = {
                "jsonrpc": "2.0",
                "id": "init",
                "method": "initialize",
                "params": {}
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Consumir resposta de inicialização
            process.stdout.readline()
            
            # Chamar ferramenta
            tool_request = {
                "jsonrpc": "2.0",
                "id": f"test-{tool_name}",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": tool_config["args"]
                }
            }
            
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            # Ler resposta
            response_line = process.stdout.readline()
            process.terminate()
            
            end_time = time.time()
            result["execution_time"] = round(end_time - start_time, 2)
            
            if response_line:
                response_data = json.loads(response_line.strip())
                result["response"] = response_data
                
                if "result" in response_data:
                    result["success"] = True
                elif "error" in response_data:
                    result["error"] = response_data["error"].get("message", "Erro desconhecido")
                else:
                    result["error"] = "Resposta malformada"
            else:
                result["error"] = "Sem resposta do servidor"
                
        except Exception as e:
            result["error"] = str(e)
            result["execution_time"] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result

    def test_tool_http(self, service_name: str, tool_name: str, tool_config: Dict) -> Dict:
        """Testa ferramenta via HTTP"""
        result = {
            "method": "http",
            "success": False,
            "response": None,
            "error": None,
            "execution_time": 0
        }
        
        # Determinar porta
        port = 3001 if service_name == "omie-mcp" else 3002
        url = f"http://localhost:{port}/mcp/tools/{tool_name}"
        
        try:
            start_time = time.time()
            
            response = requests.post(
                url,
                json={"arguments": tool_config["args"]},
                timeout=30
            )
            
            end_time = time.time()
            result["execution_time"] = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                result["success"] = True
                result["response"] = response.json()
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            result["error"] = str(e)
            result["execution_time"] = round(time.time() - start_time, 2) if 'start_time' in locals() else 0
        
        return result

    def test_all_tools(self, service_name: str) -> Dict:
        """Testa todas as ferramentas de um serviço"""
        print(f"\n🧪 Testando ferramentas do {service_name}...")
        
        tools_results = {}
        tools = self.tools_definition.get(service_name, {})
        
        for tool_name, tool_config in tools.items():
            print(f"  📋 Testando {tool_name}...")
            
            tool_result = {
                "description": tool_config["description"],
                "stdio": None,
                "http": None,
                "overall_success": False
            }
            
            # Testar via STDIO
            print(f"    🔌 STDIO...")
            tool_result["stdio"] = self.test_tool_stdio(service_name, tool_name, tool_config)
            
            # Testar via HTTP
            print(f"    🌐 HTTP...")
            tool_result["http"] = self.test_tool_http(service_name, tool_name, tool_config)
            
            # Determinar sucesso geral
            tool_result["overall_success"] = (
                tool_result["stdio"]["success"] or 
                tool_result["http"]["success"]
            )
            
            tools_results[tool_name] = tool_result
            
            # Status visual
            status = "✅" if tool_result["overall_success"] else "❌"
            print(f"    {status} {tool_name}")
        
        return tools_results

    def run_full_test(self) -> Dict:
        """Executa teste completo de todos os serviços"""
        print("🚀 INICIANDO TESTE COMPLETO DOS SERVIÇOS MCP")
        print("=" * 60)
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            print(f"\n📊 TESTANDO {service_name.upper()}")
            print("-" * 40)
            
            # Testar disponibilidade do servidor
            server_status = self.test_server_availability(service_name)
            self.results[service_name]["server_status"] = server_status
            
            print(f"  Script: {'✅' if server_status['script_exists'] else '❌'}")
            print(f"  STDIO: {'✅' if server_status['stdio_server']['available'] else '❌'}")
            print(f"  HTTP: {'✅' if server_status['http_server']['available'] else '❌'}")
            
            if server_status['http_server']['url']:
                print(f"  URL: {server_status['http_server']['url']}")
            
            # Testar ferramentas apenas se servidor estiver disponível
            if (server_status['stdio_server']['available'] or 
                server_status['http_server']['available']):
                
                tools_results = self.test_all_tools(service_name)
                self.results[service_name]["tools"] = tools_results
            else:
                print(f"  ⚠️  Servidor não disponível, pulando teste de ferramentas")
        
        return self.results

    def generate_report(self, results: Dict) -> str:
        """Gera relatório detalhado dos testes"""
        report_lines = []
        
        # Cabeçalho
        report_lines.append("📊 RELATÓRIO DE TESTES MCP")
        report_lines.append("=" * 50)
        report_lines.append(f"Data/Hora: {results['timestamp']}")
        report_lines.append("")
        
        # Resumo executivo
        report_lines.append("📈 RESUMO EXECUTIVO")
        report_lines.append("-" * 25)
        
        total_tools = 0
        successful_tools = 0
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            server_status = service_data["server_status"]
            tools = service_data.get("tools", {})
            
            service_tools = len(tools)
            service_successful = sum(1 for tool in tools.values() if tool["overall_success"])
            
            total_tools += service_tools
            successful_tools += service_successful
            
            success_rate = (service_successful / service_tools * 100) if service_tools > 0 else 0
            
            report_lines.append(f"{service_name.upper()}:")
            report_lines.append(f"  Servidor STDIO: {'✅' if server_status['stdio_server']['available'] else '❌'}")
            report_lines.append(f"  Servidor HTTP: {'✅' if server_status['http_server']['available'] else '❌'}")
            report_lines.append(f"  Ferramentas: {service_successful}/{service_tools} ({success_rate:.1f}%)")
            report_lines.append("")
        
        overall_success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 0
        report_lines.append(f"GERAL: {successful_tools}/{total_tools} ferramentas ({overall_success_rate:.1f}%)")
        report_lines.append("")
        
        # Detalhamento por serviço
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            
            report_lines.append(f"🔧 {service_name.upper()} - DETALHADO")
            report_lines.append("-" * 30)
            
            # Status do servidor
            server_status = service_data["server_status"]
            report_lines.append("Status do Servidor:")
            report_lines.append(f"  Script existe: {'✅' if server_status['script_exists'] else '❌'}")
            
            if server_status['stdio_server']['available']:
                report_lines.append("  STDIO: ✅ Disponível")
            else:
                error = server_status['stdio_server']['error'] or "Não disponível"
                report_lines.append(f"  STDIO: ❌ {error}")
            
            if server_status['http_server']['available']:
                url = server_status['http_server']['url']
                report_lines.append(f"  HTTP: ✅ Disponível ({url})")
            else:
                error = server_status['http_server']['error'] or "Não disponível"
                report_lines.append(f"  HTTP: ❌ {error}")
            
            report_lines.append("")
            
            # Ferramentas
            tools = service_data.get("tools", {})
            if tools:
                report_lines.append("Ferramentas:")
                
                for tool_name, tool_data in tools.items():
                    status = "✅" if tool_data["overall_success"] else "❌"
                    report_lines.append(f"  {status} {tool_name}")
                    report_lines.append(f"    {tool_data['description']}")
                    
                    # Detalhes STDIO
                    stdio = tool_data["stdio"]
                    if stdio:
                        stdio_status = "✅" if stdio["success"] else "❌"
                        report_lines.append(f"    STDIO: {stdio_status} ({stdio['execution_time']}s)")
                        if stdio["error"]:
                            report_lines.append(f"      Erro: {stdio['error']}")
                    
                    # Detalhes HTTP
                    http = tool_data["http"]
                    if http:
                        http_status = "✅" if http["success"] else "❌"
                        report_lines.append(f"    HTTP: {http_status} ({http['execution_time']}s)")
                        if http["error"]:
                            report_lines.append(f"      Erro: {http['error']}")
                    
                    report_lines.append("")
            else:
                report_lines.append("  ⚠️  Nenhuma ferramenta testada")
                report_lines.append("")
        
        # Recomendações
        report_lines.append("💡 RECOMENDAÇÕES")
        report_lines.append("-" * 20)
        
        recommendations = []
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            server_status = service_data["server_status"]
            
            if not server_status["script_exists"]:
                recommendations.append(f"Instalar/corrigir script do {service_name}")
            
            if not server_status["stdio_server"]["available"]:
                recommendations.append(f"Corrigir servidor STDIO do {service_name}")
            
            if not server_status["http_server"]["available"]:
                recommendations.append(f"Configurar servidor HTTP do {service_name}")
            
            tools = service_data.get("tools", {})
            failed_tools = [name for name, data in tools.items() if not data["overall_success"]]
            if failed_tools:
                recommendations.append(f"Corrigir ferramentas do {service_name}: {', '.join(failed_tools)}")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        else:
            report_lines.append("✅ Todos os serviços estão funcionando corretamente!")
        
        return "\n".join(report_lines)

    def save_report(self, results: Dict, report_text: str):
        """Salva relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar JSON detalhado
        json_filename = f"test_report_{timestamp}.json"
        json_path = os.path.join(self.project_root, json_filename)
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório texto
        txt_filename = f"test_report_{timestamp}.txt"
        txt_path = os.path.join(self.project_root, txt_filename)
        with open(txt_path, 'w') as f:
            f.write(report_text)
        
        print(f"\n📁 Relatórios salvos:")
        print(f"  JSON: {json_path}")
        print(f"  TXT: {txt_path}")
        
        return json_path, txt_path

def main():
    print("🧪 TESTE COMPLETO DOS SERVIÇOS MCP")
    print("Este script testará todas as funcionalidades dos serviços Omie MCP e Nibo MCP")
    print()
    
    tester = MCPToolsTester()
    
    # Executar testes
    results = tester.run_full_test()
    
    # Gerar relatório
    report = tester.generate_report(results)
    
    # Mostrar relatório
    print("\n" + "=" * 60)
    print(report)
    
    # Salvar arquivos
    json_path, txt_path = tester.save_report(results, report)
    
    print(f"\n🎉 Teste completo finalizado!")
    print(f"📊 Verifique os relatórios gerados para análise detalhada.")

if __name__ == "__main__":
    main()