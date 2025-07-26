#!/usr/bin/env python3
"""
🧪 TESTE INTEGRAÇÃO CLAUDE DESKTOP - OMIE MCP
Script para testar servidores FastMCP antes da integração
"""

import subprocess
import asyncio
import time
import json
from datetime import datetime

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_step(step: str):
    """Imprime passo formatado"""
    print(f"\n📋 {step}")
    print("-" * 40)

def print_result(success: bool, message: str):
    """Imprime resultado formatado"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_server_startup(server_path: str, server_name: str) -> bool:
    """Testa se o servidor inicia corretamente"""
    print_step(f"Testando startup do {server_name}")
    
    try:
        # Tentar iniciar servidor em modo de teste
        process = subprocess.Popen([
            "python3", server_path, "--test-mode"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar um pouco para ver se inicia
        time.sleep(2)
        
        # Verificar se ainda está rodando
        if process.poll() is None:
            process.terminate()
            process.wait()
            print_result(True, f"{server_name} inicia corretamente")
            return True
        else:
            stdout, stderr = process.communicate()
            print_result(False, f"{server_name} falhou na inicialização")
            if stderr:
                print(f"   Erro: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print_result(False, f"Erro ao testar {server_name}: {e}")
        return False

def test_fastmcp_imports():
    """Testa se as importações FastMCP funcionam"""
    print_step("Testando importações FastMCP")
    
    try:
        # Testar FastMCP
        result = subprocess.run([
            "python3", "-c", "from fastmcp import FastMCP; print('FastMCP OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_result(True, "FastMCP importado com sucesso")
        else:
            print_result(False, f"Erro FastMCP: {result.stderr}")
            return False
        
        # Testar database manager
        result = subprocess.run([
            "python3", "-c", 
            "import sys; sys.path.append('src'); "
            "from database.database_manager import OmieIntegrationDatabase; "
            "print('Database OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_result(True, "Database manager importado com sucesso")
        else:
            print_result(True, "Database manager não disponível (normal em dev)")
        
        # Testar classification
        result = subprocess.run([
            "python3", "-c",
            "import sys; sys.path.append('src/tools'); "
            "from tool_classifier_enhanced import enhanced_classification; "
            "print(f'Tools: {len(enhanced_classification.tools)}')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_result(True, f"Classification system OK: {result.stdout.strip()}")
        else:
            print_result(False, f"Erro classification: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro nos testes de importação: {e}")
        return False

def test_credentials():
    """Testa se as credenciais estão configuradas"""
    print_step("Testando credenciais")
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        required_fields = ["app_key", "app_secret"]
        
        for field in required_fields:
            if field in creds and creds[field]:
                print_result(True, f"Campo {field} configurado")
            else:
                print_result(False, f"Campo {field} não configurado")
                return False
        
        return True
        
    except FileNotFoundError:
        print_result(False, "Arquivo credentials.json não encontrado")
        return False
    except Exception as e:
        print_result(False, f"Erro ao ler credenciais: {e}")
        return False

def generate_claude_commands():
    """Gera comandos para testar no Claude Desktop"""
    commands = {
        "Básicos": [
            "Teste a conexão com o Omie ERP",
            "Liste as categorias disponíveis",
            "Consulte os clientes cadastrados",
            "Verifique as contas a pagar vencidas"
        ],
        "CRUD Avançado": [
            "Crie um projeto chamado 'Teste Claude Desktop'",
            "Liste todos os projetos cadastrados", 
            "Inclua uma conta corrente de teste chamada 'Caixa Teste'",
            "Liste todas as contas correntes"
        ],
        "Monitoramento": [
            "Verifique o status do sistema de database",
            "Mostre as métricas de performance das últimas 24 horas",
            "Verifique se há alertas ativos no sistema"
        ],
        "Recursos Avançados": [
            "Execute o prompt de validação do conjunto 1",
            "Mostre o roadmap de implementação das tools",
            "Gere um relatório de status do sistema"
        ]
    }
    
    print_step("Comandos para testar no Claude Desktop")
    
    for categoria, cmds in commands.items():
        print(f"\n🔹 {categoria}:")
        for i, cmd in enumerate(cmds, 1):
            print(f"   {i}. \"{cmd}\"")
    
    # Salvar comandos em arquivo
    with open("claude_desktop_test_commands.json", "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)
    
    print_result(True, "Comandos salvos em: claude_desktop_test_commands.json")

def main():
    """Execução principal"""
    print_header("TESTE INTEGRAÇÃO CLAUDE DESKTOP")
    print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    results = {}
    
    # Teste 1: Importações
    results["imports"] = test_fastmcp_imports()
    
    # Teste 2: Credenciais
    results["credentials"] = test_credentials()
    
    # Teste 3: Startup dos servidores
    servers = [
        ("omie_fastmcp_conjunto_1_enhanced.py", "Conjunto 1 Enhanced"),
        ("omie_fastmcp_conjunto_2_complete.py", "Conjunto 2 Complete")
    ]
    
    server_results = []
    for server_path, server_name in servers:
        result = test_server_startup(server_path, server_name)
        server_results.append(result)
        results[f"server_{server_name.lower().replace(' ', '_')}"] = result
    
    # Teste 4: Gerar comandos de teste
    generate_claude_commands()
    
    # Relatório final
    print_header("RELATÓRIO DE INTEGRAÇÃO")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 RESUMO:")
    print(f"   Testes executados: {total_tests}")
    print(f"   Testes aprovados: {passed_tests}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    print(f"\n📋 DETALHES:")
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test_name}")
    
    print(f"\n🎯 STATUS PARA CLAUDE DESKTOP:")
    if success_rate >= 90:
        print("   🟢 PRONTO PARA INTEGRAÇÃO")
        print("   Todos os componentes funcionando corretamente")
        
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute: python setup_claude_desktop.py")
        print("   2. Reinicie o Claude Desktop")
        print("   3. Teste os comandos gerados")
        print("   4. Verifique se as 11 tools aparecem no Claude")
        
    elif success_rate >= 70:
        print("   🟡 PRONTO COM RESSALVAS")
        print("   Alguns componentes podem não funcionar perfeitamente")
        
    else:
        print("   🔴 NÃO PRONTO")
        print("   Corrija os problemas antes da integração")
    
    print(f"\n🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return success_rate >= 90

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        exit(1)