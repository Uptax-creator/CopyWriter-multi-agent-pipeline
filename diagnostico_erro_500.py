#!/usr/bin/env python3
"""
Diagnóstico completo do erro 500 SOAP - IncluirCliente
Este script vai testar diferentes cenários para identificar a causa raiz
"""

import asyncio
import json
import os
import sys
import httpx
from datetime import datetime
from typing import Dict, Any

# Configuração de logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DiagnosticoOmie:
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

    async def _make_request(self, endpoint: str, call: str, param: Dict[str, Any], 
                           teste_nome: str = ""):
        """Faz uma requisição HTTP para a API do Omie com logging detalhado"""
        
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
                response_text = response.text
                
                logger.info(f"Status: {response.status_code}")
                logger.info(f"Headers: {dict(response.headers)}")
                logger.info(f"Response: {response_text}")
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        logger.error(f"Erro ao decodificar JSON: {response_text}")
                        return {"erro": "JSON inválido", "response": response_text}
                else:
                    return {
                        "erro": f"HTTP {response.status_code}",
                        "response": response_text,
                        "headers": dict(response.headers)
                    }
                        
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return {"erro": str(e)}

    async def teste_1_minimo_possivel(self):
        """Teste 1: Dados mínimos possíveis"""
        dados = {
            "razao_social": "TESTE DIAGNOSTICO",
            "cnpj_cpf": "11222333000155"
        }
        return await self._make_request("geral/clientes", "IncluirCliente", dados, 
                                      "Dados mínimos possíveis")

    async def teste_2_omie_documentacao(self):
        """Teste 2: Exatamente como na documentação Omie"""
        dados = {
            "razao_social": "TESTE OMIE DOC",
            "cnpj_cpf": "11222333000155",
            "email": "teste@omie.com",
            "cliente_fornecedor": "C"
        }
        return await self._make_request("geral/clientes", "IncluirCliente", dados,
                                      "Documentação Omie")

    async def teste_3_campos_obrigatorios(self):
        """Teste 3: Todos os campos possivelmente obrigatórios"""
        dados = {
            "razao_social": "TESTE CAMPOS OBRIGATORIOS",
            "cnpj_cpf": "11222333000155",
            "email": "teste@campos.com",
            "cliente_fornecedor": "C",
            "endereco": "Rua Teste, 123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234567",
            "telefone1_ddd": "11",
            "telefone1_numero": "999999999"
        }
        return await self._make_request("geral/clientes", "IncluirCliente", dados,
                                      "Todos campos obrigatórios")

    async def teste_4_validar_credenciais(self):
        """Teste 4: Validar se as credenciais estão funcionando"""
        dados = {}
        return await self._make_request("geral/clientes", "ListarClientes", dados,
                                      "Validar credenciais (ListarClientes)")

    async def teste_5_consultar_categorias(self):
        """Teste 5: Testar uma operação que sabemos que funciona"""
        dados = {"apenas_categoria_de_receita": "S"}
        return await self._make_request("geral/categorias", "ListarCategorias", dados,
                                      "Operação que funciona (categorias)")

    async def teste_6_diferentes_endpoints(self):
        """Teste 6: Testar diferentes formatos de endpoint"""
        dados_base = {
            "razao_social": "TESTE ENDPOINT",
            "cnpj_cpf": "11222333000155",
            "email": "teste@endpoint.com"
        }
        
        resultados = []
        
        # Endpoint com barra no final
        resultado1 = await self._make_request("geral/clientes", "IncluirCliente", dados_base,
                                            "Endpoint com barra")
        resultados.append(("com_barra", resultado1))
        
        # Endpoint sem barra (se diferente)
        dados_base["razao_social"] = "TESTE ENDPOINT SEM BARRA"
        resultado2 = await self._make_request("geral/clientes", "IncluirCliente", dados_base,
                                            "Endpoint sem barra")
        resultados.append(("sem_barra", resultado2))
        
        return resultados

    async def teste_7_caracteres_especiais(self):
        """Teste 7: Verificar se caracteres especiais causam problemas"""
        dados = {
            "razao_social": "TESTE CARACTERES",  # Sem acentos
            "cnpj_cpf": "11222333000155",
            "email": "teste@caracteres.com"
        }
        return await self._make_request("geral/clientes", "IncluirCliente", dados,
                                      "Sem caracteres especiais")

    async def executar_todos_testes(self):
        """Executa todos os testes diagnósticos"""
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO COMPLETO DO ERRO 500 SOAP")
        print("="*80)
        
        testes = [
            self.teste_4_validar_credenciais,
            self.teste_5_consultar_categorias,
            self.teste_1_minimo_possivel,
            self.teste_2_omie_documentacao,
            self.teste_7_caracteres_especiais,
            self.teste_3_campos_obrigatorios,
        ]
        
        resultados = {}
        
        for i, teste in enumerate(testes, 1):
            print(f"\n{'='*60}")
            print(f"Executando teste {i}/{len(testes)}: {teste.__name__}")
            print("="*60)
            
            try:
                resultado = await teste()
                resultados[teste.__name__] = resultado
                
                if isinstance(resultado, dict) and "erro" in resultado:
                    print(f"❌ ERRO: {resultado['erro']}")
                else:
                    print(f"✅ SUCESSO: {resultado}")
                    
            except Exception as e:
                print(f"💥 EXCEÇÃO: {str(e)}")
                resultados[teste.__name__] = {"erro": str(e)}
        
        # Teste especial para diferentes endpoints
        print(f"\n{'='*60}")
        print("Executando teste especial: diferentes endpoints")
        print("="*60)
        
        try:
            resultado_endpoints = await self.teste_6_diferentes_endpoints()
            resultados["teste_6_diferentes_endpoints"] = resultado_endpoints
            
            for nome, resultado in resultado_endpoints:
                if isinstance(resultado, dict) and "erro" in resultado:
                    print(f"❌ ERRO ({nome}): {resultado['erro']}")
                else:
                    print(f"✅ SUCESSO ({nome}): {resultado}")
                    
        except Exception as e:
            print(f"💥 EXCEÇÃO (endpoints): {str(e)}")
            resultados["teste_6_diferentes_endpoints"] = {"erro": str(e)}
        
        # Salvar resultados
        with open(f"diagnostico_resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
        
        # Análise final
        print(f"\n{'='*80}")
        print("📊 ANÁLISE FINAL DOS RESULTADOS")
        print("="*80)
        
        sucessos = []
        erros = []
        
        for nome, resultado in resultados.items():
            if isinstance(resultado, dict) and "erro" in resultado:
                erros.append((nome, resultado["erro"]))
            else:
                sucessos.append((nome, resultado))
        
        print(f"✅ SUCESSOS: {len(sucessos)}")
        for nome, _ in sucessos:
            print(f"  - {nome}")
        
        print(f"\n❌ ERROS: {len(erros)}")
        for nome, erro in erros:
            print(f"  - {nome}: {erro}")
        
        # Recomendações
        print(f"\n{'='*80}")
        print("🎯 RECOMENDAÇÕES")
        print("="*80)
        
        if len(sucessos) == 0:
            print("🚨 CRÍTICO: Nenhum teste passou!")
            print("   → Verificar credenciais")
            print("   → Verificar conectividade")
            print("   → Verificar se a API Omie está funcionando")
        elif "teste_4_validar_credenciais" in [s[0] for s in sucessos]:
            print("✅ Credenciais funcionam")
            if "teste_1_minimo_possivel" not in [s[0] for s in sucessos]:
                print("🔍 Problema específico com IncluirCliente")
                print("   → Verificar documentação da API")
                print("   → Verificar campos obrigatórios")
                print("   → Verificar formato dos dados")
        else:
            print("❌ Problema com credenciais ou conectividade")
        
        return resultados

if __name__ == "__main__":
    async def main():
        diagnostico = DiagnosticoOmie()
        await diagnostico.executar_todos_testes()
    
    asyncio.run(main())