"""
Ferramentas de gestão de clientes e fornecedores para o Nibo MCP Server
"""
from typing import Dict, Optional
from ..core.nibo_client import NiboClient

class NiboClientesFornecedores:
    def __init__(self, client: NiboClient):
        self.client = client
    
    async def incluir_cliente(
        self,
        nome: str,
        documento: str,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Inclui um novo cliente no Nibo"""
        dados_cliente = {
            "name": nome,
            "document": documento
        }
        
        if email:
            dados_cliente["email"] = email
        if telefone:
            dados_cliente["phone"] = telefone
        if endereco:
            dados_cliente["address"] = endereco
            
        # Adicionar outros campos opcionais
        dados_cliente.update(kwargs)
        
        return await self.client.incluir_cliente(dados_cliente)
    
    async def incluir_fornecedor(
        self,
        nome: str,
        documento: str,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Inclui um novo fornecedor no Nibo"""
        dados_fornecedor = {
            "name": nome,
            "document": documento
        }
        
        if email:
            dados_fornecedor["email"] = email
        if telefone:
            dados_fornecedor["phone"] = telefone
        if endereco:
            dados_fornecedor["address"] = endereco
            
        # Adicionar outros campos opcionais
        dados_fornecedor.update(kwargs)
        
        return await self.client.incluir_fornecedor(dados_fornecedor)
    
    async def alterar_cliente(
        self,
        cliente_id: str,
        nome: Optional[str] = None,
        documento: Optional[str] = None,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Altera um cliente existente no Nibo"""
        dados_cliente = {}
        
        if nome:
            dados_cliente["name"] = nome
        if documento:
            dados_cliente["document"] = documento
        if email:
            dados_cliente["email"] = email
        if telefone:
            dados_cliente["phone"] = telefone
        if endereco:
            dados_cliente["address"] = endereco
            
        # Adicionar outros campos opcionais
        dados_cliente.update(kwargs)
        
        return await self.client.alterar_cliente(cliente_id, dados_cliente)
    
    async def alterar_fornecedor(
        self,
        fornecedor_id: str,
        nome: Optional[str] = None,
        documento: Optional[str] = None,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        endereco: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Altera um fornecedor existente no Nibo"""
        dados_fornecedor = {}
        
        if nome:
            dados_fornecedor["name"] = nome
        if documento:
            dados_fornecedor["document"] = documento
        if email:
            dados_fornecedor["email"] = email
        if telefone:
            dados_fornecedor["phone"] = telefone
        if endereco:
            dados_fornecedor["address"] = endereco
            
        # Adicionar outros campos opcionais
        dados_fornecedor.update(kwargs)
        
        return await self.client.alterar_fornecedor(fornecedor_id, dados_fornecedor)
    
    async def excluir_cliente(self, cliente_id: str) -> Dict:
        """Exclui um cliente do Nibo"""
        return await self.client.excluir_cliente(cliente_id)
    
    async def excluir_fornecedor(self, fornecedor_id: str) -> Dict:
        """Exclui um fornecedor do Nibo"""
        return await self.client.excluir_fornecedor(fornecedor_id)
    
    async def obter_cliente_por_id(self, cliente_id: str) -> Dict:
        """Obtém um cliente específico por ID"""
        return await self.client.obter_cliente_por_id(cliente_id)
    
    async def obter_fornecedor_por_id(self, fornecedor_id: str) -> Dict:
        """Obtém um fornecedor específico por ID"""
        return await self.client.obter_fornecedor_por_id(fornecedor_id)