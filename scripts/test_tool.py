#!/usr/bin/env python3
"""
Script para testar ferramentas individuais
"""

import asyncio
import sys
import json
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.server import tool_registry

async def test_tool(tool_name: str, arguments: dict = None):
    """Testar uma ferramenta específica"""
    if arguments is None:
        arguments = {}
    
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        print(f"❌ Ferramenta '{tool_name}' não encontrada")
        print(f"Ferramentas disponíveis: {list(tool_registry.tools.keys())}")
        return False
    
    try:
        print(f"🧪 Testando ferramenta: {tool_name}")
        print(f"📋 Argumentos: {json.dumps(arguments, indent=2)}")
        
        result = await tool.safe_execute(arguments)
        
        print(f"✅ Resultado:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python scripts/test_tool.py <nome_da_ferramenta> [argumentos_json]")
        print("\\nExemplos:")
        print("  python scripts/test_tool.py consultar_categorias")
        print("  python scripts/test_tool.py consultar_categorias '{"pagina": 1}'")
        print("  python scripts/test_tool.py consultar_departamentos '{"registros_por_pagina": 10}'")
        print("\\nFerramentas disponíveis:")
        for tool_name in tool_registry.tools.keys():
            print(f"  - {tool_name}")
        return False
    
    tool_name = sys.argv[1]
    arguments = {}
    
    if len(sys.argv) > 2:
        try:
            arguments = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear argumentos JSON: {e}")
            return False
    
    success = await test_tool(tool_name, arguments)
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Erro inesperado: {e}")
        sys.exit(1)