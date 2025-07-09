"""
Cliente HTTP para API Omie
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from src.config import config
from src.utils.logger import logger

class OmieClient:
    """Cliente HTTP para comunicação com a API Omie"""
    
    def __init__(self):
        self.base_url = config.omie_base_url
        self.timeout = config.omie_timeout
        self.headers = config.get_omie_headers()
        self.auth = config.get_omie_auth()
    
    async def _make_request(self, endpoint: str, call: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """Fazer requisição para a API Omie"""
        url = f"{self.base_url}/{endpoint}"
        
        payload = [
            {
                "call": call,
                "app_key": self.auth["app_key"],
                "app_secret": self.auth["app_secret"],
                "param": [param]
            }
        ]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"POST {url} - {call}")
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Resposta: {result}")
                
                if result and len(result) > 0:
                    return result[0]
                else:
                    return {}
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout na requisição para {call}")
            raise Exception(f"Timeout na requisição para {call}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code} em {call}: {e.response.text}")
            raise Exception(f"Erro HTTP {e.response.status_code}: {e.response.text}")
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON em {call}")
            raise Exception("Erro ao decodificar resposta JSON")
        except Exception as e:
            logger.error(f"Erro na requisição {call}: {str(e)}")
            raise Exception(f"Erro na requisição {call}: {str(e)}")
    
    # ============================================================================
    # MÉTODOS DE CONSULTA
    # ============================================================================
    
    async def consultar_categorias(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar categorias"""
        return await self._make_request("geral/categorias/", "ListarCategorias", param)
    
    async def consultar_departamentos(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar departamentos"""
        return await self._make_request("geral/departamentos/", "ListarDepartamentos", param)
    
    async def consultar_tipos_documento(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar tipos de documento"""
        return await self._make_request("geral/tpdoc/", "PesquisarTipoDocumento", param)
    
    async def consultar_contas_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar contas a pagar"""
        return await self._make_request("financas/contapagar/", "ListarContasPagar", param)
    
    async def consultar_contas_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar contas a receber"""
        return await self._make_request("financas/contareceber/", "ListarContasReceber", param)
    
    async def consultar_clientes(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar clientes"""
        return await self._make_request("geral/clientes/", "ListarClientes", param)
    
    async def consultar_fornecedores(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar fornecedores"""
        return await self._make_request("geral/fornecedores/", "ListarFornecedores", param)
    
    # ============================================================================
    # MÉTODOS DE CRIAÇÃO
    # ============================================================================
    
    async def incluir_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir cliente"""
        return await self._make_request("geral/clientes/", "IncluirCliente", param)
    
    async def incluir_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir fornecedor"""
        return await self._make_request("geral/fornecedores/", "IncluirFornecedor", param)
    
    async def incluir_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir conta a pagar"""
        return await self._make_request("financas/contapagar/", "IncluirContaPagar", param)
    
    async def incluir_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Incluir conta a receber"""
        return await self._make_request("financas/contareceber/", "IncluirContaReceber", param)
    
    # ============================================================================
    # MÉTODOS DE ATUALIZAÇÃO
    # ============================================================================
    
    async def alterar_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar cliente"""
        return await self._make_request("geral/clientes/", "AlterarCliente", param)
    
    async def alterar_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar fornecedor"""
        return await self._make_request("geral/fornecedores/", "AlterarFornecedor", param)
    
    async def alterar_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar conta a pagar"""
        return await self._make_request("financas/contapagar/", "AlterarContaPagar", param)
    
    async def alterar_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Alterar conta a receber"""
        return await self._make_request("financas/contareceber/", "AlterarContaReceber", param)
    
    # ============================================================================
    # MÉTODOS DE EXCLUSÃO
    # ============================================================================
    
    async def excluir_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir cliente"""
        return await self._make_request("geral/clientes/", "ExcluirCliente", param)
    
    async def excluir_fornecedor(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir fornecedor"""
        return await self._make_request("geral/fornecedores/", "ExcluirFornecedor", param)
    
    async def excluir_conta_pagar(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir conta a pagar"""
        return await self._make_request("financas/contapagar/", "ExcluirContaPagar", param)
    
    async def excluir_conta_receber(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Excluir conta a receber"""
        return await self._make_request("financas/contareceber/", "ExcluirContaReceber", param)

# Instância global do cliente
omie_client = OmieClient()