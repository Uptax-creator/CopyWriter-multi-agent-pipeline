#!/usr/bin/env python3
"""
Script para validação completa do sistema
"""

import asyncio
import sys
import json
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.config import config
from src.server import tool_registry
from src.client.omie_client import omie_client

async def validate_config():
    """Validar configuração"""
    print("🔧 Validando configuração...")
    
    try:
        config_dict = config.to_dict()
        
        if config_dict["has_credentials"]:
            print("✅ Credenciais configuradas")
        else:
            print("❌ Credenciais não configuradas")
            return False
        
        print(f"✅ Servidor: {config_dict['server_host']}:{config_dict['server_port']}")
        print(f"✅ Debug: {config_dict['debug']}")
        print(f"✅ Log level: {config_dict['log_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

async def validate_tools():
    """Validar ferramentas"""
    print(f"\\n🛠️ Validando {len(tool_registry.tools)} ferramentas...")
    
    errors = []
    
    for tool_name, tool in tool_registry.tools.items():
        try:
            # Verificar definição da ferramenta
            definition = tool.get_tool_definition()
            
            if not definition.get("name"):
                errors.append(f"{tool_name}: Nome ausente")
            
            if not definition.get("description"):
                errors.append(f"{tool_name}: Descrição ausente")
            
            if not definition.get("inputSchema"):
                errors.append(f"{tool_name}: Schema de entrada ausente")
            
            print(f"✅ {tool_name}: OK")
            
        except Exception as e:
            errors.append(f"{tool_name}: {str(e)}")
            print(f"❌ {tool_name}: {str(e)}")
    
    if errors:
        print(f"\\n❌ Encontrados {len(errors)} erros nas ferramentas:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\\n✅ Todas as {len(tool_registry.tools)} ferramentas são válidas")
        return True

async def validate_omie_connection():
    """Validar conexão com Omie"""
    print("\\n🌐 Validando conexão com Omie...")
    
    try:
        # Testar consulta simples
        result = await omie_client.consultar_categorias({
            "pagina": 1,
            "registros_por_pagina": 1
        })
        
        if "categoria_cadastro" in result:
            print("✅ Conexão com Omie OK")
            return True
        else:
            print("❌ Resposta inesperada da API Omie")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão com Omie: {e}")
        return False

async def validate_sample_tools():
    """Validar ferramentas com dados de exemplo"""
    print("\\n🧪 Testando ferramentas com dados de exemplo...")
    
    test_cases = [
        ("consultar_categorias", {"pagina": 1, "registros_por_pagina": 3}),
        ("consultar_departamentos", {"pagina": 1, "registros_por_pagina": 3}),
        ("consultar_tipos_documento", {}),
    ]
    
    errors = []
    
    for tool_name, arguments in test_cases:
        try:
            tool = tool_registry.get_tool(tool_name)
            if not tool:
                errors.append(f"{tool_name}: Ferramenta não encontrada")
                continue
            
            result = await tool.safe_execute(arguments)
            
            if result.startswith("❌"):
                errors.append(f"{tool_name}: {result}")
                print(f"❌ {tool_name}: Erro no resultado")
            else:
                print(f"✅ {tool_name}: OK")
                
        except Exception as e:
            errors.append(f"{tool_name}: {str(e)}")
            print(f"❌ {tool_name}: {str(e)}")
    
    if errors:
        print(f"\\n❌ Encontrados {len(errors)} erros nos testes:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\\n✅ Todos os testes passaram")
        return True

async def main():
    """Função principal"""
    print("🚀 Iniciando validação completa do Omie MCP Server v2.0.0\\n")
    
    results = []
    
    # Validar configuração
    results.append(await validate_config())
    
    # Validar ferramentas
    results.append(await validate_tools())
    
    # Validar conexão com Omie
    results.append(await validate_omie_connection())
    
    # Testar ferramentas
    results.append(await validate_sample_tools())
    
    # Resultado final
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\\n📊 RESULTADO FINAL:")
    print(f"✅ Passou: {success_count}/{total_count} validações")
    
    if all(results):
        print("\\n🎉 SISTEMA TOTALMENTE VALIDADO!")
        print("✅ Todas as validações passaram")
        print("✅ Sistema pronto para uso")
        return True
    else:
        print(f"\\n❌ VALIDAÇÃO FALHOU!")
        print(f"❌ {total_count - success_count} validações falharam")
        print("❌ Corrija os erros antes de usar o sistema")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n🛑 Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Erro inesperado: {e}")
        sys.exit(1)