"""
Adaptador para Nibo MCP - Converte chamadas universais para formato Nibo
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("nibo-adapter")

class NiboAdapter:
    """Adaptador para comunicação com Nibo MCP Server"""
    
    def __init__(self, nibo_client=None):
        self.nibo_client = nibo_client
        self.platform_name = "nibo"
        
    def map_universal_to_nibo(self, tool_name: str, universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia parâmetros universais para formato Nibo"""
        
        # Mapeamentos específicos do Nibo
        field_mappings = {
            "page": "pagina",
            "limit": "registros_por_pagina",
            "start_date": "data_inicio",
            "end_date": "data_fim",
            "name": "name",
            "document": "document",
            "entity_id": "id",
            "supplier_id": "supplier_id",
            "customer_id": "customer_id",
            "document_number": "document_number",
            "due_date": "due_date",
            "amount": "amount",
            "category": "category_id"
        }
        
        nibo_params = {}
        for universal_key, value in universal_params.items():
            nibo_key = field_mappings.get(universal_key, universal_key)
            nibo_params[nibo_key] = value
            
        return nibo_params
    
    def map_nibo_to_universal(self, tool_name: str, nibo_result: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia resultado do Nibo para formato universal"""
        
        if not isinstance(nibo_result, dict):
            return {"data": nibo_result, "platform": "nibo"}
            
        # Mapeamentos de resposta específicos
        if "clientes" in nibo_result:
            return {
                "entities": nibo_result["clientes"],
                "total": nibo_result.get("total", len(nibo_result["clientes"])),
                "platform": "nibo",
                "entity_type": "cliente"
            }
        
        if "fornecedores" in nibo_result:
            return {
                "entities": nibo_result["fornecedores"],
                "total": nibo_result.get("total", len(nibo_result["fornecedores"])),
                "platform": "nibo",
                "entity_type": "fornecedor"
            }
            
        if "categorias" in nibo_result:
            return {
                "entities": nibo_result["categorias"],
                "total": nibo_result.get("total", len(nibo_result["categorias"])),
                "platform": "nibo",
                "entity_type": "categoria"
            }
            
        if "centros_custo" in nibo_result:
            return {
                "entities": nibo_result["centros_custo"],
                "total": nibo_result.get("total", len(nibo_result["centros_custo"])),
                "platform": "nibo",
                "entity_type": "centro_custo"
            }
            
        if "socios" in nibo_result:
            return {
                "entities": nibo_result["socios"],
                "total": nibo_result.get("total", len(nibo_result["socios"])),
                "platform": "nibo",
                "entity_type": "socio"
            }
            
        # Resposta genérica
        return {
            "data": nibo_result,
            "platform": "nibo"
        }
    
    async def call_tool(self, tool_name: str, universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Chama ferramenta do Nibo com parâmetros universais"""
        try:
            # Mapear parâmetros universais para formato Nibo
            nibo_params = self.map_universal_to_nibo(tool_name, universal_params)
            
            # Mapear nomes de ferramentas se necessário
            nibo_tool_name = self.map_tool_name(tool_name)
            
            # Simular chamada para Nibo (substituir pela chamada real)
            if self.nibo_client:
                nibo_result = await self.nibo_client.call_tool(nibo_tool_name, nibo_params)
            else:
                nibo_result = await self.simulate_nibo_call(nibo_tool_name, nibo_params)
            
            # Mapear resultado para formato universal
            universal_result = self.map_nibo_to_universal(tool_name, nibo_result)
            
            return universal_result
            
        except Exception as e:
            logger.error(f"Erro no adaptador Nibo para {tool_name}: {e}")
            return {
                "error": str(e),
                "platform": "nibo",
                "tool": tool_name
            }
    
    def map_tool_name(self, universal_tool_name: str) -> str:
        """Mapeia nome da ferramenta universal para nome específico do Nibo"""
        
        # Mapeamentos específicos
        tool_mappings = {
            "consultar_departamentos": "consultar_centros_custo",  # Nibo usa centros_custo
            "consultar_centros_custo": "consultar_centros_custo",  # Nativo
        }
        
        return tool_mappings.get(universal_tool_name, universal_tool_name)
    
    async def simulate_nibo_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simula chamada para Nibo (desenvolvimento)"""
        await asyncio.sleep(0.1)  # Simular delay de API
        
        if tool_name == "consultar_clientes":
            return {
                "clientes": [
                    {
                        "id": 1,
                        "name": "Cliente Nibo Ltda",
                        "document": "98.765.432/0001-10",
                        "email": "contato@clientenibo.com",
                        "phone": "(11) 8888-8888"
                    }
                ],
                "total": 1
            }
        
        if tool_name == "consultar_categorias":
            return {
                "categorias": [
                    {"id": 1, "nome": "Vendas", "ativo": True},
                    {"id": 2, "nome": "Compras", "ativo": True}
                ],
                "total": 2
            }
        
        if tool_name == "consultar_centros_custo":
            return {
                "centros_custo": [
                    {"id": 1, "nome": "Comercial", "ativo": True},
                    {"id": 2, "nome": "Financeiro", "ativo": True}
                ],
                "total": 2
            }
        
        if tool_name == "consultar_socios":
            return {
                "socios": [
                    {
                        "id": 1,
                        "nome": "João Silva",
                        "documento": "123.456.789-00",
                        "email": "joao@empresa.com",
                        "participacao": 50.0
                    }
                ],
                "total": 1
            }
        
        return {"resultado": "sucesso", "dados": params}
    
    def get_available_tools(self) -> list:
        """Retorna lista de ferramentas disponíveis no Nibo"""
        return [
            "consultar_categorias",
            "consultar_centros_custo",
            "consultar_clientes",
            "consultar_fornecedores",
            "consultar_contas_pagar",
            "consultar_contas_receber",
            "consultar_socios",
            "incluir_cliente",
            "incluir_fornecedor",
            "incluir_socio",
            "alterar_cliente",
            "alterar_fornecedor",
            "alterar_socio",
            "excluir_cliente",
            "excluir_fornecedor",
            "excluir_socio",
            "obter_cliente_por_id",
            "obter_fornecedor_por_id",
            "obter_socio_por_id",
            "incluir_conta_pagar",
            "incluir_conta_receber",
            "alterar_conta_pagar",
            "alterar_conta_receber",
            "excluir_conta_pagar",
            "excluir_conta_receber",
            "consultar_conta_pagar_por_id",
            "consultar_conta_receber_por_id",
            "consultar_departamentos",
            "buscar_dados_contato_cliente",
            "buscar_dados_contato_fornecedor",
            "incluir_multiplos_clientes",
            "incluir_multiplos_fornecedores",
            "testar_conexao"
        ]