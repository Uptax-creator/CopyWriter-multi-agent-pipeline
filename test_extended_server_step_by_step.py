#!/usr/bin/env python3
"""
🧪 TESTE SISTEMÁTICO SERVIDOR ESTENDIDO - OMIE MCP
Testes etapa por etapa - não avança sem validação completa
"""

import subprocess
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple

class ExtendedServerTester:
    def __init__(self):
        self.test_results = {}
        self.current_step = 0
        self.total_steps = 6
        self.failed_tests = []
        
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*70)
        print(f"🧪 {title}")
        print("="*70)

    def print_step(self, step: str):
        """Imprime passo formatado"""
        self.current_step += 1
        print(f"\n📋 ETAPA {self.current_step}/{self.total_steps}: {step}")
        print("-" * 50)

    def print_result(self, success: bool, message: str):
        """Imprime resultado formatado"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
        if not success:
            self.failed_tests.append(f"Etapa {self.current_step}: {message}")

    def test_server_startup(self) -> bool:
        """ETAPA 1: Testa startup do servidor estendido"""
        self.print_step("Verificação de Startup do Servidor Estendido")
        
        try:
            process = subprocess.Popen([
                "python3", "omie_fastmcp_extended.py", "--test-mode"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                if "17 ferramentas validadas" in stdout:
                    self.print_result(True, "Servidor estendido inicia com 17 ferramentas")
                    return True
                else:
                    self.print_result(False, f"Número de ferramentas incorreto: {stdout}")
                    return False
            else:
                self.print_result(False, f"Falha na inicialização: {stderr}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Erro ao testar startup: {e}")
            return False

    def test_homologated_tools_structure(self) -> bool:
        """ETAPA 2: Verifica estrutura das tools homologadas"""
        self.print_step("Validação das Tools Homologadas")
        
        # Tools homologadas esperadas
        expected_tools = [
            "teste_conexao",
            "lista_empresas", 
            "info_empresa"
        ]
        
        try:
            with open("omie_fastmcp_extended.py", "r") as f:
                content = f.read()
            
            tools_found = 0
            for tool in expected_tools:
                if f"async def {tool}(" in content:
                    self.print_result(True, f"Tool homologada encontrada: {tool}")
                    tools_found += 1
                else:
                    self.print_result(False, f"Tool homologada NÃO encontrada: {tool}")
            
            if tools_found == len(expected_tools):
                self.print_result(True, f"Todas as {len(expected_tools)} tools homologadas implementadas")
                return True
            else:
                self.print_result(False, f"Apenas {tools_found}/{len(expected_tools)} tools homologadas encontradas")
                return False
                
        except Exception as e:
            self.print_result(False, f"Erro ao verificar tools homologadas: {e}")
            return False

    def test_new_tools_structure(self) -> bool:
        """ETAPA 3: Verifica implementação das novas tools"""
        self.print_step("Validação das Novas Tools Implementadas")
        
        new_tools = [
            ("consultar_contas_receber", "baseada em consultar_contas_pagar"),
            ("incluir_cliente", "com tag 'cliente'")
        ]
        
        try:
            with open("omie_fastmcp_extended.py", "r") as f:
                content = f.read()
            
            tools_validated = 0
            for tool_name, description in new_tools:
                if f"async def {tool_name}(" in content:
                    self.print_result(True, f"Nova tool encontrada: {tool_name}")
                    
                    # Validações específicas
                    if tool_name == "consultar_contas_receber":
                        if "a_receber" in content and "recebido" in content:
                            self.print_result(True, "consultar_contas_receber tem filtros de status")
                            tools_validated += 1
                        else:
                            self.print_result(False, "consultar_contas_receber sem filtros adequados")
                    
                    elif tool_name == "incluir_cliente":
                        if '"cliente"' in content and "tags" in content:
                            self.print_result(True, "incluir_cliente aplica tag 'cliente'")
                            tools_validated += 1
                        else:
                            self.print_result(False, "incluir_cliente não aplica tag corretamente")
                else:
                    self.print_result(False, f"Nova tool NÃO encontrada: {tool_name}")
            
            if tools_validated == len(new_tools):
                return True
            else:
                return False
                
        except Exception as e:
            self.print_result(False, f"Erro ao verificar novas tools: {e}")
            return False

    def test_omie_client_updates(self) -> bool:
        """ETAPA 4: Verifica atualizações no OmieClient"""
        self.print_step("Validação de Atualizações no OmieClient")
        
        try:
            with open("src/client/omie_client.py", "r") as f:
                content = f.read()
            
            # Verificar se consultar_contas_receber foi adicionado
            if "async def consultar_contas_receber(" in content:
                self.print_result(True, "Método consultar_contas_receber adicionado ao OmieClient")
                
                # Verificar endpoint correto
                if "financas/contareceber" in content and "ListarContasReceber" in content:
                    self.print_result(True, "Endpoint correto para contas a receber configurado")
                    return True
                else:
                    self.print_result(False, "Endpoint incorreto para contas a receber")
                    return False
            else:
                self.print_result(False, "Método consultar_contas_receber NÃO adicionado ao OmieClient")
                return False
                
        except Exception as e:
            self.print_result(False, f"Erro ao verificar OmieClient: {e}")
            return False

    def test_imports_and_dependencies(self) -> bool:
        """ETAPA 5: Testa todas as importações e dependências"""
        self.print_step("Validação de Importações e Dependências")
        
        tests = [
            ("FastMCP", "from fastmcp import FastMCP; print('FastMCP OK')"),
            ("OmieClient", "import sys; sys.path.append('src'); from src.client.omie_client import OmieClient; print('OmieClient OK')"),
            ("Credentials", "import json; f=open('credentials.json'); json.load(f); f.close(); print('Credentials OK')")
        ]
        
        passed_tests = 0
        for test_name, test_code in tests:
            try:
                result = subprocess.run([
                    "python3", "-c", test_code
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.print_result(True, f"{test_name} importado com sucesso")
                    passed_tests += 1
                else:
                    self.print_result(False, f"Erro em {test_name}: {result.stderr}")
                    
            except Exception as e:
                self.print_result(False, f"Erro ao testar {test_name}: {e}")
        
        return passed_tests == len(tests)

    def test_tool_counts_and_structure(self) -> bool:
        """ETAPA 6: Verifica contagem e estrutura final"""
        self.print_step("Validação de Contagem e Estrutura Final")
        
        try:
            with open("omie_fastmcp_extended.py", "r") as f:
                content = f.read()
            
            # Contar @mcp.tool
            tool_decorators = content.count("@mcp.tool")
            expected_tools = 17
            
            if tool_decorators == expected_tools:
                self.print_result(True, f"Contagem correta: {tool_decorators} tools encontradas")
            else:
                self.print_result(False, f"Contagem incorreta: {tool_decorators} tools (esperado: {expected_tools})")
                return False
            
            # Verificar resources
            if "@mcp.resource" in content:
                self.print_result(True, "Resources implementados")
            else:
                self.print_result(False, "Resources não encontrados")
                return False
            
            # Verificar prompt
            if "@mcp.prompt" in content:
                self.print_result(True, "Prompt de validação implementado")
            else:
                self.print_result(False, "Prompt de validação não encontrado")
                return False
            
            return True
            
        except Exception as e:
            self.print_result(False, f"Erro na validação final: {e}")
            return False

    def generate_test_report(self):
        """Gera relatório final dos testes"""
        self.print_header("RELATÓRIO FINAL DOS TESTES")
        
        passed_steps = sum(1 for result in self.test_results.values() if result)
        total_steps = len(self.test_results)
        success_rate = (passed_steps / total_steps) * 100
        
        print(f"\n📊 RESUMO:")
        print(f"   Etapas executadas: {total_steps}")
        print(f"   Etapas aprovadas: {passed_steps}")
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        print(f"\n📋 DETALHES POR ETAPA:")
        for i, (step_name, result) in enumerate(self.test_results.items(), 1):
            icon = "✅" if result else "❌"
            print(f"   {icon} Etapa {i}: {step_name}")
        
        if self.failed_tests:
            print(f"\n❌ FALHAS IDENTIFICADAS:")
            for failure in self.failed_tests:
                print(f"   • {failure}")
        
        print(f"\n🎯 STATUS FINAL:")
        if success_rate == 100:
            print("   🟢 TODAS AS ETAPAS APROVADAS")
            print("   Sistema estendido pronto para uso")
            
            print(f"\n🚀 PRÓXIMOS PASSOS:")
            print("   1. Configurar Claude Desktop com servidor estendido")
            print("   2. Testar tools homologadas no Claude Desktop")
            print("   3. Validar novas funcionalidades implementadas")
            print("   4. Executar testes de integração completos")
            
        elif success_rate >= 80:
            print("   🟡 MAIORIA DAS ETAPAS APROVADAS")
            print("   Sistema pode funcionar com limitações")
            
        else:
            print("   🔴 MUITAS ETAPAS REPROVADAS") 
            print("   Corrija os problemas antes de continuar")
        
        print(f"\n📈 FERRAMENTAS IMPLEMENTADAS:")
        print("   🔹 Tools Homologadas: 3 (teste_conexao, lista_empresas, info_empresa)")
        print("   🔹 Tools Básicas: 3 (categorias, clientes, contas_pagar)")
        print("   ✨ Tools Novas: 2 (contas_receber, incluir_cliente)")
        print("   🔧 Tools CRUD: 9 (projetos, lançamentos, contas)")
        print("   📊 TOTAL: 17 ferramentas")
        
        return success_rate == 100

    def run_all_tests(self):
        """Executa todos os testes em sequência"""
        self.print_header("TESTE SISTEMÁTICO SERVIDOR ESTENDIDO")
        print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🎯 Execução etapa por etapa - não avança sem validação")
        
        # Definir testes em ordem
        tests = [
            ("Startup do Servidor", self.test_server_startup),
            ("Tools Homologadas", self.test_homologated_tools_structure),
            ("Novas Tools", self.test_new_tools_structure),
            ("Atualizações OmieClient", self.test_omie_client_updates),
            ("Importações", self.test_imports_and_dependencies),
            ("Estrutura Final", self.test_tool_counts_and_structure)
        ]
        
        # Executar testes sequencialmente
        for step_name, test_function in tests:
            result = test_function()
            self.test_results[step_name] = result
            
            if not result:
                print(f"\n⚠️  ETAPA {self.current_step} REPROVADA - INTERROMPENDO TESTES")
                print("🔍 Corrija os problemas antes de continuar")
                break
            else:
                print(f"\n✅ ETAPA {self.current_step} APROVADA - Continuando...")
        
        # Gerar relatório
        success = self.generate_test_report()
        
        print(f"\n🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return success

def main():
    """Execução principal"""
    tester = ExtendedServerTester()
    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main()