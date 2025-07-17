"""
Utilitários de compatibilidade entre Omie e Nibo
Mapeia diferenças de nomenclatura entre as plataformas
"""
from typing import Dict, Any

class CompatibilityMapper:
    """Mapeador de compatibilidade entre terminologias"""
    
    # Mapeamento de nomes de ferramentas
    TOOL_ALIASES = {
        # Omie → Nibo
        "consultar_departamentos": "consultar_centros_custo",
        "incluir_departamento": "incluir_centro_custo",
        "alterar_departamento": "alterar_centro_custo",
        "excluir_departamento": "excluir_centro_custo",
        
        # Nibo → Omie (reverse mapping)
        "consultar_centros_custo": "consultar_departamentos",
        "incluir_centro_custo": "incluir_departamento", 
        "alterar_centro_custo": "alterar_departamento",
        "excluir_centro_custo": "excluir_departamento"
    }
    
    # Mapeamento de campos
    FIELD_MAPPINGS = {
        "omie_to_nibo": {
            "codigo_departamento": "centro_custo_id",
            "descricao_departamento": "nome_centro_custo",
            "departamento_ativo": "centro_custo_ativo"
        },
        "nibo_to_omie": {
            "centro_custo_id": "codigo_departamento",
            "nome_centro_custo": "descricao_departamento", 
            "centro_custo_ativo": "departamento_ativo"
        }
    }
    
    @classmethod
    def resolve_tool_name(cls, tool_name: str) -> str:
        """Resolve alias de ferramenta para nome real"""
        return cls.TOOL_ALIASES.get(tool_name, tool_name)
    
    @classmethod
    def map_fields_omie_to_nibo(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia campos do formato Omie para Nibo"""
        mapped_data = {}
        mapping = cls.FIELD_MAPPINGS["omie_to_nibo"]
        
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            mapped_data[mapped_key] = value
            
        return mapped_data
    
    @classmethod
    def map_fields_nibo_to_omie(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia campos do formato Nibo para Omie"""
        mapped_data = {}
        mapping = cls.FIELD_MAPPINGS["nibo_to_omie"]
        
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            mapped_data[mapped_key] = value
            
        return mapped_data
    
    @classmethod
    def get_platform_equivalents(cls, tool_name: str) -> Dict[str, str]:
        """Retorna equivalências entre plataformas"""
        equivalents = {
            "current": tool_name,
            "alias": cls.TOOL_ALIASES.get(tool_name),
            "reverse_alias": None
        }
        
        # Buscar alias reverso
        for key, value in cls.TOOL_ALIASES.items():
            if value == tool_name:
                equivalents["reverse_alias"] = key
                break
                
        return equivalents

class DepartmentoCentroCustoAdapter:
    """Adapter específico para Departamentos ↔ Centros de Custo"""
    
    @staticmethod
    def departamento_to_centro_custo(departamento_data: Dict) -> Dict:
        """Converte dados de departamento (Omie) para centro de custo (Nibo)"""
        mapping = {
            "codigo": "id",
            "descricao": "name", 
            "ativo": "active",
            "codigo_departamento": "costCenterId",
            "descricao_departamento": "description"
        }
        
        centro_custo = {}
        for omie_field, nibo_field in mapping.items():
            if omie_field in departamento_data:
                centro_custo[nibo_field] = departamento_data[omie_field]
                
        return centro_custo
    
    @staticmethod
    def centro_custo_to_departamento(centro_custo_data: Dict) -> Dict:
        """Converte dados de centro de custo (Nibo) para departamento (Omie)"""
        mapping = {
            "id": "codigo",
            "name": "descricao",
            "active": "ativo", 
            "costCenterId": "codigo_departamento",
            "description": "descricao_departamento"
        }
        
        departamento = {}
        for nibo_field, omie_field in mapping.items():
            if nibo_field in centro_custo_data:
                departamento[omie_field] = centro_custo_data[nibo_field]
                
        return departamento