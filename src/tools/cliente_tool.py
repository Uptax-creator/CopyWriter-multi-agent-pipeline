"""
Ferramentas para gerenciamento de clientes e fornecedores
"""

from typing import Dict, Any
from src.tools.base import CrudTool
from src.client.omie_client import omie_client
from src.utils.validators import OmieValidators, OmieCodeValidators

class IncluirClienteTool(CrudTool):
    """Ferramenta para incluir cliente"""
    
    def get_name(self) -> str:
        return "incluir_cliente"
    
    def get_description(self) -> str:
        return "Inclui um novo cliente no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cnpj_cpf": {
                    "type": "string",
                    "description": "CNPJ ou CPF do cliente"
                },
                "razao_social": {
                    "type": "string",
                    "description": "Razão social do cliente"
                },
                "nome_fantasia": {
                    "type": "string",
                    "description": "Nome fantasia do cliente"
                },
                "email": {
                    "type": "string",
                    "description": "Email do cliente"
                },
                "telefone": {
                    "type": "string",
                    "description": "Telefone do cliente"
                },
                "codigo_cliente_integracao": {
                    "type": "string",
                    "description": "Código de integração do cliente"
                }
            },
            "required": ["cnpj_cpf", "razao_social"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Validar CNPJ/CPF
        cnpj_cpf = arguments["cnpj_cpf"]
        if not OmieValidators.validar_cnpj(cnpj_cpf) and not OmieValidators.validar_cpf(cnpj_cpf):
            return "❌ CNPJ/CPF inválido"
        
        # Verificar se cliente já existe
        cliente_existente = await OmieCodeValidators.validar_cnpj_cliente(cnpj_cpf)
        if cliente_existente:
            return f"❌ Cliente já cadastrado com código: {cliente_existente.get('codigo_cliente_omie')}"
        
        # Montar dados do cliente
        dados_cliente = {
            "cnpj_cpf": cnpj_cpf,
            "razao_social": arguments["razao_social"],
            "codigo_cliente_integracao": arguments.get("codigo_cliente_integracao", cnpj_cpf)
        }
        
        # Campos opcionais
        if "nome_fantasia" in arguments:
            dados_cliente["nome_fantasia"] = arguments["nome_fantasia"]
        if "email" in arguments:
            if OmieValidators.validar_email(arguments["email"]):
                dados_cliente["email"] = arguments["email"]
            else:
                return "❌ Email inválido"
        if "telefone" in arguments:
            if OmieValidators.validar_telefone(arguments["telefone"]):
                dados_cliente["telefone1_numero"] = arguments["telefone"]
            else:
                return "❌ Telefone inválido"
        
        # Incluir cliente
        result = await omie_client.incluir_cliente(dados_cliente)
        
        # Formatar resposta
        return self.format_crud_response("inclusão de cliente", result)

class IncluirFornecedorTool(CrudTool):
    """Ferramenta para incluir fornecedor"""
    
    def get_name(self) -> str:
        return "incluir_fornecedor"
    
    def get_description(self) -> str:
        return "Inclui um novo fornecedor no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cnpj_cpf": {
                    "type": "string",
                    "description": "CNPJ ou CPF do fornecedor"
                },
                "razao_social": {
                    "type": "string",
                    "description": "Razão social do fornecedor"
                },
                "nome_fantasia": {
                    "type": "string",
                    "description": "Nome fantasia do fornecedor"
                },
                "email": {
                    "type": "string",
                    "description": "Email do fornecedor"
                },
                "telefone": {
                    "type": "string",
                    "description": "Telefone do fornecedor"
                },
                "codigo_fornecedor_integracao": {
                    "type": "string",
                    "description": "Código de integração do fornecedor"
                }
            },
            "required": ["cnpj_cpf", "razao_social"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Validar CNPJ/CPF
        cnpj_cpf = arguments["cnpj_cpf"]
        if not OmieValidators.validar_cnpj(cnpj_cpf) and not OmieValidators.validar_cpf(cnpj_cpf):
            return "❌ CNPJ/CPF inválido"
        
        # Verificar se fornecedor já existe
        fornecedor_existente = await OmieCodeValidators.validar_cnpj_fornecedor(cnpj_cpf)
        if fornecedor_existente:
            return f"❌ Fornecedor já cadastrado com código: {fornecedor_existente.get('codigo_fornecedor_omie')}"
        
        # Montar dados do fornecedor
        dados_fornecedor = {
            "cnpj_cpf": cnpj_cpf,
            "razao_social": arguments["razao_social"],
            "codigo_fornecedor_integracao": arguments.get("codigo_fornecedor_integracao", cnpj_cpf)
        }
        
        # Campos opcionais
        if "nome_fantasia" in arguments:
            dados_fornecedor["nome_fantasia"] = arguments["nome_fantasia"]
        if "email" in arguments:
            if OmieValidators.validar_email(arguments["email"]):
                dados_fornecedor["email"] = arguments["email"]
            else:
                return "❌ Email inválido"
        if "telefone" in arguments:
            if OmieValidators.validar_telefone(arguments["telefone"]):
                dados_fornecedor["telefone1_numero"] = arguments["telefone"]
            else:
                return "❌ Telefone inválido"
        
        # Incluir fornecedor
        result = await omie_client.incluir_fornecedor(dados_fornecedor)
        
        # Formatar resposta
        return self.format_crud_response("inclusão de fornecedor", result)

class AlterarClienteTool(CrudTool):
    """Ferramenta para alterar cliente"""
    
    def get_name(self) -> str:
        return "alterar_cliente"
    
    def get_description(self) -> str:
        return "Altera um cliente existente no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "codigo_cliente_omie": {
                    "type": "string",
                    "description": "Código do cliente no Omie (obrigatório para alteração)"
                },
                "cnpj_cpf": {
                    "type": "string",
                    "description": "CNPJ ou CPF do cliente"
                },
                "razao_social": {
                    "type": "string",
                    "description": "Razão social do cliente"
                },
                "nome_fantasia": {
                    "type": "string",
                    "description": "Nome fantasia do cliente"
                },
                "email": {
                    "type": "string",
                    "description": "Email do cliente"
                },
                "telefone": {
                    "type": "string",
                    "description": "Telefone do cliente"
                }
            },
            "required": ["codigo_cliente_omie"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Montar dados do cliente
        dados_cliente = {
            "codigo_cliente_omie": arguments["codigo_cliente_omie"]
        }
        
        # Validar e adicionar campos opcionais
        if "cnpj_cpf" in arguments:
            cnpj_cpf = arguments["cnpj_cpf"]
            if not OmieValidators.validar_cnpj(cnpj_cpf) and not OmieValidators.validar_cpf(cnpj_cpf):
                return "❌ CNPJ/CPF inválido"
            dados_cliente["cnpj_cpf"] = cnpj_cpf
        
        if "razao_social" in arguments:
            dados_cliente["razao_social"] = arguments["razao_social"]
        
        if "nome_fantasia" in arguments:
            dados_cliente["nome_fantasia"] = arguments["nome_fantasia"]
        
        if "email" in arguments:
            if OmieValidators.validar_email(arguments["email"]):
                dados_cliente["email"] = arguments["email"]
            else:
                return "❌ Email inválido"
        
        if "telefone" in arguments:
            if OmieValidators.validar_telefone(arguments["telefone"]):
                dados_cliente["telefone1_numero"] = arguments["telefone"]
            else:
                return "❌ Telefone inválido"
        
        # Alterar cliente
        result = await omie_client.alterar_cliente(dados_cliente)
        
        # Formatar resposta
        return self.format_crud_response("alteração de cliente", result)

class AlterarFornecedorTool(CrudTool):
    """Ferramenta para alterar fornecedor"""
    
    def get_name(self) -> str:
        return "alterar_fornecedor"
    
    def get_description(self) -> str:
        return "Altera um fornecedor existente no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "codigo_fornecedor_omie": {
                    "type": "string",
                    "description": "Código do fornecedor no Omie (obrigatório para alteração)"
                },
                "cnpj_cpf": {
                    "type": "string",
                    "description": "CNPJ ou CPF do fornecedor"
                },
                "razao_social": {
                    "type": "string",
                    "description": "Razão social do fornecedor"
                },
                "nome_fantasia": {
                    "type": "string",
                    "description": "Nome fantasia do fornecedor"
                },
                "email": {
                    "type": "string",
                    "description": "Email do fornecedor"
                },
                "telefone": {
                    "type": "string",
                    "description": "Telefone do fornecedor"
                }
            },
            "required": ["codigo_fornecedor_omie"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Montar dados do fornecedor
        dados_fornecedor = {
            "codigo_fornecedor_omie": arguments["codigo_fornecedor_omie"]
        }
        
        # Validar e adicionar campos opcionais
        if "cnpj_cpf" in arguments:
            cnpj_cpf = arguments["cnpj_cpf"]
            if not OmieValidators.validar_cnpj(cnpj_cpf) and not OmieValidators.validar_cpf(cnpj_cpf):
                return "❌ CNPJ/CPF inválido"
            dados_fornecedor["cnpj_cpf"] = cnpj_cpf
        
        if "razao_social" in arguments:
            dados_fornecedor["razao_social"] = arguments["razao_social"]
        
        if "nome_fantasia" in arguments:
            dados_fornecedor["nome_fantasia"] = arguments["nome_fantasia"]
        
        if "email" in arguments:
            if OmieValidators.validar_email(arguments["email"]):
                dados_fornecedor["email"] = arguments["email"]
            else:
                return "❌ Email inválido"
        
        if "telefone" in arguments:
            if OmieValidators.validar_telefone(arguments["telefone"]):
                dados_fornecedor["telefone1_numero"] = arguments["telefone"]
            else:
                return "❌ Telefone inválido"
        
        # Alterar fornecedor
        result = await omie_client.alterar_fornecedor(dados_fornecedor)
        
        # Formatar resposta
        return self.format_crud_response("alteração de fornecedor", result)