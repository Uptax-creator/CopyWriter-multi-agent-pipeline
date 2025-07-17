#!/usr/bin/env python3
"""
Teste simplificado de credenciais e ferramentas
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

def test_credentials():
    """Testa se as credenciais estão configuradas"""
    print("🔐 TESTANDO CREDENCIAIS")
    print("=" * 30)
    
    results = {"omie": {}, "nibo": {}}
    
    # Testar credenciais Omie
    omie_cred_path = "/Users/kleberdossantosribeiro/omie-mcp/credentials.json"
    if os.path.exists(omie_cred_path):
        try:
            with open(omie_cred_path, 'r') as f:
                omie_creds = json.load(f)
            
            app_key = omie_creds.get("app_key", "")
            app_secret = omie_creds.get("app_secret", "")
            
            results["omie"] = {
                "file_exists": True,
                "has_app_key": bool(app_key and len(app_key) > 10),
                "has_app_secret": bool(app_secret and len(app_secret) > 10),
                "app_key_preview": app_key[:8] + "..." if app_key else "vazio",
                "app_secret_preview": app_secret[:8] + "..." if app_secret else "vazio"
            }
            
            print(f"✅ Omie credentials.json existe")
            print(f"  App Key: {'✅' if results['omie']['has_app_key'] else '❌'} {results['omie']['app_key_preview']}")
            print(f"  App Secret: {'✅' if results['omie']['has_app_secret'] else '❌'} {results['omie']['app_secret_preview']}")
            
        except Exception as e:
            results["omie"] = {"file_exists": True, "error": str(e)}
            print(f"❌ Erro ao ler credenciais Omie: {e}")
    else:
        results["omie"] = {"file_exists": False}
        print(f"❌ Arquivo de credenciais Omie não encontrado: {omie_cred_path}")
    
    # Testar credenciais Nibo
    nibo_cred_path = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/credentials.json"
    if os.path.exists(nibo_cred_path):
        try:
            with open(nibo_cred_path, 'r') as f:
                nibo_creds = json.load(f)
            
            token = nibo_creds.get("token", "")
            company_id = nibo_creds.get("company_id", "")
            
            results["nibo"] = {
                "file_exists": True,
                "has_token": bool(token and len(token) > 10),
                "has_company_id": bool(company_id),
                "token_preview": token[:8] + "..." if token else "vazio",
                "company_id_preview": company_id[:8] + "..." if company_id else "vazio"
            }
            
            print(f"\n✅ Nibo credentials.json existe")
            print(f"  Token: {'✅' if results['nibo']['has_token'] else '❌'} {results['nibo']['token_preview']}")
            print(f"  Company ID: {'✅' if results['nibo']['has_company_id'] else '❌'} {results['nibo']['company_id_preview']}")
            
        except Exception as e:
            results["nibo"] = {"file_exists": True, "error": str(e)}
            print(f"❌ Erro ao ler credenciais Nibo: {e}")
    else:
        results["nibo"] = {"file_exists": False}
        print(f"❌ Arquivo de credenciais Nibo não encontrado: {nibo_cred_path}")
    
    return results

def test_http_endpoints():
    """Testa endpoints HTTP dos servidores"""
    print(f"\n🌐 TESTANDO ENDPOINTS HTTP")
    print("=" * 35)
    
    results = {"omie": {}, "nibo": {}}
    
    # Testar Omie HTTP
    omie_url = "http://localhost:3001"
    print(f"Testando Omie: {omie_url}")
    
    try:
        response = requests.get(omie_url, timeout=5)
        results["omie"] = {
            "server_online": True,
            "status_code": response.status_code,
            "response_preview": response.text[:100] + "..." if len(response.text) > 100 else response.text
        }
        print(f"  ✅ Servidor online - Status: {response.status_code}")
        
        # Testar endpoint de ferramentas
        try:
            tools_response = requests.get(f"{omie_url}/mcp/tools", timeout=5)
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                tools_count = len(tools_data.get("tools", []))
                results["omie"]["tools_endpoint"] = True
                results["omie"]["tools_count"] = tools_count
                print(f"  ✅ Endpoint /mcp/tools - {tools_count} ferramentas")
            else:
                results["omie"]["tools_endpoint"] = False
                print(f"  ❌ Endpoint /mcp/tools - Status: {tools_response.status_code}")
        except Exception as e:
            results["omie"]["tools_endpoint"] = False
            print(f"  ❌ Erro no endpoint tools: {e}")
            
    except Exception as e:
        results["omie"] = {"server_online": False, "error": str(e)}
        print(f"  ❌ Servidor offline: {e}")
    
    # Testar Nibo HTTP
    nibo_url = "http://localhost:3002"
    print(f"\nTestando Nibo: {nibo_url}")
    
    try:
        response = requests.get(nibo_url, timeout=5)
        results["nibo"] = {
            "server_online": True,
            "status_code": response.status_code,
            "response_preview": response.text[:100] + "..." if len(response.text) > 100 else response.text
        }
        print(f"  ✅ Servidor online - Status: {response.status_code}")
        
        # Testar endpoint de ferramentas
        try:
            tools_response = requests.get(f"{nibo_url}/mcp/tools", timeout=5)
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                tools_count = len(tools_data.get("tools", []))
                results["nibo"]["tools_endpoint"] = True
                results["nibo"]["tools_count"] = tools_count
                print(f"  ✅ Endpoint /mcp/tools - {tools_count} ferramentas")
            else:
                results["nibo"]["tools_endpoint"] = False
                print(f"  ❌ Endpoint /mcp/tools - Status: {tools_response.status_code}")
        except Exception as e:
            results["nibo"]["tools_endpoint"] = False
            print(f"  ❌ Erro no endpoint tools: {e}")
            
    except Exception as e:
        results["nibo"] = {"server_online": False, "error": str(e)}
        print(f"  ❌ Servidor offline: {e}")
    
    return results

def test_single_tool(service, url, tool_name, args=None):
    """Testa uma ferramenta específica"""
    if args is None:
        args = {}
    
    try:
        tool_url = f"{url}/mcp/tools/{tool_name}"
        response = requests.post(
            tool_url,
            json={"arguments": args},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "status_code": response.status_code,
                "response_size": len(str(result)),
                "response_preview": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text[:200]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_basic_tools():
    """Testa ferramentas básicas"""
    print(f"\n🔧 TESTANDO FERRAMENTAS BÁSICAS")
    print("=" * 40)
    
    results = {"omie": {}, "nibo": {}}
    
    # Testar ferramenta básica do Omie
    if requests.get("http://localhost:3001", timeout=2).status_code == 200:
        print("Testando Omie - testar_conexao...")
        omie_result = test_single_tool("omie", "http://localhost:3001", "testar_conexao")
        results["omie"]["testar_conexao"] = omie_result
        
        if omie_result["success"]:
            print(f"  ✅ testar_conexao funcionou")
            print(f"    Resposta: {omie_result['response_preview']}")
        else:
            print(f"  ❌ testar_conexao falhou: {omie_result.get('error', 'Erro desconhecido')}")
        
        # Testar consultar_categorias
        print("Testando Omie - consultar_categorias...")
        omie_cat_result = test_single_tool("omie", "http://localhost:3001", "consultar_categorias", {"pagina": 1, "registros_por_pagina": 5})
        results["omie"]["consultar_categorias"] = omie_cat_result
        
        if omie_cat_result["success"]:
            print(f"  ✅ consultar_categorias funcionou")
        else:
            print(f"  ❌ consultar_categorias falhou: {omie_cat_result.get('error', 'Erro desconhecido')}")
    
    except Exception as e:
        print(f"❌ Não foi possível testar Omie: {e}")
        results["omie"]["error"] = str(e)
    
    # Testar ferramenta básica do Nibo
    try:
        if requests.get("http://localhost:3002", timeout=2).status_code == 200:
            print(f"\nTestando Nibo - testar_conexao...")
            nibo_result = test_single_tool("nibo", "http://localhost:3002", "testar_conexao")
            results["nibo"]["testar_conexao"] = nibo_result
            
            if nibo_result["success"]:
                print(f"  ✅ testar_conexao funcionou")
                print(f"    Resposta: {nibo_result['response_preview']}")
            else:
                print(f"  ❌ testar_conexao falhou: {nibo_result.get('error', 'Erro desconhecido')}")
    
    except Exception as e:
        print(f"❌ Não foi possível testar Nibo: {e}")
        results["nibo"]["error"] = str(e)
    
    return results

def test_stdio_connection():
    """Testa conexão STDIO básica"""
    print(f"\n📡 TESTANDO CONEXÃO STDIO")
    print("=" * 30)
    
    results = {"omie": {}, "nibo": {}}
    
    # Testar Omie STDIO
    omie_script = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    if os.path.exists(omie_script):
        print("Testando Omie STDIO...")
        try:
            process = subprocess.Popen([
                sys.executable, omie_script, "--mode", "stdio"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Enviar inicialização
            init_request = {
                "jsonrpc": "2.0",
                "id": "test-init",
                "method": "initialize",
                "params": {}
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Ler resposta
            response_line = process.stdout.readline()
            process.terminate()
            
            if response_line and "jsonrpc" in response_line:
                response_data = json.loads(response_line.strip())
                results["omie"] = {
                    "stdio_works": True,
                    "response": response_data
                }
                print(f"  ✅ STDIO funcionando")
                print(f"    Protocolo: {response_data.get('result', {}).get('protocolVersion', 'N/A')}")
            else:
                results["omie"] = {"stdio_works": False, "error": "Sem resposta válida"}
                print(f"  ❌ STDIO não respondeu corretamente")
                
        except Exception as e:
            results["omie"] = {"stdio_works": False, "error": str(e)}
            print(f"  ❌ Erro no STDIO: {e}")
    else:
        results["omie"] = {"stdio_works": False, "error": "Script não encontrado"}
        print(f"  ❌ Script não encontrado: {omie_script}")
    
    return results

def run_comprehensive_test():
    """Executa teste abrangente"""
    print("🧪 TESTE ABRANGENTE DE CREDENCIAIS E FERRAMENTAS")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "credentials": test_credentials(),
        "http_endpoints": test_http_endpoints(),
        "basic_tools": test_basic_tools(),
        "stdio_connection": test_stdio_connection()
    }
    
    # Resumo
    print(f"\n📊 RESUMO DOS TESTES")
    print("=" * 25)
    
    # Credenciais
    omie_creds_ok = results["credentials"]["omie"].get("has_app_key", False) and results["credentials"]["omie"].get("has_app_secret", False)
    nibo_creds_ok = results["credentials"]["nibo"].get("has_token", False) and results["credentials"]["nibo"].get("has_company_id", False)
    
    print(f"🔐 Credenciais:")
    print(f"  Omie: {'✅' if omie_creds_ok else '❌'}")
    print(f"  Nibo: {'✅' if nibo_creds_ok else '❌'}")
    
    # Servidores HTTP
    omie_http_ok = results["http_endpoints"]["omie"].get("server_online", False)
    nibo_http_ok = results["http_endpoints"]["nibo"].get("server_online", False)
    
    print(f"🌐 Servidores HTTP:")
    print(f"  Omie: {'✅' if omie_http_ok else '❌'}")
    print(f"  Nibo: {'✅' if nibo_http_ok else '❌'}")
    
    # Ferramentas
    omie_tools_ok = results["basic_tools"]["omie"].get("testar_conexao", {}).get("success", False)
    nibo_tools_ok = results["basic_tools"]["nibo"].get("testar_conexao", {}).get("success", False)
    
    print(f"🔧 Ferramentas Básicas:")
    print(f"  Omie: {'✅' if omie_tools_ok else '❌'}")
    print(f"  Nibo: {'✅' if nibo_tools_ok else '❌'}")
    
    # STDIO
    omie_stdio_ok = results["stdio_connection"]["omie"].get("stdio_works", False)
    
    print(f"📡 STDIO:")
    print(f"  Omie: {'✅' if omie_stdio_ok else '❌'}")
    
    # Contagem de ferramentas descobertas
    omie_tools_count = results["http_endpoints"]["omie"].get("tools_count", 0)
    nibo_tools_count = results["http_endpoints"]["nibo"].get("tools_count", 0)
    
    print(f"📋 Ferramentas Descobertas:")
    print(f"  Omie: {omie_tools_count} ferramentas")
    print(f"  Nibo: {nibo_tools_count} ferramentas")
    
    # Status geral
    all_systems_ok = all([
        omie_creds_ok or nibo_creds_ok,  # Pelo menos uma credencial
        omie_http_ok or nibo_http_ok,    # Pelo menos um servidor
        omie_tools_ok or nibo_tools_ok   # Pelo menos uma ferramenta
    ])
    
    print(f"\n🎯 STATUS GERAL: {'✅ FUNCIONANDO' if all_systems_ok else '❌ PROBLEMAS DETECTADOS'}")
    
    # Salvar resultados
    output_file = "/Users/kleberdossantosribeiro/omie-mcp/test_results_comprehensive.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Recomendações
    print(f"\n💡 PRÓXIMOS PASSOS:")
    
    if not results["http_endpoints"]["omie"].get("server_online", False):
        print("1. Iniciar servidor HTTP Omie: python scripts/service_toggle.py start omie-mcp")
    
    if not results["http_endpoints"]["nibo"].get("server_online", False):
        print("2. Iniciar servidor HTTP Nibo: python scripts/service_toggle.py start nibo-mcp")
    
    if not results["credentials"]["omie"].get("has_app_key", False):
        print("3. Configurar credenciais Omie no arquivo credentials.json")
    
    if not results["credentials"]["nibo"].get("has_token", False):
        print("4. Configurar credenciais Nibo no arquivo nibo-mcp/credentials.json")
    
    total_tools = results["http_endpoints"]["omie"].get("tools_count", 0) + results["http_endpoints"]["nibo"].get("tools_count", 0)
    if total_tools < 40:
        print(f"5. Investigar por que apenas {total_tools} ferramentas foram descobertas (esperado: 51)")
    
    print(f"\n🎉 Teste concluído!")