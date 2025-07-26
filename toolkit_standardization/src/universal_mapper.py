#!/usr/bin/env python3
"""
Universal Mapper para Padronização de Ferramentas ERP
Implementa o padrão universal de nomenclatura para todos os ERPs
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ERPPlatform(Enum):
    """Plataformas ERP suportadas"""
    OMIE = "omie"
    NIBO = "nibo"
    SAP = "sap"
    ORACLE = "oracle"
    QUICKBOOKS = "quickbooks"
    DYNAMICS = "dynamics"


class UniversalAction(Enum):
    """Ações universais padronizadas"""
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"


class UniversalEntity(Enum):
    """Entidades universais padronizadas"""
    CUSTOMERS = "customers"
    VENDORS = "vendors"
    INVOICES = "invoices"
    PRODUCTS = "products"
    ACCOUNTS = "accounts"
    PAYMENTS = "payments"
    CATEGORIES = "categories"
    DEPARTMENTS = "departments"
    PARTNERS = "partners"


@dataclass
class ToolMapping:
    """Mapeamento de ferramenta universal"""
    universal_name: str
    description: str
    action: UniversalAction
    entity: UniversalEntity
    platform_mappings: Dict[ERPPlatform, str] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)


class UniversalMapper:
    """Mapper universal para ferramentas ERP"""
    
    def __init__(self):
        self.mappings: Dict[str, ToolMapping] = {}
        self.platform_aliases: Dict[ERPPlatform, Dict[str, str]] = {}
        self._init_standard_mappings()
    
    def _init_standard_mappings(self):
        """Inicializa mapeamentos padrão"""
        
        # Customers (Clientes)
        self.add_mapping(
            universal_name="get_customers_list",
            description="Lista clientes cadastrados",
            action=UniversalAction.GET,
            entity=UniversalEntity.CUSTOMERS,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_clientes",
                ERPPlatform.NIBO: "consultar_clientes",
                ERPPlatform.SAP: "GET_CUSTOMER_LIST",
                ERPPlatform.ORACLE: "list_customers",
                ERPPlatform.QUICKBOOKS: "query_customers"
            },
            input_schema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1},
                    "limit": {"type": "integer", "default": 50},
                    "active_only": {"type": "boolean", "default": True}
                }
            }
        )
        
        # Categories (Categorias)
        self.add_mapping(
            universal_name="get_categories_list",
            description="Lista categorias cadastradas",
            action=UniversalAction.GET,
            entity=UniversalEntity.CATEGORIES,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_categorias",
                ERPPlatform.NIBO: "consultar_categorias",
                ERPPlatform.SAP: "GET_CATEGORY_LIST",
                ERPPlatform.ORACLE: "list_categories"
            }
        )
        
        # Departments (Departamentos)
        self.add_mapping(
            universal_name="get_departments_list",
            description="Lista departamentos/centros de custo",
            action=UniversalAction.GET,
            entity=UniversalEntity.DEPARTMENTS,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_departamentos",
                ERPPlatform.NIBO: "consultar_centros_custo",
                ERPPlatform.SAP: "GET_COST_CENTERS",
                ERPPlatform.ORACLE: "list_departments"
            }
        )
        
        # Vendors (Fornecedores)
        self.add_mapping(
            universal_name="get_vendors_list",
            description="Lista fornecedores cadastrados",
            action=UniversalAction.GET,
            entity=UniversalEntity.VENDORS,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_fornecedores",
                ERPPlatform.NIBO: "consultar_fornecedores",
                ERPPlatform.SAP: "GET_VENDOR_LIST",
                ERPPlatform.ORACLE: "list_suppliers"
            }
        )
        
        # Create Customer
        self.add_mapping(
            universal_name="create_customer",
            description="Criar novo cliente",
            action=UniversalAction.CREATE,
            entity=UniversalEntity.CUSTOMERS,
            platform_mappings={
                ERPPlatform.OMIE: "incluir_cliente",
                ERPPlatform.NIBO: "incluir_cliente",
                ERPPlatform.SAP: "CREATE_CUSTOMER",
                ERPPlatform.ORACLE: "create_customer"
            }
        )
        
        # Accounts Payable
        self.add_mapping(
            universal_name="get_accounts_payable_list",
            description="Lista contas a pagar",
            action=UniversalAction.GET,
            entity=UniversalEntity.ACCOUNTS,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_contas_pagar",
                ERPPlatform.NIBO: "consultar_contas_pagar",
                ERPPlatform.SAP: "GET_PAYABLES_LIST",
                ERPPlatform.ORACLE: "list_payables"
            }
        )
        
        # Accounts Receivable
        self.add_mapping(
            universal_name="get_accounts_receivable_list",
            description="Lista contas a receber",
            action=UniversalAction.GET,
            entity=UniversalEntity.ACCOUNTS,
            platform_mappings={
                ERPPlatform.OMIE: "consultar_contas_receber",
                ERPPlatform.NIBO: "consultar_contas_receber",
                ERPPlatform.SAP: "GET_RECEIVABLES_LIST",
                ERPPlatform.ORACLE: "list_receivables"
            }
        )
    
    def add_mapping(self, universal_name: str, description: str, 
                   action: UniversalAction, entity: UniversalEntity,
                   platform_mappings: Dict[ERPPlatform, str],
                   input_schema: Dict[str, Any] = None,
                   output_schema: Dict[str, Any] = None,
                   aliases: Dict[str, str] = None):
        """Adiciona um novo mapeamento"""
        
        mapping = ToolMapping(
            universal_name=universal_name,
            description=description,
            action=action,
            entity=entity,
            platform_mappings=platform_mappings,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            aliases=aliases or {}
        )
        
        self.mappings[universal_name] = mapping
    
    def get_platform_tool_name(self, universal_name: str, platform: ERPPlatform) -> Optional[str]:
        """Obtém nome da ferramenta para plataforma específica"""
        mapping = self.mappings.get(universal_name)
        if not mapping:
            return None
        
        return mapping.platform_mappings.get(platform)
    
    def get_universal_name(self, platform_name: str, platform: ERPPlatform) -> Optional[str]:
        """Obtém nome universal a partir do nome da plataforma"""
        for universal_name, mapping in self.mappings.items():
            if mapping.platform_mappings.get(platform) == platform_name:
                return universal_name
        return None
    
    def get_all_tools_for_platform(self, platform: ERPPlatform) -> Dict[str, str]:
        """Retorna todos os mapeamentos para uma plataforma"""
        result = {}
        for universal_name, mapping in self.mappings.items():
            platform_name = mapping.platform_mappings.get(platform)
            if platform_name:
                result[universal_name] = platform_name
        return result
    
    def validate_tool_compatibility(self, universal_name: str, platforms: List[ERPPlatform]) -> Dict[ERPPlatform, bool]:
        """Valida compatibilidade de ferramenta entre plataformas"""
        mapping = self.mappings.get(universal_name)
        if not mapping:
            return {platform: False for platform in platforms}
        
        result = {}
        for platform in platforms:
            result[platform] = platform in mapping.platform_mappings
        
        return result
    
    def generate_tool_schema(self, universal_name: str, platform: ERPPlatform) -> Dict[str, Any]:
        """Gera schema da ferramenta para plataforma específica"""
        mapping = self.mappings.get(universal_name)
        if not mapping:
            return {}
        
        platform_name = mapping.platform_mappings.get(platform)
        if not platform_name:
            return {}
        
        return {
            "name": platform_name,
            "universal_name": universal_name,
            "description": mapping.description,
            "platform": platform.value,
            "action": mapping.action.value,
            "entity": mapping.entity.value,
            "inputSchema": mapping.input_schema,
            "outputSchema": mapping.output_schema
        }
    
    def transform_parameters(self, universal_name: str, platform: ERPPlatform, 
                           universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma parâmetros universais para plataforma específica"""
        
        # Mapeamentos de parâmetros comuns
        param_mappings = {
            ERPPlatform.OMIE: {
                "page": "pagina",
                "limit": "registros_por_pagina",
                "document": "cnpj_cpf",
                "name": "razao_social",
                "start_date": "data_inicio",
                "end_date": "data_fim"
            },
            ERPPlatform.NIBO: {
                "page": "pagina",
                "limit": "registros_por_pagina",
                "document": "cnpj_cpf",
                "name": "nome",
                "start_date": "data_inicio",
                "end_date": "data_fim"
            },
            ERPPlatform.SAP: {
                "page": "SKIP",
                "limit": "TOP",
                "document": "TAX_ID",
                "name": "NAME",
                "start_date": "START_DATE",
                "end_date": "END_DATE"
            }
        }
        
        platform_mapping = param_mappings.get(platform, {})
        transformed_params = {}
        
        for universal_param, value in universal_params.items():
            platform_param = platform_mapping.get(universal_param, universal_param)
            transformed_params[platform_param] = value
        
        return transformed_params
    
    def export_mappings(self, file_path: str):
        """Exporta mapeamentos para arquivo JSON"""
        export_data = {}
        
        for universal_name, mapping in self.mappings.items():
            export_data[universal_name] = {
                "description": mapping.description,
                "action": mapping.action.value,
                "entity": mapping.entity.value,
                "platform_mappings": {
                    platform.value: tool_name 
                    for platform, tool_name in mapping.platform_mappings.items()
                },
                "input_schema": mapping.input_schema,
                "output_schema": mapping.output_schema,
                "aliases": mapping.aliases
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def import_mappings(self, file_path: str):
        """Importa mapeamentos de arquivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for universal_name, data in import_data.items():
            platform_mappings = {
                ERPPlatform(platform): tool_name
                for platform, tool_name in data["platform_mappings"].items()
            }
            
            self.add_mapping(
                universal_name=universal_name,
                description=data["description"],
                action=UniversalAction(data["action"]),
                entity=UniversalEntity(data["entity"]),
                platform_mappings=platform_mappings,
                input_schema=data.get("input_schema", {}),
                output_schema=data.get("output_schema", {}),
                aliases=data.get("aliases", {})
            )


# Instância global do mapper
universal_mapper = UniversalMapper()


def get_mapper() -> UniversalMapper:
    """Retorna instância global do mapper"""
    return universal_mapper


# Funções utilitárias
def map_tool_name(universal_name: str, platform: ERPPlatform) -> Optional[str]:
    """Função utilitária para mapear nome da ferramenta"""
    return universal_mapper.get_platform_tool_name(universal_name, platform)


def reverse_map_tool_name(platform_name: str, platform: ERPPlatform) -> Optional[str]:
    """Função utilitária para mapear nome da plataforma para universal"""
    return universal_mapper.get_universal_name(platform_name, platform)


def validate_compatibility(universal_name: str, platforms: List[ERPPlatform]) -> Dict[ERPPlatform, bool]:
    """Função utilitária para validar compatibilidade"""
    return universal_mapper.validate_tool_compatibility(universal_name, platforms)


if __name__ == "__main__":
    # Exemplo de uso
    mapper = get_mapper()
    
    # Testar mapeamento
    print("🧪 Testando Universal Mapper...")
    
    # Omie
    omie_tool = mapper.get_platform_tool_name("get_customers_list", ERPPlatform.OMIE)
    print(f"✅ Omie: get_customers_list -> {omie_tool}")
    
    # Nibo
    nibo_tool = mapper.get_platform_tool_name("get_customers_list", ERPPlatform.NIBO)
    print(f"✅ Nibo: get_customers_list -> {nibo_tool}")
    
    # SAP
    sap_tool = mapper.get_platform_tool_name("get_customers_list", ERPPlatform.SAP)
    print(f"✅ SAP: get_customers_list -> {sap_tool}")
    
    # Validar compatibilidade
    compatibility = mapper.validate_tool_compatibility(
        "get_customers_list", 
        [ERPPlatform.OMIE, ERPPlatform.NIBO, ERPPlatform.SAP]
    )
    print(f"✅ Compatibilidade: {compatibility}")
    
    # Exportar mapeamentos
    mapper.export_mappings("universal_mappings.json")
    print("✅ Mapeamentos exportados para universal_mappings.json")
    
    print("🎉 Teste concluído!")