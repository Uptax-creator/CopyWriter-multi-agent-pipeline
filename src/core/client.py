#!/usr/bin/env python3
"""
Cliente base para comunicação com a API Omie
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("omie-client")


class OmieClient:
    """Cliente para comunicação com a API Omie"""
    
    def __init__(self):
        self.app_key = os.getenv("OMIE_APP_KEY")
        self.app_secret = os.getenv("OMIE_APP_SECRET")
        self.base_url = "https://app.omie.com.br/api/v1"
        
        if not self.app_key or not self.app_secret:
            logger.error("❌ ERRO: Configure as variáveis de ambiente OMIE_APP_KEY e OMIE_APP_SECRET")
            sys.exit(1)
    
    async def make_request(self, endpoint: str, call: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para a API Omie
        
        Args:
            endpoint: Endpoint da API (ex: "geral/clientes/")
            call: Ação a ser executada (ex: "IncluirCliente")
            param: Parâmetros da requisição
            
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/{endpoint}"
        
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"📤 Requisição para {url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Resposta recebida: {response.status_code}")
                logger.debug(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Erro HTTP {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """Testa conexão com a API Omie"""
        try:
            await self.make_request("geral/categorias/", "ListarCategorias", {})
            logger.info("✅ Conexão com API Omie OK")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {str(e)}")
            return False