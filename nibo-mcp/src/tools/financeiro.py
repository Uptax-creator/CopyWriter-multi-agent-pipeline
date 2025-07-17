"""
Ferramentas financeiras para o Nibo MCP Server
"""
from typing import Dict, Optional
from ..core.nibo_client import NiboClient

class NiboFinanceiro:
    def __init__(self, client: NiboClient):
        self.client = client
    
    async def incluir_conta_pagar(
        self,
        fornecedor_id: str,
        valor: float,
        data_vencimento: str,
        categoria_id: Optional[str] = None,
        centro_custo_id: Optional[str] = None,
        descricao: Optional[str] = None,
        numero_documento: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Inclui uma nova conta a pagar no Nibo"""
        dados_conta = {
            "supplierId": fornecedor_id,
            "value": valor,
            "dueDate": data_vencimento
        }
        
        if categoria_id:
            dados_conta["categoryId"] = categoria_id
        if centro_custo_id:
            dados_conta["costCenterId"] = centro_custo_id
        if descricao:
            dados_conta["description"] = descricao
        if numero_documento:
            dados_conta["documentNumber"] = numero_documento
            
        # Adicionar outros campos opcionais
        dados_conta.update(kwargs)
        
        return await self.client.incluir_conta_pagar(dados_conta)
    
    async def incluir_conta_receber(
        self,
        cliente_id: str,
        valor: float,
        data_vencimento: str,
        categoria_id: Optional[str] = None,
        centro_custo_id: Optional[str] = None,
        descricao: Optional[str] = None,
        numero_documento: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Inclui uma nova conta a receber no Nibo"""
        dados_conta = {
            "clientId": cliente_id,
            "value": valor,
            "dueDate": data_vencimento
        }
        
        if categoria_id:
            dados_conta["categoryId"] = categoria_id
        if centro_custo_id:
            dados_conta["costCenterId"] = centro_custo_id
        if descricao:
            dados_conta["description"] = descricao
        if numero_documento:
            dados_conta["documentNumber"] = numero_documento
            
        # Adicionar outros campos opcionais
        dados_conta.update(kwargs)
        
        return await self.client.incluir_conta_receber(dados_conta)
    
    async def alterar_conta_pagar(
        self,
        conta_id: str,
        fornecedor_id: Optional[str] = None,
        valor: Optional[float] = None,
        data_vencimento: Optional[str] = None,
        categoria_id: Optional[str] = None,
        centro_custo_id: Optional[str] = None,
        descricao: Optional[str] = None,
        numero_documento: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Altera uma conta a pagar existente no Nibo"""
        dados_conta = {}
        
        if fornecedor_id:
            dados_conta["supplierId"] = fornecedor_id
        if valor is not None:
            dados_conta["value"] = valor
        if data_vencimento:
            dados_conta["dueDate"] = data_vencimento
        if categoria_id:
            dados_conta["categoryId"] = categoria_id
        if centro_custo_id:
            dados_conta["costCenterId"] = centro_custo_id
        if descricao:
            dados_conta["description"] = descricao
        if numero_documento:
            dados_conta["documentNumber"] = numero_documento
            
        # Adicionar outros campos opcionais
        dados_conta.update(kwargs)
        
        return await self.client.alterar_conta_pagar(conta_id, dados_conta)
    
    async def alterar_conta_receber(
        self,
        conta_id: str,
        cliente_id: Optional[str] = None,
        valor: Optional[float] = None,
        data_vencimento: Optional[str] = None,
        categoria_id: Optional[str] = None,
        centro_custo_id: Optional[str] = None,
        descricao: Optional[str] = None,
        numero_documento: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Altera uma conta a receber existente no Nibo"""
        dados_conta = {}
        
        if cliente_id:
            dados_conta["clientId"] = cliente_id
        if valor is not None:
            dados_conta["value"] = valor
        if data_vencimento:
            dados_conta["dueDate"] = data_vencimento
        if categoria_id:
            dados_conta["categoryId"] = categoria_id
        if centro_custo_id:
            dados_conta["costCenterId"] = centro_custo_id
        if descricao:
            dados_conta["description"] = descricao
        if numero_documento:
            dados_conta["documentNumber"] = numero_documento
            
        # Adicionar outros campos opcionais
        dados_conta.update(kwargs)
        
        return await self.client.alterar_conta_receber(conta_id, dados_conta)
    
    async def excluir_conta_pagar(self, conta_id: str) -> Dict:
        """Exclui uma conta a pagar do Nibo"""
        return await self.client.excluir_conta_pagar(conta_id)
    
    async def excluir_conta_receber(self, conta_id: str) -> Dict:
        """Exclui uma conta a receber do Nibo"""
        return await self.client.excluir_conta_receber(conta_id)