"""
Cliente HTTP para API do Nibo ERP
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp
from datetime import datetime

from .config import NiboConfig

logger = logging.getLogger("nibo-client")

class NiboClient:
    def __init__(self, config: Optional[NiboConfig] = None):
        self.config = config or NiboConfig()
        if not self.config.is_configured():
            raise ValueError("Credenciais do Nibo não configuradas")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """Faz requisição HTTP para a API do Nibo"""
        url = self.config.get_api_url(endpoint)
        headers = self.config.get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        # Adiciona API token nos parâmetros também (conforme documentação)
        if params is None:
            params = {}
        params["apitoken"] = self.config.api_token
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Erro na API Nibo: {response.status} - {error_text}")
                        raise Exception(f"Erro na API: {response.status} - {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão: {e}")
            raise Exception(f"Erro de conexão com a API Nibo: {e}")
    
    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================
    
    async def consultar_clientes(
        self, 
        skip: int = 0, 
        top: int = 50,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict:
        """Consulta clientes"""
        params = {
            "$top": min(top, 500)  # Máximo 500 conforme documentação
        }
        
        # API do Nibo exige $orderby quando usa $skip
        if skip > 0:
            params["$skip"] = skip
            params["$orderby"] = order_by or "name"
        elif order_by:
            params["$orderby"] = order_by
            
        if filter_expr:
            params["$filter"] = filter_expr
            
        return await self._make_request("GET", "clients", params=params)
    
    async def consultar_fornecedores(
        self, 
        skip: int = 0, 
        top: int = 50,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict:
        """Consulta fornecedores"""
        params = {
            "$top": min(top, 500)
        }
        
        # API do Nibo exige $orderby quando usa $skip
        if skip > 0:
            params["$skip"] = skip
            params["$orderby"] = order_by or "name"
        elif order_by:
            params["$orderby"] = order_by
            
        if filter_expr:
            params["$filter"] = filter_expr
            
        return await self._make_request("GET", "suppliers", params=params)
    
    async def consultar_contas_pagar(
        self, 
        skip: int = 0, 
        top: int = 50,
        order_by: Optional[str] = "dueDate",
        filter_expr: Optional[str] = None
    ) -> Dict:
        """Consulta contas a pagar (débitos)"""
        params = {
            "$skip": skip,
            "$top": min(top, 500),
            "$orderby": order_by
        }
        
        if filter_expr:
            params["$filter"] = filter_expr
            
        return await self._make_request("GET", "schedules/debit", params=params)
    
    async def consultar_contas_receber(
        self, 
        skip: int = 0, 
        top: int = 50,
        order_by: Optional[str] = "dueDate",
        filter_expr: Optional[str] = None
    ) -> Dict:
        """Consulta contas a receber (créditos)"""
        params = {
            "$skip": skip,
            "$top": min(top, 500),
            "$orderby": order_by
        }
        
        if filter_expr:
            params["$filter"] = filter_expr
            
        return await self._make_request("GET", "schedules/credit", params=params)
    
    async def consultar_categorias(
        self, 
        skip: int = 0, 
        top: int = 50
    ) -> Dict:
        """Consulta categorias"""
        params = {
            "$skip": skip,
            "$top": min(top, 500)
        }
        return await self._make_request("GET", "categories", params=params)
    
    async def consultar_centros_custo(
        self, 
        skip: int = 0, 
        top: int = 50
    ) -> Dict:
        """Consulta centros de custo"""
        params = {
            "$top": min(top, 500)
        }
        
        # API do Nibo exige $orderby quando usa $skip
        if skip > 0:
            params["$skip"] = skip
            params["$orderby"] = "name"
            
        return await self._make_request("GET", "costcenters", params=params)
    
    async def consultar_socios(
        self, 
        skip: int = 0, 
        top: int = 50,
        order_by: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict:
        """Consulta sócios (partners)"""
        params = {
            "$top": min(top, 500)
        }
        
        # API do Nibo exige $orderby quando usa $skip
        if skip > 0:
            params["$skip"] = skip
            params["$orderby"] = order_by or "name"
        elif order_by:
            params["$orderby"] = order_by
            
        if filter_expr:
            params["$filter"] = filter_expr
            
        return await self._make_request("GET", "partners", params=params)
    
    # ========================================================================
    # MÉTODOS DE CRIAÇÃO
    # ========================================================================
    
    async def incluir_cliente(self, dados_cliente: Dict) -> Dict:
        """Inclui um novo cliente"""
        return await self._make_request("POST", "clients", json_data=dados_cliente)
    
    async def incluir_fornecedor(self, dados_fornecedor: Dict) -> Dict:
        """Inclui um novo fornecedor"""
        return await self._make_request("POST", "suppliers", json_data=dados_fornecedor)
    
    async def incluir_conta_pagar(self, dados_conta: Dict) -> Dict:
        """Inclui uma nova conta a pagar"""
        return await self._make_request("POST", "schedules/debit", json_data=dados_conta)
    
    async def incluir_conta_receber(self, dados_conta: Dict) -> Dict:
        """Inclui uma nova conta a receber"""
        return await self._make_request("POST", "schedules/credit", json_data=dados_conta)
    
    async def incluir_socio(self, dados_socio: Dict) -> Dict:
        """Inclui um novo sócio"""
        return await self._make_request("POST", "partners", json_data=dados_socio)
    
    # ========================================================================
    # MÉTODOS DE ATUALIZAÇÃO
    # ========================================================================
    
    async def alterar_cliente(self, cliente_id: str, dados_cliente: Dict) -> Dict:
        """Altera um cliente existente"""
        return await self._make_request("PUT", f"clients/{cliente_id}", json_data=dados_cliente)
    
    async def alterar_fornecedor(self, fornecedor_id: str, dados_fornecedor: Dict) -> Dict:
        """Altera um fornecedor existente"""
        return await self._make_request("PUT", f"suppliers/{fornecedor_id}", json_data=dados_fornecedor)
    
    async def alterar_conta_pagar(self, conta_id: str, dados_conta: Dict) -> Dict:
        """Altera uma conta a pagar existente"""
        return await self._make_request("PUT", f"schedules/debit/{conta_id}", json_data=dados_conta)
    
    async def alterar_conta_receber(self, conta_id: str, dados_conta: Dict) -> Dict:
        """Altera uma conta a receber existente"""
        return await self._make_request("PUT", f"schedules/credit/{conta_id}", json_data=dados_conta)
    
    async def alterar_socio(self, socio_id: str, dados_socio: Dict) -> Dict:
        """Altera um sócio existente"""
        return await self._make_request("PUT", f"partners/{socio_id}", json_data=dados_socio)
    
    # ========================================================================
    # MÉTODOS DE EXCLUSÃO
    # ========================================================================
    
    async def excluir_cliente(self, cliente_id: str) -> Dict:
        """Exclui um cliente"""
        return await self._make_request("DELETE", f"clients/{cliente_id}")
    
    async def excluir_fornecedor(self, fornecedor_id: str) -> Dict:
        """Exclui um fornecedor"""
        return await self._make_request("DELETE", f"suppliers/{fornecedor_id}")
    
    async def excluir_conta_pagar(self, conta_id: str) -> Dict:
        """Exclui uma conta a pagar"""
        return await self._make_request("DELETE", f"schedules/debit/{conta_id}")
    
    async def excluir_conta_receber(self, conta_id: str) -> Dict:
        """Exclui uma conta a receber"""
        return await self._make_request("DELETE", f"schedules/credit/{conta_id}")
    
    async def excluir_socio(self, socio_id: str) -> Dict:
        """Exclui um sócio"""
        return await self._make_request("DELETE", f"partners/{socio_id}")
    
    # ========================================================================
    # MÉTODOS DE CONSULTA INDIVIDUAL
    # ========================================================================
    
    async def obter_socio_por_id(self, socio_id: str) -> Dict:
        """Obtém um sócio específico por ID"""
        return await self._make_request("GET", f"partners/{socio_id}")
    
    async def obter_cliente_por_id(self, cliente_id: str) -> Dict:
        """Obtém um cliente específico por ID"""
        return await self._make_request("GET", f"clients/{cliente_id}")
    
    async def obter_fornecedor_por_id(self, fornecedor_id: str) -> Dict:
        """Obtém um fornecedor específico por ID"""
        return await self._make_request("GET", f"suppliers/{fornecedor_id}")
    
    # ========================================================================
    # MÉTODO DE TESTE
    # ========================================================================
    
    async def testar_conexao(self) -> Dict:
        """Testa a conexão com a API"""
        try:
            # Tenta buscar as categorias como teste
            result = await self.consultar_categorias(top=1)
            return {
                "success": True,
                "message": "Conexão com API Nibo estabelecida com sucesso",
                "api_response": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao conectar com API Nibo: {str(e)}"
            }