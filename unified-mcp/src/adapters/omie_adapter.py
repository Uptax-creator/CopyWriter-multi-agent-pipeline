"""
Adaptador para Omie MCP - Converte chamadas universais para formato Omie
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("omie-adapter")

class OmieAdapter:
    """Adaptador para comunicação com Omie MCP Server"""
    
    def __init__(self, omie_client=None):
        self.omie_client = omie_client
        self.platform_name = "omie"
        
    def map_universal_to_omie(self, tool_name: str, universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia parâmetros universais para formato Omie"""
        
        # Mapeamentos específicos do Omie
        field_mappings = {
            "page": "pagina",
            "limit": "registros_por_pagina",
            "start_date": "data_inicio",
            "end_date": "data_fim",
            "name": "razao_social",
            "document": "cnpj_cpf",
            "entity_id": "codigo_cliente",
            "supplier_id": "codigo_fornecedor",
            "document_number": "numero_documento",
            "due_date": "data_vencimento",
            "amount": "valor_documento",
            "category": "codigo_categoria"
        }
        
        omie_params = {}
        for universal_key, value in universal_params.items():
            omie_key = field_mappings.get(universal_key, universal_key)
            omie_params[omie_key] = value
            
        return omie_params
    
    def map_omie_to_universal(self, tool_name: str, omie_result: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia resultado do Omie para formato universal"""
        
        if not isinstance(omie_result, dict):
            return {"data": omie_result, "platform": "omie"}
            
        # Mapeamentos de resposta específicos
        if "clientes_cadastro" in omie_result:
            return {
                "entities": omie_result["clientes_cadastro"],
                "total_pages": omie_result.get("total_de_paginas", 1),
                "current_page": omie_result.get("pagina", 1),
                "platform": "omie",
                "entity_type": "cliente"
            }
        
        if "fornecedores_cadastro" in omie_result:
            return {
                "entities": omie_result["fornecedores_cadastro"],
                "total_pages": omie_result.get("total_de_paginas", 1),
                "current_page": omie_result.get("pagina", 1),
                "platform": "omie",
                "entity_type": "fornecedor"
            }
            
        if "categorias" in omie_result:
            return {
                "entities": omie_result["categorias"],
                "total_pages": omie_result.get("total_de_paginas", 1),
                "current_page": omie_result.get("pagina", 1),
                "platform": "omie",
                "entity_type": "categoria"
            }
            
        # Resposta genérica
        return {
            "data": omie_result,
            "platform": "omie"
        }
    
    async def call_tool(self, tool_name: str, universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Chama ferramenta do Omie com parâmetros universais"""
        try:
            # Mapear parâmetros universais para formato Omie
            omie_params = self.map_universal_to_omie(tool_name, universal_params)
            
            # Mapear nomes de ferramentas se necessário
            omie_tool_name = self.map_tool_name(tool_name)
            
            # Simular chamada para Omie (substituir pela chamada real)
            if self.omie_client:
                omie_result = await self.omie_client.call_tool(omie_tool_name, omie_params)
            else:
                omie_result = await self.simulate_omie_call(omie_tool_name, omie_params)
            
            # Mapear resultado para formato universal
            universal_result = self.map_omie_to_universal(tool_name, omie_result)
            
            return universal_result
            
        except Exception as e:
            logger.error(f"Erro no adaptador Omie para {tool_name}: {e}")
            return {
                "error": str(e),
                "platform": "omie",
                "tool": tool_name
            }
    
    def map_tool_name(self, universal_tool_name: str) -> str:
        """Mapeia nome da ferramenta universal para nome específico do Omie"""
        
        # Mapeamentos específicos
        tool_mappings = {
            "consultar_departamentos": "consultar_departamentos",  # Omie usa departamentos
            "consultar_centros_custo": "consultar_departamentos",  # Alias
        }
        
        return tool_mappings.get(universal_tool_name, universal_tool_name)
    
    async def simulate_omie_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simula chamada para Omie (desenvolvimento)"""
        await asyncio.sleep(0.1)  # Simular delay de API
        
        if tool_name == "consultar_clientes":
            return {
                "clientes_cadastro": [
                    {
                        "codigo_cliente": 1,
                        "razao_social": "Empresa Teste Ltda",
                        "cnpj_cpf": "12.345.678/0001-90",
                        "email": "contato@empresa.com",
                        "telefone": "(11) 9999-9999"
                    }
                ],
                "total_de_paginas": 1,
                "pagina": 1
            }
        
        if tool_name == "consultar_categorias":
            return {
                "categorias": [
                    {"codigo": "1", "descricao": "Vendas"},
                    {"codigo": "2", "descricao": "Compras"}
                ],
                "total_de_paginas": 1,
                "pagina": 1
            }
        
        if tool_name == "consultar_departamentos":
            return {
                "departamentos": [
                    {"codigo": "1", "nome": "Comercial"},
                    {"codigo": "2", "nome": "Financeiro"}
                ],
                "total_de_paginas": 1,
                "pagina": 1
            }
        
        return {"resultado": "sucesso", "dados": params}
    
    def get_available_tools(self) -> list:
        """Retorna lista de ferramentas disponíveis no Omie"""
        return [
            "consultar_categorias",
            "consultar_departamentos",
            "consultar_clientes",
            "consultar_fornecedores",
            "consultar_contas_pagar",
            "consultar_contas_receber",
            "consultar_tipos_documento",
            "incluir_cliente",
            "incluir_fornecedor",
            "alterar_cliente",
            "alterar_fornecedor",
            "criar_conta_pagar",
            "criar_conta_receber",
            "atualizar_conta_pagar",
            "atualizar_conta_receber",
            "consultar_cliente_por_codigo",
            "consultar_fornecedor_por_codigo",
            "buscar_dados_contato_cliente",
            "buscar_dados_contato_fornecedor",
            "cadastrar_cliente_fornecedor"
        ]