"""
Ferramentas para gerenciamento de contas a pagar
"""

from typing import Dict, Any, List
from src.tools.base import CrudTool
from src.client.omie_client import omie_client
from src.utils.validators import OmieValidators, OmieCodeValidators

class IncluirContaPagarTool(CrudTool):
    """Ferramenta para incluir conta a pagar"""
    
    def get_name(self) -> str:
        return "incluir_conta_pagar"
    
    def get_description(self) -> str:
        return "Inclui uma nova conta a pagar no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cnpj_fornecedor": {
                    "type": "string",
                    "description": "CNPJ do fornecedor"
                },
                "data_vencimento": {
                    "type": "string",
                    "description": "Data de vencimento (DD/MM/YYYY)"
                },
                "valor_documento": {
                    "type": "number",
                    "description": "Valor do documento"
                },
                "codigo_categoria": {
                    "type": "string",
                    "description": "Código da categoria"
                },
                "observacao": {
                    "type": "string",
                    "description": "Observação sobre a conta"
                },
                "numero_documento": {
                    "type": "string",
                    "description": "Número do documento"
                },
                "codigo_departamento": {
                    "type": "string",
                    "description": "Código do departamento"
                },
                "codigo_lancamento_integracao": {
                    "type": "string",
                    "description": "Código de integração do lançamento"
                }
            },
            "required": ["cnpj_fornecedor", "data_vencimento", "valor_documento", "codigo_categoria"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Validar CNPJ do fornecedor
        cnpj_fornecedor = arguments["cnpj_fornecedor"]
        if not OmieValidators.validar_cnpj(cnpj_fornecedor):
            return "❌ CNPJ do fornecedor inválido"
        
        # Verificar se fornecedor existe
        fornecedor = await OmieCodeValidators.validar_cnpj_fornecedor(cnpj_fornecedor)
        if not fornecedor:
            return f"❌ Fornecedor com CNPJ {cnpj_fornecedor} não encontrado"
        
        # Validar data de vencimento
        data_vencimento = arguments["data_vencimento"]
        if not OmieValidators.validar_data(data_vencimento):
            return "❌ Data de vencimento inválida. Use o formato DD/MM/YYYY"
        
        # Validar valor
        valor_documento = arguments["valor_documento"]
        if not OmieValidators.validar_valor(valor_documento):
            return "❌ Valor do documento deve ser um número positivo"
        
        # Validar categoria
        codigo_categoria = arguments["codigo_categoria"]
        categoria = await OmieCodeValidators.validar_codigo_categoria(codigo_categoria)
        if not categoria:
            return f"❌ Categoria {codigo_categoria} não encontrada"
        
        # Montar dados da conta a pagar
        dados_conta = {
            "codigo_fornecedor_omie": fornecedor["codigo_fornecedor_omie"],
            "data_vencimento": data_vencimento,
            "valor_documento": float(valor_documento),
            "codigo_categoria": codigo_categoria,
            "codigo_lancamento_integracao": arguments.get("codigo_lancamento_integracao", f"CP_{cnpj_fornecedor}_{data_vencimento}")
        }
        
        # Campos opcionais
        if "observacao" in arguments:
            dados_conta["observacao"] = arguments["observacao"]
        if "numero_documento" in arguments:
            dados_conta["numero_documento"] = arguments["numero_documento"]
        
        # Validar e adicionar departamento
        if "codigo_departamento" in arguments:
            codigo_departamento = arguments["codigo_departamento"]
            departamento = await OmieCodeValidators.validar_codigo_departamento(codigo_departamento)
            if not departamento:
                return f"❌ Departamento {codigo_departamento} não encontrado"
            
            # Adicionar distribuição de departamento
            dados_conta["distribuicao"] = [{
                "cCodDep": codigo_departamento,
                "nPerc": 100.0,
                "nValor": float(valor_documento)
            }]
        
        # Incluir conta a pagar
        result = await omie_client.incluir_conta_pagar(dados_conta)
        
        # Formatar resposta
        return self.format_crud_response("inclusão de conta a pagar", result)

class AlterarContaPagarTool(CrudTool):
    """Ferramenta para alterar conta a pagar"""
    
    def get_name(self) -> str:
        return "alterar_conta_pagar"
    
    def get_description(self) -> str:
        return "Altera uma conta a pagar existente no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "codigo_lancamento_omie": {
                    "type": "string",
                    "description": "Código do lançamento no Omie (obrigatório para alteração)"
                },
                "data_vencimento": {
                    "type": "string",
                    "description": "Data de vencimento (DD/MM/YYYY)"
                },
                "valor_documento": {
                    "type": "number",
                    "description": "Valor do documento"
                },
                "codigo_categoria": {
                    "type": "string",
                    "description": "Código da categoria"
                },
                "observacao": {
                    "type": "string",
                    "description": "Observação sobre a conta"
                },
                "numero_documento": {
                    "type": "string",
                    "description": "Número do documento"
                },
                "codigo_departamento": {
                    "type": "string",
                    "description": "Código do departamento"
                }
            },
            "required": ["codigo_lancamento_omie"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Montar dados da conta a pagar
        dados_conta = {
            "codigo_lancamento_omie": arguments["codigo_lancamento_omie"]
        }
        
        # Validar e adicionar campos opcionais
        if "data_vencimento" in arguments:
            data_vencimento = arguments["data_vencimento"]
            if not OmieValidators.validar_data(data_vencimento):
                return "❌ Data de vencimento inválida. Use o formato DD/MM/YYYY"
            dados_conta["data_vencimento"] = data_vencimento
        
        if "valor_documento" in arguments:
            valor_documento = arguments["valor_documento"]
            if not OmieValidators.validar_valor(valor_documento):
                return "❌ Valor do documento deve ser um número positivo"
            dados_conta["valor_documento"] = float(valor_documento)
        
        if "codigo_categoria" in arguments:
            codigo_categoria = arguments["codigo_categoria"]
            categoria = await OmieCodeValidators.validar_codigo_categoria(codigo_categoria)
            if not categoria:
                return f"❌ Categoria {codigo_categoria} não encontrada"
            dados_conta["codigo_categoria"] = codigo_categoria
        
        if "observacao" in arguments:
            dados_conta["observacao"] = arguments["observacao"]
        
        if "numero_documento" in arguments:
            dados_conta["numero_documento"] = arguments["numero_documento"]
        
        # Validar e adicionar departamento
        if "codigo_departamento" in arguments:
            codigo_departamento = arguments["codigo_departamento"]
            departamento = await OmieCodeValidators.validar_codigo_departamento(codigo_departamento)
            if not departamento:
                return f"❌ Departamento {codigo_departamento} não encontrado"
            
            # Adicionar distribuição de departamento
            valor_documento = arguments.get("valor_documento", 0)
            dados_conta["distribuicao"] = [{
                "cCodDep": codigo_departamento,
                "nPerc": 100.0,
                "nValor": float(valor_documento) if valor_documento else None
            }]
        
        # Alterar conta a pagar
        result = await omie_client.alterar_conta_pagar(dados_conta)
        
        # Formatar resposta
        return self.format_crud_response("alteração de conta a pagar", result)

class ExcluirContaPagarTool(CrudTool):
    """Ferramenta para excluir conta a pagar"""
    
    def get_name(self) -> str:
        return "excluir_conta_pagar"
    
    def get_description(self) -> str:
        return "Exclui uma conta a pagar existente no Omie ERP"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "codigo_lancamento_omie": {
                    "type": "string",
                    "description": "Código do lançamento no Omie (obrigatório para exclusão)"
                }
            },
            "required": ["codigo_lancamento_omie"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        # Montar dados para exclusão
        dados_exclusao = {
            "codigo_lancamento_omie": arguments["codigo_lancamento_omie"]
        }
        
        # Excluir conta a pagar
        result = await omie_client.excluir_conta_pagar(dados_exclusao)
        
        # Formatar resposta
        return self.format_crud_response("exclusão de conta a pagar", result)