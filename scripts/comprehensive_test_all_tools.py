#!/usr/bin/env python3
"""
Script de teste COMPLETO para todas as ferramentas MCP
Baseado na análise real dos servidores híbridos
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

class ComprehensiveMCPTester:
    def __init__(self):
        self.project_root = "/Users/kleberdossantosribeiro/omie-mcp"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "omie-mcp": {"server_status": {}, "tools": {}},
            "nibo-mcp": {"server_status": {}, "tools": {}}
        }
        
        # Ferramentas baseadas na análise dos servidores reais
        self.tools_definition = {
            "omie-mcp": {
                # Ferramentas básicas sempre disponíveis
                "testar_conexao": {
                    "args": {},
                    "description": "Teste de conexão básica com Omie ERP"
                },
                "consultar_categorias": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar categorias do Omie ERP"
                },
                "consultar_departamentos": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar departamentos do Omie ERP"
                },
                "consultar_tipos_documento": {
                    "args": {},
                    "description": "Consultar tipos de documento"
                },
                "consultar_contas_pagar": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar contas a pagar"
                },
                "consultar_contas_receber": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar contas a receber"
                },
                
                # Ferramentas avançadas (baseadas em src/tools/)
                "consultar_clientes": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar clientes cadastrados"
                },
                "consultar_fornecedores": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar fornecedores cadastrados"
                },
                "consultar_cliente_por_codigo": {
                    "args": {"codigo": "12345"},
                    "description": "Consultar cliente específico por código"
                },
                "consultar_fornecedor_por_codigo": {
                    "args": {"codigo": "12345"},
                    "description": "Consultar fornecedor específico por código"
                },
                "buscar_dados_contato_cliente": {
                    "args": {"codigo": "12345"},
                    "description": "Buscar dados de contato de cliente"
                },
                
                # CRUD Clientes/Fornecedores
                "incluir_cliente": {
                    "args": {
                        "razao_social": "Teste Cliente MCP",
                        "nome_fantasia": "Teste MCP",
                        "cnpj_cpf": "12345678000195",
                        "telefone1_ddd": "11",
                        "telefone1_numero": "999999999",
                        "email": "teste@mcp.com"
                    },
                    "description": "Incluir novo cliente"
                },
                "incluir_fornecedor": {
                    "args": {
                        "razao_social": "Teste Fornecedor MCP",
                        "nome_fantasia": "Fornecedor Test",
                        "cnpj_cpf": "98765432000111",
                        "telefone1_ddd": "11",
                        "telefone1_numero": "888888888",
                        "email": "fornecedor@mcp.com"
                    },
                    "description": "Incluir novo fornecedor"
                },
                "alterar_cliente": {
                    "args": {
                        "codigo": "12345",
                        "razao_social": "Cliente Alterado MCP"
                    },
                    "description": "Alterar dados de cliente"
                },
                "alterar_fornecedor": {
                    "args": {
                        "codigo": "12345",
                        "razao_social": "Fornecedor Alterado MCP"
                    },
                    "description": "Alterar dados de fornecedor"
                },
                
                # CRUD Contas a Pagar
                "incluir_conta_pagar": {
                    "args": {
                        "codigo_cliente_fornecedor": "12345",
                        "valor_documento": 100.00,
                        "data_vencimento": "31/12/2024",
                        "observacao": "Teste MCP conta pagar"
                    },
                    "description": "Incluir nova conta a pagar"
                },
                "alterar_conta_pagar": {
                    "args": {
                        "codigo": "12345",
                        "valor_documento": 150.00
                    },
                    "description": "Alterar conta a pagar"
                },
                "excluir_conta_pagar": {
                    "args": {"codigo": "12345"},
                    "description": "Excluir conta a pagar"
                },
                
                # CRUD Contas a Receber  
                "incluir_conta_receber": {
                    "args": {
                        "codigo_cliente": "12345",
                        "valor_documento": 200.00,
                        "data_vencimento": "31/12/2024",
                        "observacao": "Teste MCP conta receber"
                    },
                    "description": "Incluir nova conta a receber"
                },
                "alterar_conta_receber": {
                    "args": {
                        "codigo": "12345",
                        "valor_documento": 250.00
                    },
                    "description": "Alterar conta a receber"
                },
                "excluir_conta_receber": {
                    "args": {"codigo": "12345"},
                    "description": "Excluir conta a receber"
                }
            },
            
            "nibo-mcp": {
                # Ferramentas básicas sempre disponíveis
                "testar_conexao": {
                    "args": {},
                    "description": "Teste de conexão básica com Nibo"
                },
                "consultar_categorias": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar categorias do Nibo"
                },
                "consultar_centros_custo": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar centros de custo"
                },
                "consultar_socios": {
                    "args": {},
                    "description": "Consultar sócios da empresa"
                },
                
                # Ferramentas de consulta (baseadas em src/tools/)
                "consultar_clientes": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar clientes Nibo"
                },
                "consultar_fornecedores": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar fornecedores Nibo"
                },
                "consultar_contas_pagar": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar contas a pagar Nibo"
                },
                "consultar_contas_receber": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar contas a receber Nibo"
                },
                
                # Ferramentas de CRUD
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
                },
                
                # Ferramentas adicionais esperadas (baseado no número 31)
                "incluir_cliente": {
                    "args": {
                        "nome": "Cliente Teste Individual",
                        "documento": "12345678000195",
                        "email": "individual@mcp.com"
                    },
                    "description": "Incluir cliente individual"
                },
                "incluir_fornecedor": {
                    "args": {
                        "nome": "Fornecedor Teste",
                        "documento": "98765432000111",
                        "email": "fornecedor@mcp.com"
                    },
                    "description": "Incluir fornecedor"
                },
                "alterar_cliente": {
                    "args": {
                        "id": "12345",
                        "nome": "Cliente Alterado"
                    },
                    "description": "Alterar dados de cliente"
                },
                "alterar_fornecedor": {
                    "args": {
                        "id": "12345",
                        "nome": "Fornecedor Alterado"
                    },
                    "description": "Alterar dados de fornecedor"
                },
                "excluir_cliente": {
                    "args": {"id": "12345"},
                    "description": "Excluir cliente"
                },
                "excluir_fornecedor": {
                    "args": {"id": "12345"},
                    "description": "Excluir fornecedor"
                },
                "incluir_conta_pagar": {
                    "args": {
                        "fornecedor_id": "12345",
                        "valor": 100.00,
                        "data_vencimento": "2024-12-31",
                        "descricao": "Teste conta pagar"
                    },
                    "description": "Incluir conta a pagar"
                },
                "incluir_conta_receber": {
                    "args": {
                        "cliente_id": "12345",
                        "valor": 200.00,
                        "data_vencimento": "2024-12-31",
                        "descricao": "Teste conta receber"
                    },
                    "description": "Incluir conta a receber"
                },
                "alterar_conta_pagar": {
                    "args": {
                        "id": "12345",
                        "valor": 150.00
                    },
                    "description": "Alterar conta a pagar"
                },
                "alterar_conta_receber": {
                    "args": {
                        "id": "12345",
                        "valor": 250.00
                    },
                    "description": "Alterar conta a receber"
                },
                "excluir_conta_pagar": {
                    "args": {"id": "12345"},
                    "description": "Excluir conta a pagar"
                },
                "excluir_conta_receber": {
                    "args": {"id": "12345"},
                    "description": "Excluir conta a receber"
                },
                "consultar_produtos": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar produtos"
                },
                "incluir_produto": {
                    "args": {
                        "nome": "Produto Teste",
                        "codigo": "PROD001",
                        "preco": 50.00
                    },
                    "description": "Incluir produto"
                },
                "alterar_produto": {
                    "args": {
                        "id": "12345",
                        "nome": "Produto Alterado"
                    },
                    "description": "Alterar produto"
                },
                "excluir_produto": {
                    "args": {"id": "12345"},
                    "description": "Excluir produto"
                },
                "consultar_empresas": {
                    "args": {},
                    "description": "Consultar empresas"
                },
                "consultar_plano_contas": {
                    "args": {"pagina": 1, "registros_por_pagina": 10},
                    "description": "Consultar plano de contas"
                },
                "consultar_movimento_financeiro": {
                    "args": {
                        "data_inicio": "2024-01-01",
                        "data_fim": "2024-12-31"
                    },
                    "description": "Consultar movimento financeiro"
                },
                "gerar_relatorio_financeiro": {
                    "args": {
                        "tipo": "balancete",
                        "data_inicio": "2024-01-01",
                        "data_fim": "2024-12-31"
                    },
                    "description": "Gerar relatório financeiro"
                },
                "sincronizar_dados": {
                    "args": {},
                    "description": "Sincronizar dados com Nibo"
                },
                "backup_dados": {
                    "args": {},
                    "description": "Fazer backup dos dados"
                },
                "validar_integridade": {
                    "args": {},
                    "description": "Validar integridade dos dados"
                }
            }
        }

    def get_actual_tools_from_server(self, service_name: str) -> List[str]:
        """Descobre ferramentas reais consultando o servidor"""
        tools = []
        
        # Determinar script e porta
        if service_name == "omie-mcp":
            script_path = os.path.join(self.project_root, "omie_mcp_server_hybrid.py")
            http_port = 3001
        else:
            script_path = os.path.join(self.project_root, "nibo-mcp", "nibo_mcp_server_hybrid.py")
            http_port = 3002
        
        # Tentar via HTTP
        try:
            response = requests.get(f"http://localhost:{http_port}/mcp/tools", timeout=10)
            if response.status_code == 200:
                data = response.json()
                tools = [tool["name"] for tool in data.get("tools", [])]
                print(f"  📡 Descoberto via HTTP: {len(tools)} ferramentas")
                return tools
        except Exception as e:
            print(f"  ⚠️  HTTP falhou: {e}")
        
        # Tentar via STDIO
        try:
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
            process.stdout.readline()  # Consumir resposta init
            
            # Listar ferramentas
            list_request = {
                "jsonrpc": "2.0",
                "id": "list",
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write(json.dumps(list_request) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            process.terminate()
            
            if response_line:
                response_data = json.loads(response_line.strip())
                if "result" in response_data and "tools" in response_data["result"]:
                    tools = [tool["name"] for tool in response_data["result"]["tools"]]
                    print(f"  📡 Descoberto via STDIO: {len(tools)} ferramentas")
        
        except Exception as e:
            print(f"  ⚠️  STDIO falhou: {e}")
        
        return tools

    def test_server_availability(self, service_name: str) -> Dict:
        """Testa disponibilidade do servidor e descobre ferramentas reais"""
        print(f"🔍 Analisando servidor {service_name}...")
        
        result = {
            "stdio_server": {"available": False, "error": None},
            "http_server": {"available": False, "error": None, "url": None},
            "script_exists": False,
            "actual_tools": []
        }
        
        # Verificar se script existe
        if service_name == "omie-mcp":
            script_path = os.path.join(self.project_root, "omie_mcp_server_hybrid.py")
            http_port = 3001
        else:
            script_path = os.path.join(self.project_root, "nibo-mcp", "nibo_mcp_server_hybrid.py")
            http_port = 3002
        
        result["script_exists"] = os.path.exists(script_path)
        result["http_server"]["url"] = f"http://localhost:{http_port}"
        
        if not result["script_exists"]:
            result["stdio_server"]["error"] = f"Script não encontrado: {script_path}"
            result["http_server"]["error"] = f"Script não encontrado: {script_path}"
            return result
        
        # Descobrir ferramentas reais
        actual_tools = self.get_actual_tools_from_server(service_name)
        result["actual_tools"] = actual_tools
        
        # Atualizar lista de ferramentas para teste baseada na descoberta
        if actual_tools:
            print(f"  📋 Atualizando lista de ferramentas com descobertas reais")
            # Manter apenas ferramentas que realmente existem ou adicionar novas
            discovered_tools = {}
            for tool_name in actual_tools:
                if tool_name in self.tools_definition[service_name]:
                    discovered_tools[tool_name] = self.tools_definition[service_name][tool_name]
                else:
                    # Ferramenta descoberta mas não mapeada
                    discovered_tools[tool_name] = {
                        "args": {},
                        "description": f"Ferramenta descoberta: {tool_name}"
                    }
            
            self.tools_definition[service_name] = discovered_tools
            print(f"  ✅ Lista atualizada com {len(discovered_tools)} ferramentas")
        
        # Testar disponibilidade básica
        try:
            response = requests.get(result["http_server"]["url"], timeout=5)
            if response.status_code == 200:
                result["http_server"]["available"] = True
        except:
            pass
        
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
            process.stdout.readline()  # Consumir init
            
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
        
        print(f"  📋 Total de ferramentas a testar: {len(tools)}")
        
        for tool_name, tool_config in tools.items():
            print(f"    🔧 {tool_name}...")
            
            tool_result = {
                "description": tool_config["description"],
                "stdio": None,
                "http": None,
                "overall_success": False
            }
            
            # Testar via STDIO
            tool_result["stdio"] = self.test_tool_stdio(service_name, tool_name, tool_config)
            
            # Testar via HTTP
            tool_result["http"] = self.test_tool_http(service_name, tool_name, tool_config)
            
            # Determinar sucesso geral
            tool_result["overall_success"] = (
                tool_result["stdio"]["success"] or 
                tool_result["http"]["success"]
            )
            
            tools_results[tool_name] = tool_result
            
            # Status visual
            status = "✅" if tool_result["overall_success"] else "❌"
            stdio_status = "📡" if tool_result["stdio"]["success"] else "❌"
            http_status = "🌐" if tool_result["http"]["success"] else "❌"
            print(f"      {status} {tool_name} ({stdio_status}/{http_status})")
        
        return tools_results

    def run_comprehensive_test(self) -> Dict:
        """Executa teste abrangente de todos os serviços"""
        print("🚀 TESTE ABRANGENTE DOS SERVIÇOS MCP")
        print("=" * 70)
        print("Este teste descobre as ferramentas reais e testa TODAS!")
        print()
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            print(f"\n📊 ANALISANDO {service_name.upper()}")
            print("-" * 50)
            
            # Testar disponibilidade e descobrir ferramentas
            server_status = self.test_server_availability(service_name)
            self.results[service_name]["server_status"] = server_status
            
            print(f"  Script: {'✅' if server_status['script_exists'] else '❌'}")
            print(f"  STDIO: {'✅' if server_status['stdio_server']['available'] else '❌'}")
            print(f"  HTTP: {'✅' if server_status['http_server']['available'] else '❌'}")
            
            if server_status['http_server']['url']:
                print(f"  URL: {server_status['http_server']['url']}")
            
            actual_tools = server_status.get('actual_tools', [])
            if actual_tools:
                print(f"  🔍 Ferramentas descobertas: {len(actual_tools)}")
                print(f"  📋 Lista: {', '.join(actual_tools[:10])}{'...' if len(actual_tools) > 10 else ''}")
            
            # Testar todas as ferramentas
            if len(self.tools_definition[service_name]) > 0:
                tools_results = self.test_all_tools(service_name)
                self.results[service_name]["tools"] = tools_results
            else:
                print(f"  ⚠️  Nenhuma ferramenta para testar")
        
        return self.results

    def generate_comprehensive_report(self, results: Dict) -> str:
        """Gera relatório abrangente dos testes"""
        report_lines = []
        
        # Cabeçalho
        report_lines.append("📊 RELATÓRIO ABRANGENTE DE TESTES MCP")
        report_lines.append("=" * 60)
        report_lines.append(f"Data/Hora: {results['timestamp']}")
        report_lines.append("")
        
        # Resumo executivo
        report_lines.append("📈 RESUMO EXECUTIVO")
        report_lines.append("-" * 30)
        
        total_tools = 0
        successful_tools = 0
        total_actual_tools = 0
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            server_status = service_data["server_status"]
            tools = service_data.get("tools", {})
            actual_tools = server_status.get("actual_tools", [])
            
            service_tools = len(tools)
            service_successful = sum(1 for tool in tools.values() if tool["overall_success"])
            
            total_tools += service_tools
            successful_tools += service_successful
            total_actual_tools += len(actual_tools)
            
            success_rate = (service_successful / service_tools * 100) if service_tools > 0 else 0
            
            report_lines.append(f"{service_name.upper()}:")
            report_lines.append(f"  Servidor STDIO: {'✅' if server_status['stdio_server']['available'] else '❌'}")
            report_lines.append(f"  Servidor HTTP: {'✅' if server_status['http_server']['available'] else '❌'}")
            report_lines.append(f"  Ferramentas descobertas: {len(actual_tools)}")
            report_lines.append(f"  Ferramentas testadas: {service_tools}")
            report_lines.append(f"  Taxa de sucesso: {service_successful}/{service_tools} ({success_rate:.1f}%)")
            
            if len(actual_tools) != service_tools:
                diff = len(actual_tools) - service_tools
                report_lines.append(f"  ⚠️  Diferença descoberta vs testada: {diff}")
            
            report_lines.append("")
        
        overall_success_rate = (successful_tools / total_tools * 100) if total_tools > 0 else 0
        report_lines.append(f"TOTAL GERAL:")
        report_lines.append(f"  Ferramentas descobertas: {total_actual_tools}")
        report_lines.append(f"  Ferramentas testadas: {total_tools}")
        report_lines.append(f"  Taxa de sucesso: {successful_tools}/{total_tools} ({overall_success_rate:.1f}%)")
        report_lines.append("")
        
        # Detalhamento por serviço
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            
            report_lines.append(f"🔧 {service_name.upper()} - ANÁLISE DETALHADA")
            report_lines.append("-" * 40)
            
            # Status do servidor
            server_status = service_data["server_status"]
            actual_tools = server_status.get("actual_tools", [])
            
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
            
            if actual_tools:
                report_lines.append(f"  Ferramentas descobertas ({len(actual_tools)}):")
                for tool in actual_tools:
                    report_lines.append(f"    • {tool}")
            
            report_lines.append("")
            
            # Ferramentas testadas
            tools = service_data.get("tools", {})
            if tools:
                successful = sum(1 for tool in tools.values() if tool["overall_success"])
                report_lines.append(f"Resultado dos Testes ({successful}/{len(tools)} sucessos):")
                
                for tool_name, tool_data in tools.items():
                    status = "✅" if tool_data["overall_success"] else "❌"
                    report_lines.append(f"  {status} {tool_name}")
                    report_lines.append(f"    {tool_data['description']}")
                    
                    # Detalhes por protocolo
                    stdio = tool_data["stdio"]
                    http = tool_data["http"]
                    
                    if stdio and http:
                        stdio_icon = "✅" if stdio["success"] else "❌"
                        http_icon = "✅" if http["success"] else "❌"
                        report_lines.append(f"    📡 STDIO: {stdio_icon} ({stdio['execution_time']}s)")
                        report_lines.append(f"    🌐 HTTP: {http_icon} ({http['execution_time']}s)")
                        
                        if stdio["error"]:
                            report_lines.append(f"      STDIO erro: {stdio['error']}")
                        if http["error"]:
                            report_lines.append(f"      HTTP erro: {http['error']}")
                    
                    report_lines.append("")
            else:
                report_lines.append("  ⚠️  Nenhuma ferramenta foi testada")
                report_lines.append("")
        
        # Análise de cobertura
        report_lines.append("📋 ANÁLISE DE COBERTURA")
        report_lines.append("-" * 30)
        
        for service_name in ["omie-mcp", "nibo-mcp"]:
            service_data = results[service_name]
            server_status = service_data["server_status"]
            tools = service_data.get("tools", {})
            actual_tools = set(server_status.get("actual_tools", []))
            tested_tools = set(tools.keys())
            
            report_lines.append(f"{service_name.upper()}:")
            
            # Ferramentas descobertas mas não testadas
            not_tested = actual_tools - tested_tools
            if not_tested:
                report_lines.append(f"  🔍 Descobertas mas não testadas ({len(not_tested)}):")
                for tool in sorted(not_tested):
                    report_lines.append(f"    • {tool}")
            
            # Ferramentas testadas mas não descobertas
            extra_tested = tested_tools - actual_tools
            if extra_tested:
                report_lines.append(f"  🧪 Testadas mas não descobertas ({len(extra_tested)}):")
                for tool in sorted(extra_tested):
                    report_lines.append(f"    • {tool}")
            
            if not not_tested and not extra_tested:
                report_lines.append("  ✅ Cobertura completa!")
            
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
            
            # Recomendações baseadas na cobertura
            actual_tools = set(server_status.get("actual_tools", []))
            tested_tools = set(service_data.get("tools", {}).keys())
            not_tested = actual_tools - tested_tools
            
            if not_tested:
                recommendations.append(f"Adicionar testes para ferramentas descobertas do {service_name}: {', '.join(sorted(not_tested))}")
            
            # Ferramentas com falha
            tools = service_data.get("tools", {})
            failed_tools = [name for name, data in tools.items() if not data["overall_success"]]
            if failed_tools:
                recommendations.append(f"Corrigir ferramentas com falha do {service_name}: {', '.join(failed_tools)}")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        else:
            report_lines.append("✅ Todos os serviços estão funcionando perfeitamente!")
        
        return "\n".join(report_lines)

    def save_comprehensive_report(self, results: Dict, report_text: str):
        """Salva relatório abrangente em arquivos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar JSON detalhado
        json_filename = f"comprehensive_test_report_{timestamp}.json"
        json_path = os.path.join(self.project_root, json_filename)
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório texto
        txt_filename = f"comprehensive_test_report_{timestamp}.txt"
        txt_path = os.path.join(self.project_root, txt_filename)
        with open(txt_path, 'w') as f:
            f.write(report_text)
        
        print(f"\n📁 Relatórios abrangentes salvos:")
        print(f"  JSON: {json_path}")
        print(f"  TXT: {txt_path}")
        
        return json_path, txt_path

def main():
    print("🧪 TESTE ABRANGENTE DOS SERVIÇOS MCP")
    print("Este script descobre e testa TODAS as ferramentas disponíveis!")
    print("=" * 70)
    print()
    
    tester = ComprehensiveMCPTester()
    
    # Executar testes abrangentes
    results = tester.run_comprehensive_test()
    
    # Gerar relatório abrangente
    report = tester.generate_comprehensive_report(results)
    
    # Mostrar relatório
    print("\n" + "=" * 70)
    print(report)
    
    # Salvar arquivos
    json_path, txt_path = tester.save_comprehensive_report(results, report)
    
    # Resumo final
    total_omie = len(results["omie-mcp"].get("tools", {}))
    total_nibo = len(results["nibo-mcp"].get("tools", {}))
    total_discovered_omie = len(results["omie-mcp"]["server_status"].get("actual_tools", []))
    total_discovered_nibo = len(results["nibo-mcp"]["server_status"].get("actual_tools", []))
    
    print(f"\n🎉 TESTE ABRANGENTE CONCLUÍDO!")
    print(f"📊 Omie MCP: {total_omie} testadas / {total_discovered_omie} descobertas")
    print(f"📊 Nibo MCP: {total_nibo} testadas / {total_discovered_nibo} descobertas")
    print(f"📋 Verifique os relatórios para análise completa!")

if __name__ == "__main__":
    main()