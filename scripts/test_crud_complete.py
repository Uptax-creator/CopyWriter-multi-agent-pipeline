#!/usr/bin/env python3
"""
🧪 Teste CRUD Completo - Cliente e Fornecedor
Testa criação, alteração, consulta e exclusão
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
import aiohttp

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

class CrudTester:
    """Testador CRUD completo"""
    
    def __init__(self):
        self.server_url = "http://localhost:3000"
        self.cliente_codigo = None
        self.fornecedor_codigo = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Chama uma ferramenta do servidor"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "name": tool_name,
                    "arguments": arguments
                }
                
                async with session.post(
                    f"{self.server_url}/mcp/tools/{tool_name}",
                    json=arguments,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": result,
                            "status": response.status
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status": response.status
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 0
            }
    
    async def test_criar_cliente(self):
        """Teste 1: Criar cliente de teste"""
        self.log("🧪 Teste 1: Criando cliente de teste...")
        
        cliente_data = {
            "razao_social": "EMPRESA TESTE CLIENTE LTDA",
            "cnpj_cpf": "11222333000181",  # CNPJ válido de teste
            "email": "cliente.teste@exemplo.com.br",
            "telefone": "11999991234"
        }
        
        result = await self.call_tool("incluir_cliente", cliente_data)
        
        if result["success"]:
            self.log("✅ Cliente criado com sucesso!")
            
            # Extrair código do cliente da resposta
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            if "Código Omie:" in response_text:
                # Tentar extrair o código
                lines = response_text.split("\n")
                for line in lines:
                    if "Código Omie:" in line:
                        try:
                            self.cliente_codigo = int(line.split(":")[-1].strip())
                            self.log(f"📋 Cliente código: {self.cliente_codigo}")
                            break
                        except:
                            pass
            
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao criar cliente: {result['error']}", "ERROR")
            return False
    
    async def test_criar_fornecedor(self):
        """Teste 2: Criar fornecedor de teste"""
        self.log("🧪 Teste 2: Criando fornecedor de teste...")
        
        fornecedor_data = {
            "razao_social": "FORNECEDOR TESTE LTDA",
            "cnpj_cpf": "22333444000195",  # CNPJ válido de teste
            "email": "fornecedor.teste@exemplo.com.br",
            "telefone": "11888885678"
        }
        
        result = await self.call_tool("incluir_fornecedor", fornecedor_data)
        
        if result["success"]:
            self.log("✅ Fornecedor criado com sucesso!")
            
            # Extrair código do fornecedor da resposta
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            if "Código Omie:" in response_text:
                # Tentar extrair o código
                lines = response_text.split("\n")
                for line in lines:
                    if "Código Omie:" in line:
                        try:
                            self.fornecedor_codigo = int(line.split(":")[-1].strip())
                            self.log(f"📋 Fornecedor código: {self.fornecedor_codigo}")
                            break
                        except:
                            pass
            
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao criar fornecedor: {result['error']}", "ERROR")
            return False
    
    async def test_consultar_cliente_por_codigo(self):
        """Teste 3: Consultar cliente por código"""
        if not self.cliente_codigo:
            self.log("⏭️ Pulando teste - cliente não foi criado", "WARN")
            return False
        
        self.log("🧪 Teste 3: Consultando cliente por código...")
        
        result = await self.call_tool("consultar_cliente_por_codigo", {
            "codigo_cliente_omie": self.cliente_codigo
        })
        
        if result["success"]:
            self.log("✅ Cliente consultado com sucesso!")
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao consultar cliente: {result['error']}", "ERROR")
            return False
    
    async def test_consultar_fornecedor_por_codigo(self):
        """Teste 4: Consultar fornecedor por código"""
        if not self.fornecedor_codigo:
            self.log("⏭️ Pulando teste - fornecedor não foi criado", "WARN")
            return False
        
        self.log("🧪 Teste 4: Consultando fornecedor por código...")
        
        result = await self.call_tool("consultar_fornecedor_por_codigo", {
            "codigo_cliente_omie": self.fornecedor_codigo
        })
        
        if result["success"]:
            self.log("✅ Fornecedor consultado com sucesso!")
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao consultar fornecedor: {result['error']}", "ERROR")
            return False
    
    async def test_buscar_dados_contato_cliente(self):
        """Teste 5: Buscar dados de contato do cliente"""
        if not self.cliente_codigo:
            self.log("⏭️ Pulando teste - cliente não foi criado", "WARN")
            return False
        
        self.log("🧪 Teste 5: Buscando dados de contato do cliente...")
        
        result = await self.call_tool("buscar_dados_contato_cliente", {
            "codigo_cliente_omie": self.cliente_codigo
        })
        
        if result["success"]:
            self.log("✅ Dados de contato consultados com sucesso!")
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao buscar dados de contato: {result['error']}", "ERROR")
            return False
    
    async def test_alterar_cliente(self):
        """Teste 6: Alterar cliente"""
        if not self.cliente_codigo:
            self.log("⏭️ Pulando teste - cliente não foi criado", "WARN")
            return False
        
        self.log("🧪 Teste 6: Alterando cliente...")
        
        alteracao_data = {
            "codigo_cliente_omie": self.cliente_codigo,
            "razao_social": "EMPRESA TESTE CLIENTE ALTERADA LTDA",
            "email": "cliente.alterado@exemplo.com.br",
            "telefone": "(11) 99999-9999"
        }
        
        result = await self.call_tool("alterar_cliente", alteracao_data)
        
        if result["success"]:
            self.log("✅ Cliente alterado com sucesso!")
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao alterar cliente: {result['error']}", "ERROR")
            return False
    
    async def test_alterar_fornecedor(self):
        """Teste 7: Alterar fornecedor"""
        if not self.fornecedor_codigo:
            self.log("⏭️ Pulando teste - fornecedor não foi criado", "WARN")
            return False
        
        self.log("🧪 Teste 7: Alterando fornecedor...")
        
        alteracao_data = {
            "codigo_cliente_omie": self.fornecedor_codigo,
            "razao_social": "FORNECEDOR TESTE ALTERADO LTDA",
            "email": "fornecedor.alterado@exemplo.com.br",
            "telefone": "(11) 88888-8888"
        }
        
        result = await self.call_tool("alterar_fornecedor", alteracao_data)
        
        if result["success"]:
            self.log("✅ Fornecedor alterado com sucesso!")
            response_text = result["data"].get("content", [{}])[0].get("text", "")
            print(f"📄 Resposta: {response_text}")
            return True
        else:
            self.log(f"❌ Erro ao alterar fornecedor: {result['error']}", "ERROR")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        self.log("🚀 Iniciando testes CRUD completos")
        
        tests = [
            ("Criar Cliente", self.test_criar_cliente),
            ("Criar Fornecedor", self.test_criar_fornecedor),
            ("Consultar Cliente por Código", self.test_consultar_cliente_por_codigo),
            ("Consultar Fornecedor por Código", self.test_consultar_fornecedor_por_codigo),
            ("Buscar Dados Contato Cliente", self.test_buscar_dados_contato_cliente),
            ("Alterar Cliente", self.test_alterar_cliente),
            ("Alterar Fornecedor", self.test_alterar_fornecedor),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            try:
                success = await test_func()
                results.append((test_name, success))
            except Exception as e:
                self.log(f"❌ Erro inesperado em {test_name}: {e}", "ERROR")
                results.append((test_name, False))
            
            # Pequeno delay entre testes
            await asyncio.sleep(1)
        
        # Resumo final
        print(f"\n{'='*60}")
        print("📊 RESUMO DOS TESTES CRUD")
        print('='*60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{test_name.ljust(35)} {status}")
            if success:
                passed += 1
        
        print('='*60)
        print(f"📈 Taxa de sucesso: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if self.cliente_codigo:
            print(f"👤 Cliente de teste criado: Código {self.cliente_codigo}")
        if self.fornecedor_codigo:
            print(f"🏢 Fornecedor de teste criado: Código {self.fornecedor_codigo}")
        
        print("\n💡 Dica: Use estes códigos para testes futuros!")
        
        return passed == total

async def main():
    """Função principal"""
    tester = CrudTester()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))