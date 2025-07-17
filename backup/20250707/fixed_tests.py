#!/usr/bin/env python3
"""
Testes CORRIGIDOS com as soluções dos problemas identificados
Salve como: ~/omie-mcp/fixed_tests.py
"""

import os
import json
import httpx
import asyncio
from datetime import datetime

# Credenciais
APP_KEY = os.getenv("OMIE_APP_KEY")
APP_SECRET = os.getenv("OMIE_APP_SECRET")

print("🔧 TESTES CORRIGIDOS - APLICANDO SOLUÇÕES")
print("=" * 50)
print(f"App Key: {APP_KEY[:8]}...****" if APP_KEY else "❌ App Key não encontrada")

if not APP_KEY or not APP_SECRET:
    print("\n❌ ERRO: Credenciais não configuradas!")
    exit(1)

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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = {"error": response.text, "status": response.status_code}
                try:
                    json_error = response.json()
                    if "faultstring" in json_error:
                        error_data["faultstring"] = json_error["faultstring"]
                except:
                    pass
                return error_data

async def test_cadastro_cliente_corrigido():
    """Teste cadastro de cliente COM campo codigo_cliente_integracao"""
    print("\n🧪 TESTE CORRIGIDO: Cadastro Cliente")
    print("-" * 40)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # CORREÇÃO: Adicionar codigo_cliente_integracao obrigatório
    dados_corrigidos = {
        "codigo_cliente_integracao": f"MCP_{timestamp}",  # ✅ CAMPO OBRIGATÓRIO ADICIONADO
        "razao_social": "Teste Corrigido MCP Ltda",
        "cnpj_cpf": "12345678000190",
        "email": f"teste.corrigido.{timestamp}@mcp.com",
        "inativo": "N"
    }
    
    print("📋 Dados sendo enviados:")
    print(json.dumps(dados_corrigidos, indent=2))
    
    try:
        result = await client._make_request("geral/clientes", "IncluirCliente", dados_corrigidos)
        
        if "error" not in result:
            print("✅ SUCESSO! Cliente cadastrado com correção!")
            
            if "codigo_cliente_omie" in result:
                codigo = result["codigo_cliente_omie"]
                print(f"🎯 Cliente criado com código: {codigo}")
                print(f"🔗 Código integração: {dados_corrigidos['codigo_cliente_integracao']}")
                return True, codigo, dados_corrigidos['codigo_cliente_integracao']
            else:
                print(f"⚠️  Resposta inesperada: {result}")
        else:
            print(f"❌ Ainda com erro: {result}")
            if "faultstring" in result:
                print(f"💡 Detalhes: {result['faultstring']}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False, None, None

async def test_conta_pagar_corrigida(codigo_cliente):
    """Teste conta a pagar COM status corrigido"""
    print(f"\n🧪 TESTE CORRIGIDO: Conta a Pagar (cliente: {codigo_cliente})")
    print("-" * 40)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # CORREÇÃO: STATUS_TITULO com máximo 3 caracteres
    dados_corrigidos = {
        "codigo_cliente_fornecedor": codigo_cliente,
        "numero_documento": f"COR-{timestamp}",
        "data_vencimento": "31/12/2025",
        "valor_documento": 150.00,
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABE"  # ✅ CORRIGIDO: 3 caracteres em vez de "ABERTO"
    }
    
    print("📋 Dados sendo enviados:")
    print(json.dumps(dados_corrigidos, indent=2))
    
    try:
        result = await client._make_request("financas/contapagar", "IncluirContaPagar", dados_corrigidos)
        
        if "error" not in result:
            print("✅ SUCESSO! Conta a pagar criada com correção!")
            
            if "codigo_lancamento_omie" in result:
                codigo = result["codigo_lancamento_omie"]
                print(f"🎯 Conta criada com código: {codigo}")
                print(f"💰 Valor: R$ {dados_corrigidos['valor_documento']:,.2f}")
                print(f"📅 Vencimento: {dados_corrigidos['data_vencimento']}")
                return True, codigo
            else:
                print(f"⚠️  Resposta inesperada: {result}")
        else:
            print(f"❌ Ainda com erro: {result}")
            if "faultstring" in result:
                print(f"💡 Detalhes: {result['faultstring']}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False, None

async def test_conta_pagar_com_cliente_existente():
    """Teste conta a pagar usando cliente já existente"""
    print(f"\n🧪 TESTE: Conta a Pagar com Cliente Existente")
    print("-" * 40)
    
    # Código do primeiro cliente encontrado no diagnóstico
    codigo_cliente_existente = 2197692289
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Dados corrigidos para conta a pagar
    dados_corrigidos = {
        "codigo_cliente_fornecedor": codigo_cliente_existente,
        "numero_documento": f"EX-{timestamp}",
        "data_vencimento": "31/12/2025",
        "valor_documento": 200.00,
        "data_emissao": datetime.now().strftime("%d/%m/%Y"),
        "status_titulo": "ABE"  # ✅ CORRIGIDO: 3 caracteres
    }
    
    print("📋 Dados sendo enviados:")
    print(json.dumps(dados_corrigidos, indent=2))
    
    try:
        result = await client._make_request("financas/contapagar", "IncluirContaPagar", dados_corrigidos)
        
        if "error" not in result:
            print("✅ SUCESSO! Conta a pagar criada com cliente existente!")
            
            if "codigo_lancamento_omie" in result:
                codigo = result["codigo_lancamento_omie"]
                print(f"🎯 Conta criada com código: {codigo}")
                print(f"👤 Cliente: {codigo_cliente_existente}")
                print(f"💰 Valor: R$ {dados_corrigidos['valor_documento']:,.2f}")
                return True, codigo
            else:
                print(f"⚠️  Resposta inesperada: {result}")
        else:
            print(f"❌ Ainda com erro: {result}")
            if "faultstring" in result:
                print(f"💡 Detalhes: {result['faultstring']}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False, None

async def test_all_working_features():
    """Testa todas as funcionalidades que já funcionam"""
    print(f"\n🧪 TESTE: Funcionalidades que já funcionam")
    print("-" * 40)
    
    client = OmieTestClient(APP_KEY, APP_SECRET)
    
    # 1. Categorias
    print("📊 Testando categorias...")
    categorias = await client._make_request("geral/categorias", "ListarCategorias", {"pagina": 1, "registros_por_pagina": 5})
    categorias_ok = "error" not in categorias
    total_cat = categorias.get("total_de_registros", 0) if categorias_ok else 0
    
    # 2. Departamentos
    print("🏢 Testando departamentos...")
    departamentos = await client._make_request("geral/departamentos", "ListarDepartamentos", {"pagina": 1, "registros_por_pagina": 5})
    departamentos_ok = "error" not in departamentos
    total_dep = departamentos.get("total_de_registros", 0) if departamentos_ok else 0
    
    # 3. Contas a pagar
    print("💰 Testando contas a pagar...")
    contas_pagar = await client._make_request("financas/contapagar", "ListarContasPagar", {"pagina": 1, "registros_por_pagina": 5})
    contas_pagar_ok = "error" not in contas_pagar
    total_cp = contas_pagar.get("total_de_registros", 0) if contas_pagar_ok else 0
    
    # 4. Contas a receber
    print("💵 Testando contas a receber...")
    contas_receber = await client._make_request("financas/contareceber", "ListarContasReceber", {"pagina": 1, "registros_por_pagina": 5})
    contas_receber_ok = "error" not in contas_receber
    total_cr = contas_receber.get("total_de_registros", 0) if contas_receber_ok else 0
    
    return {
        "categorias": {"ok": categorias_ok, "total": total_cat},
        "departamentos": {"ok": departamentos_ok, "total": total_dep},
        "contas_pagar": {"ok": contas_pagar_ok, "total": total_cp},
        "contas_receber": {"ok": contas_receber_ok, "total": total_cr}
    }

async def main():
    """Função principal - aplica todas as correções"""
    
    print("\n🚀 APLICANDO TODAS AS CORREÇÕES")
    print("=" * 50)
    
    # 1. Testar funcionalidades que já funcionam
    working_features = await test_all_working_features()
    
    # 2. Testar cadastro de cliente corrigido
    cliente_ok, cliente_codigo, cliente_integracao = await test_cadastro_cliente_corrigido()
    
    # 3. Testar conta a pagar com cliente recém-criado
    conta_nova_ok, conta_nova_codigo = False, None
    if cliente_ok and cliente_codigo:
        conta_nova_ok, conta_nova_codigo = await test_conta_pagar_corrigida(cliente_codigo)
    
    # 4. Testar conta a pagar com cliente existente
    conta_existente_ok, conta_existente_codigo = await test_conta_pagar_com_cliente_existente()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 RESUMO DAS CORREÇÕES APLICADAS")
    print("=" * 60)
    
    # Funcionalidades que já funcionavam
    working_count = 0
    print("✅ Funcionalidades que já funcionavam:")
    for feature, data in working_features.items():
        status = "✅" if data["ok"] else "❌"
        print(f"   {status} {feature}: {data['total']} registros")
        if data["ok"]:
            working_count += 1
    
    # Funcionalidades corrigidas
    fixed_count = 0
    print("\n🔧 Funcionalidades corrigidas:")
    
    if cliente_ok:
        print(f"   ✅ Cadastro Cliente: CORRIGIDO (código: {cliente_codigo})")
        print(f"      💡 Solução: campo 'codigo_cliente_integracao' obrigatório")
        fixed_count += 1
    else:
        print(f"   ❌ Cadastro Cliente: ainda com problemas")
    
    if conta_nova_ok or conta_existente_ok:
        print(f"   ✅ Conta a Pagar: CORRIGIDA")
        if conta_nova_ok:
            print(f"      🎯 Nova conta criada: {conta_nova_codigo}")
        if conta_existente_ok:
            print(f"      🎯 Conta com cliente existente: {conta_existente_codigo}")
        print(f"      💡 Solução: status_titulo máximo 3 chars ('ABE')")
        fixed_count += 1
    else:
        print(f"   ❌ Conta a Pagar: ainda com problemas")
    
    # Funcionalidades removidas
    print("\n❌ Funcionalidades removidas (APIs não disponíveis):")
    print("   ❌ Tipos de Documento: API sem métodos funcionais")
    
    # Total final
    total_working = working_count + fixed_count
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   ✅ Funcionalidades funcionando: {total_working}/6")
    print(f"   📈 Taxa de sucesso: {(total_working/6)*100:.1f}%")
    
    if total_working >= 5:
        print("\n🎉 EXCELENTE! Servidor MCP pode ser criado com confiança!")
        print("🚀 Próximos passos:")
        print("   1. Criar servidor otimizado com funcionalidades corrigidas")
        print("   2. Configurar Claude Desktop")
        print("   3. Testar no Claude Desktop")
    elif total_working >= 4:
        print("\n👍 BOM! Maioria das funcionalidades funcionando!")
        print("🔧 Pode prosseguir com servidor otimizado")
    else:
        print("\n⚠️  Ainda há problemas a resolver")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())