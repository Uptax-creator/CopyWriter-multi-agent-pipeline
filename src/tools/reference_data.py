#!/usr/bin/env python3
"""
Ferramentas para consulta de dados de referência da API Omie
"""

import logging
from typing import Dict, Any, List

from ..core.client import OmieClient
from ..core.exceptions import OmieAPIError
from ..core.models import CategoriaResponse, DepartamentoResponse, TipoDocumentoRequest

logger = logging.getLogger("omie-reference-data")


class ReferenceDataTools:
    """Ferramentas para consulta de dados de referência"""
    
    def __init__(self, client: OmieClient):
        self.client = client
    
    async def consultar_categorias(self) -> List[CategoriaResponse]:
        """
        Consulta categorias de receita e despesa
        
        Returns:
            Lista de categorias
        """
        try:
            logger.info("🔍 Consultando categorias...")
            
            result = await self.client.make_request(
                endpoint="geral/categorias/",
                call="ListarCategorias",
                param={}
            )
            
            if "categoria_cadastro" in result:
                categorias = []
                for cat in result["categoria_cadastro"]:
                    categorias.append(CategoriaResponse(
                        codigo=cat.get("codigo", ""),
                        descricao=cat.get("descricao", ""),
                        tipo=cat.get("tipo", "")
                    ))
                
                logger.info(f"✅ {len(categorias)} categorias encontradas")
                return categorias
            
            logger.warning("⚠️ Nenhuma categoria encontrada")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar categorias: {str(e)}")
            raise OmieAPIError("CATEGORIA_ERROR", f"Erro ao consultar categorias: {str(e)}")
    
    async def consultar_departamentos(self) -> List[DepartamentoResponse]:
        """
        Consulta departamentos
        
        Returns:
            Lista de departamentos
        """
        try:
            logger.info("🔍 Consultando departamentos...")
            
            result = await self.client.make_request(
                endpoint="geral/departamentos/",
                call="ListarDepartamentos",
                param={}
            )
            
            if "departamento_cadastro" in result:
                departamentos = []
                for dep in result["departamento_cadastro"]:
                    departamentos.append(DepartamentoResponse(
                        codigo=dep.get("codigo", ""),
                        descricao=dep.get("descricao", "")
                    ))
                
                logger.info(f"✅ {len(departamentos)} departamentos encontrados")
                return departamentos
            
            logger.warning("⚠️ Nenhum departamento encontrado")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar departamentos: {str(e)}")
            raise OmieAPIError("DEPARTAMENTO_ERROR", f"Erro ao consultar departamentos: {str(e)}")
    
    async def consultar_tipos_documento(self, request: TipoDocumentoRequest) -> List[Dict[str, Any]]:
        """
        Consulta tipos de documento
        
        Args:
            request: Parâmetros da consulta
            
        Returns:
            Lista de tipos de documento
        """
        try:
            logger.info("🔍 Consultando tipos de documento...")
            
            param = {
                "filtrar_apenas_ativo": request.filtrar_apenas_ativo,
                "filtrar_por_codigo": request.filtrar_por_codigo
            }
            
            result = await self.client.make_request(
                endpoint="geral/tipodoc/",
                call="ListarTiposDocumento",
                param=param
            )
            
            if "tipos_documento" in result:
                tipos = result["tipos_documento"]
                logger.info(f"✅ {len(tipos)} tipos de documento encontrados")
                return tipos
            
            logger.warning("⚠️ Nenhum tipo de documento encontrado")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar tipos de documento: {str(e)}")
            raise OmieAPIError("TIPO_DOC_ERROR", f"Erro ao consultar tipos de documento: {str(e)}")
    
    async def pesquisar_tipos_documento(self, codigo: str = "") -> List[Dict[str, Any]]:
        """
        Pesquisa tipos de documento (versão alternativa)
        
        Args:
            codigo: Código para filtrar
            
        Returns:
            Lista de tipos de documento
        """
        try:
            logger.info("🔍 Pesquisando tipos de documento...")
            
            param = {
                "filtrar_apenas_ativo": "S",
                "filtrar_por_codigo": codigo
            }
            
            result = await self.client.make_request(
                endpoint="geral/tipodoc/",
                call="PesquisarTiposDocumento",
                param=param
            )
            
            if "tipos_documento" in result:
                tipos = result["tipos_documento"]
                logger.info(f"✅ {len(tipos)} tipos de documento encontrados")
                return tipos
            
            logger.warning("⚠️ Nenhum tipo de documento encontrado")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao pesquisar tipos de documento: {str(e)}")
            raise OmieAPIError("TIPO_DOC_SEARCH_ERROR", f"Erro ao pesquisar tipos de documento: {str(e)}")


# Instância global para uso nas ferramentas MCP
reference_tools = None

def get_reference_tools() -> ReferenceDataTools:
    """Obtém instância das ferramentas de dados de referência"""
    global reference_tools
    if reference_tools is None:
        client = OmieClient()
        reference_tools = ReferenceDataTools(client)
    return reference_tools