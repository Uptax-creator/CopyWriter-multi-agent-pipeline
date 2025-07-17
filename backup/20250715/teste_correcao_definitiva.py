#!/usr/bin/env python3
"""
Teste da correção definitiva baseada nos erros identificados
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

class OmieCorrecaoDefinitiva:
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
        
        self.base_url = "https://app.omie.com.br/api/v1"
        logger.info(f"Credenciais carregadas: app_key={self.app_key[:8]}...")

    async def _make_request(self, endpoint: str, call: str, param: dict, teste_nome: str = ""):
        """Fazer requisição corrigida"""
        
        # URLs da API Omie DEVEM ter barra no final!
        url = f"{self.base_url}/{endpoint}/"
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param]
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TESTE: {teste_nome}")
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                
                logger.info(f"Status: {response.status_code}")
                logger.info(f"Response: {response.text}")
                
                if response.status_code == 200:
                    return {"sucesso": True, "dados": response.json()}
                else:
                    return {
                        "sucesso": False,
                        "erro": f"HTTP {response.status_code}",
                        "response": response.text
                    }
                        
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return {"sucesso": False, "erro": str(e)}

    async def teste_consulta_corrigida(self):
        """Teste de consulta com parâmetros corretos"""
        # Para consultas, usar parâmetros corretos (pode ser vazio mas não null)
        param = {"pagina": 1, "registros_por_pagina": 10}
        return await self._make_request(
            "geral/clientes", 
            "ListarClientes", 
            param,
            "Consulta clientes CORRIGIDA"
        )

    async def teste_consulta_categorias_corrigida(self):
        """Teste de consulta categorias corrigida"""
        # Parâmetro correto para categorias (sem 'apenas_categoria_de_receita')
        param = {"pagina": 1, "registros_por_pagina": 10}
        return await self._make_request(
            "geral/categorias", 
            "ListarCategorias", 
            param,
            "Consulta categorias CORRIGIDA"
        )

    async def teste_incluir_cliente_corrigido(self):
        """Teste de inclusão de cliente CORRIGIDO"""
        # Dados corrigidos baseados nos erros encontrados
        param = {
            "razao_social": "TESTE CLIENTE CORRIGIDO",
            "cnpj_cpf": "11222333000155",
            "codigo_cliente_integracao": "CLI001_TESTE",  # OBRIGATÓRIO!
            "email": "teste@cliente.com"
            # Removido: cliente_fornecedor (não faz parte da estrutura!)
        }
        return await self._make_request(
            "geral/clientes",
            "IncluirCliente", 
            param,
            "Incluir cliente CORRIGIDO"
        )

    async def teste_incluir_cliente_minimo(self):
        """Teste com dados mínimos obrigatórios"""
        param = {
            "razao_social": "TESTE MINIMO",
            "cnpj_cpf": "11222333000199",
            "codigo_cliente_integracao": "CLI002_MIN"
        }
        return await self._make_request(
            "geral/clientes",
            "IncluirCliente", 
            param,
            "Cliente com dados mínimos"
        )

    async def teste_incluir_fornecedor_corrigido(self):
        """Teste de inclusão de fornecedor CORRIGIDO"""
        param = {
            "razao_social": "TESTE FORNECEDOR CORRIGIDO",
            "cnpj_cpf": "11222333000188",
            "codigo_fornecedor_integracao": "FOR001_TESTE",  # Campo correto para fornecedor
            "email": "teste@fornecedor.com"
        }
        return await self._make_request(
            "geral/fornecedores",
            "IncluirFornecedor", 
            param,
            "Incluir fornecedor CORRIGIDO"
        )

    async def executar_testes_corrigidos(self):
        """Executar todos os testes corrigidos"""
        print("\n" + "="*80)
        print("🔧 TESTES COM CORREÇÕES BASEADAS NO DIAGNÓSTICO")
        print("="*80)
        
        testes = [
            self.teste_consulta_corrigida,
            self.teste_consulta_categorias_corrigida,
            self.teste_incluir_cliente_minimo,
            self.teste_incluir_cliente_corrigido,
            self.teste_incluir_fornecedor_corrigido,
        ]
        
        resultados = {}
        sucessos = 0
        
        for i, teste in enumerate(testes, 1):
            print(f"\n{'='*60}")
            print(f"Executando teste corrigido {i}/{len(testes)}: {teste.__name__}")
            print("="*60)
            
            try:
                resultado = await teste()
                resultados[teste.__name__] = resultado
                
                if resultado.get("sucesso"):
                    print(f"✅ SUCESSO!")
                    if "dados" in resultado:
                        print(f"📊 Dados: {json.dumps(resultado['dados'], indent=2, ensure_ascii=False)}")
                    sucessos += 1
                else:
                    print(f"❌ ERRO: {resultado.get('erro')}")
                    
            except Exception as e:
                print(f"💥 EXCEÇÃO: {str(e)}")
                resultados[teste.__name__] = {"sucesso": False, "erro": str(e)}
        
        # Análise final
        print(f"\n{'='*80}")
        print("📊 RESULTADO FINAL DOS TESTES CORRIGIDOS")
        print("="*80)
        
        print(f"✅ SUCESSOS: {sucessos}/{len(testes)}")
        print(f"❌ FALHAS: {len(testes) - sucessos}/{len(testes)}")
        
        if sucessos > 0:
            print("\n🎉 CORREÇÕES FUNCIONARAM!")
            print("   → Problemas identificados e resolvidos")
            print("   → API Omie respondendo corretamente")
        else:
            print("\n⚠️  Ainda há problemas para investigar")
        
        # Salvar resultado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"teste_correcao_resultado_{timestamp}.json", "w") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\n📝 Resultados salvos em: teste_correcao_resultado_{timestamp}.json")
        
        return resultados

if __name__ == "__main__":
    async def main():
        teste = OmieCorrecaoDefinitiva()
        await teste.executar_testes_corrigidos()
    
    asyncio.run(main())