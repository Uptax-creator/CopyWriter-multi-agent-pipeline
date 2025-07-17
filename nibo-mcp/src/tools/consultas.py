"""
Ferramentas de consulta para o Nibo MCP Server
"""
from typing import Dict, Optional
from ..core.nibo_client import NiboClient

class NiboConsultas:
    def __init__(self, client: NiboClient):
        self.client = client
    
    async def consultar_clientes(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        filtrar_por_nome: Optional[str] = None,
        filtrar_por_documento: Optional[str] = None
    ) -> Dict:
        """Consulta clientes no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        # Montar filtro OData
        filters = []
        if filtrar_por_nome:
            filters.append(f"contains(name, '{filtrar_por_nome}')")
        if filtrar_por_documento:
            filters.append(f"document eq '{filtrar_por_documento}'")
        
        filter_expr = " and ".join(filters) if filters else None
        
        return await self.client.consultar_clientes(
            skip=skip,
            top=registros_por_pagina,
            filter_expr=filter_expr
        )
    
    async def consultar_fornecedores(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        filtrar_por_nome: Optional[str] = None,
        filtrar_por_documento: Optional[str] = None
    ) -> Dict:
        """Consulta fornecedores no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        filters = []
        if filtrar_por_nome:
            filters.append(f"contains(name, '{filtrar_por_nome}')")
        if filtrar_por_documento:
            filters.append(f"document eq '{filtrar_por_documento}'")
        
        filter_expr = " and ".join(filters) if filters else None
        
        return await self.client.consultar_fornecedores(
            skip=skip,
            top=registros_por_pagina,
            filter_expr=filter_expr
        )
    
    async def consultar_contas_pagar(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        filtrar_por_valor_maximo: Optional[float] = None,
        filtrar_por_data_vencimento_inicial: Optional[str] = None,
        filtrar_por_data_vencimento_final: Optional[str] = None
    ) -> Dict:
        """Consulta contas a pagar no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        filters = []
        if filtrar_por_valor_maximo:
            filters.append(f"value le {filtrar_por_valor_maximo}")
        if filtrar_por_data_vencimento_inicial:
            filters.append(f"dueDate ge datetime'{filtrar_por_data_vencimento_inicial}T00:00:00'")
        if filtrar_por_data_vencimento_final:
            filters.append(f"dueDate le datetime'{filtrar_por_data_vencimento_final}T23:59:59'")
        
        filter_expr = " and ".join(filters) if filters else None
        
        return await self.client.consultar_contas_pagar(
            skip=skip,
            top=registros_por_pagina,
            filter_expr=filter_expr
        )
    
    async def consultar_contas_receber(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        filtrar_por_valor_maximo: Optional[float] = None,
        filtrar_por_data_vencimento_inicial: Optional[str] = None,
        filtrar_por_data_vencimento_final: Optional[str] = None
    ) -> Dict:
        """Consulta contas a receber no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        filters = []
        if filtrar_por_valor_maximo:
            filters.append(f"value le {filtrar_por_valor_maximo}")
        if filtrar_por_data_vencimento_inicial:
            filters.append(f"dueDate ge datetime'{filtrar_por_data_vencimento_inicial}T00:00:00'")
        if filtrar_por_data_vencimento_final:
            filters.append(f"dueDate le datetime'{filtrar_por_data_vencimento_final}T23:59:59'")
        
        filter_expr = " and ".join(filters) if filters else None
        
        return await self.client.consultar_contas_receber(
            skip=skip,
            top=registros_por_pagina,
            filter_expr=filter_expr
        )
    
    async def consultar_categorias(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50
    ) -> Dict:
        """Consulta categorias no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        return await self.client.consultar_categorias(
            skip=skip,
            top=registros_por_pagina
        )
    
    async def consultar_centros_custo(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50
    ) -> Dict:
        """Consulta centros de custo no Nibo"""
        skip = (pagina - 1) * registros_por_pagina
        
        return await self.client.consultar_centros_custo(
            skip=skip,
            top=registros_por_pagina
        )