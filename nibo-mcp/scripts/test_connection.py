#!/usr/bin/env python3
"""
Script para testar a conectividade com a API do Nibo
"""
import asyncio
import json
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import NiboConfig
from src.core.nibo_client import NiboClient

async def main():
    """Testa a conexão com a API do Nibo"""
    print("🔧 Testando conectividade com API do Nibo...")
    
    try:
        # Inicializar configuração
        config = NiboConfig()
        print(f"✅ Configuração carregada")
        print(f"   - Base URL: {config.current_company.base_url if config.current_company else 'N/A'}")
        print(f"   - API Token configurado: {'Sim' if config.api_token else 'Não'}")
        print(f"   - Company ID configurado: {'Sim' if config.company_id else 'Não'}")
        
        if not config.is_configured():
            print("❌ Credenciais não configuradas!")
            print("   Configure o arquivo credentials.json ou variáveis de ambiente:")
            print("   - NIBO_API_TOKEN")
            print("   - NIBO_COMPANY_ID")
            return
        
        # Inicializar cliente
        client = NiboClient(config)
        print("✅ Cliente Nibo inicializado")
        
        # Testar conexão
        print("🌐 Testando conexão...")
        result = await client.testar_conexao()
        
        if result["success"]:
            print("✅ Conexão estabelecida com sucesso!")
            print(f"   Resposta da API: {json.dumps(result['api_response'], indent=2)}")
        else:
            print("❌ Falha na conexão!")
            print(f"   Erro: {result['message']}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    asyncio.run(main())