#!/usr/bin/env python3
"""
Teste Completo para MCP Omie ERP - TODAS AS FERRAMENTAS
Foco especial em contas a pagar e receber com CNPJ válido

Testa especificamente:
1. cadastrar_cliente_fornecedor ✅ (com CNPJ válido)
2. consultar_tipos_documento ✅
3. criar_conta_pagar ✅ (ferramenta pendente)
4. criar_conta_receber ✅ (ferramenta pendente) 
5. consultar_contas_pagar ✅
6. consultar_contas_receber ✅

CNPJ usado: 24.493.607/0001-19 (válido fornecido pelo usuário)
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import httpx


class OmieMCPCompleteRester:
    """Classe para testar TODAS as ferramentas do MCP Omie"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.codigo_cliente_criado = None  # Para armazenar o código do cliente criado
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{'='*70}")
        print(f"🔧 {title}")
        print(f"{'='*70}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Imprime mensagem informativa"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """Imprime mensagem de aviso"""
        print(f"⚠️  {message}")
    
    def print_highlight(self, message: str):
        """Imprime mensagem destacada"""
        print(f"🎯 {message}")
    
    async def test_server_status(self) -> bool:
        """Testa se o servidor completo está rodando"""
        self.print_header("TESTE 1: Status do Servidor Completo")
        
        try:
            response = await self.client.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Servidor completo está rodando!")
                self.print_info(f"Versão: {data.get('version', 'N/A')}")
                self.print_info(f"Ferramentas: {len(data.get('tools', []))} disponíveis")
                
                # Verificar recursos de teste
                if "test_features" in data:
                    self.print_highlight("Recursos de teste disponíveis:")
                    for feature in data["test_features"]:
                        print(f"    {feature}")
                
                # Verificar dados de teste
                if "test_data_sample" in data:
                    sample = data["test_data_sample"]
                    self.print_info(f"CNPJ para testes: {sample.get('cnpj_usado', 'N/A')}")
                    self.print_info(f"Localização: {sample.get('cidade', 'N/A')}/{sample.get('estado', 'N/A')}")
                
                return True
            else:
                self.print_error(f"Servidor retornou status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Não foi possível conectar ao servidor: {e}")
            self.print_info("Certifique-se que o servidor completo está rodando na porta 8000")
            return False
    
    async def test_get_test_data(self) -> Dict:
        """Obtém dados de teste realistas do servidor"""
        self.print_header("TESTE 2: Obtendo Dados de Teste Realistas")
        
        try:
            response = await self.client.get(f"{self.base_url}/test/dados-realistas")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Dados de teste obtidos!")
                
                test_data = data.get("dados_de_teste", {})
                if "cliente_teste" in test_data:
                    cliente = test_data["cliente_teste"]
                    self.print_info(f"Empresa: {cliente.get('razao_social', 'N/A')}")
                    self.print_info(f"CNPJ: {cliente.get('cnpj_cpf', 'N/A')}")
                    self.print_info(f"E-mail: {cliente.get('email', 'N/A')}")
                
                return test_data
            else:
                self.print_error(f"Erro ao obter dados de teste: {response.status_code}")
                return {}
                
        except Exception as e:
            self.print_error(f"Erro ao obter dados de teste: {e}")
            return {}
    
    async def test_mcp_tools_list(self) -> bool:
        """Testa a listagem de ferramentas MCP"""
        self.print_header("TESTE 3: Listagem de Ferramentas MCP")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    self.print_success(f"Encontradas {len(tools)} ferramentas!")
                    
                    expected_tools = [
                        "cadastrar_cliente_fornecedor",
                        "consultar_tipos_documento",
                        "criar_conta_pagar",
                        "criar_conta_receber",  # Nova ferramenta
                        "consultar_contas_pagar",
                        "consultar_contas_receber"
                    ]
                    
                    found_tools = []
                    for tool in tools:
                        name = tool['name']
                        is_expected = name in expected_tools
                        status = "✅" if is_expected else "⚠️"
                        print(f"    {status} {name}")
                        if is_expected:
                            found_tools.append(name)
                    
                    missing_tools = set(expected_tools) - set(found_tools)
                    if missing_tools:
                        self.print_warning(f"Ferramentas faltando: {', '.join(missing_tools)}")
                    else:
                        self.print_highlight("TODAS as ferramentas esperadas estão disponíveis!")
                    
                    return len(missing_tools) == 0
                else:
                    self.print_error("Resposta inválida da listagem de ferramentas")
                    return False
            else:
                self.print_error(f"Erro na listagem: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao listar ferramentas: {e}")
            return False
    
    async def test_consultar_tipos_documento(self) -> bool:
        """Testa consulta de tipos de documentos"""
        self.print_header("TESTE 4: Consultar Tipos de Documentos")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "consultar_tipos_documento",
                    "arguments": {}
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("Tipos de documentos consultados!")
                    
                    # Verificar tipos importantes
                    tipos_importantes = ["NF", "BOL", "DUP", "PIX", "REC"]
                    tipos_encontrados = []
                    
                    for tipo in tipos_importantes:
                        if tipo in result_text:
                            tipos_encontrados.append(tipo)
                    
                    self.print_info(f"Tipos importantes encontrados: {', '.join(tipos_encontrados)}")
                    
                    return len(tipos_encontrados) >= 3
                else:
                    self.print_error("Erro na resposta")
                    return False
            else:
                self.print_error(f"Erro na consulta: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao consultar tipos: {e}")
            return False
    
    async def test_cadastrar_cliente_com_cnpj_valido(self, test_data: Dict) -> Optional[int]:
        """Testa cadastro com CNPJ válido fornecido pelo usuário"""
        self.print_header("TESTE 5: Cadastrar Cliente com CNPJ Válido (24.493.607/0001-19)")
        
        if not test_data or "cliente_teste" not in test_data:
            self.print_error("Dados de teste não disponíveis")
            return None
        
        dados_cliente = test_data["cliente_teste"].copy()
        
        # Garantir que está usando o CNPJ correto
        dados_cliente["cnpj_cpf"] = "24493607000119"  # CNPJ válido sem pontuação
        
        # Tornar único
        timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
        dados_cliente["razao_social"] = f"TESTE COMPLETO MCP LTDA {timestamp}"
        dados_cliente["email"] = f"teste.completo.{timestamp}@testeomie.com.br"
        
        self.print_info(f"Cadastrando: {dados_cliente['razao_social']}")
        self.print_info(f"CNPJ: {dados_cliente['cnpj_cpf']} (válido)")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "cadastrar_cliente_fornecedor",
                    "arguments": dados_cliente
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("Cliente cadastrado com CNPJ válido!")
                    
                    # Extrair código do cliente
                    import re
                    codigo_matches = re.findall(r'[Cc]ódigo.*?(\d+)', result_text)
                    if codigo_matches:
                        codigo_cliente = int(codigo_matches[0])
                        self.codigo_cliente_criado = codigo_cliente
                        self.print_highlight(f"CÓDIGO DO CLIENTE CRIADO: {codigo_cliente}")
                        self.print_info("Este código será usado nos próximos testes!")
                        return codigo_cliente
                    else:
                        self.print_warning("Cliente criado mas código não extraído automaticamente")
                        # Tentar extrair de outra forma
                        numeros = re.findall(r'\d+', result_text)
                        if numeros:
                            codigo_cliente = int(numeros[0])
                            self.codigo_cliente_criado = codigo_cliente
                            self.print_info(f"Código extraído: {codigo_cliente}")
                            return codigo_cliente
                        return None
                else:
                    self.print_error("Erro na resposta do cadastro")
                    return None
            else:
                self.print_error(f"Erro no cadastro: {response.status_code}")
                if response.text:
                    self.print_info(f"Detalhes: {response.text[:200]}...")
                return None
                
        except Exception as e:
            self.print_error(f"Erro ao cadastrar cliente: {e}")
            return None
    
    async def test_criar_conta_pagar(self, codigo_cliente: int) -> bool:
        """Testa criação de conta a pagar - FERRAMENTA PENDENTE"""
        self.print_header("TESTE 6: Criar Conta a Pagar (FERRAMENTA PENDENTE)")
        
        # Data de vencimento: 45 dias no futuro
        data_vencimento = (datetime.now() + timedelta(days=45)).strftime("%d/%m/%Y")
        timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
        
        dados_conta = {
            "codigo_cliente_fornecedor": codigo_cliente,
            "numero_documento": f"NF-TESTE-PAGAR-{timestamp}",
            "data_vencimento": data_vencimento,
            "valor_documento": 1250.75,
            "codigo_categoria": "1.01.01",
            "observacao": "Conta a pagar criada via teste completo MCP - CNPJ válido",
            "numero_parcela": 1
        }
        
        self.print_info(f"Fornecedor: {codigo_cliente}")
        self.print_info(f"Documento: {dados_conta['numero_documento']}")
        self.print_info(f"Valor: R$ {dados_conta['valor_documento']:,.2f}")
        self.print_info(f"Vencimento: {data_vencimento}")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "criar_conta_pagar",
                    "arguments": dados_conta
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("CONTA A PAGAR CRIADA COM SUCESSO!")
                    
                    # Verificar se contém informações esperadas
                    if "Código do Lançamento" in result_text:
                        self.print_highlight("Código do lançamento encontrado na resposta!")
                    if "R$" in result_text:
                        self.print_info("Valor monetário confirmado na resposta")
                    
                    # Mostrar trecho da resposta
                    lines = result_text.split('\n')[:8]
                    self.print_info("Resposta resumida:")
                    for line in lines:
                        if line.strip():
                            print(f"    {line}")
                    
                    return True
                else:
                    self.print_error("Erro na resposta da criação")
                    return False
            else:
                self.print_error(f"Erro na criação: {response.status_code}")
                if response.text:
                    self.print_info(f"Detalhes: {response.text[:200]}...")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao criar conta a pagar: {e}")
            return False
    
    async def test_criar_conta_receber(self, codigo_cliente: int) -> bool:
        """Testa criação de conta a receber - FERRAMENTA PENDENTE"""
        self.print_header("TESTE 7: Criar Conta a Receber (FERRAMENTA PENDENTE)")
        
        # Data de vencimento: 30 dias no futuro
        data_vencimento = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
        timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
        
        dados_conta = {
            "codigo_cliente_fornecedor": codigo_cliente,
            "numero_documento": f"NF-TESTE-RECEBER-{timestamp}",
            "data_vencimento": data_vencimento,
            "valor_documento": 2500.50,
            "codigo_categoria": "1.01.02",  # Categoria de receita
            "observacao": "Conta a receber criada via teste completo MCP - CNPJ válido",
            "numero_parcela": 1
        }
        
        self.print_info(f"Cliente: {codigo_cliente}")
        self.print_info(f"Documento: {dados_conta['numero_documento']}")
        self.print_info(f"Valor: R$ {dados_conta['valor_documento']:,.2f}")
        self.print_info(f"Vencimento: {data_vencimento}")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "criar_conta_receber",
                    "arguments": dados_conta
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("CONTA A RECEBER CRIADA COM SUCESSO!")
                    
                    # Verificar se contém informações esperadas
                    if "Código do Lançamento" in result_text:
                        self.print_highlight("Código do lançamento encontrado na resposta!")
                    if "R$" in result_text:
                        self.print_info("Valor monetário confirmado na resposta")
                    
                    # Mostrar trecho da resposta
                    lines = result_text.split('\n')[:8]
                    self.print_info("Resposta resumida:")
                    for line in lines:
                        if line.strip():
                            print(f"    {line}")
                    
                    return True
                else:
                    self.print_error("Erro na resposta da criação")
                    return False
            else:
                self.print_error(f"Erro na criação: {response.status_code}")
                if response.text:
                    self.print_info(f"Detalhes: {response.text[:200]}...")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao criar conta a receber: {e}")
            return False
    
    async def test_consultar_contas_pagar(self, codigo_cliente: int) -> bool:
        """Testa consulta de contas a pagar"""
        self.print_header("TESTE 8: Consultar Contas a Pagar")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "consultar_contas_pagar",
                    "arguments": {
                        "codigo_cliente_fornecedor": codigo_cliente,
                        "pagina": 1,
                        "registros_por_pagina": 10
                    }
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("Consulta de contas a pagar executada!")
                    
                    # Verificar estrutura da resposta
                    if "encontradas:" in result_text or "Nenhuma conta" in result_text:
                        self.print_info("Resposta tem estrutura esperada")
                    if f"Fornecedor: {codigo_cliente}" in result_text:
                        self.print_highlight("Filtro por fornecedor aplicado corretamente!")
                    
                    return True
                else:
                    self.print_error("Erro na resposta")
                    return False
            else:
                self.print_error(f"Erro na consulta: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao consultar contas a pagar: {e}")
            return False
    
    async def test_consultar_contas_receber(self, codigo_cliente: int) -> bool:
        """Testa consulta de contas a receber"""
        self.print_header("TESTE 9: Consultar Contas a Receber")
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "consultar_contas_receber",
                    "arguments": {
                        "codigo_cliente_fornecedor": codigo_cliente,
                        "pagina": 1,
                        "registros_por_pagina": 10
                    }
                }
            }
            
            response = await self.client.post(f"{self.base_url}/mcp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    result_text = data["result"]["content"][0]["text"]
                    self.print_success("Consulta de contas a receber executada!")
                    
                    # Verificar estrutura da resposta
                    if "encontradas:" in result_text or "Nenhuma conta" in result_text:
                        self.print_info("Resposta tem estrutura esperada")
                    if f"Cliente: {codigo_cliente}" in result_text:
                        self.print_highlight("Filtro por cliente aplicado corretamente!")
                    
                    return True
                else:
                    self.print_error("Erro na resposta")
                    return False
            else:
                self.print_error(f"Erro na consulta: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao consultar contas a receber: {e}")
            return False
    
    async def test_fluxo_automatizado(self) -> bool:
        """Testa o fluxo automatizado do servidor"""
        self.print_header("TESTE 10: Fluxo Automatizado do Servidor")
        
        try:
            response = await self.client.post(f"{self.base_url}/test/fluxo-completo")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "sucesso":
                    self.print_success("Fluxo automatizado executado com sucesso!")
                    
                    resultados = data.get("resultados", [])
                    for resultado in resultados:
                        self.print_info(resultado)
                    
                    return True
                else:
                    self.print_error(f"Fluxo falhou: {data.get('erro', 'Erro desconhecido')}")
                    return False
            else:
                self.print_error(f"Erro no fluxo: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro no fluxo automatizado: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes com foco nas ferramentas pendentes"""
        print("🚀 INICIANDO TESTES COMPLETOS - TODAS AS FERRAMENTAS MCP OMIE")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🎯 FOCO: Testar contas a pagar e receber com CNPJ válido")
        print("📋 CNPJ de teste: 24.493.607/0001-19")
        
        resultados = {}
        
        # Teste 1: Status do servidor
        resultados['servidor'] = await self.test_server_status()
        
        if not resultados['servidor']:
            self.print_error("❌ FALHA CRÍTICA: Servidor não está rodando!")
            return
        
        # Teste 2: Obter dados de teste
        test_data = await self.test_get_test_data()
        resultados['dados_teste'] = bool(test_data)
        
        # Teste 3: Listagem de ferramentas
        resultados['ferramentas_completas'] = await self.test_mcp_tools_list()
        
        # Teste 4: Tipos de documentos
        resultados['tipos_documento'] = await self.test_consultar_tipos_documento()
        
        # Teste 5: Cadastrar cliente com CNPJ válido
        codigo_cliente = None
        if resultados['dados_teste']:
            codigo_cliente = await self.test_cadastrar_cliente_com_cnpj_valido(test_data)
            resultados['cadastro_cnpj_valido'] = codigo_cliente is not None
        else:
            resultados['cadastro_cnpj_valido'] = False
            self.print_error("Pulando cadastro - sem dados de teste")
        
        # Testes das ferramentas PENDENTES (foco principal)
        if codigo_cliente:
            self.print_highlight(f"INICIANDO TESTES DAS FERRAMENTAS PENDENTES com cliente {codigo_cliente}")
            
            # Teste 6: Criar conta a pagar (PENDENTE)
            resultados['criar_conta_pagar'] = await self.test_criar_conta_pagar(codigo_cliente)
            
            # Teste 7: Criar conta a receber (PENDENTE)  
            resultados['criar_conta_receber'] = await self.test_criar_conta_receber(codigo_cliente)
            
            # Teste 8: Consultar contas a pagar
            resultados['consultar_contas_pagar'] = await self.test_consultar_contas_pagar(codigo_cliente)
            
            # Teste 9: Consultar contas a receber
            resultados['consultar_contas_receber'] = await self.test_consultar_contas_receber(codigo_cliente)
        else:
            self.print_error("❌ FALHA CRÍTICA: Sem cliente para testar as ferramentas pendentes!")
            resultados['criar_conta_pagar'] = False
            resultados['criar_conta_receber'] = False  
            resultados['consultar_contas_pagar'] = False
            resultados['consultar_contas_receber'] = False
        
        # Teste 10: Fluxo automatizado
        resultados['fluxo_automatizado'] = await self.test_fluxo_automatizado()
        
        # RESUMO FINAL COM FOCO NAS FERRAMENTAS PENDENTES
        self.print_header("RESUMO FINAL - TESTES COMPLETOS")
        
        total_testes = len(resultados)
        testes_ok = sum(1 for resultado in resultados.values() if resultado)
        
        # Resultados gerais
        for nome, resultado in resultados.items():
            status = "✅ PASSOU" if resultado else "❌ FALHOU"
            display_name = nome.replace('_', ' ').title()
            print(f"{display_name}: {status}")
        
        print(f"\n📊 RESULTADO GERAL: {testes_ok}/{total_testes} testes passaram")
        
        # Foco nas ferramentas pendentes
        self.print_highlight("RESULTADO DAS FERRAMENTAS PENDENTES:")
        ferramentas_pendentes = {
            'criar_conta_pagar': 'Criar Conta a Pagar',
            'criar_conta_receber': 'Criar Conta a Receber',
            'consultar_contas_pagar': 'Consultar Contas a Pagar', 
            'consultar_contas_receber': 'Consultar Contas a Receber'
        }
        
        pendentes_ok = 0
        for key, name in ferramentas_pendentes.items():
            if key in resultados:
                status = "✅ FUNCIONANDO" if resultados[key] else "❌ FALHANDO"
                print(f"    {name}: {status}")
                if resultados[key]:
                    pendentes_ok += 1
        
        print(f"\n🎯 FERRAMENTAS PENDENTES: {pendentes_ok}/{len(ferramentas_pendentes)} funcionando")
        
        # Conclusão
        if pendentes_ok == len(ferramentas_pendentes):
            self.print_success("🎉 SUCESSO TOTAL! Todas as ferramentas pendentes estão funcionando!")
            self.print_highlight("✅ CNPJ válido funcionou corretamente")
            self.print_highlight("✅ Contas a pagar e receber criadas com sucesso")
            self.print_info("🔧 Pronto para configurar no Claude Desktop!")
        elif pendentes_ok >= len(ferramentas_pendentes) - 1:
            self.print_warning("⚠️  Quase todas as ferramentas pendentes funcionaram")
            self.print_info("Verifique os detalhes dos erros acima")
        else:
            self.print_error("❌ Muitas ferramentas pendentes falharam")
            self.print_info("💡 Dicas:")
            self.print_info("1. Verifique se as credenciais do Omie estão corretas")
            self.print_info("2. Confirme se o CNPJ 24.493.607/0001-19 é aceito pela API")
            self.print_info("3. Verifique os logs do servidor para detalhes")
        
        # Informações para usar no Claude Desktop
        if self.codigo_cliente_criado:
            self.print_highlight(f"CÓDIGO DO CLIENTE PARA TESTES: {self.codigo_cliente_criado}")
            self.print_info("Use este código para testar no Claude Desktop!")


async def main():
    """Função principal"""
    print("🔧 TESTE COMPLETO MCP OMIE - TODAS AS FERRAMENTAS")
    print("🎯 Foco especial: Ferramentas pendentes com CNPJ válido")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("""
Uso: python test_complete_omie_mcp.py [opções]

Opções:
  --help          Mostra esta ajuda
  --url URL       URL base do servidor (padrão: http://localhost:8000)

Este teste foca especificamente nas ferramentas que estavam pendentes:
- ✅ criar_conta_pagar (com CNPJ válido)
- ✅ criar_conta_receber (com CNPJ válido)
- ✅ consultar_contas_pagar  
- ✅ consultar_contas_receber

CNPJ usado: 24.493.607/0001-19 (fornecido pelo usuário)

Exemplos:
  python test_complete_omie_mcp.py
  python test_complete_omie_mcp.py --url http://localhost:8000
            """)
            return
        elif sys.argv[1] == "--url" and len(sys.argv) > 2:
            base_url = sys.argv[2]
        else:
            base_url = "http://localhost:8000"
    else:
        base_url = "http://localhost:8000"
    
    print(f"🌐 Testando servidor completo em: {base_url}")
    
    try:
        async with OmieMCPCompleteRester(base_url) as tester:
            await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro crítico durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Verificar dependência
    try:
        import httpx
    except ImportError:
        print("❌ ERRO: httpx não está instalado")
        print("📦 Instale com: pip install httpx")
        sys.exit(1)
    
    # Executar testes
    asyncio.run(main())