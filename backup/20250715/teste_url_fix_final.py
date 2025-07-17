#!/usr/bin/env python3
"""
Teste de correção final - Resolver erros HTTP 301
Baseado na análise dos resultados: URLs ainda incorretas
"""

import asyncio
import json
import os
import httpx
from datetime import datetime

# Configuração de logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OmieUrlFixFinal:
    def __init__(self):
        # Carregar credenciais
        self.app_key = os.getenv("OMIE_APP_KEY")
        self.app_secret = os.getenv("OMIE_APP_SECRET")
        
        if not self.app_key or not self.app_secret:
            try:
                with open("credentials.json", "r") as f:
                    creds = json.load(f)
                    self.app_key = creds.get("app_key")
                    self.app_secret = creds.get("app_secret")
            except:
                raise ValueError("Credenciais não encontradas!")
        
        # URL base CORRETA - sem trailing slash
        self.base_url = "https://app.omie.com.br/api/v1"
        logger.info(f"Credenciais carregadas: app_key={self.app_key[:8]}...")

    async def _make_request(self, endpoint: str, call: str, param: dict, teste_nome: str = ""):
        """Fazer requisição com URL correta"""
        
        # URL CORRETA: base + endpoint + trailing slash OBRIGATÓRIA
        if not endpoint.endswith('/'):
            endpoint = endpoint + '/'
        
        url = f"{self.base_url}/{endpoint}"
        
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param]
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TESTE: {teste_nome}")
        logger.info(f"URL FINAL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.post(url, json=payload)
                
                logger.info(f"Status: {response.status_code}")
                logger.info(f"URL Final (após redirects): {response.url}")
                logger.info(f"Response: {response.text}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return {"sucesso": True, "dados": data}
                    except:
                        return {"sucesso": True, "dados": response.text}
                else:
                    return {
                        "sucesso": False,
                        "erro": f"HTTP {response.status_code}",
                        "response": response.text,
                        "url_final": str(response.url)
                    }
                        
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return {"sucesso": False, "erro": str(e)}

    async def teste_consulta_clientes(self):
        """Teste básico de consulta - deve funcionar"""
        param = {"pagina": 1, "registros_por_pagina": 10}
        return await self._make_request(
            "geral/clientes/", 
            "ListarClientes", 
            param,
            "Consulta clientes - URL corrigida"
        )

    async def teste_consulta_categorias(self):
        """Teste de consulta categorias"""
        param = {"pagina": 1, "registros_por_pagina": 10}
        return await self._make_request(
            "geral/categorias/", 
            "ListarCategorias", 
            param,
            "Consulta categorias - URL corrigida"
        )

    async def teste_incluir_cliente_v1(self):
        """Teste incluir cliente - versão 1"""
        param = {
            "razao_social": "TESTE URL FIX V1",
            "cnpj_cpf": "11222333000155",
            "codigo_cliente_integracao": "URL_FIX_V1"
        }
        return await self._make_request(
            "geral/clientes/",
            "IncluirCliente", 
            param,
            "Incluir cliente V1 - URL corrigida"
        )

    async def teste_incluir_cliente_v2(self):
        """Teste incluir cliente - versão 2 com mais campos"""
        param = {
            "razao_social": "TESTE URL FIX V2",
            "cnpj_cpf": "11222333000188",
            "codigo_cliente_integracao": "URL_FIX_V2",
            "email": "teste@urlfix.com"
        }
        return await self._make_request(
            "geral/clientes/",
            "IncluirCliente", 
            param,
            "Incluir cliente V2 - URL corrigida"
        )

    async def teste_incluir_fornecedor(self):
        """Teste incluir fornecedor"""
        param = {
            "razao_social": "TESTE FORNECEDOR URL FIX",
            "cnpj_cpf": "11222333000199",
            "codigo_fornecedor_integracao": "FOR_URL_FIX"
        }
        return await self._make_request(
            "geral/fornecedores/",
            "IncluirFornecedor", 
            param,
            "Incluir fornecedor - URL corrigida"
        )

    async def executar_testes_finais(self):
        """Executar testes com URLs corrigidas"""
        print("\n" + "="*80)
        print("🔧 TESTE FINAL - CORREÇÃO DE URL HTTP 301")
        print("="*80)
        
        testes = [
            self.teste_consulta_clientes,
            self.teste_consulta_categorias,
            self.teste_incluir_cliente_v1,
            self.teste_incluir_cliente_v2,
            self.teste_incluir_fornecedor,
        ]
        
        resultados = {}
        sucessos = 0
        
        for i, teste in enumerate(testes, 1):
            print(f"\n{'='*60}")
            print(f"Executando teste {i}/{len(testes)}: {teste.__name__}")
            print("="*60)
            
            try:
                resultado = await teste()
                resultados[teste.__name__] = resultado
                
                if resultado.get("sucesso"):
                    print(f"✅ SUCESSO!")
                    sucessos += 1
                else:
                    print(f"❌ ERRO: {resultado.get('erro')}")
                    if 'url_final' in resultado:
                        print(f"🔗 URL Final: {resultado['url_final']}")
                    
            except Exception as e:
                print(f"💥 EXCEÇÃO: {str(e)}")
                resultados[teste.__name__] = {"sucesso": False, "erro": str(e)}
        
        # Análise final
        print(f"\n{'='*80}")
        print("📊 RESULTADO FINAL DOS TESTES DE URL")
        print("="*80)
        
        print(f"✅ SUCESSOS: {sucessos}/{len(testes)}")
        print(f"❌ FALHAS: {len(testes) - sucessos}/{len(testes)}")
        
        if sucessos == len(testes):
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("   → URLs corrigidas funcionando")
            print("   → API Omie respondendo corretamente")
            print("   → Problema HTTP 301 resolvido")
        elif sucessos > 0:
            print(f"\n🔧 PROGRESSO: {sucessos} de {len(testes)} funcionando")
            print("   → Algumas URLs corrigidas")
            print("   → Investigar falhas restantes")
        else:
            print("\n⚠️  Ainda há problemas com URLs")
            print("   → Verificar formato de endpoint")
            print("   → Analisar redirects")
        
        # Salvar resultado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"teste_url_fix_resultado_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\n📝 Resultados salvos em: {filename}")
        
        return resultados

if __name__ == "__main__":
    async def main():
        teste = OmieUrlFixFinal()
        await teste.executar_testes_finais()
    
    asyncio.run(main())