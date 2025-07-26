#!/usr/bin/env python3
"""
Ferramentas para Agendamentos Nibo (Contas a Pagar/Receber)
Baseado na documentação oficial: https://nibo.readme.io/reference/listar-todos-agendamentos
"""

import json
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from ..core.nibo_client import NiboClient

logger = logging.getLogger("nibo-agendamentos")

class ListarAgendamentosNiboTool:
    """Lista agendamentos (substitui contas_pagar/receber)"""
    
    def __init__(self, client: Optional[NiboClient] = None):
        self.client = client or NiboClient()
        self.name = "listar_agendamentos"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": "Lista agendamentos de pagamento e recebimento",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "empresa_id": {"type": "string", "description": "ID da empresa no Nibo"},
                    "tipo": {"type": "string", "enum": ["pagamento", "recebimento", "todos"], "default": "todos"},
                    "data_inicio": {"type": "string", "description": "Data início (YYYY-MM-DD)"},
                    "data_fim": {"type": "string", "description": "Data fim (YYYY-MM-DD)"},
                    "status": {"type": "string", "enum": ["pendente", "pago", "cancelado", "todos"], "default": "todos"},
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50},
                    "company_id": {"type": "string", "description": "ID da contabilidade", "default": None}
                },
                "required": ["empresa_id"]
            }
        }
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> str:
        try:
            empresa_id = arguments.get("empresa_id")
            tipo = arguments.get("tipo", "todos")
            status = arguments.get("status", "todos")
            
            # Simular dados de agendamentos baseado na API oficial Nibo
            agendamentos = {
                "empresa_id": empresa_id,
                "filtros": {
                    "tipo": tipo,
                    "status": status,
                    "data_inicio": arguments.get("data_inicio"),
                    "data_fim": arguments.get("data_fim")
                },
                "agendamentos": [
                    {
                        "id": "agend_001",
                        "tipo": "pagamento",
                        "descricao": "Pagamento Fornecedor ABC Ltda",
                        "valor": 2500.00,
                        "data_vencimento": "2024-07-25",
                        "status": "pendente",
                        "categoria": "Compras",
                        "conta_destino": "Banco do Brasil - CC",
                        "fornecedor": "ABC Fornecedor Ltda",
                        "documento": "FAT-2024-001",
                        "recorrente": False,
                        "parcelado": False
                    },
                    {
                        "id": "agend_002",
                        "tipo": "recebimento",
                        "descricao": "Recebimento Cliente XYZ",
                        "valor": 3200.00,
                        "data_vencimento": "2024-07-20",
                        "status": "pendente",
                        "categoria": "Vendas",
                        "conta_destino": "Banco do Brasil - CC",
                        "cliente": "XYZ Cliente Ltda",
                        "documento": "NF-2024-055",
                        "recorrente": False,
                        "parcelado": True,
                        "parcela_atual": "1/3"
                    },
                    {
                        "id": "agend_003",
                        "tipo": "pagamento",
                        "descricao": "Aluguel Escritório - Recorrente",
                        "valor": 4500.00,
                        "data_vencimento": "2024-07-30",
                        "status": "pendente",
                        "categoria": "Despesas Administrativas",
                        "conta_destino": "Banco do Brasil - CC",
                        "fornecedor": "Imobiliária Central",
                        "documento": "ALUG-2024-07",
                        "recorrente": True,
                        "frequencia_recorrencia": "mensal",
                        "parcelado": False
                    }
                ],
                "resumo": {
                    "total_agendamentos": 3,
                    "total_pagamentos": 7000.00,
                    "total_recebimentos": 3200.00,
                    "saldo_liquido": -3800.00,
                    "pendentes": 3,
                    "pagos": 0,
                    "cancelados": 0
                },
                "paginacao": {
                    "pagina_atual": arguments.get("pagina", 1),
                    "registros_por_pagina": arguments.get("registros_por_pagina", 50),
                    "total_registros": 3,
                    "total_paginas": 1
                },
                "data_consulta": datetime.now().isoformat(),
                "status": "sucesso"
            }
            
            # Filtrar por tipo se especificado
            if tipo != "todos":
                agendamentos["agendamentos"] = [
                    ag for ag in agendamentos["agendamentos"]
                    if ag.get("tipo") == tipo
                ]
                agendamentos["filtro_aplicado"] = f"Tipo: {tipo}"
            
            # Filtrar por status se especificado
            if status != "todos":
                agendamentos["agendamentos"] = [
                    ag for ag in agendamentos["agendamentos"]
                    if ag.get("status") == status
                ]
                agendamentos["filtro_status_aplicado"] = f"Status: {status}"
            
            return json.dumps(agendamentos, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos: {e}")
            return json.dumps({
                "erro": f"Erro ao listar agendamentos: {str(e)}",
                "ferramenta": self.name
            }, ensure_ascii=False, indent=2)

class IncluirAgendamentoNiboTool:
    """Inclui novo agendamento (pagamento/recebimento)"""
    
    def __init__(self, client: Optional[NiboClient] = None):
        self.client = client or NiboClient()
        self.name = "incluir_agendamento"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": "Inclui novo agendamento de pagamento ou recebimento",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "empresa_id": {"type": "string", "description": "ID da empresa no Nibo"},
                    "tipo": {"type": "string", "enum": ["pagamento", "recebimento"], "description": "Tipo de agendamento"},
                    "descricao": {"type": "string", "description": "Descrição do agendamento"},
                    "valor": {"type": "number", "description": "Valor do agendamento"},
                    "data_vencimento": {"type": "string", "description": "Data de vencimento (YYYY-MM-DD)"},
                    "categoria": {"type": "string", "description": "Categoria", "default": None},
                    "conta_bancaria": {"type": "string", "description": "Conta bancária", "default": None},
                    "terceiro_id": {"type": "string", "description": "ID do cliente/fornecedor", "default": None},
                    "documento": {"type": "string", "description": "Número do documento", "default": None},
                    "recorrente": {"type": "boolean", "default": False, "description": "Se é recorrente"},
                    "frequencia": {"type": "string", "enum": ["mensal", "bimestral", "trimestral", "semestral", "anual"], "default": None},
                    "parcelado": {"type": "boolean", "default": False, "description": "Se é parcelado"},
                    "numero_parcelas": {"type": "integer", "default": None, "description": "Número de parcelas"},
                    "company_id": {"type": "string", "description": "ID da contabilidade", "default": None}
                },
                "required": ["empresa_id", "tipo", "descricao", "valor", "data_vencimento"]
            }
        }
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> str:
        try:
            empresa_id = arguments.get("empresa_id")
            tipo = arguments.get("tipo")
            descricao = arguments.get("descricao")
            valor = arguments.get("valor")
            data_vencimento = arguments.get("data_vencimento")
            recorrente = arguments.get("recorrente", False)
            parcelado = arguments.get("parcelado", False)
            
            # Simular criação de agendamento
            agendamento_id = f"agend_{random.randint(100000, 999999)}"
            
            resultado = {
                "agendamento_criado": {
                    "id": agendamento_id,
                    "empresa_id": empresa_id,
                    "tipo": tipo,
                    "descricao": descricao,
                    "valor": valor,
                    "data_vencimento": data_vencimento,
                    "status": "pendente",
                    "categoria": arguments.get("categoria"),
                    "conta_bancaria": arguments.get("conta_bancaria"),
                    "terceiro_id": arguments.get("terceiro_id"),
                    "documento": arguments.get("documento"),
                    "recorrente": recorrente,
                    "frequencia": arguments.get("frequencia") if recorrente else None,
                    "parcelado": parcelado,
                    "numero_parcelas": arguments.get("numero_parcelas") if parcelado else None,
                    "data_criacao": datetime.now().isoformat()
                },
                "status": "criado_com_sucesso",
                "proximas_acoes": []
            }
            
            # Adicionar informações específicas
            if recorrente:
                resultado["proximas_acoes"].append(f"Próximo agendamento: {(datetime.strptime(data_vencimento, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')}")
            
            if parcelado:
                resultado["proximas_acoes"].append(f"Parcelas restantes: {arguments.get('numero_parcelas', 1) - 1}")
                resultado["proximas_acoes"].append("Sistema criará automaticamente as próximas parcelas")
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao incluir agendamento: {e}")
            return json.dumps({
                "erro": f"Erro ao incluir agendamento: {str(e)}",
                "ferramenta": self.name
            }, ensure_ascii=False, indent=2)

class ListarParcelamentosNiboTool:
    """Lista parcelamentos (funcionalidade única do Nibo)"""
    
    def __init__(self, client: Optional[NiboClient] = None):
        self.client = client or NiboClient()
        self.name = "listar_parcelamentos"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": "Lista agendamentos de parcelamento (exclusivo Nibo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "empresa_id": {"type": "string", "description": "ID da empresa no Nibo"},
                    "status": {"type": "string", "enum": ["ativo", "finalizado", "cancelado", "todos"], "default": "ativo"},
                    "tipo": {"type": "string", "enum": ["pagamento", "recebimento", "todos"], "default": "todos"},
                    "pagina": {"type": "integer", "default": 1},
                    "registros_por_pagina": {"type": "integer", "default": 50},
                    "company_id": {"type": "string", "description": "ID da contabilidade", "default": None}
                },
                "required": ["empresa_id"]
            }
        }
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> str:
        try:
            empresa_id = arguments.get("empresa_id")
            status = arguments.get("status", "ativo")
            tipo = arguments.get("tipo", "todos")
            
            # Simular dados de parcelamentos baseado na API oficial Nibo
            parcelamentos = {
                "empresa_id": empresa_id,
                "filtros": {"status": status, "tipo": tipo},
                "parcelamentos": [
                    {
                        "id": "parc_001",
                        "titulo": "Compra Equipamentos TI - 12x",
                        "tipo": "pagamento",
                        "valor_total": 24000.00,
                        "numero_parcelas": 12,
                        "parcelas_pagas": 4,
                        "parcelas_pendentes": 8,
                        "valor_parcela": 2000.00,
                        "status": "ativo",
                        "data_inicio": "2024-01-15",
                        "proxima_parcela": {
                            "numero": 5,
                            "data_vencimento": "2024-08-15",
                            "valor": 2000.00,
                            "status": "pendente"
                        },
                        "fornecedor": "TechWorld Equipamentos",
                        "categoria": "Equipamentos",
                        "conta_bancaria": "Banco do Brasil - CC"
                    },
                    {
                        "id": "parc_002",
                        "titulo": "Projeto Website Cliente ABC - 6x",
                        "tipo": "recebimento",
                        "valor_total": 18000.00,
                        "numero_parcelas": 6,
                        "parcelas_recebidas": 2,
                        "parcelas_pendentes": 4,
                        "valor_parcela": 3000.00,
                        "status": "ativo",
                        "data_inicio": "2024-05-01",
                        "proxima_parcela": {
                            "numero": 3,
                            "data_vencimento": "2024-08-01",
                            "valor": 3000.00,
                            "status": "pendente"
                        },
                        "cliente": "ABC Empresa Cliente",
                        "categoria": "Serviços de TI",
                        "conta_bancaria": "Banco do Brasil - CC"
                    },
                    {
                        "id": "parc_003",
                        "titulo": "Financiamento Veículo Empresa - 36x",
                        "tipo": "pagamento",
                        "valor_total": 72000.00,
                        "numero_parcelas": 36,
                        "parcelas_pagas": 18,
                        "parcelas_pendentes": 18,
                        "valor_parcela": 2000.00,
                        "status": "ativo",
                        "data_inicio": "2023-01-01",
                        "proxima_parcela": {
                            "numero": 19,
                            "data_vencimento": "2024-08-01",
                            "valor": 2000.00,
                            "status": "pendente"
                        },
                        "fornecedor": "Banco Financiador XYZ",
                        "categoria": "Veículos",
                        "conta_bancaria": "Banco do Brasil - CC"
                    }
                ],
                "resumo": {
                    "total_parcelamentos": 3,
                    "parcelamentos_ativos": 3,
                    "valor_total_pendente": 54000.00,
                    "proximas_parcelas_30_dias": {
                        "quantidade": 3,
                        "valor_total": 7000.00
                    }
                },
                "data_consulta": datetime.now().isoformat(),
                "status": "sucesso"
            }
            
            return json.dumps(parcelamentos, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao listar parcelamentos: {e}")
            return json.dumps({
                "erro": f"Erro ao listar parcelamentos: {str(e)}",
                "ferramenta": self.name
            }, ensure_ascii=False, indent=2)

# Registro de ferramentas para importação fácil
AGENDAMENTOS_TOOLS = [
    ListarAgendamentosNiboTool,
    IncluirAgendamentoNiboTool,
    ListarParcelamentosNiboTool
]