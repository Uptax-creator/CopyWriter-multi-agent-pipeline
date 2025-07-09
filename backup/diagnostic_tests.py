#!/usr/bin/env python3
"""
Testes diagnósticos para resolver os erros 500
Salve como: ~/omie-mcp/diagnostic_tests.py
"""

import os
import json
import httpx
import asyncio
from datetime import datetime

# Credenciais
APP_KEY = os.getenv("OMIE_APP_KEY")
APP_SECRET = os.getenv("OMIE_APP_SECRET")

print("🔍 TESTES DIAGNÓSTICOS - ERROS 500")
print("=" * 50)
print(f"App Key: {APP_KEY[:8]}...****" if APP_KEY else "❌ App Key não encontrada")
print(f"App Secret: {APP_SECRET[:8]}...****" if APP_SECRET else "❌ App Secret não encontrada")

if not APP_KEY or not APP_SECRET:
    print("\n❌ ERRO: Credenciais não configuradas!")
    exit(1)

# Cliente HTTP para Omie
class OmieTestClient:
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://app.omie.com.br/api/v1"
    
    async def _make_request(self, endpoint: str, call: str, params: dict) -> dict:
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        url = f"{self.base_url}/{endpoint}/"
        
        print(f"📡 URL: {url}")
        print(f"📡 Call: {call}")
        print(f"📡 Params: {json.dumps(params, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                print(f"💥 Erro 500 - Resposta completa:")
                print(response.text)
            
            return response.json() if response.status_code == 200 else {"error": response.text, "status": response.status_code}

async def test_tipos_documento_methods():
    """Testa diferentes métodos para tipos de documento"""
    print("\n🧪 DIAGNÓSTICO 1: Tipos de Documento - Testando métodos")
    print("-" * 60)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    # Métodos possíveis baseados na documentação
    methods_to_test = [
        "ListarTiposDocumento",
        "ListarTiposDoc", 
        "listarTiposDocumento",
        "listarTiposDoc"
    ]
    
    for method in methods_to_test:
        print(f"\n🔍 Testando método: {method}")
        print("-" * 30)
        
        try:
            result = await client._make_request("geral/tiposdoc", method, {})
            
            if "error" not in result:
                print(f"✅ SUCESSO com método: {method}")
                
                # Mostrar estrutura da resposta
                if isinstance(result, dict):
                    print("📋 Estrutura da resposta:")
                    for key in result.keys():
                        value = result[key]
                        print(f"   • {key}: {type(value)} ({len(value) if isinstance(value, list) else 'N/A'})")
                        
                        # Se for lista, mostrar exemplo
                        if isinstance(value, list) and len(value) > 0:
                            print(f"     Exemplo: {value[0]}")
                
                return True, method
            else:
                print(f"❌ Falhou com método: {method}")
                
        except Exception as e:
            print(f"❌ Erro com método {method}: {e}")
    
    return False, None

async def test_cliente_fornecedor_minimal():
    """Testa cadastro de cliente com dados mínimos"""
    print("\n🧪 DIAGNÓSTICO 2: Cliente/Fornecedor - Dados mínimos")
    print("-" * 60)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    # Testes com diferentes combinações de dados
    test_cases = [
        {
            "name": "Apenas campos obrigatórios",
            "data": {
                "razao_social": "Teste Minimal Ltda",
                "cnpj_cpf": "12345678000195",
                "email": "teste@minimal.com"
            }
        },
        {
            "name": "Com campo inativo explícito",
            "data": {
                "razao_social": "Teste Inativo Ltda",
                "cnpj_cpf": "12345678000196",
                "email": "teste@inativo.com",
                "inativo": "N"
            }
        },
        {
            "name": "Com tags simples",
            "data": {
                "razao_social": "Teste Tags Ltda",
                "cnpj_cpf": "12345678000197",
                "email": "teste@tags.com",
                "tags": [{"tag": "TESTE"}]
            }
        },
        {
            "name": "CNPJ válido diferente",
            "data": {
                "razao_social": "Teste CNPJ Válido Ltda",
                "cnpj_cpf": "11222333000144",  # CNPJ com estrutura válida
                "email": "teste@cnpjvalido.com"
            }
        },
        {
            "name": "CPF em vez de CNPJ",
            "data": {
                "razao_social": "Teste CPF",
                "cnpj_cpf": "12345678901",  # CPF
                "email": "teste@cpf.com"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testando: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = await client._make_request("geral/clientes", "IncluirCliente", test_case['data'])
            
            if "error" not in result:
                print(f"✅ SUCESSO com: {test_case['name']}")
                
                if "codigo_cliente_omie" in result:
                    codigo = result["codigo_cliente_omie"]
                    print(f"🎯 Cliente criado com código: {codigo}")
                    return True, test_case['data'], codigo
                else:
                    print(f"⚠️  Resposta inesperada: {result}")
            else:
                print(f"❌ Falhou: {test_case['name']}")
                if result.get("status") == 500:
                    # Tentar extrair mais detalhes do erro
                    error_text = result.get("error", "")
                    if "faultstring" in error_text:
                        print(f"💡 Detalhe do erro: {error_text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return False, None, None

async def test_existing_client_for_conta_pagar():
    """Busca clientes existentes para usar na criação de conta a pagar"""
    print("\n🧪 DIAGNÓSTICO 3: Buscar clientes existentes")
    print("-" * 60)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    try:
        # Listar clientes existentes
        result = await client._make_request("geral/clientes", "ListarClientes", {"pagina": 1, "registros_por_pagina": 5})
        
        if "error" not in result:
            clientes = result.get("clientes_cadastro", [])
            
            if clientes:
                print(f"✅ Encontrados {len(clientes)} clientes existentes:")
                
                for i, cliente in enumerate(clientes):
                    codigo = cliente.get("codigo_cliente_omie", "N/A")
                    razao = cliente.get("razao_social", "N/A")
                    cnpj = cliente.get("cnpj_cpf", "N/A")
                    print(f"   {i+1}. Código: {codigo} | {razao} | {cnpj}")
                
                # Retornar o primeiro cliente para testar conta a pagar
                primeiro_cliente = clientes[0]
                codigo_cliente = primeiro_cliente.get("codigo_cliente_omie")
                
                if codigo_cliente:
                    print(f"\n🎯 Usando cliente código {codigo_cliente} para teste de conta a pagar")
                    return True, codigo_cliente
            else:
                print("❌ Nenhum cliente encontrado")
        else:
            print(f"❌ Erro ao listar clientes: {result}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False, None

async def test_conta_pagar_with_existing_client(codigo_cliente):
    """Testa criação de conta a pagar com cliente existente"""
    print(f"\n🧪 DIAGNÓSTICO 4: Criação de conta a pagar (cliente: {codigo_cliente})")
    print("-" * 60)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Dados mínimos para conta a pagar
    dados_conta = {
        "codigo_cliente_fornecedor": codigo_cliente,
        "numero_documento": f"DIAG-{timestamp}",
        "data_vencimento": "31/12/2025",
        "valor_documento": 100.00,
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABERTO"
    }
    
    try:
        result = await client._make_request("financas/contapagar", "IncluirContaPagar", dados_conta)
        
        if "error" not in result:
            print("✅ SUCESSO na criação de conta a pagar!")
            
            if "codigo_lancamento_omie" in result:
                codigo = result["codigo_lancamento_omie"]
                print(f"🎯 Conta criada com código: {codigo}")
                return True
            else:
                print(f"⚠️  Resposta inesperada: {result}")
        else:
            print(f"❌ Erro na criação de conta a pagar: {result}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False

async def main():
    """Função principal - executa todos os diagnósticos"""
    
    print("\n🚀 INICIANDO DIAGNÓSTICOS DETALHADOS")
    print("=" * 60)
    
    # Diagnóstico 1: Tipos de documento
    tipos_ok, tipos_method = await test_tipos_documento_methods()
    
    # Diagnóstico 2: Cadastro de cliente
    cliente_ok, cliente_data, cliente_codigo = await test_cliente_fornecedor_minimal()
    
    # Diagnóstico 3: Se não conseguiu criar, buscar existente
    if not cliente_ok:
        print("\n💡 Como não conseguiu criar cliente, buscando existentes...")
        existing_ok, existing_codigo = await test_existing_client_for_conta_pagar()
        if existing_ok:
            cliente_codigo = existing_codigo
            cliente_ok = True
    
    # Diagnóstico 4: Conta a pagar
    conta_ok = False
    if cliente_ok and cliente_codigo:
        conta_ok = await test_conta_pagar_with_existing_client(cliente_codigo)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 RESUMO DOS DIAGNÓSTICOS")
    print("=" * 60)
    
    print(f"📄 Tipos de Documento: {'✅ RESOLVIDO' if tipos_ok else '❌ PROBLEMA PERSISTE'}")
    if tipos_ok:
        print(f"   💡 Método funcionando: {tipos_method}")
    
    print(f"👥 Cadastro Cliente: {'✅ RESOLVIDO' if cliente_ok else '❌ PROBLEMA PERSISTE'}")
    if cliente_ok and cliente_data:
        print(f"   💡 Dados que funcionam: {cliente_data}")
    
    print(f"💰 Conta a Pagar: {'✅ RESOLVIDO' if conta_ok else '❌ PROBLEMA PERSISTE'}")
    
    success_count = sum([tipos_ok, cliente_ok, conta_ok])
    print(f"\n📊 Taxa de resolução: {success_count}/3 problemas resolvidos ({success_count/3*100:.1f}%)")
    
    if success_count == 3:
        print("🎉 TODOS OS PROBLEMAS RESOLVIDOS!")
        print("🚀 Agora você pode criar a versão final com 7 ferramentas funcionando!")
    elif success_count >= 1:
        print("👍 Alguns problemas resolvidos!")
        print("🔧 Use as soluções encontradas para atualizar o servidor")
    else:
        print("⚠️  Problemas complexos identificados")
        print("💡 Pode ser necessário verificar permissões da conta ou configuração do Omie")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())