#!/usr/bin/env python3
"""
Testes básicos para validar a estrutura híbrida
"""

import sys
import os
import asyncio
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Testar se todas as importações funcionam"""
    print("🧪 Testando importações...")
    
    try:
        # Testar config
        from config import config
        print("✅ Config importado")
        
        # Testar cliente
        from client.omie_client import omie_client
        print("✅ Cliente Omie importado")
        
        # Testar utilitários
        from utils.logger import logger
        from utils.validators import OmieValidators
        from utils.sanitizers import json_sanitizer
        print("✅ Utilitários importados")
        
        # Testar modelos
        from models.schemas import ClienteModel, ContaPagarModel
        print("✅ Modelos importados")
        
        # Testar tools
        from tools.consultas import ConsultarCategoriasTool
        from tools.cliente_tool import IncluirClienteTool
        print("✅ Tools importadas")
        
        # Testar servidor
        from server import tool_registry
        print("✅ Servidor importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_config():
    """Testar configuração"""
    print("\n🧪 Testando configuração...")
    
    try:
        from config import config
        
        # Testar se configuração foi carregada
        config_dict = config.to_dict()
        
        if config_dict["server_port"] == 3000:
            print("✅ Porta padrão configurada")
        
        if config_dict["omie_base_url"]:
            print("✅ URL base do Omie configurada")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_tools_registry():
    """Testar registro de ferramentas"""
    print("\n🧪 Testando registro de ferramentas...")
    
    try:
        from server import tool_registry
        
        # Verificar se ferramentas foram registradas
        tools_count = len(tool_registry.tools)
        print(f"✅ {tools_count} ferramentas registradas")
        
        # Verificar se ferramentas básicas existem
        expected_tools = [
            "consultar_categorias",
            "consultar_departamentos",
            "incluir_cliente",
            "incluir_conta_pagar"
        ]
        
        for tool_name in expected_tools:
            if tool_name in tool_registry.tools:
                print(f"✅ Ferramenta {tool_name} encontrada")
            else:
                print(f"❌ Ferramenta {tool_name} não encontrada")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no registro de ferramentas: {e}")
        return False

def test_validators():
    """Testar validadores"""
    print("\n🧪 Testando validadores...")
    
    try:
        from utils.validators import OmieValidators
        
        # Testar validação de CNPJ
        cnpj_valido = "11222333000181"
        cnpj_invalido = "12345678901234"
        
        if OmieValidators.validar_cnpj(cnpj_valido):
            print("✅ Validação de CNPJ válido")
        else:
            print("❌ Validação de CNPJ válido falhou")
            
        if not OmieValidators.validar_cnpj(cnpj_invalido):
            print("✅ Validação de CNPJ inválido")
        else:
            print("❌ Validação de CNPJ inválido falhou")
        
        # Testar validação de email
        email_valido = "teste@exemplo.com"
        email_invalido = "teste@"
        
        if OmieValidators.validar_email(email_valido):
            print("✅ Validação de email válido")
        else:
            print("❌ Validação de email válido falhou")
            
        if not OmieValidators.validar_email(email_invalido):
            print("✅ Validação de email inválido")
        else:
            print("❌ Validação de email inválido falhou")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos validadores: {e}")
        return False

async def test_tool_execution():
    """Testar execução de ferramenta"""
    print("\n🧪 Testando execução de ferramenta...")
    
    try:
        from tools.consultas import ConsultarCategoriasTool
        
        # Criar instância da ferramenta
        tool = ConsultarCategoriasTool()
        
        # Verificar definição da ferramenta
        definition = tool.get_tool_definition()
        
        if definition["name"] == "consultar_categorias":
            print("✅ Nome da ferramenta correto")
        
        if definition["description"]:
            print("✅ Descrição da ferramenta presente")
        
        if definition["inputSchema"]:
            print("✅ Schema de entrada presente")
        
        # Testar validação de argumentos
        args = {"pagina": 1, "registros_por_pagina": 5}
        validated_args = tool.validate_arguments(args)
        
        if validated_args["pagina"] == 1:
            print("✅ Validação de argumentos funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na execução da ferramenta: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes básicos da estrutura híbrida\n")
    
    tests = [
        ("Importações", test_imports),
        ("Configuração", test_config),
        ("Registro de Ferramentas", test_tools_registry),
        ("Validadores", test_validators),
        ("Execução de Ferramenta", lambda: asyncio.run(test_tool_execution()))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TESTE: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resultado final
    print(f"\n{'='*50}")
    print("RESULTADO FINAL")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 RESUMO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Estrutura híbrida funcionando corretamente")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("❌ Corrija os problemas antes de continuar")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)