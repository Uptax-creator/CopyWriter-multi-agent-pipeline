"""
🔐 Cliente HTTP para API Omie com Universal Credentials Manager
Versão integrada que obtém credenciais do UCM em vez de credentials.json
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from src.client.ucm_credentials_client import ucm_client
from src.utils.logger import logger

class OmieClientUCM:
    """Cliente HTTP para comunicação com a API Omie via UCM"""
    
    def __init__(self):
        self.timeout = 30
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Credenciais serão obtidas dinamicamente do UCM
        self._credentials = None
        
        logger.info("🔐 OmieClientUCM inicializado")
    
    async def _ensure_credentials(self):
        """Garantir que as credenciais estão disponíveis"""
        if not self._credentials:
            self._credentials = await ucm_client.get_credentials()
            logger.debug("🔄 Credenciais UCM carregadas")
    
    async def _make_request(self, endpoint: str, call: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """Fazer requisição para a API Omie usando credenciais UCM"""
        
        # Garantir credenciais
        await self._ensure_credentials()
        
        url = f"{self._credentials['base_url']}/{endpoint}"
        
        payload = [
            {
                "call": call,
                "app_key": self._credentials["app_key"],
                "app_secret": self._credentials["app_secret"],
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
            
            # Se erro de autenticação, tentar refresh das credenciais
            if e.response.status_code in [401, 403]:
                logger.warning("🔄 Erro de autenticação, refreshing credenciais UCM...")
                self._credentials = await ucm_client.refresh_credentials()
                raise Exception(f"Erro de autenticação - credenciais atualizadas, tente novamente")
            
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
    
    async def consultar_cliente_por_codigo(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar cliente por código"""
        return await self._make_request("geral/clientes/", "ConsultarCliente", param)
    
    async def consultar_fornecedor_por_codigo(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Consultar fornecedor por código"""
        return await self._make_request("geral/fornecedores/", "ConsultarFornecedor", param)
    
    async def buscar_dados_contato_cliente(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar dados de contato do cliente"""
        return await self._make_request("geral/clientes/", "ConsultarCliente", param)
    
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
    
    # ============================================================================
    # MÉTODOS AUXILIARES UCM
    # ============================================================================
    
    async def test_ucm_connection(self) -> bool:
        """Testar conexão com UCM"""
        return await ucm_client.test_connection()
    
    async def list_available_companies(self) -> list:
        """Listar empresas disponíveis no UCM"""
        return await ucm_client.list_companies()
    
    async def switch_company(self, company_key: str):
        """Trocar empresa ativa"""
        ucm_client.set_company(company_key)
        self._credentials = None  # Forçar reload das credenciais
        logger.info(f"🏢 Empresa alterada para: {company_key}")
    
    async def get_current_credentials_info(self) -> Dict[str, Any]:
        """Obter informações das credenciais atuais (sem dados sensíveis)"""
        await self._ensure_credentials()
        
        return {
            "base_url": self._credentials["base_url"],
            "has_app_key": bool(self._credentials.get("app_key")),
            "has_app_secret": bool(self._credentials.get("app_secret")),
            "company_key": ucm_client.company_key,
            "project_name": ucm_client.project_name
        }

# Instância global do cliente UCM
omie_client_ucm = OmieClientUCM()