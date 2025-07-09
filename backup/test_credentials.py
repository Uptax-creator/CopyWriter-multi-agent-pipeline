#!/usr/bin/env python3
"""
Script para testar TODAS as ferramentas do servidor MCP Omie completo
Salve este arquivo como: ~/omie-mcp/test_complete_features.py

Testa todas as 7 ferramentas:
1. cadastrar_cliente_fornecedor
2. consultar_categorias  
3. consultar_departamentos
4. consultar_tipos_documento
5. criar_conta_pagar
6. consultar_contas_pagar
7. consultar_contas_receber
"""

import os
import json
import httpx
import asyncio
from datetime import datetime, timedelta

# Credenciais
APP_KEY = os.getenv("OMIE_APP_KEY")
APP_SECRET = os.getenv("OMIE_APP_SECRET")

print("🔍 TESTE COMPLETO DE TODAS AS FERRAMENTAS OMIE MCP")
print("=" * 60)
print(f"App Key: {APP_KEY[:8]}...****" if APP_KEY else "❌ App Key não encontrada")
print(f"App Secret: {APP_SECRET[:8]}...****" if APP_SECRET else "❌ App Secret não encontrada")

if not APP_KEY or not APP_SECRET:
    print("\n❌ ERRO: Credenciais não configuradas!")
    print("Configure com:")
    print("export OMIE_APP_KEY='sua_app_key'")
    print("export OMIE_APP_SECRET='seu_app_secret'")
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

# Resultados dos testes
test_results = {}

async def test_1_consultar_categorias():
    """Teste 1: Consultar categorias"""
    print("\n🧪 TESTE 1: Consultar Categorias")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        params = {"pagina": 1, "registros_por_pagina": 10}
        result = await client._make_request("geral/categorias", "ListarCategorias", params)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["consultar_categorias"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        categorias = result.get("categoria_cadastro", [])
        total = result.get("total_de_registros", 0)
        
        print(f"✅ Sucesso! Encontradas {total} categorias")
        if categorias:
            print("📋 Primeiras categorias:")
            for i, cat in enumerate(categorias[:3]):
                codigo = cat.get("codigo", "N/A")
                descricao = cat.get("descricao", "N/A")
                print(f"   {i+1}. {codigo} - {descricao}")
        
        test_results["consultar_categorias"] = {"status": "sucesso", "total": total}
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["consultar_categorias"] = {"status": "erro", "message": str(e)}
        return False

async def test_2_consultar_departamentos():
    """Teste 2: Consultar departamentos"""
    print("\n🧪 TESTE 2: Consultar Departamentos")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        params = {"pagina": 1, "registros_por_pagina": 10}
        result = await client._make_request("geral/departamentos", "ListarDepartamentos", params)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["consultar_departamentos"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        departamentos = result.get("departamento_cadastro", [])
        total = result.get("total_de_registros", 0)
        
        print(f"✅ Sucesso! Encontrados {total} departamentos")
        if departamentos:
            print("📋 Primeiros departamentos:")
            for i, dept in enumerate(departamentos[:3]):
                codigo = dept.get("codigo", "N/A")
                descricao = dept.get("descricao", "N/A")
                print(f"   {i+1}. {codigo} - {descricao}")
        
        test_results["consultar_departamentos"] = {"status": "sucesso", "total": total}
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["consultar_departamentos"] = {"status": "erro", "message": str(e)}
        return False

async def test_3_consultar_tipos_documento():
    """Teste 3: Consultar tipos de documentos"""
    print("\n🧪 TESTE 3: Consultar Tipos de Documento")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        result = await client._make_request("geral/tiposdocumento", "ListarTiposDocumento", {})
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["consultar_tipos_documento"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        tipos = result.get("tipos_documento", [])
        
        print(f"✅ Sucesso! Encontrados {len(tipos)} tipos de documento")
        if tipos:
            print("📋 Primeiros tipos:")
            for i, tipo in enumerate(tipos[:5]):
                codigo = tipo.get("codigo", "N/A")
                descricao = tipo.get("descricao", "N/A")
                print(f"   {i+1}. {codigo} - {descricao}")
        
        test_results["consultar_tipos_documento"] = {"status": "sucesso", "total": len(tipos)}
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["consultar_tipos_documento"] = {"status": "erro", "message": str(e)}
        return False

async def test_4_cadastrar_cliente():
    """Teste 4: Cadastrar cliente"""
    print("\n🧪 TESTE 4: Cadastrar Cliente/Fornecedor")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dados = {
            "razao_social": f"Teste Completo MCP {timestamp}",
            "cnpj_cpf": f"12345678{timestamp[-6:]}",  # CNPJ fictício único
            "email": f"teste.completo.{timestamp}@mcp.com",
            "nome_fantasia": f"MCP Test {timestamp}",
            "tags": [{"tag": "TESTE_MCP_COMPLETO"}],
            "inativo": "N"
        }
        
        result = await client._make_request("geral/clientes", "IncluirCliente", dados)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["cadastrar_cliente_fornecedor"] = {"status": "erro", "message": result['faultstring']}
            return False, None
        
        codigo_cliente = result.get("codigo_cliente_omie")
        if codigo_cliente:
            print(f"✅ Sucesso! Cliente cadastrado com código: {codigo_cliente}")
            print(f"📋 Razão Social: {dados['razao_social']}")
            print(f"📧 Email: {dados['email']}")
            
            test_results["cadastrar_cliente_fornecedor"] = {
                "status": "sucesso", 
                "codigo_cliente": codigo_cliente,
                "razao_social": dados['razao_social']
            }
            return True, codigo_cliente
        else:
            print(f"⚠️  Resposta inesperada: {result}")
            test_results["cadastrar_cliente_fornecedor"] = {"status": "parcial", "response": str(result)}
            return False, None
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["cadastrar_cliente_fornecedor"] = {"status": "erro", "message": str(e)}
        return False, None

async def test_5_consultar_contas_pagar():
    """Teste 5: Consultar contas a pagar"""
    print("\n🧪 TESTE 5: Consultar Contas a Pagar")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        params = {"pagina": 1, "registros_por_pagina": 5}
        result = await client._make_request("financas/contapagar", "ListarContasPagar", params)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["consultar_contas_pagar"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        contas = result.get("conta_pagar_cadastro", [])
        total = result.get("total_de_registros", 0)
        
        print(f"✅ Sucesso! Encontradas {total} contas a pagar")
        if contas:
            print("📋 Primeiras contas:")
            for i, conta in enumerate(contas[:3]):
                doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                status = conta.get("status_titulo", "N/A")
                print(f"   {i+1}. Doc: {doc} | R$ {valor:,.2f} | Status: {status}")
        
        test_results["consultar_contas_pagar"] = {"status": "sucesso", "total": total}
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["consultar_contas_pagar"] = {"status": "erro", "message": str(e)}
        return False

async def test_6_consultar_contas_receber():
    """Teste 6: Consultar contas a receber"""
    print("\n🧪 TESTE 6: Consultar Contas a Receber")
    print("-" * 40)
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        params = {"pagina": 1, "registros_por_pagina": 5}
        result = await client._make_request("financas/contareceber", "ListarContasReceber", params)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["consultar_contas_receber"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        contas = result.get("conta_receber_cadastro", [])
        total = result.get("total_de_registros", 0)
        
        print(f"✅ Sucesso! Encontradas {total} contas a receber")
        if contas:
            print("📋 Primeiras contas:")
            for i, conta in enumerate(contas[:3]):
                doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                status = conta.get("status_titulo", "N/A")
                print(f"   {i+1}. Doc: {doc} | R$ {valor:,.2f} | Status: {status}")
        
        test_results["consultar_contas_receber"] = {"status": "sucesso", "total": total}
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["consultar_contas_receber"] = {"status": "erro", "message": str(e)}
        return False

async def test_7_criar_conta_pagar(codigo_fornecedor=None):
    """Teste 7: Criar conta a pagar"""
    print("\n🧪 TESTE 7: Criar Conta a Pagar")
    print("-" * 40)
    
    if not codigo_fornecedor:
        print("⚠️  Pulando teste - nenhum fornecedor disponível")
        print("💡 Para testar, você precisa ter um fornecedor cadastrado")
        test_results["criar_conta_pagar"] = {"status": "pulado", "message": "Sem fornecedor"}
        return False
    
    try:
        client = OmieTestClient(APP_KEY, APP_SECRET)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dados = {
            "codigo_cliente_fornecedor": codigo_fornecedor,
            "numero_documento": f"MCP-TEST-{timestamp}",
            "data_vencimento": "31/12/2025",
            "valor_documento": 500.00,
            "codigo_categoria": "1.01.01",
            "observacao": f"Conta de teste MCP criada em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "numero_parcela": 1,
            "codigo_tipo_documento": "01",
            "data_emissao": datetime.now().strftime("%d/%m/%Y"),
            "data_entrada": datetime.now().strftime("%d/%m/%Y"),
            "status_titulo": "ABERTO"
        }
        
        result = await client._make_request("financas/contapagar", "IncluirContaPagar", dados)
        
        if "faultstring" in result:
            print(f"❌ Erro: {result['faultstring']}")
            test_results["criar_conta_pagar"] = {"status": "erro", "message": result['faultstring']}
            return False
        
        codigo_lancamento = result.get("codigo_lancamento_omie")
        if codigo_lancamento:
            print(f"✅ Sucesso! Conta a pagar criada com código: {codigo_lancamento}")
            print(f"📋 Documento: {dados['numero_documento']}")
            print(f"💰 Valor: R$ {dados['valor_documento']:,.2f}")
            print(f"📅 Vencimento: {dados['data_vencimento']}")
            
            test_results["criar_conta_pagar"] = {
                "status": "sucesso", 
                "codigo_lancamento": codigo_lancamento,
                "numero_documento": dados['numero_documento']
            }
            return True
        else:
            print(f"⚠️  Resposta inesperada: {result}")
            test_results["criar_conta_pagar"] = {"status": "parcial", "response": str(result)}
            return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        test_results["criar_conta_pagar"] = {"status": "erro", "message": str(e)}
        return False

async def main():
    """Função principal - executa todos os testes"""
    
    print("\n🚀 INICIANDO TESTES DE TODAS AS FERRAMENTAS")
    print("=" * 60)
    
    # Executar testes em ordem
    success_count = 0
    total_tests = 7
    
    # Teste 1: Categorias
    if await test_1_consultar_categorias():
        success_count += 1
    
    # Teste 2: Departamentos  
    if await test_2_consultar_departamentos():
        success_count += 1
    
    # Teste 3: Tipos de documento
    if await test_3_consultar_tipos_documento():
        success_count += 1
    
    # Teste 4: Cadastrar cliente (necessário para teste 7)
    cadastro_ok, codigo_cliente = await test_4_cadastrar_cliente()
    if cadastro_ok:
        success_count += 1
    
    # Teste 5: Consultar contas a pagar
    if await test_5_consultar_contas_pagar():
        success_count += 1
    
    # Teste 6: Consultar contas a receber
    if await test_6_consultar_contas_receber():
        success_count += 1
    
    # Teste 7: Criar conta a pagar (usa o cliente cadastrado como fornecedor)
    if await test_7_criar_conta_pagar(codigo_cliente):
        success_count += 1
    
    # Resumo final
    print("\n" + "=" * 60)
    print("🎯 RESUMO DOS TESTES")
    print("=" * 60)
    
    print(f"📊 Resultado geral: {success_count}/{total_tests} testes bem-sucedidos")
    print(f"✅ Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    print("\n📋 Detalhamento por ferramenta:")
    
    tools = [
        ("consultar_categorias", "Consultar Categorias"),
        ("consultar_departamentos", "Consultar Departamentos"), 
        ("consultar_tipos_documento", "Consultar Tipos de Documento"),
        ("cadastrar_cliente_fornecedor", "Cadastrar Cliente/Fornecedor"),
        ("consultar_contas_pagar", "Consultar Contas a Pagar"),
        ("consultar_contas_receber", "Consultar Contas a Receber"),
        ("criar_conta_pagar", "Criar Conta a Pagar")
    ]
    
    for tool_key, tool_name in tools:
        result = test_results.get(tool_key, {"status": "não_testado"})
        status = result["status"]
        
        if status == "sucesso":
            icon = "✅"
            extra = f" ({result.get('total', 'N/A')} registros)" if 'total' in result else ""
        elif status == "erro":
            icon = "❌"
            extra = f" - {result.get('message', 'Erro desconhecido')}"
        elif status == "pulado":
            icon = "⏭️ "
            extra = f" - {result.get('message', 'Pulado')}"
        else:
            icon = "⚠️ "
            extra = " - Status desconhecido"
        
        print(f"   {icon} {tool_name}{extra}")
    
    print("\n💡 Dicas:")
    if success_count == total_tests:
        print("🎉 Perfeito! Todas as ferramentas estão funcionando!")
        print("🚀 Você pode prosseguir com a configuração do Claude Desktop")
    elif success_count >= 5:
        print("👍 Maioria das ferramentas funcionando!")
        print("🔧 Verifique os erros específicos acima")
    else:
        print("⚠️  Várias ferramentas com problemas")
        print("🔍 Verifique suas credenciais e configuração do Omie")
    
    print("\n📱 Próximos passos:")
    print("1. Substitua o omie_http_server.py pela versão completa")
    print("2. Reinicie o servidor com python omie_http_server.py") 
    print("3. Teste via navegador: http://localhost:8000/docs")
    print("4. Configure o Claude Desktop")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())