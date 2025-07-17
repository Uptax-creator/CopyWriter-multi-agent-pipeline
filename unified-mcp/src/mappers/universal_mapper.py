"""
Mapeador Universal - Converte dados entre diferentes formatos de ERP
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("universal-mapper")

class UniversalMapper:
    """Mapeador universal para padronização de dados entre ERPs"""
    
    def __init__(self):
        self.load_mappings()
    
    def load_mappings(self):
        """Carrega mapeamentos de configuração"""
        try:
            with open('/Users/kleberdossantosribeiro/omie-mcp/unified-mcp/config/tool_mapping.json', 'r') as f:
                self.mappings = json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar mapeamentos: {e}")
            self.mappings = self.get_default_mappings()
    
    def get_default_mappings(self) -> Dict[str, Any]:
        """Retorna mapeamentos padrão caso arquivo não exista"""
        return {
            "field_mappings": {
                "cliente": {
                    "omie": {"id": "codigo_cliente", "name": "razao_social", "document": "cnpj_cpf"},
                    "nibo": {"id": "id", "name": "name", "document": "document"}
                }
            },
            "date_formats": {
                "omie": "DD/MM/YYYY",
                "nibo": "YYYY-MM-DD",
                "universal": "ISO"
            }
        }
    
    def map_entity_fields(self, entity_type: str, data: Dict[str, Any], from_platform: str, to_platform: str) -> Dict[str, Any]:
        """Mapeia campos de uma entidade entre plataformas"""
        
        if entity_type not in self.mappings.get("field_mappings", {}):
            return data
        
        entity_mappings = self.mappings["field_mappings"][entity_type]
        
        if from_platform not in entity_mappings or to_platform not in entity_mappings:
            return data
        
        from_mapping = entity_mappings[from_platform]
        to_mapping = entity_mappings[to_platform]
        
        # Criar mapeamento reverso
        reverse_mapping = {v: k for k, v in from_mapping.items()}
        
        mapped_data = {}
        for key, value in data.items():
            if key in reverse_mapping:
                universal_key = reverse_mapping[key]
                target_key = to_mapping.get(universal_key, key)
                mapped_data[target_key] = value
            else:
                mapped_data[key] = value
        
        return mapped_data
    
    def normalize_date(self, date_str: str, from_platform: str, to_format: str = "universal") -> str:
        """Normaliza formato de data entre plataformas"""
        
        if not date_str:
            return date_str
        
        try:
            # Formato Omie: DD/MM/YYYY
            if from_platform == "omie":
                if "/" in date_str:
                    day, month, year = date_str.split("/")
                    date_obj = datetime(int(year), int(month), int(day))
                else:
                    return date_str
            
            # Formato Nibo: YYYY-MM-DD
            elif from_platform == "nibo":
                if "-" in date_str:
                    year, month, day = date_str.split("-")
                    date_obj = datetime(int(year), int(month), int(day))
                else:
                    return date_str
            
            else:
                return date_str
            
            # Converter para formato desejado
            if to_format == "universal" or to_format == "iso":
                return date_obj.isoformat()[:10]  # YYYY-MM-DD
            elif to_format == "omie":
                return date_obj.strftime("%d/%m/%Y")
            elif to_format == "nibo":
                return date_obj.strftime("%Y-%m-%d")
            
            return date_str
            
        except Exception as e:
            logger.error(f"Erro ao normalizar data {date_str} de {from_platform}: {e}")
            return date_str
    
    def normalize_document(self, document: str, from_platform: str, to_platform: str) -> str:
        """Normaliza formato de documento (CPF/CNPJ)"""
        
        if not document:
            return document
        
        # Remover formatação
        clean_doc = ''.join(filter(str.isdigit, document))
        
        # Formato Omie: sempre com pontuação
        if to_platform == "omie":
            if len(clean_doc) == 11:  # CPF
                return f"{clean_doc[:3]}.{clean_doc[3:6]}.{clean_doc[6:9]}-{clean_doc[9:]}"
            elif len(clean_doc) == 14:  # CNPJ
                return f"{clean_doc[:2]}.{clean_doc[2:5]}.{clean_doc[5:8]}/{clean_doc[8:12]}-{clean_doc[12:]}"
        
        # Formato Nibo: sem pontuação
        elif to_platform == "nibo":
            return clean_doc
        
        return document
    
    def normalize_currency(self, amount: Any, from_platform: str, to_platform: str) -> float:
        """Normaliza valores monetários"""
        
        if not amount:
            return 0.0
        
        try:
            # Converter para float
            if isinstance(amount, str):
                # Remover formatação brasileira
                clean_amount = amount.replace("R$", "").replace(".", "").replace(",", ".").strip()
                return float(clean_amount)
            
            return float(amount)
            
        except Exception as e:
            logger.error(f"Erro ao normalizar valor {amount}: {e}")
            return 0.0
    
    def merge_results(self, omie_result: Dict[str, Any], nibo_result: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """Mescla resultados de ambas as plataformas"""
        
        merged_result = {
            "entities": [],
            "total_omie": 0,
            "total_nibo": 0,
            "platforms": ["omie", "nibo"],
            "entity_type": entity_type
        }
        
        # Processar resultado Omie
        if omie_result and not omie_result.get("error"):
            omie_entities = omie_result.get("entities", [])
            for entity in omie_entities:
                normalized_entity = self.map_entity_fields(entity_type, entity, "omie", "universal")
                normalized_entity["_platform"] = "omie"
                merged_result["entities"].append(normalized_entity)
            merged_result["total_omie"] = len(omie_entities)
        
        # Processar resultado Nibo
        if nibo_result and not nibo_result.get("error"):
            nibo_entities = nibo_result.get("entities", [])
            for entity in nibo_entities:
                normalized_entity = self.map_entity_fields(entity_type, entity, "nibo", "universal")
                normalized_entity["_platform"] = "nibo"
                merged_result["entities"].append(normalized_entity)
            merged_result["total_nibo"] = len(nibo_entities)
        
        merged_result["total"] = merged_result["total_omie"] + merged_result["total_nibo"]
        
        return merged_result
    
    def create_universal_response(self, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria resposta padronizada universal"""
        
        response = {
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        return response
    
    def get_compatibility_note(self, tool_name: str) -> Optional[str]:
        """Retorna nota de compatibilidade para ferramenta"""
        
        aliases = self.mappings.get("aliases", {})
        
        if tool_name in aliases:
            return aliases[tool_name].get("note")
        
        return None