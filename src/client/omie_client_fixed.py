"""
Cliente HTTP para API Omie - Versão corrigida para resolver erro 500 SOAP
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from src.config import config
from src.utils.logger import logger

class OmieClientFixed:
    """Cliente HTTP corrigido para comunicação com a API Omie"""
    
    def __init__(self):
        self.base_url = config.omie_base_url
        self.timeout = config.omie_timeout
        self.headers = config.get_omie_headers()
        self.auth = config.get_omie_auth()
    
    async def _make_request(self, endpoint: str, call: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """Fazer requisição para a API Omie com correções para erro 500"""
        # Corrigir URL - remover barra dupla e garantir formato correto
        url = f"{self.base_url}/{endpoint.rstrip('/')}"
        
        # Payload NO FORMATO CORRETO da API Omie (não é array!)
        payload = {
            "call": call,
            "app_key": self.auth["app_key"],
            "app_secret": self.auth["app_secret"],
            "param": [param]  # Este deve ser um array
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"🔗 POST {url}")
                logger.debug(f"📤 Call: {call}")
                logger.debug(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                
                response = await client.post(url, json=payload, headers=self.headers)
                
                # Log da resposta para debugging
                logger.debug(f"📥 Status: {response.status_code}")
                logger.debug(f"📥 Headers: {dict(response.headers)}")
                
                response_text = await response.aread()
                logger.debug(f"📥 Response: {response_text.decode()}")
                
                # Verificar se houve erro HTTP
                if response.status_code != 200:
                    error_msg = f"Erro HTTP {response.status_code}: {response_text.decode()}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # Tentar decodificar JSON
                try:
                    result = response.json()
                    logger.debug(f"✅ Resposta decodificada: {result}")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao decodificar JSON: {e}")
                    logger.error(f"❌ Resposta bruta: {response_text.decode()}")
                    raise Exception(f"Erro ao decodificar JSON: {e}")
                    
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout na requisição para {call}")
            raise Exception(f"Timeout na requisição para {call}")
        except httpx.HTTPStatusError as e:
            logger.error(f"🚨 Erro HTTP {e.response.status_code} em {call}: {e.response.text}")
            raise Exception(f"Erro HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"💥 Erro na requisição {call}: {str(e)}")
            raise Exception(f"Erro na requisição {call}: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE CONSULTA (FUNCIONAM)
    # ============================================================================
    
    async def consultar_categorias(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar categorias"""
        return await self._make_request("geral/categorias", "ListarCategorias", param)
    
    async def consultar_departamentos(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar departamentos"""
        return await self._make_request("geral/departamentos", "ListarDepartamentos", param)
    
    async def consultar_tipos_documento(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar tipos de documento"""
        return await self._make_request("geral/tpdoc", "PesquisarTipoDocumento", param)
    
    async def consultar_contas_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar contas a pagar"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", param)
    
    async def consultar_contas_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar contas a receber"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", param)
    
    async def consultar_clientes(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar clientes"""
        return await self._make_request("geral/clientes", "ListarClientes", param)
    
    async def consultar_fornecedores(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar fornecedores"""
        return await self._make_request("geral/fornecedores", "ListarFornecedores", param)
    
    # ============================================================================
    # MÉTODOS DE CRIAÇÃO (CORRIGIDOS)
    # ============================================================================
    
    async def incluir_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir cliente - VERSÃO CORRIGIDA"""
        # Limpar e validar dados antes de enviar
        dados_limpos = self._limpar_dados_cliente(param)
        logger.info(f"🔧 Incluindo cliente: {dados_limpos}")
        
        return await self._make_request("geral/clientes", "IncluirCliente", dados_limpos)
    
    async def incluir_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir fornecedor - VERSÃO CORRIGIDA"""
        # Limpar e validar dados antes de enviar
        dados_limpos = self._limpar_dados_fornecedor(param)
        logger.info(f"🔧 Incluindo fornecedor: {dados_limpos}")
        
        return await self._make_request("geral/fornecedores", "IncluirFornecedor", dados_limpos)
    
    async def incluir_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir conta a pagar"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", param)
    
    async def incluir_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir conta a receber"""
        return await self._make_request("financas/contareceber", "IncluirContaReceber", param)
    
    # ============================================================================
    # MÉTODOS DE ATUALIZAÇÃO
    # ============================================================================
    
    async def alterar_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar cliente"""
        return await self._make_request("geral/clientes", "AlterarCliente", param)
    
    async def alterar_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar fornecedor"""
        return await self._make_request("geral/fornecedores", "AlterarFornecedor", param)
    
    async def alterar_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar conta a pagar"""
        return await self._make_request("financas/contapagar", "AlterarContaPagar", param)
    
    async def alterar_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar conta a receber"""
        return await self._make_request("financas/contareceber", "AlterarContaReceber", param)
    
    # ============================================================================
    # MÉTODOS DE EXCLUSÃO
    # ============================================================================
    
    async def excluir_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir cliente"""
        return await self._make_request("geral/clientes", "ExcluirCliente", param)
    
    async def excluir_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir fornecedor"""
        return await self._make_request("geral/fornecedores", "ExcluirFornecedor", param)
    
    async def excluir_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir conta a pagar"""
        return await self._make_request("financas/contapagar", "ExcluirContaPagar", param)
    
    async def excluir_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir conta a receber"""
        return await self._make_request("financas/contareceber", "ExcluirContaReceber", param)
    
    # ============================================================================
    # MÉTODOS DE LIMPEZA DE DADOS
    # ============================================================================
    
    def _limpar_dados_cliente(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Limpar e validar dados do cliente"""
        dados_limpos = {}
        
        # Campos obrigatórios
        if "cnpj_cpf" in dados:
            dados_limpos["cnpj_cpf"] = str(dados["cnpj_cpf"]).replace(".", "").replace("/", "").replace("-", "")
        
        if "razao_social" in dados:
            dados_limpos["razao_social"] = str(dados["razao_social"]).strip()
        
        # Campos opcionais
        campos_opcionais = [
            "nome_fantasia", "email", "telefone1_numero", "telefone1_ddd",
            "endereco", "numero", "complemento", "bairro", "cidade", "estado", "cep",
            "codigo_cliente_integracao", "observacoes"
        ]
        
        for campo in campos_opcionais:
            if campo in dados and dados[campo]:
                dados_limpos[campo] = str(dados[campo]).strip()
        
        # Definir como cliente por padrão
        dados_limpos["cliente_fornecedor"] = "C"
        
        return dados_limpos
    
    def _limpar_dados_fornecedor(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Limpar e validar dados do fornecedor"""
        dados_limpos = {}
        
        # Campos obrigatórios
        if "cnpj_cpf" in dados:
            dados_limpos["cnpj_cpf"] = str(dados["cnpj_cpf"]).replace(".", "").replace("/", "").replace("-", "")
        
        if "razao_social" in dados:
            dados_limpos["razao_social"] = str(dados["razao_social"]).strip()
        
        # Campos opcionais
        campos_opcionais = [
            "nome_fantasia", "email", "telefone1_numero", "telefone1_ddd",
            "endereco", "numero", "complemento", "bairro", "cidade", "estado", "cep",
            "codigo_fornecedor_integracao", "observacoes"
        ]
        
        for campo in campos_opcionais:
            if campo in dados and dados[campo]:
                dados_limpos[campo] = str(dados[campo]).strip()
        
        # Definir como fornecedor por padrão
        dados_limpos["cliente_fornecedor"] = "F"
        
        return dados_limpos

# Instância global do cliente corrigido
omie_client_fixed = OmieClientFixed()