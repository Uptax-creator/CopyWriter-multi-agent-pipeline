"""
Classe base para todas as ferramentas MCP
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.utils.logger import logger
from src.utils.sanitizers import json_sanitizer

class MCPToolSchema(BaseModel):
    """Schema para definição de ferramenta MCP"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class BaseTool(ABC):
    """Classe base para todas as ferramentas MCP"""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.input_schema = self.get_input_schema()
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna o nome da ferramenta"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retorna a descrição da ferramenta"""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Retorna o schema de entrada da ferramenta"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """Executa a ferramenta com os argumentos fornecidos"""
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Retorna a definição completa da ferramenta para MCP"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e sanitiza os argumentos de entrada"""
        try:
            # Sanitizar argumentos
            sanitized_args = json_sanitizer.sanitize_json(arguments)
            
            # Log dos argumentos recebidos
            logger.debug(f"Argumentos para {self.name}: {sanitized_args}")
            
            return sanitized_args
            
        except Exception as e:
            logger.error(f"Erro ao validar argumentos para {self.name}: {e}")
            raise ValueError(f"Argumentos inválidos: {str(e)}")
    
    def format_response(self, data: Any) -> str:
        """Formata a resposta para texto legível"""
        try:
            if isinstance(data, dict):
                return self._format_dict_response(data)
            elif isinstance(data, list):
                return self._format_list_response(data)
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Erro ao formatar resposta de {self.name}: {e}")
            return f"Erro ao formatar resposta: {str(e)}"
    
    def _format_dict_response(self, data: Dict[str, Any]) -> str:
        """Formata resposta em formato de dicionário"""
        lines = []
        
        # Verificar se é uma resposta de erro
        if "faultstring" in data:
            return f"❌ Erro: {data['faultstring']}"
        
        # Formatar dados normalmente
        for key, value in data.items():
            if isinstance(value, list) and value:
                lines.append(f"**{key.replace('_', ' ').title()}:**")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"- {self._format_dict_item(item)}")
                    else:
                        lines.append(f"- {item}")
            elif isinstance(value, dict):
                lines.append(f"**{key.replace('_', ' ').title()}:**")
                lines.append(f"  {self._format_dict_item(value)}")
            else:
                lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
        
        return "\\n".join(lines)
    
    def _format_list_response(self, data: List[Any]) -> str:
        """Formata resposta em formato de lista"""
        if not data:
            return "Nenhum resultado encontrado."
        
        lines = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                lines.append(f"{i}. {self._format_dict_item(item)}")
            else:
                lines.append(f"{i}. {item}")
        
        return "\\n".join(lines)
    
    def _format_dict_item(self, item: Dict[str, Any]) -> str:
        """Formata item individual de dicionário"""
        # Campos comuns para exibição
        display_fields = ["codigo", "descricao", "nome", "razao_social", "cnpj_cpf", "valor_documento"]
        
        parts = []
        for field in display_fields:
            if field in item and item[field]:
                parts.append(f"{field}: {item[field]}")
        
        # Se não encontrou campos comuns, mostrar os primeiros 3
        if not parts:
            keys = list(item.keys())[:3]
            for key in keys:
                if item[key]:
                    parts.append(f"{key}: {item[key]}")
        
        return " | ".join(parts)
    
    def handle_error(self, error: Exception) -> str:
        """Trata erros e retorna mensagem formatada"""
        error_msg = str(error)
        
        # Extrair faultstring se presente
        if "faultstring" in error_msg:
            try:
                import json
                error_data = json.loads(error_msg)
                if "faultstring" in error_data:
                    return f"❌ Erro Omie: {error_data['faultstring']}"
            except:
                pass
        
        logger.error(f"Erro na ferramenta {self.name}: {error_msg}")
        return f"❌ Erro: {error_msg}"
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> str:
        """Executa a ferramenta com tratamento de erros"""
        try:
            # Validar argumentos
            validated_args = self.validate_arguments(arguments)
            
            # Executar ferramenta
            result = await self.execute(validated_args)
            
            # Log do resultado
            logger.info(f"Ferramenta {self.name} executada com sucesso")
            
            return result
            
        except Exception as e:
            return self.handle_error(e)

class ConsultaTool(BaseTool):
    """Classe base para ferramentas de consulta"""
    
    def get_base_input_schema(self) -> Dict[str, Any]:
        """Schema base para consultas com paginação"""
        return {
            "type": "object",
            "properties": {
                "pagina": {
                    "type": "integer",
                    "description": "Número da página (padrão: 1)",
                    "default": 1,
                    "minimum": 1
                },
                "registros_por_pagina": {
                    "type": "integer",
                    "description": "Registros por página (padrão: 50, máximo: 500)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 500
                }
            },
            "required": []
        }

class CrudTool(BaseTool):
    """Classe base para ferramentas CRUD"""
    
    def get_base_input_schema(self) -> Dict[str, Any]:
        """Schema base para operações CRUD"""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def format_crud_response(self, operation: str, data: Dict[str, Any]) -> str:
        """Formata resposta de operação CRUD"""
        if "faultstring" in data:
            return f"❌ Erro ao {operation}: {data['faultstring']}"
        
        # Buscar código identificador
        codigo = None
        for key in ["codigo_cliente_omie", "codigo_fornecedor_omie", "codigo_lancamento_omie"]:
            if key in data:
                codigo = data[key]
                break
        
        if codigo:
            return f"✅ {operation.capitalize()} realizado com sucesso. Código: {codigo}"
        else:
            return f"✅ {operation.capitalize()} realizado com sucesso."