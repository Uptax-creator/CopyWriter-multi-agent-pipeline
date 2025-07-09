"""
Validadores para dados do Omie ERP
"""

import re
from typing import Optional, Dict, Any, List
from src.client.omie_client import omie_client
from src.utils.logger import logger

class ValidationError(Exception):
    """Exceção para erros de validação"""
    pass

class OmieValidators:
    """Classe para validações específicas do Omie"""
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """Validar formato do CNPJ"""
        if not cnpj:
            return False
        
        # Remove caracteres especiais
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verifica se todos os dígitos são iguais
        if len(set(cnpj)) == 1:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cnpj_parcial: str, pesos: List[int]) -> int:
            soma = sum(int(d) * p for d, p in zip(cnpj_parcial, pesos))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito1 = calcular_digito(cnpj[:12], pesos1)
        
        # Segundo dígito
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = calcular_digito(cnpj[:13], pesos2)
        
        return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Validar formato do CPF"""
        if not cpf:
            return False
        
        # Remove caracteres especiais
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial: str, multiplicador: int) -> int:
            soma = sum(int(d) * (multiplicador - i) for i, d in enumerate(cpf_parcial))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito
        digito1 = calcular_digito(cpf[:9], 10)
        
        # Segundo dígito
        digito2 = calcular_digito(cpf[:10], 11)
        
        return cpf[9] == str(digito1) and cpf[10] == str(digito2)
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Validar formato do email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Validar formato do telefone"""
        if not telefone:
            return False
        
        # Remove caracteres especiais
        telefone = re.sub(r'[^0-9]', '', telefone)
        
        # Verifica se tem entre 10 e 11 dígitos
        return len(telefone) in [10, 11]
    
    @staticmethod
    def validar_cep(cep: str) -> bool:
        """Validar formato do CEP"""
        if not cep:
            return False
        
        # Remove caracteres especiais
        cep = re.sub(r'[^0-9]', '', cep)
        
        # Verifica se tem 8 dígitos
        return len(cep) == 8
    
    @staticmethod
    def validar_valor(valor: Any) -> bool:
        """Validar se o valor é um número positivo"""
        try:
            float_valor = float(valor)
            return float_valor >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_data(data: str) -> bool:
        """Validar formato da data DD/MM/YYYY"""
        if not data:
            return False
        
        pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(pattern, data):
            return False
        
        try:
            dia, mes, ano = map(int, data.split('/'))
            
            # Validações básicas
            if mes < 1 or mes > 12:
                return False
            
            if dia < 1 or dia > 31:
                return False
            
            if ano < 1900 or ano > 2100:
                return False
            
            # Validação específica por mês
            dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            
            # Ano bissexto
            if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                dias_por_mes[1] = 29
            
            return dia <= dias_por_mes[mes - 1]
            
        except ValueError:
            return False

class OmieCodeValidators:
    """Validadores para códigos do Omie"""
    
    @staticmethod
    async def validar_codigo_categoria(codigo: str) -> Optional[str]:
        """Validar se o código da categoria existe"""
        if not codigo:
            return None
        
        try:
            resultado = await omie_client.consultar_categorias({
                "pagina": 1,
                "registros_por_pagina": 100
            })
            
            categorias = resultado.get("categoria_cadastro", [])
            
            for categoria in categorias:
                if categoria.get("codigo") == codigo:
                    return categoria.get("descricao", "N/A")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar categoria {codigo}: {e}")
            return None
    
    @staticmethod
    async def validar_codigo_departamento(codigo: str) -> Optional[str]:
        """Validar se o código do departamento existe"""
        if not codigo:
            return None
        
        try:
            resultado = await omie_client.consultar_departamentos({
                "pagina": 1,
                "registros_por_pagina": 100
            })
            
            departamentos = resultado.get("departamentos", [])
            
            for departamento in departamentos:
                if departamento.get("codigo") == codigo:
                    return departamento.get("descricao", "N/A")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar departamento {codigo}: {e}")
            return None
    
    @staticmethod
    async def validar_codigo_tipo_documento(codigo: str) -> Optional[str]:
        """Validar se o código do tipo de documento existe"""
        if not codigo:
            return None
        
        try:
            resultado = await omie_client.consultar_tipos_documento({
                "filtrar_por_codigo": codigo
            })
            
            tipos = resultado.get("tipos_documento_cadastro", [])
            
            for tipo in tipos:
                if tipo.get("codigo") == codigo:
                    return tipo.get("descricao", "N/A")
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar tipo documento {codigo}: {e}")
            return None
    
    @staticmethod
    async def validar_cnpj_cliente(cnpj: str) -> Optional[Dict[str, Any]]:
        """Validar se o CNPJ existe como cliente"""
        if not cnpj or not OmieValidators.validar_cnpj(cnpj):
            return None
        
        try:
            resultado = await omie_client.consultar_clientes({
                "cnpj_cpf": cnpj
            })
            
            clientes = resultado.get("clientes_cadastro", [])
            
            if clientes:
                return clientes[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar cliente {cnpj}: {e}")
            return None
    
    @staticmethod
    async def validar_cnpj_fornecedor(cnpj: str) -> Optional[Dict[str, Any]]:
        """Validar se o CNPJ existe como fornecedor"""
        if not cnpj or not OmieValidators.validar_cnpj(cnpj):
            return None
        
        try:
            resultado = await omie_client.consultar_fornecedores({
                "cnpj_cpf": cnpj
            })
            
            fornecedores = resultado.get("fornecedor_cadastro", [])
            
            if fornecedores:
                return fornecedores[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar fornecedor {cnpj}: {e}")
            return None