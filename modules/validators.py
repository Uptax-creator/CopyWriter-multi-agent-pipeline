"""
Validadores para códigos do Omie ERP
"""

import logging
from typing import Optional
from .omie_client import OmieClient


logger = logging.getLogger("omie-mcp-complete")


class OmieValidators:
    """Validadores para códigos do Omie ERP"""
    
    def __init__(self, omie_client: OmieClient):
        self.omie_client = omie_client
    
    async def validar_codigo_categoria(self, codigo: str) -> Optional[str]:
        """Valida se o código da categoria existe"""
        try:
            resultado = await self.omie_client.consultar_categorias({"pagina": 1, "registros_por_pagina": 200})
            categorias = resultado.get("categoria_cadastro", [])
            
            for categoria in categorias:
                if categoria.get("codigo") == codigo:
                    return categoria.get("descricao", "N/A")
            
            return None
        except:
            return None

    async def validar_codigo_departamento(self, codigo: str) -> Optional[str]:
        """Valida se o código do departamento existe"""
        try:
            resultado = await self.omie_client.consultar_departamentos({"pagina": 1, "registros_por_pagina": 100})
            departamentos = resultado.get("departamentos", [])
            
            for departamento in departamentos:
                if departamento.get("codigo") == codigo:
                    return departamento.get("descricao", "N/A")
            
            return None
        except:
            return None

    async def validar_codigo_tipo_documento(self, codigo: str) -> Optional[str]:
        """Valida se o código do tipo de documento existe"""
        try:
            resultado = await self.omie_client.consultar_tipos_documento()
            tipos = resultado.get("tipo_documento_cadastro", [])
            
            for tipo in tipos:
                if tipo.get("codigo") == codigo:
                    return tipo.get("descricao", "N/A")
            
            return None
        except:
            return None
    
    async def validar_codigos_obrigatorios(self, args: dict) -> list:
        """Valida todos os códigos obrigatórios e retorna lista de erros"""
        validacoes_codigo = []
        
        # Validar categoria
        if args.get("codigo_categoria"):
            categoria_desc = await self.validar_codigo_categoria(args["codigo_categoria"])
            if categoria_desc is None:
                validacoes_codigo.append(f"• Categoria '{args['codigo_categoria']}' não encontrada")
        
        # Validar departamento
        if args.get("codigo_departamento"):
            departamento_desc = await self.validar_codigo_departamento(args["codigo_departamento"])
            if departamento_desc is None:
                validacoes_codigo.append(f"• Departamento '{args['codigo_departamento']}' não encontrado")
        
        # Validar tipo documento
        if args.get("codigo_tipo_documento"):
            tipo_doc_desc = await self.validar_codigo_tipo_documento(args["codigo_tipo_documento"])
            if tipo_doc_desc is None:
                validacoes_codigo.append(f"• Tipo documento '{args['codigo_tipo_documento']}' não encontrado")
        
        return validacoes_codigo
    
    def formatar_erro_validacao(self, validacoes_codigo: list) -> str:
        """Formata mensagem de erro para códigos inválidos"""
        return f"""❌ Erro: Códigos inválidos:

{chr(10).join(validacoes_codigo)}

💡 Use as ferramentas de consulta para obter códigos válidos:
• consultar_categorias - Para códigos de categoria
• consultar_departamentos - Para códigos de departamento
• consultar_tipos_documento - Para códigos de tipo de documento"""