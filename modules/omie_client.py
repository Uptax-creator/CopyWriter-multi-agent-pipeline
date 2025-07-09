"""
Cliente HTTP para comunicação com a API do Omie ERP
"""

import json
import logging
from typing import Dict, Any
import httpx
from fastapi import HTTPException


logger = logging.getLogger("omie-mcp-complete")


class OmieClient:
    """Cliente HTTP para comunicação com a API do Omie"""
    
    def __init__(self, app_key: str, app_secret: str, base_url: str = "https://app.omie.com.br/api/v1"):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = base_url
        
    async def _make_request(self, endpoint: str, call: str, params: Dict) -> Dict:
        """Faz requisição para a API do Omie"""
        
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        url = f"{self.base_url}/{endpoint}/"
        logger.info(f"📡 Requisição Omie: {endpoint}/{call}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"❌ Erro HTTP {response.status_code}: {error_text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Erro HTTP {response.status_code}: {error_text}"
                    )
                
                result = response.json()
                
                # Verificar se há erro do Omie
                if isinstance(result, dict) and "faultstring" in result:
                    error_msg = result.get("faultstring", "Erro Omie")
                    logger.error(f"❌ Erro Omie: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"Erro Omie: {error_msg}")
                
                logger.info(f"✅ Resposta Omie: Sucesso")
                return result
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro interno: {e}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
    
    # ========== MÉTODOS PRINCIPAIS ==========
    
    async def cadastrar_cliente_fornecedor(self, dados: Dict) -> Dict:
        """Cadastra cliente/fornecedor no Omie"""
        return await self._make_request("geral/clientes", "IncluirCliente", dados)
    
    async def criar_conta_pagar(self, dados: Dict) -> Dict:
        """Cria conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "IncluirContaPagar", dados)
    
    async def atualizar_conta_pagar(self, dados: Dict) -> Dict:
        """Atualiza conta a pagar no Omie"""
        return await self._make_request("financas/contapagar", "AlterarContaPagar", dados)
    
    async def criar_conta_receber(self, dados: Dict) -> Dict:
        """Cria conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "IncluirContaReceber", dados)
    
    async def atualizar_conta_receber(self, dados: Dict) -> Dict:
        """Atualiza conta a receber no Omie"""
        return await self._make_request("financas/contareceber", "AlterarContaReceber", dados)
    
    # ========== MÉTODOS DE CONSULTA ==========
    
    async def consultar_categorias(self, params: Dict = None) -> Dict:
        """Consulta categorias de receita/despesa"""
        if params is None:
            params = {"pagina": 1, "registros_por_pagina": 50}
        return await self._make_request("geral/categorias", "ListarCategorias", params)
    
    async def consultar_departamentos(self, params: Dict = None) -> Dict:
        """Consulta departamentos"""
        if params is None:
            params = {"pagina": 1, "registros_por_pagina": 50}
        return await self._make_request("geral/departamentos", "ListarDepartamentos", params)
    
    async def consultar_tipos_documento(self, params: Dict = None) -> Dict:
        """Consulta tipos de documentos"""
        if params is None:
            params = {"codigo": ""}
        return await self._make_request("geral/tiposdoc", "PesquisarTipoDocumento", params)
    
    async def consultar_contas_pagar(self, params: Dict) -> Dict:
        """Consulta contas a pagar com filtros"""
        return await self._make_request("financas/contapagar", "ListarContasPagar", params)
    
    async def consultar_contas_receber(self, params: Dict) -> Dict:
        """Consulta contas a receber com filtros"""
        return await self._make_request("financas/contareceber", "ListarContasReceber", params)
    
    async def consultar_cliente_fornecedor_por_cnpj(self, cnpj_cpf: str) -> Dict:
        """Consulta cliente/fornecedor por CNPJ/CPF (busca em todas as páginas)"""
        
        # Remover formatação do CNPJ para comparação
        cnpj_limpo = cnpj_cpf.replace(".", "").replace("/", "").replace("-", "")
        
        pagina = 1
        max_tentativas = 10  # Limitar tentativas para evitar loop infinito
        
        while pagina <= max_tentativas:
            try:
                params = {
                    "pagina": pagina,
                    "registros_por_pagina": 50,
                    "apenas_importado_api": "N"
                }
                
                resultado = await self._make_request("geral/clientes", "ListarClientes", params)
                
                clientes = resultado.get("clientes_cadastro", [])
                
                # Buscar cliente por CNPJ
                for cliente in clientes:
                    cliente_cnpj = cliente.get("cnpj_cpf", "").replace(".", "").replace("/", "").replace("-", "")
                    if cliente_cnpj == cnpj_limpo:
                        return {"clientes_cadastro": [cliente]}
                
                # Verificar se há mais páginas
                total_paginas = resultado.get("total_de_paginas", 1)
                if pagina >= total_paginas:
                    break
                    
                pagina += 1
                
            except HTTPException as e:
                # Se erro 500 (página não existe), parar busca
                if "Não existem registros para a página" in str(e.detail):
                    break
                raise
        
        # Cliente não encontrado
        return {"clientes_cadastro": []}