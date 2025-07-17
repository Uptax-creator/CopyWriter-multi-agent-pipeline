#!/usr/bin/env python3
"""
Teste final - Correção do CNPJ e verificação de endpoints
Problema identificado: CNPJ inválido e endpoint de fornecedores não existe
"""

import asyncio
import json
import os
import httpx
from datetime import datetime
import random

# Configuração de logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OmieTesteCorrecaoFinal:
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

    def gerar_cnpj_valido(self):
        """Gerar um CNPJ válido para teste"""
        # Base simples para gerar CNPJ de teste válido
        base = [1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0, 1]
        
        # Calcular primeiro dígito verificador
        soma = 0
        peso = 5
        for i in range(12):
            soma += base[i] * peso
            peso -= 1
            if peso < 2:
                peso = 9
        
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        # Calcular segundo dígito verificador
        base.append(dv1)
        soma = 0
        peso = 6
        for i in range(13):
            soma += base[i] * peso
            peso -= 1
            if peso < 2:
                peso = 9
        
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        base.append(dv2)
        
        # Formar o CNPJ
        cnpj = ''.join(map(str, base))
        return cnpj

    def gerar_cpf_valido(self):
        """Gerar um CPF válido para teste"""
        # Gerar 9 primeiros dígitos aleatórios
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcular primeiro dígito verificador
        soma = sum(cpf[i] * (10 - i) for i in range(9))
        dv1 = 0 if soma % 11 < 2 else 11 - (soma % 11)
        cpf.append(dv1)
        
        # Calcular segundo dígito verificador
        soma = sum(cpf[i] * (11 - i) for i in range(10))
        dv2 = 0 if soma % 11 < 2 else 11 - (soma % 11)
        cpf.append(dv2)
        
        return ''.join(map(str, cpf))

    async def _make_request(self, endpoint: str, call: str, param: dict, teste_nome: str = ""):
        """Fazer requisição com URL correta"""
        
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
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.post(url, json=payload)
                
                logger.info(f"Status: {response.status_code}")
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
                        "response": response.text
                    }
                        
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return {"sucesso": False, "erro": str(e)}

    async def teste_incluir_cliente_cnpj_valido(self):
        """Teste incluir cliente com CNPJ válido"""
        cnpj_valido = self.gerar_cnpj_valido()
        
        param = {
            "razao_social": "TESTE CNPJ VALIDO LTDA",
            "cnpj_cpf": cnpj_valido,
            "codigo_cliente_integracao": f"CLI_VALIDO_{cnpj_valido[:8]}"
        }
        return await self._make_request(
            "geral/clientes/",
            "IncluirCliente", 
            param,
            f"Cliente com CNPJ válido: {cnpj_valido}"
        )

    async def teste_incluir_cliente_cpf_valido(self):
        """Teste incluir cliente pessoa física com CPF válido"""
        cpf_valido = self.gerar_cpf_valido()
        
        param = {
            "razao_social": "TESTE CPF VALIDO",
            "cnpj_cpf": cpf_valido,
            "codigo_cliente_integracao": f"CLI_PF_{cpf_valido[:6]}",
            "pessoa_fisica": "S"
        }
        return await self._make_request(
            "geral/clientes/",
            "IncluirCliente", 
            param,
            f"Cliente PF com CPF válido: {cpf_valido}"
        )

    async def teste_incluir_cliente_completo(self):
        """Teste incluir cliente com dados mais completos"""
        cnpj_valido = self.gerar_cnpj_valido()
        
        param = {
            "razao_social": "EMPRESA TESTE COMPLETA LTDA",
            "nome_fantasia": "Teste Completa",
            "cnpj_cpf": cnpj_valido,
            "codigo_cliente_integracao": f"CLI_COMP_{cnpj_valido[:8]}",
            "email": "teste@empresacompleta.com",
            "telefone1_ddd": "11",
            "telefone1_numero": "999999999",
            "endereco": "Rua Teste",
            "endereco_numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234567"
        }
        return await self._make_request(
            "geral/clientes/",
            "IncluirCliente", 
            param,
            f"Cliente completo: {cnpj_valido}"
        )

    async def verificar_endpoints_fornecedores(self):
        """Verificar quais endpoints de fornecedores existem"""
        endpoints_para_testar = [
            "geral/fornecedor/",  # Singular
            "geral/fornecedores/",  # Plural
            "financas/fornecedor/",  # Outro módulo
            "fornecedores/",  # Direto
        ]
        
        resultados = []
        
        for endpoint in endpoints_para_testar:
            param = {"pagina": 1, "registros_por_pagina": 1}
            
            resultado = await self._make_request(
                endpoint,
                "ListarFornecedores", 
                param,
                f"Testar endpoint: {endpoint}"
            )
            
            resultados.append({
                "endpoint": endpoint,
                "resultado": resultado
            })
        
        return resultados

    async def executar_testes_completos(self):
        """Executar testes completos com correções"""
        print("\n" + "="*80)
        print("🔧 TESTE COMPLETO - CORREÇÃO CNPJ E ENDPOINTS")
        print("="*80)
        
        resultados = {}
        sucessos = 0
        total_testes = 0
        
        # Teste 1: Cliente com CNPJ válido
        print(f"\n{'='*60}")
        print("Teste 1: Cliente com CNPJ válido")
        print("="*60)
        
        try:
            resultado = await self.teste_incluir_cliente_cnpj_valido()
            resultados["cliente_cnpj_valido"] = resultado
            total_testes += 1
            
            if resultado.get("sucesso"):
                print("✅ SUCESSO: Cliente criado com CNPJ válido!")
                sucessos += 1
            else:
                print(f"❌ ERRO: {resultado.get('erro')}")
                
        except Exception as e:
            print(f"💥 EXCEÇÃO: {str(e)}")
            resultados["cliente_cnpj_valido"] = {"sucesso": False, "erro": str(e)}
            total_testes += 1
        
        # Teste 2: Cliente pessoa física
        print(f"\n{'='*60}")
        print("Teste 2: Cliente pessoa física com CPF válido")
        print("="*60)
        
        try:
            resultado = await self.teste_incluir_cliente_cpf_valido()
            resultados["cliente_cpf_valido"] = resultado
            total_testes += 1
            
            if resultado.get("sucesso"):
                print("✅ SUCESSO: Cliente PF criado com CPF válido!")
                sucessos += 1
            else:
                print(f"❌ ERRO: {resultado.get('erro')}")
                
        except Exception as e:
            print(f"💥 EXCEÇÃO: {str(e)}")
            resultados["cliente_cpf_valido"] = {"sucesso": False, "erro": str(e)}
            total_testes += 1
        
        # Teste 3: Cliente completo
        print(f"\n{'='*60}")
        print("Teste 3: Cliente com dados completos")
        print("="*60)
        
        try:
            resultado = await self.teste_incluir_cliente_completo()
            resultados["cliente_completo"] = resultado
            total_testes += 1
            
            if resultado.get("sucesso"):
                print("✅ SUCESSO: Cliente completo criado!")
                sucessos += 1
            else:
                print(f"❌ ERRO: {resultado.get('erro')}")
                
        except Exception as e:
            print(f"💥 EXCEÇÃO: {str(e)}")
            resultados["cliente_completo"] = {"sucesso": False, "erro": str(e)}
            total_testes += 1
        
        # Teste 4: Verificar endpoints de fornecedores
        print(f"\n{'='*60}")
        print("Teste 4: Verificar endpoints de fornecedores")
        print("="*60)
        
        try:
            resultado_fornecedores = await self.verificar_endpoints_fornecedores()
            resultados["verificacao_fornecedores"] = resultado_fornecedores
            
            print("📋 Resultados da verificação de endpoints:")
            for item in resultado_fornecedores:
                endpoint = item["endpoint"]
                resultado = item["resultado"]
                
                if resultado.get("sucesso"):
                    print(f"✅ {endpoint}: FUNCIONA")
                else:
                    print(f"❌ {endpoint}: {resultado.get('erro')}")
                
        except Exception as e:
            print(f"💥 EXCEÇÃO na verificação: {str(e)}")
            resultados["verificacao_fornecedores"] = {"erro": str(e)}
        
        # Análise final
        print(f"\n{'='*80}")
        print("📊 RESULTADO FINAL DOS TESTES")
        print("="*80)
        
        print(f"✅ SUCESSOS: {sucessos}/{total_testes}")
        print(f"❌ FALHAS: {total_testes - sucessos}/{total_testes}")
        
        if sucessos == total_testes:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("   → CNPJ/CPF corrigidos funcionando")
            print("   → API Omie totalmente funcional")
            print("   → Problema HTTP 500 RESOLVIDO!")
        elif sucessos > 0:
            print(f"\n🔧 PROGRESSO SIGNIFICATIVO!")
            print(f"   → {sucessos} de {total_testes} testes funcionando")
            print("   → Problema CNPJ identificado e corrigido")
            print("   → API básica funcionando")
        else:
            print("\n⚠️  Ainda há problemas para investigar")
        
        # Salvar resultado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"teste_final_resultado_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\n📝 Resultados salvos em: {filename}")
        
        return resultados

if __name__ == "__main__":
    async def main():
        teste = OmieTesteCorrecaoFinal()
        await teste.executar_testes_completos()
    
    asyncio.run(main())