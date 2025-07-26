#!/usr/bin/env python3
"""
🏷️ SISTEMA DE CLASSIFICAÇÃO AVANÇADO PARA TOOLS OMIE FASTMCP
Organização inteligente com tags, categorias e metadados
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

# =============================================================================
# ENUMS PARA CLASSIFICAÇÃO
# =============================================================================

class ToolCategory(Enum):
    """Categorias principais das ferramentas"""
    SISTEMA = "sistema"
    ORGANIZACIONAL = "organizacional"
    FINANCEIRO = "financeiro"
    COMERCIAL = "comercial"
    PRODUTOS = "produtos"
    RELATORIOS = "relatorios"
    ADMINISTRATIVO = "administrativo"

class ToolType(Enum):
    """Tipos de operação das ferramentas"""
    CONSULTA = "consulta"
    LISTAGEM = "listagem"
    CADASTRO = "cadastro"
    ATUALIZACAO = "atualizacao"
    EXCLUSAO = "exclusao"
    RELATORIO = "relatorio"
    DASHBOARD = "dashboard"
    VALIDACAO = "validacao"
    LOTE = "lote"

class ToolComplexity(Enum):
    """Nível de complexidade das ferramentas"""
    BASICA = "basica"          # Operações simples de consulta
    INTERMEDIARIA = "intermediaria"  # Operações com filtros e lógica
    AVANCADA = "avancada"      # Operações complexas, CRUD, lotes
    ESPECIALIZADA = "especializada"  # Relatórios e análises customizadas

class ToolPriority(Enum):
    """Prioridade de implementação/uso"""
    CRITICA = "critica"        # Essencial para operação
    ALTA = "alta"             # Muito importante
    MEDIA = "media"           # Importante
    BAIXA = "baixa"           # Nice to have

class ToolStatus(Enum):
    """Status de implementação"""
    IMPLEMENTADA = "implementada"
    EM_DESENVOLVIMENTO = "em_desenvolvimento"
    PLANEJADA = "planejada"
    TESTE = "teste"
    PRODUCAO = "producao"
    DEPRECIADA = "depreciada"

# =============================================================================
# DATACLASS PARA METADADOS DA TOOL
# =============================================================================

@dataclass
class ToolMetadata:
    """Metadados completos de uma ferramenta"""
    
    # Identificação
    name: str
    display_name: str
    description: str
    
    # Classificação
    category: ToolCategory
    type: ToolType
    complexity: ToolComplexity
    priority: ToolPriority
    status: ToolStatus
    
    # Tags e labels
    tags: Set[str] = field(default_factory=set)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Informações técnicas
    version: str = "1.0.0"
    author: str = "Claude Code Assistant"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Parâmetros e configurações
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    response_format: str = "json"
    supports_pagination: bool = False
    supports_filters: bool = False
    supports_batch: bool = False
    
    # Performance e limites
    estimated_response_time_ms: int = 2000
    max_records_per_page: int = 50
    rate_limit_per_minute: int = 60
    
    # Dependências e relacionamentos
    dependencies: List[str] = field(default_factory=list)
    related_tools: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    
    # Documentação
    examples: List[Dict[str, Any]] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

# =============================================================================
# SISTEMA DE CLASSIFICAÇÃO
# =============================================================================

class ToolClassificationSystem:
    """Sistema central de classificação e gestão de tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolMetadata] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        
    def register_tool(self, metadata: ToolMetadata) -> None:
        """Registra uma nova tool no sistema"""
        self.tools[metadata.name] = metadata
        
        # Indexar por categoria
        if metadata.category not in self.categories:
            self.categories[metadata.category] = []
        self.categories[metadata.category].append(metadata.name)
        
        # Indexar por tags
        for tag in metadata.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(metadata.name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """Retorna tools de uma categoria específica"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tools_by_tag(self, tag: str) -> List[ToolMetadata]:
        """Retorna tools com uma tag específica"""
        tool_names = self.tags.get(tag, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tools_by_complexity(self, complexity: ToolComplexity) -> List[ToolMetadata]:
        """Retorna tools de um nível de complexidade"""
        return [tool for tool in self.tools.values() if tool.complexity == complexity]
    
    def get_tools_by_priority(self, priority: ToolPriority) -> List[ToolMetadata]:
        """Retorna tools de uma prioridade específica"""
        return [tool for tool in self.tools.values() if tool.priority == priority]
    
    def search_tools(self, 
                    query: str = None,
                    category: ToolCategory = None,
                    complexity: ToolComplexity = None,
                    priority: ToolPriority = None,
                    status: ToolStatus = None,
                    tags: List[str] = None) -> List[ToolMetadata]:
        """Busca avançada de tools com múltiplos filtros"""
        results = list(self.tools.values())
        
        # Filtro por categoria
        if category:
            results = [t for t in results if t.category == category]
        
        # Filtro por complexidade
        if complexity:
            results = [t for t in results if t.complexity == complexity]
        
        # Filtro por prioridade
        if priority:
            results = [t for t in results if t.priority == priority]
        
        # Filtro por status
        if status:
            results = [t for t in results if t.status == status]
        
        # Filtro por tags
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
        
        # Filtro por query de texto
        if query:
            query_lower = query.lower()
            results = [
                t for t in results 
                if (query_lower in t.name.lower() or 
                    query_lower in t.display_name.lower() or 
                    query_lower in t.description.lower())
            ]
        
        return results
    
    def generate_tool_registry(self) -> Dict[str, Any]:
        """Gera registro completo de todas as tools"""
        return {
            "metadata": {
                "total_tools": len(self.tools),
                "categories": {cat.value: len(tools) for cat, tools in self.categories.items()},
                "generated_at": datetime.now().isoformat()
            },
            "tools": {
                name: {
                    "name": tool.name,
                    "display_name": tool.display_name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "type": tool.type.value,
                    "complexity": tool.complexity.value,
                    "priority": tool.priority.value,
                    "status": tool.status.value,
                    "tags": list(tool.tags),
                    "version": tool.version,
                    "supports_pagination": tool.supports_pagination,
                    "supports_filters": tool.supports_filters,
                    "supports_batch": tool.supports_batch,
                    "estimated_response_time_ms": tool.estimated_response_time_ms
                }
                for name, tool in self.tools.items()
            }
        }

# =============================================================================
# DEFINIÇÕES DAS TOOLS - CONJUNTO 1
# =============================================================================

def create_conjunto1_tools() -> List[ToolMetadata]:
    """Cria metadados para todas as tools do Conjunto 1"""
    
    tools = []
    
    # 1. consultar_categorias
    tools.append(ToolMetadata(
        name="consultar_categorias",
        display_name="Consultar Categorias",
        description="Consulta categorias cadastradas no Omie ERP com filtros avançados",
        category=ToolCategory.ORGANIZACIONAL,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"categorias", "consulta", "filtros", "organizacao"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "default": 50},
            {"name": "filtro_descricao", "type": "str", "optional": True},
            {"name": "apenas_ativas", "type": "bool", "default": True}
        ],
        use_cases=["Organizar transações por categoria", "Validar categorias ativas"],
        related_tools=["consultar_departamentos", "consultar_projetos"]
    ))
    
    # 2. consultar_departamentos
    tools.append(ToolMetadata(
        name="consultar_departamentos",
        display_name="Consultar Departamentos",
        description="Consulta departamentos cadastrados no Omie ERP",
        category=ToolCategory.ORGANIZACIONAL,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"departamentos", "consulta", "organizacao"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "default": 50},
            {"name": "apenas_ativos", "type": "bool", "default": True}
        ],
        use_cases=["Organizar custos por departamento", "Relatórios departamentais"],
        related_tools=["consultar_categorias", "consultar_projetos"]
    ))
    
    # 3. consultar_projetos
    tools.append(ToolMetadata(
        name="consultar_projetos",
        display_name="Consultar Projetos",
        description="Consulta projetos cadastrados no Omie ERP com filtros por status",
        category=ToolCategory.ORGANIZACIONAL,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.MEDIA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"projetos", "consulta", "status", "organizacao"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "default": 50},
            {"name": "status_projeto", "type": "str", "optional": True}
        ],
        use_cases=["Controle de projetos", "Relatórios por projeto"],
        related_tools=["consultar_categorias", "consultar_departamentos"]
    ))
    
    # 4. consultar_tipos_documento
    tools.append(ToolMetadata(
        name="consultar_tipos_documento",
        display_name="Consultar Tipos de Documento",
        description="Consulta tipos de documento no Omie ERP com filtros por categoria",
        category=ToolCategory.SISTEMA,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.MEDIA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"documentos", "tipos", "consulta", "sistema"},
        supports_filters=True,
        parameters=[
            {"name": "codigo", "type": "str", "optional": True},
            {"name": "categoria", "type": "str", "optional": True}
        ],
        use_cases=["Configuração de documentos", "Validação de tipos"],
        related_tools=["consultar_lancamentos"]
    ))
    
    # 5. listar_clientes
    tools.append(ToolMetadata(
        name="listar_clientes",
        display_name="Listar Clientes",
        description="Lista clientes cadastrados com filtros avançados por nome, cidade e status",
        category=ToolCategory.COMERCIAL,
        type=ToolType.LISTAGEM,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.CRITICA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"clientes", "listagem", "comercial", "filtros"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "default": 50},
            {"name": "filtro_nome", "type": "str", "optional": True},
            {"name": "apenas_ativos", "type": "bool", "default": True},
            {"name": "filtro_cidade", "type": "str", "optional": True}
        ],
        use_cases=["Gestão de relacionamento", "Campanhas de marketing", "Cobrança"],
        related_tools=["listar_fornecedores", "consultar_contas_receber"]
    ))
    
    # 6. listar_fornecedores
    tools.append(ToolMetadata(
        name="listar_fornecedores",
        display_name="Listar Fornecedores",
        description="Lista fornecedores cadastrados com filtros por nome e status",
        category=ToolCategory.COMERCIAL,
        type=ToolType.LISTAGEM,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"fornecedores", "listagem", "comercial"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "default": 50},
            {"name": "filtro_nome", "type": "str", "optional": True},
            {"name": "apenas_ativos", "type": "bool", "default": True}
        ],
        use_cases=["Gestão de fornecedores", "Compras", "Pagamentos"],
        related_tools=["listar_clientes", "consultar_contas_pagar"]
    ))
    
    # 7. consultar_contas_pagar
    tools.append(ToolMetadata(
        name="consultar_contas_pagar",
        display_name="Consultar Contas a Pagar",
        description="Consulta contas a pagar com filtros avançados por status (vencido/a_vencer/pago)",
        category=ToolCategory.FINANCEIRO,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.CRITICA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"contas_pagar", "financeiro", "status", "vencimento"},
        supports_pagination=True,
        supports_filters=True,
        estimated_response_time_ms=3000,
        parameters=[
            {"name": "data_inicio", "type": "str", "optional": True},
            {"name": "data_fim", "type": "str", "optional": True},
            {"name": "status", "type": "str", "default": "todos"},
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "filtro_fornecedor", "type": "str", "optional": True}
        ],
        use_cases=["Fluxo de caixa", "Contas vencidas", "Planejamento financeiro"],
        related_tools=["consultar_contas_receber", "listar_fornecedores"],
        limitations=["Não inclui transações canceladas/excluídas"]
    ))
    
    # 8. consultar_contas_receber
    tools.append(ToolMetadata(
        name="consultar_contas_receber",
        display_name="Consultar Contas a Receber",
        description="Consulta contas a receber com filtros avançados por status (vencido/a_vencer/pago)",
        category=ToolCategory.FINANCEIRO,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.CRITICA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"contas_receber", "financeiro", "status", "vencimento"},
        supports_pagination=True,
        supports_filters=True,
        estimated_response_time_ms=3000,
        parameters=[
            {"name": "data_inicio", "type": "str", "optional": True},
            {"name": "data_fim", "type": "str", "optional": True},
            {"name": "status", "type": "str", "default": "todos"},
            {"name": "pagina", "type": "int", "default": 1},
            {"name": "filtro_cliente", "type": "str", "optional": True}
        ],
        use_cases=["Fluxo de caixa", "Cobrança", "Análise de inadimplência"],
        related_tools=["consultar_contas_pagar", "listar_clientes"],
        limitations=["Não inclui transações canceladas/excluídas"]
    ))
    
    # 9. consultar_lancamentos
    tools.append(ToolMetadata(
        name="consultar_lancamentos",
        display_name="Consultar Lançamentos",
        description="Consulta lançamentos financeiros por período e tipo",
        category=ToolCategory.FINANCEIRO,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"lancamentos", "financeiro", "periodo", "tipos"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "data_inicio", "type": "str", "optional": True},
            {"name": "data_fim", "type": "str", "optional": True},
            {"name": "tipo_lancamento", "type": "str", "optional": True},
            {"name": "pagina", "type": "int", "default": 1}
        ],
        use_cases=["Conciliação bancária", "Fluxo de caixa", "Auditoria"],
        related_tools=["consultar_contas_correntes"]
    ))
    
    # 10. consultar_contas_correntes
    tools.append(ToolMetadata(
        name="consultar_contas_correntes",
        display_name="Consultar Contas Correntes",
        description="Consulta contas correntes cadastradas por tipo (banco/caixa/aplicação)",
        category=ToolCategory.FINANCEIRO,
        type=ToolType.CONSULTA,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.IMPLEMENTADA,
        tags={"contas_correntes", "financeiro", "bancos", "caixa"},
        supports_pagination=True,
        supports_filters=True,
        parameters=[
            {"name": "apenas_ativas", "type": "bool", "default": True},
            {"name": "tipo_conta", "type": "str", "optional": True},
            {"name": "pagina", "type": "int", "default": 1}
        ],
        use_cases=["Gestão financeira", "Conciliação", "Relatórios"],
        related_tools=["consultar_lancamentos"]
    ))
    
    return tools

# =============================================================================
# INSTÂNCIA GLOBAL DO SISTEMA
# =============================================================================

# Criar instância global
classification_system = ToolClassificationSystem()

# Registrar tools do Conjunto 1
for tool in create_conjunto1_tools():
    classification_system.register_tool(tool)

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_tools_summary() -> Dict[str, Any]:
    """Retorna resumo organizado das tools"""
    return {
        "total_tools": len(classification_system.tools),
        "por_categoria": {
            categoria.value: len(classification_system.get_tools_by_category(categoria))
            for categoria in ToolCategory
        },
        "por_complexidade": {
            complexidade.value: len(classification_system.get_tools_by_complexity(complexidade))
            for complexidade in ToolComplexity
        },
        "por_prioridade": {
            prioridade.value: len(classification_system.get_tools_by_priority(prioridade))
            for prioridade in ToolPriority
        },
        "tags_mais_usadas": {
            tag: len(tools) for tag, tools in 
            sorted(classification_system.tags.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        }
    }

def export_classification_json() -> str:
    """Exporta classificação completa em JSON"""
    return json.dumps(classification_system.generate_tool_registry(), 
                     ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("🏷️ SISTEMA DE CLASSIFICAÇÃO OMIE FASTMCP")
    print("=" * 50)
    
    summary = get_tools_summary()
    print(f"📊 Total de Tools: {summary['total_tools']}")
    print("\n📋 Por Categoria:")
    for cat, count in summary['por_categoria'].items():
        if count > 0:
            print(f"   {cat}: {count} tools")
    
    print("\n🔹 Por Complexidade:")
    for comp, count in summary['por_complexidade'].items():
        if count > 0:
            print(f"   {comp}: {count} tools")
    
    print("\n🏷️ Tags mais usadas:")
    for tag, count in list(summary['tags_mais_usadas'].items())[:5]:
        print(f"   #{tag}: {count} tools")
    
    print("\n✅ Sistema de classificação implementado com sucesso!")
    print("🔍 Use classification_system para buscar e organizar tools")
    print("📊 Use get_tools_summary() para visão geral")
    print("💾 Use export_classification_json() para exportar")