"""
Ferramentas de consulta para o Omie MCP
"""

from typing import Dict, Any
from src.tools.base import ConsultaTool
from src.client.omie_client import omie_client

class ConsultarCategoriasTool(ConsultaTool):
    """Ferramenta para consultar categorias"""
    
    def get_name(self) -> str:
        return "consultar_categorias"
    
    def get_description(self) -> str:
        return "Consulta as categorias cadastradas no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_codigo"] = {
            "type": "string",
            "description": "Filtrar por código da categoria"
        }
        schema["properties"]["filtrar_por_descricao"] = {
            "type": "string",
            "description": "Filtrar por descrição da categoria"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_codigo" in arguments:
            params["filtrar_por_codigo"] = arguments["filtrar_por_codigo"]
        if "filtrar_por_descricao" in arguments:
            params["filtrar_por_descricao"] = arguments["filtrar_por_descricao"]
        
        # Fazer consulta
        result = await omie_client.consultar_categorias(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarDepartamentosTool(ConsultaTool):
    """Ferramenta para consultar departamentos"""
    
    def get_name(self) -> str:
        return "consultar_departamentos"
    
    def get_description(self) -> str:
        return "Consulta os departamentos cadastrados no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_codigo"] = {
            "type": "string",
            "description": "Filtrar por código do departamento"
        }
        schema["properties"]["filtrar_por_descricao"] = {
            "type": "string",
            "description": "Filtrar por descrição do departamento"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_codigo" in arguments:
            params["filtrar_por_codigo"] = arguments["filtrar_por_codigo"]
        if "filtrar_por_descricao" in arguments:
            params["filtrar_por_descricao"] = arguments["filtrar_por_descricao"]
        
        # Fazer consulta
        result = await omie_client.consultar_departamentos(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarTiposDocumentoTool(ConsultaTool):
    """Ferramenta para consultar tipos de documento"""
    
    def get_name(self) -> str:
        return "consultar_tipos_documento"
    
    def get_description(self) -> str:
        return "Consulta os tipos de documento cadastrados no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filtrar_por_codigo": {
                    "type": "string",
                    "description": "Filtrar por código do tipo de documento"
                },
                "filtrar_por_descricao": {
                    "type": "string",
                    "description": "Filtrar por descrição do tipo de documento"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros
        params = {}
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_codigo" in arguments:
            params["filtrar_por_codigo"] = arguments["filtrar_por_codigo"]
        if "filtrar_por_descricao" in arguments:
            params["filtrar_por_descricao"] = arguments["filtrar_por_descricao"]
        
        # Fazer consulta
        result = await omie_client.consultar_tipos_documento(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarContasPagarTool(ConsultaTool):
    """Ferramenta para consultar contas a pagar"""
    
    def get_name(self) -> str:
        return "consultar_contas_pagar"
    
    def get_description(self) -> str:
        return "Consulta as contas a pagar cadastradas no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_codigo_lancamento"] = {
            "type": "string",
            "description": "Filtrar por código do lançamento"
        }
        schema["properties"]["filtrar_por_fornecedor"] = {
            "type": "string",
            "description": "Filtrar por código do fornecedor"
        }
        schema["properties"]["filtrar_por_data_inicial"] = {
            "type": "string",
            "description": "Filtrar por data inicial (DD/MM/YYYY)"
        }
        schema["properties"]["filtrar_por_data_final"] = {
            "type": "string",
            "description": "Filtrar por data final (DD/MM/YYYY)"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_codigo_lancamento" in arguments:
            params["filtrar_por_codigo_lancamento"] = arguments["filtrar_por_codigo_lancamento"]
        if "filtrar_por_fornecedor" in arguments:
            params["filtrar_por_fornecedor"] = arguments["filtrar_por_fornecedor"]
        if "filtrar_por_data_inicial" in arguments:
            params["filtrar_por_data_inicial"] = arguments["filtrar_por_data_inicial"]
        if "filtrar_por_data_final" in arguments:
            params["filtrar_por_data_final"] = arguments["filtrar_por_data_final"]
        
        # Fazer consulta
        result = await omie_client.consultar_contas_pagar(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarContasReceberTool(ConsultaTool):
    """Ferramenta para consultar contas a receber"""
    
    def get_name(self) -> str:
        return "consultar_contas_receber"
    
    def get_description(self) -> str:
        return "Consulta as contas a receber cadastradas no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_codigo_lancamento"] = {
            "type": "string",
            "description": "Filtrar por código do lançamento"
        }
        schema["properties"]["filtrar_por_cliente"] = {
            "type": "string",
            "description": "Filtrar por código do cliente"
        }
        schema["properties"]["filtrar_por_data_inicial"] = {
            "type": "string",
            "description": "Filtrar por data inicial (DD/MM/YYYY)"
        }
        schema["properties"]["filtrar_por_data_final"] = {
            "type": "string",
            "description": "Filtrar por data final (DD/MM/YYYY)"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_codigo_lancamento" in arguments:
            params["filtrar_por_codigo_lancamento"] = arguments["filtrar_por_codigo_lancamento"]
        if "filtrar_por_cliente" in arguments:
            params["filtrar_por_cliente"] = arguments["filtrar_por_cliente"]
        if "filtrar_por_data_inicial" in arguments:
            params["filtrar_por_data_inicial"] = arguments["filtrar_por_data_inicial"]
        if "filtrar_por_data_final" in arguments:
            params["filtrar_por_data_final"] = arguments["filtrar_por_data_final"]
        
        # Fazer consulta
        result = await omie_client.consultar_contas_receber(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarClientesTool(ConsultaTool):
    """Ferramenta para consultar clientes"""
    
    def get_name(self) -> str:
        return "consultar_clientes"
    
    def get_description(self) -> str:
        return "Consulta os clientes cadastrados no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_nome"] = {
            "type": "string",
            "description": "Filtrar por nome do cliente"
        }
        schema["properties"]["cnpj_cpf"] = {
            "type": "string",
            "description": "Filtrar por CNPJ/CPF do cliente"
        }
        schema["properties"]["codigo_cliente_omie"] = {
            "type": "string",
            "description": "Filtrar por código do cliente no Omie"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_nome" in arguments:
            params["filtrar_por_nome"] = arguments["filtrar_por_nome"]
        if "cnpj_cpf" in arguments:
            params["cnpj_cpf"] = arguments["cnpj_cpf"]
        if "codigo_cliente_omie" in arguments:
            params["codigo_cliente_omie"] = arguments["codigo_cliente_omie"]
        
        # Fazer consulta
        result = await omie_client.consultar_clientes(params)
        
        # Formatar resposta
        return self.format_response(result)

class ConsultarFornecedoresTool(ConsultaTool):
    """Ferramenta para consultar fornecedores"""
    
    def get_name(self) -> str:
        return "consultar_fornecedores"
    
    def get_description(self) -> str:
        return "Consulta os fornecedores cadastrados no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        schema = self.get_base_input_schema()
        schema["properties"]["filtrar_por_nome"] = {
            "type": "string",
            "description": "Filtrar por nome do fornecedor"
        }
        schema["properties"]["cnpj_cpf"] = {
            "type": "string",
            "description": "Filtrar por CNPJ/CPF do fornecedor"
        }
        schema["properties"]["codigo_fornecedor_omie"] = {
            "type": "string",
            "description": "Filtrar por código do fornecedor no Omie"
        }
        return schema
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Definir parâmetros padrão
        params = {
            "pagina": arguments.get("pagina", 1),
            "registros_por_pagina": arguments.get("registros_por_pagina", 50)
        }
        
        # Adicionar filtros se fornecidos
        if "filtrar_por_nome" in arguments:
            params["filtrar_por_nome"] = arguments["filtrar_por_nome"]
        if "cnpj_cpf" in arguments:
            params["cnpj_cpf"] = arguments["cnpj_cpf"]
        if "codigo_fornecedor_omie" in arguments:
            params["codigo_fornecedor_omie"] = arguments["codigo_fornecedor_omie"]
        
        # Fazer consulta
        result = await omie_client.consultar_fornecedores(params)
        
        # Formatar resposta
        return self.format_response(result)