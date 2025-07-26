#!/usr/bin/env python3
"""
Teste para identificar problemas nos schemas MCP
"""

import json
import subprocess
import sys

def test_schema_validation():
    """Testa validação de schemas"""
    
    # Schema problemático possível
    problematic_schema = {
        "name": "consultar_contas_pagar",
        "description": "Consulta contas a pagar do Omie ERP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                "pagina": {"type": "integer", "description": "Página", "default": 1},
                "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
            }
        }
    }
    
    # Schema simples
    simple_schema = {
        "name": "testar_conexao",
        "description": "Testa conexão",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    print("Schema problemático:")
    print(json.dumps(problematic_schema, indent=2, ensure_ascii=False))
    print("\nSchema simples:")
    print(json.dumps(simple_schema, indent=2, ensure_ascii=False))
    
    # Testar se JSON é válido
    try:
        json.dumps(problematic_schema)
        print("✅ Schema problemático é JSON válido")
    except Exception as e:
        print(f"❌ Schema problemático tem erro JSON: {e}")
    
    try:
        json.dumps(simple_schema)
        print("✅ Schema simples é JSON válido")
    except Exception as e:
        print(f"❌ Schema simples tem erro JSON: {e}")

def test_mcp_response_format():
    """Testa formato de resposta MCP"""
    
    # Resposta tools/list que pode estar causando problema
    tools_response = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "tools": [
                {
                    "name": "testar_conexao",
                    "description": "Testa conexão com a API do Omie ERP",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    }
    
    print("\nTeste de formato de resposta MCP:")
    try:
        response_json = json.dumps(tools_response, ensure_ascii=False)
        print("✅ Resposta MCP é JSON válida")
        print(f"Tamanho: {len(response_json)} caracteres")
        
        # Verificar se há caracteres problemáticos
        if '"' in response_json and "'" not in response_json:
            print("✅ Aspas estão OK")
        else:
            print("⚠️ Possível problema com aspas")
            
    except Exception as e:
        print(f"❌ Erro na resposta MCP: {e}")

if __name__ == "__main__":
    test_schema_validation()
    test_mcp_response_format()