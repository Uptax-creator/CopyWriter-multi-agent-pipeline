"""
Ferramentas de gestão de sócios para o Nibo MCP Server
(Funcionalidade exclusiva do Nibo - não existe no Omie)
"""
from typing import Dict, Optional
from ..core.nibo_client import NiboClient

class NiboSocios:
    def __init__(self, client: NiboClient):
        self.client = client
    
    async def consultar_socios(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        filtrar_por_nome: Optional[str] = None,
        filtrar_por_documento: Optional[str] = None,
        filtrar_por_ativo: Optional[bool] = None
    ) -> Dict:
        """Consulta sócios no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        # Montar filtro OData
        filters = []
        if filtrar_por_nome:
            filters.append(f"contains(name, '{filtrar_por_nome}')")
        if filtrar_por_documento:
            filters.append(f"document eq '{filtrar_por_documento}'")
        if filtrar_por_ativo is not None:
            filters.append(f"active eq {str(filtrar_por_ativo).lower()}")
        
        filter_expr = " and ".join(filters) if filters else None
        
        return await self.client.consultar_socios(
            skip=skip,
            top=registros_por_pagina,
            filter_expr=filter_expr
        )
    
    async def incluir_socio(
        self,
        nome: str,
        documento: str,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        participacao_percentual: Optional[float] = None,
        ativo: bool = True,
        **kwargs
    ) -> Dict:
        """Inclui um novo sócio no Nibo"""
        dados_socio = {
            "name": nome,
            "document": documento,
            "active": ativo
        }
        
        if email:
            dados_socio["email"] = email
        if telefone:
            dados_socio["phone"] = telefone
        if endereco:
            dados_socio["address"] = endereco
        if participacao_percentual is not None:
            dados_socio["participationPercentage"] = participacao_percentual
            
        # Adicionar outros campos opcionais
        dados_socio.update(kwargs)
        
        return await self.client.incluir_socio(dados_socio)
    
    async def alterar_socio(
        self,
        socio_id: str,
        nome: Optional[str] = None,
        documento: Optional[str] = None,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        participacao_percentual: Optional[float] = None,
        ativo: Optional[bool] = None,
        **kwargs
    ) -> Dict:
        """Altera um sócio existente no Nibo"""
        dados_socio = {}
        
        if nome:
            dados_socio["name"] = nome
        if documento:
            dados_socio["document"] = documento
        if email:
            dados_socio["email"] = email
        if telefone:
            dados_socio["phone"] = telefone
        if endereco:
            dados_socio["address"] = endereco
        if participacao_percentual is not None:
            dados_socio["participationPercentage"] = participacao_percentual
        if ativo is not None:
            dados_socio["active"] = ativo
            
        # Adicionar outros campos opcionais
        dados_socio.update(kwargs)
        
        return await self.client.alterar_socio(socio_id, dados_socio)
    
    async def excluir_socio(self, socio_id: str) -> Dict:
        """Exclui um sócio do Nibo"""
        return await self.client.excluir_socio(socio_id)
    
    async def obter_socio_por_id(self, socio_id: str) -> Dict:
        """Obtém um sócio específico por ID"""
        return await self.client.obter_socio_por_id(socio_id)