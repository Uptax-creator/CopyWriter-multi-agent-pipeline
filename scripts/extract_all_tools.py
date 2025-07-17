#!/usr/bin/env python3
"""
Script para extrair todas as ferramentas disponíveis nos servidores MCP
"""

import sys
import os
import json
import importlib.util
import inspect
from typing import Dict, List, Any
from pathlib import Path

def extract_omie_tools() -> List[Dict[str, Any]]:
    """Extrai todas as ferramentas do Omie MCP"""
    tools = []
    
    # Adicionar path do projeto
    project_root = "/Users/kleberdossantosribeiro/omie-mcp"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # Importar todas as ferramentas do arquivo servidor
        from src.tools.consultas import (
            ConsultarCategoriasTool,
            ConsultarDepartamentosTool, 
            ConsultarTiposDocumentoTool,
            ConsultarContasPagarTool,
            ConsultarContasReceberTool,
            ConsultarClientesTool,
            ConsultarFornecedoresTool,
            ConsultarClientePorCodigoTool,
            ConsultarFornecedorPorCodigoTool,
            BuscarDadosContatoClienteTool
        )
        from src.tools.cliente_tool import (
            IncluirClienteTool,
            IncluirFornecedorTool,
            AlterarClienteTool,
            AlterarFornecedorTool
        )
        from src.tools.contas_pagar import (
            IncluirContaPagarTool,
            AlterarContaPagarTool,
            ExcluirContaPagarTool
        )
        from src.tools.contas_receber import (
            IncluirContaReceberTool,
            AlterarContaReceberTool,
            ExcluirContaReceberTool
        )
        
        # Lista de todas as classes de ferramentas
        tool_classes = [
            # Consultas
            ConsultarCategoriasTool,
            ConsultarDepartamentosTool,
            ConsultarTiposDocumentoTool,
            ConsultarContasPagarTool,
            ConsultarContasReceberTool,
            ConsultarClientesTool,
            ConsultarFornecedoresTool,
            ConsultarClientePorCodigoTool,
            ConsultarFornecedorPorCodigoTool,
            BuscarDadosContatoClienteTool,
            
            # Cliente/Fornecedor
            IncluirClienteTool,
            IncluirFornecedorTool,
            AlterarClienteTool,
            AlterarFornecedorTool,
            
            # Contas a Pagar
            IncluirContaPagarTool,
            AlterarContaPagarTool,
            ExcluirContaPagarTool,
            
            # Contas a Receber
            IncluirContaReceberTool,
            AlterarContaReceberTool,
            ExcluirContaReceberTool
        ]
        
        for tool_class in tool_classes:
            try:
                tool_instance = tool_class()
                tool_definition = tool_instance.get_tool_definition()
                
                # Adicionar informações de teste baseadas no tipo
                test_args = generate_test_args_omie(tool_definition["name"])
                
                tools.append({
                    "name": tool_definition["name"],
                    "description": tool_definition["description"],
                    "input_schema": tool_definition.get("inputSchema", {}),
                    "test_args": test_args,
                    "class_name": tool_class.__name__
                })
                
            except Exception as e:
                print(f"Erro ao processar {tool_class.__name__}: {e}")
    
    except Exception as e:
        print(f"Erro ao importar ferramentas do Omie: {e}")
    
    return tools

def extract_nibo_tools() -> List[Dict[str, Any]]:
    """Extrai todas as ferramentas do Nibo MCP"""
    tools = []
    
    # Adicionar path do nibo-mcp
    nibo_path = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp"
    if nibo_path not in sys.path:
        sys.path.insert(0, nibo_path)
    
    try:
        # Importar ferramentas do Nibo
        from src.tools.consultas import (
            ConsultarCategoriasNiboTool,
            ConsultarCentrosCustoNiboTool,
            ConsultarClientesNiboTool,
            ConsultarFornecedoresNiboTool
        )
        from src.tools.socios import (
            ConsultarSociosNiboTool,
            IncluirSocioNiboTool
        )
        from src.tools.financeiro import (
            ConsultarContasPagarNiboTool,
            ConsultarContasReceberNiboTool
        )
        from src.tools.clientes_fornecedores import (
            IncluirMultiplosClientesNiboTool
        )
        
        # Lista de classes de ferramentas do Nibo
        tool_classes = [
            # Consultas
            ConsultarCategoriasNiboTool,
            ConsultarCentrosCustoNiboTool,
            ConsultarClientesNiboTool,
            ConsultarFornecedoresNiboTool,
            
            # Sócios
            ConsultarSociosNiboTool,
            IncluirSocioNiboTool,
            
            # Financeiro
            ConsultarContasPagarNiboTool,
            ConsultarContasReceberNiboTool,
            
            # Clientes/Fornecedores
            IncluirMultiplosClientesNiboTool
        ]
        
        for tool_class in tool_classes:
            try:
                tool_instance = tool_class()
                tool_definition = tool_instance.get_tool_definition()
                
                # Adicionar informações de teste baseadas no tipo
                test_args = generate_test_args_nibo(tool_definition["name"])
                
                tools.append({
                    "name": tool_definition["name"],
                    "description": tool_definition["description"],
                    "input_schema": tool_definition.get("inputSchema", {}),
                    "test_args": test_args,
                    "class_name": tool_class.__name__
                })
                
            except Exception as e:
                print(f"Erro ao processar {tool_class.__name__}: {e}")
    
    except Exception as e:
        print(f"Erro ao importar ferramentas do Nibo: {e}")
    
    return tools

def generate_test_args_omie(tool_name: str) -> Dict[str, Any]:
    """Gera argumentos de teste para ferramentas do Omie"""
    
    # Argumentos específicos por ferramenta
    specific_args = {
        "testar_conexao": {},
        "consultar_categorias": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_departamentos": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_tipos_documento": {},
        "consultar_contas_pagar": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_contas_receber": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_clientes": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_fornecedores": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_cliente_por_codigo": {"codigo": "12345"},
        "consultar_fornecedor_por_codigo": {"codigo": "12345"},
        "buscar_dados_contato_cliente": {"codigo": "12345"},
        
        "incluir_cliente": {
            "razao_social": "Teste Cliente MCP",
            "nome_fantasia": "Teste MCP",
            "cnpj_cpf": "12345678000195",
            "telefone1_ddd": "11",
            "telefone1_numero": "999999999",
            "email": "teste@mcp.com"
        },
        "incluir_fornecedor": {
            "razao_social": "Teste Fornecedor MCP",
            "nome_fantasia": "Teste Fornecedor MCP",
            "cnpj_cpf": "98765432000111",
            "telefone1_ddd": "11",
            "telefone1_numero": "888888888",
            "email": "fornecedor@mcp.com"
        },
        "alterar_cliente": {
            "codigo": "12345",
            "razao_social": "Cliente Alterado MCP"
        },
        "alterar_fornecedor": {
            "codigo": "12345", 
            "razao_social": "Fornecedor Alterado MCP"
        },
        
        "incluir_conta_pagar": {
            "codigo_cliente_fornecedor": "12345",
            "valor_documento": 100.00,
            "data_vencimento": "31/12/2024",
            "observacao": "Teste MCP conta pagar"
        },
        "alterar_conta_pagar": {
            "codigo": "12345",
            "valor_documento": 150.00
        },
        "excluir_conta_pagar": {
            "codigo": "12345"
        },
        
        "incluir_conta_receber": {
            "codigo_cliente": "12345",
            "valor_documento": 200.00,
            "data_vencimento": "31/12/2024",
            "observacao": "Teste MCP conta receber"
        },
        "alterar_conta_receber": {
            "codigo": "12345",
            "valor_documento": 250.00
        },
        "excluir_conta_receber": {
            "codigo": "12345"
        }
    }
    
    return specific_args.get(tool_name, {})

def generate_test_args_nibo(tool_name: str) -> Dict[str, Any]:
    """Gera argumentos de teste para ferramentas do Nibo"""
    
    specific_args = {
        "testar_conexao": {},
        "consultar_categorias": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_centros_custo": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_clientes": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_fornecedores": {"pagina": 1, "registros_por_pagina": 10},
        
        "consultar_socios": {},
        "incluir_socio": {
            "nome": "Teste Sócio MCP",
            "cpf": "12345678900",
            "percentual_participacao": 100.0
        },
        
        "consultar_contas_pagar": {"pagina": 1, "registros_por_pagina": 10},
        "consultar_contas_receber": {"pagina": 1, "registros_por_pagina": 10},
        
        "incluir_multiplos_clientes": {
            "clientes": [
                {
                    "nome": "Cliente Teste MCP 1",
                    "documento": "12345678000195", 
                    "email": "cliente1@mcp.com"
                }
            ]
        }
    }
    
    return specific_args.get(tool_name, {})

def discover_tools_from_files() -> Dict[str, List[str]]:
    """Descobre ferramentas analisando arquivos diretamente"""
    
    result = {"omie": [], "nibo": []}
    
    # Buscar no servidor híbrido do Omie
    omie_hybrid_path = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    if os.path.exists(omie_hybrid_path):
        with open(omie_hybrid_path, 'r') as f:
            content = f.read()
            # Buscar definições de nome de ferramenta
            import re
            names = re.findall(r'"name":\s*"([^"]+)"', content)
            result["omie"].extend(names)
    
    # Buscar no servidor híbrido do Nibo  
    nibo_hybrid_path = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py"
    if os.path.exists(nibo_hybrid_path):
        with open(nibo_hybrid_path, 'r') as f:
            content = f.read()
            import re
            names = re.findall(r'"name":\s*"([^"]+)"', content)
            result["nibo"].extend(names)
    
    return result

def main():
    print("🔍 EXTRAÇÃO DE FERRAMENTAS MCP")
    print("=" * 40)
    
    # Tentar extrair via importação
    print("\n📋 Extraindo ferramentas do Omie MCP...")
    omie_tools = extract_omie_tools()
    print(f"  Encontradas: {len(omie_tools)} ferramentas")
    
    print("\n📋 Extraindo ferramentas do Nibo MCP...")
    nibo_tools = extract_nibo_tools()
    print(f"  Encontradas: {len(nibo_tools)} ferramentas")
    
    # Se não encontrou muitas, tentar descoberta por arquivos
    if len(omie_tools) < 15 or len(nibo_tools) < 20:
        print("\n🔍 Descobrindo ferramentas por análise de arquivos...")
        discovered = discover_tools_from_files()
        print(f"  Omie descobertos: {len(discovered['omie'])} nomes")
        print(f"  Nibo descobertos: {len(discovered['nibo'])} nomes")
        
        if discovered["omie"]:
            print(f"  Omie: {', '.join(discovered['omie'])}")
        if discovered["nibo"]:
            print(f"  Nibo: {', '.join(discovered['nibo'])}")
    
    # Resultados finais
    print(f"\n📊 RESUMO FINAL:")
    print(f"  Omie MCP: {len(omie_tools)} ferramentas extraídas")
    for tool in omie_tools:
        print(f"    • {tool['name']}")
    
    print(f"\n  Nibo MCP: {len(nibo_tools)} ferramentas extraídas")
    for tool in nibo_tools:
        print(f"    • {tool['name']}")
    
    # Salvar resultado
    result = {
        "omie_tools": omie_tools,
        "nibo_tools": nibo_tools,
        "total_omie": len(omie_tools),
        "total_nibo": len(nibo_tools)
    }
    
    output_file = "/Users/kleberdossantosribeiro/omie-mcp/extracted_tools.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado salvo em: {output_file}")
    
    return result

if __name__ == "__main__":
    main()