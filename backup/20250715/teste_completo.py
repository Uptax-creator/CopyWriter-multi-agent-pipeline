#!/usr/bin/env python3
import asyncio
import json
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def teste_completo():
    print("🧪 TESTE COMPLETO DA APLICAÇÃO")
    print("="*50)
    
    client = OmieClientFinalCorrigido()
    
    # 1. Testar conexão
    print("1. Testando conexão...")
    if not await client.teste_conexao():
        print("❌ Falha na conexão")
        return
    
    # 2. Testar consultas
    print("\n2. Testando consultas...")
    try:
        clientes = await client.listar_clientes({"pagina": 1, "registros_por_pagina": 5})
        print(f"✅ Clientes: {len(clientes.get('clientes_cadastro', []))} encontrados")
        
        categorias = await client.listar_categorias({"pagina": 1, "registros_por_pagina": 5})
        print(f"✅ Categorias: {len(categorias.get('categoria_cadastro', []))} encontradas")
        
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")
        return
    
    # 3. Testar criação (se não houver rate limit)
    print("\n3. Testando criação...")
    try:
        resultado = await client.teste_cliente_completo()
        print("✅ Cliente de teste criado com sucesso!")
        print(f"🆔 ID: {resultado.get('codigo_cliente_omie', 'N/A')}")
        
    except Exception as e:
        if "Rate limit" in str(e) or "425" in str(e):
            print("⏳ Rate limit ativo - criação adiada")
        else:
            print(f"❌ Erro na criação: {e}")
    
    print("\n🎉 TESTE COMPLETO FINALIZADO!")

if __name__ == "__main__":
    asyncio.run(teste_completo())