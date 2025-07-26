#!/usr/bin/env python3
"""
🏷️ CLASSIFICADOR ENHANCED DE TOOLS OMIE MCP
Sistema avançado para classificação e gestão das novas tools documentadas
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

# =============================================================================
# ENUMS APRIMORADOS PARA NOVAS TOOLS
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
    PROJETOS = "projetos"  # Nova categoria
    LANCAMENTOS = "lancamentos"  # Nova categoria  
    CONTAS_CORRENTES = "contas_correntes"  # Nova categoria

class ToolType(Enum):
    """Tipos de operação das ferramentas"""
    CONSULTA = "consulta"
    LISTAGEM = "listagem"
    LISTAR = "listar"  # Alias para LISTAGEM
    CADASTRO = "cadastro"
    INCLUIR = "incluir"  # Específico Omie
    ALTERAR = "alterar"  # Específico Omie
    EXCLUIR = "excluir"  # Específico Omie
    RELATORIO = "relatorio"
    DASHBOARD = "dashboard"
    VALIDACAO = "validacao"
    LOTE = "lote"

class ToolComplexity(Enum):
    """Nível de complexidade das ferramentas"""
    BASICA = "basica"          # Operações simples CRUD
    INTERMEDIARIA = "intermediaria"  # Operações com lógica de negócio
    AVANCADA = "avancada"      # Operações complexas, validações múltiplas
    ESPECIALIZADA = "especializada"  # Operações críticas, integrações complexas

class ToolPriority(Enum):
    """Prioridade de implementação/uso"""
    CRITICA = "critica"        # Essencial para operação
    ALTA = "alta"             # Muito importante
    MEDIA = "media"           # Importante
    BAIXA = "baixa"           # Nice to have

class ToolStatus(Enum):
    """Status de implementação"""
    PLANEJADA = "planejada"
    EM_DESENVOLVIMENTO = "em_desenvolvimento"
    IMPLEMENTADA = "implementada"
    TESTE = "teste"
    PRODUCAO = "producao"
    DEPRECIADA = "depreciada"

class OMIEOperationType(Enum):
    """Tipos específicos de operação da API Omie"""
    INCLUIR = "Incluir"
    LISTAR = "Listar"
    ALTERAR = "Alterar"
    EXCLUIR = "Excluir"
    CONSULTAR = "Consultar"
    OBTER = "Obter"

# =============================================================================
# DATACLASS ENHANCED PARA TOOLS OMIE
# =============================================================================

@dataclass
class OmieToolMetadata:
    """Metadados completos de uma ferramenta Omie MCP"""
    
    # Identificação básica
    name: str
    display_name: str
    description: str
    
    # Classificação
    category: ToolCategory
    type: ToolType
    complexity: ToolComplexity
    priority: ToolPriority
    status: ToolStatus
    
    # Informações específicas da API Omie
    omie_endpoint: str
    omie_call: str  # Nome do método na API Omie (ex: "IncluirProjeto")
    omie_operation: OMIEOperationType
    
    # Tags e labels
    tags: Set[str] = field(default_factory=set)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Parâmetros da API
    required_parameters: List[Dict[str, Any]] = field(default_factory=list)
    optional_parameters: List[Dict[str, Any]] = field(default_factory=list)
    
    # Exemplo de request/response
    curl_example: str = ""
    request_example: Dict[str, Any] = field(default_factory=dict)
    response_example: Dict[str, Any] = field(default_factory=dict)
    
    # Informações técnicas
    version: str = "1.0.0"
    author: str = "Claude Code Assistant"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Performance e limites
    estimated_response_time_ms: int = 2000
    max_records_per_page: int = 50
    rate_limit_per_minute: int = 60
    
    # Dependências e relacionamentos
    dependencies: List[str] = field(default_factory=list)
    related_tools: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    
    # Validações e regras de negócio
    business_rules: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    error_codes: Dict[str, str] = field(default_factory=dict)
    
    # Documentação
    use_cases: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

# =============================================================================
# DEFINIÇÕES DAS NOVAS TOOLS DOCUMENTADAS
# =============================================================================

def create_projeto_tools() -> List[OmieToolMetadata]:
    """Cria metadados para tools de projetos"""
    
    tools = []
    
    # 1. incluir_projeto
    tools.append(OmieToolMetadata(
        name="incluir_projeto",
        display_name="Incluir Projeto",
        description="Inclui novo projeto no Omie ERP com validações de negócio",
        category=ToolCategory.PROJETOS,
        type=ToolType.INCLUIR,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/projetos/",
        omie_call="IncluirProjeto",
        omie_operation=OMIEOperationType.INCLUIR,
        tags={"projetos", "incluir", "gestao", "organizacao"},
        required_parameters=[
            {"name": "codint", "type": "str", "description": "Código interno do projeto"},
            {"name": "nome", "type": "str", "description": "Nome do projeto"},
            {"name": "inativo", "type": "str", "description": "Status ativo/inativo (S/N)", "default": "N"}
        ],
        curl_example='''curl -s https://app.omie.com.br/api/v1/geral/projetos/ \\
 -H 'Content-type: application/json' \\
 -d '{"call":"IncluirProjeto","param":[{"codint":"1234","nome":"teste","inativo":"N"}],"app_key":"#APP_KEY#","app_secret":"#APP_SECRET#"}\'''',
        request_example={
            "codint": "1234",
            "nome": "teste", 
            "inativo": "N"
        },
        response_example={
            "codigo": 3227314028,
            "codInt": "1234",
            "status": "0",
            "descricao": "Projeto cadastrado com sucesso!"
        },
        business_rules=[
            "Código interno deve ser único",
            "Nome do projeto é obrigatório",
            "Status padrão é ativo ('N')"
        ],
        validation_rules=[
            "codint não pode ser vazio",
            "nome deve ter entre 1 e 100 caracteres",
            "inativo deve ser 'S' ou 'N'"
        ],
        use_cases=[
            "Criar novos projetos para organização",
            "Segregar custos e receitas por projeto",
            "Controle de atividades por projeto"
        ],
        related_tools=["listar_projetos", "excluir_projeto"],
        estimated_response_time_ms=1500
    ))
    
    # 2. listar_projetos
    tools.append(OmieToolMetadata(
        name="listar_projetos",
        display_name="Listar Projetos",
        description="Lista projetos cadastrados com paginação e filtros",
        category=ToolCategory.PROJETOS,
        type=ToolType.LISTAR,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/projetos/",
        omie_call="ListarProjetos",
        omie_operation=OMIEOperationType.LISTAR,
        tags={"projetos", "listar", "consulta"},
        required_parameters=[
            {"name": "pagina", "type": "int", "description": "Página para listagem", "default": 1},
            {"name": "registros_por_pagina", "type": "int", "description": "Registros por página", "default": 50}
        ],
        optional_parameters=[
            {"name": "apenas_importado_api", "type": "str", "description": "Filtrar apenas importados via API", "default": "N"}
        ],
        use_cases=[
            "Listar todos os projetos",
            "Paginar grandes volumes de projetos",
            "Filtrar projetos por origem"
        ],
        related_tools=["incluir_projeto", "excluir_projeto"]
    ))
    
    # 3. excluir_projeto
    tools.append(OmieToolMetadata(
        name="excluir_projeto",
        display_name="Excluir Projeto",
        description="Exclui projeto do Omie ERP com validações de segurança",
        category=ToolCategory.PROJETOS,
        type=ToolType.EXCLUIR,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.MEDIA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/projetos/",
        omie_call="ExcluirProjeto",
        omie_operation=OMIEOperationType.EXCLUIR,
        tags={"projetos", "excluir", "remover"},
        required_parameters=[
            {"name": "codigo", "type": "int", "description": "Código do projeto (alternativo)"},
            {"name": "codint", "type": "str", "description": "Código interno do projeto"}
        ],
        business_rules=[
            "Projeto não pode ter lançamentos associados",
            "Apenas projetos sem movimentação podem ser excluídos",
            "Operação irreversível - requer confirmação"
        ],
        validation_rules=[
            "codigo OU codint deve ser fornecido",
            "Projeto deve existir no sistema",
            "Verificar dependências antes da exclusão"
        ],
        limitations=[
            "Não é possível excluir projetos com movimentação",
            "Operação irreversível"
        ],
        use_cases=[
            "Remover projetos criados incorretamente",
            "Limpeza de projetos de teste",
            "Manutenção da base de dados"
        ],
        related_tools=["incluir_projeto", "listar_projetos"],
        estimated_response_time_ms=1000
    ))
    
    return tools

def create_lancamento_tools() -> List[OmieToolMetadata]:
    """Cria metadados para tools de lançamentos"""
    
    tools = []
    
    # 4. incluir_lancamento
    tools.append(OmieToolMetadata(
        name="incluir_lancamento",
        display_name="Incluir Lançamento",
        description="Inclui lançamento em conta corrente com validações financeiras",
        category=ToolCategory.LANCAMENTOS,
        type=ToolType.INCLUIR,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.CRITICA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/financas/contacorrentelancamentos/",
        omie_call="IncluirLancCC",
        omie_operation=OMIEOperationType.INCLUIR,
        tags={"lancamentos", "financeiro", "conta_corrente", "incluir"},
        required_parameters=[
            {"name": "cCodIntLanc", "type": "str", "description": "Código interno do lançamento"},
            {"name": "cabecalho", "type": "dict", "description": "Dados do cabeçalho"},
            {"name": "detalhes", "type": "dict", "description": "Detalhes do lançamento"}
        ],
        request_example={
            "cCodIntLanc": "1753042011",
            "cabecalho": {
                "nCodCC": 427619317,
                "dDtLanc": "20/07/2025",
                "nValorLanc": 123.46
            },
            "detalhes": {
                "cCodCateg": "1.01.02",
                "cTipo": "DIN",
                "nCodCliente": 2485994,
                "cObs": "Referente a jardinagem executada na matriz"
            }
        },
        business_rules=[
            "Código interno deve ser único",
            "Conta corrente deve existir",
            "Valor deve ser maior que zero",
            "Data não pode ser futura para alguns tipos"
        ],
        validation_rules=[
            "nCodCC deve existir na base",
            "dDtLanc deve estar no formato DD/MM/AAAA",
            "nValorLanc deve ser numérico positivo",
            "cCodCateg deve ser categoria válida"
        ],
        use_cases=[
            "Registrar entradas de caixa",
            "Lançar movimentações bancárias",
            "Controle de fluxo de caixa"
        ],
        estimated_response_time_ms=2000
    ))
    
    # 5. listar_lancamentos
    tools.append(OmieToolMetadata(
        name="listar_lancamentos",
        display_name="Listar Lançamentos",
        description="Lista lançamentos de conta corrente com filtros avançados",
        category=ToolCategory.LANCAMENTOS,
        type=ToolType.LISTAR,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.CRITICA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/financas/contacorrentelancamentos/",
        omie_call="ListarLancCC",
        omie_operation=OMIEOperationType.LISTAR,
        tags={"lancamentos", "financeiro", "listagem", "consulta"},
        required_parameters=[
            {"name": "nPagina", "type": "int", "description": "Número da página", "default": 1},
            {"name": "nRegPorPagina", "type": "int", "description": "Registros por página", "default": 20}
        ],
        use_cases=[
            "Consultar movimentações financeiras",
            "Gerar relatórios de fluxo de caixa",
            "Auditoria de lançamentos"
        ],
        estimated_response_time_ms=3000
    ))
    
    # 6. alterar_lancamento
    tools.append(OmieToolMetadata(
        name="alterar_lancamento", 
        display_name="Alterar Lançamento",
        description="Altera lançamento existente com validações de integridade",
        category=ToolCategory.LANCAMENTOS,
        type=ToolType.ALTERAR,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/financas/contacorrentelancamentos/",
        omie_call="AlterarLancCC",
        omie_operation=OMIEOperationType.ALTERAR,
        tags={"lancamentos", "alterar", "financeiro"},
        business_rules=[
            "Lançamento deve existir",
            "Não alterar lançamentos conciliados",
            "Manter auditoria das alterações"
        ],
        limitations=[
            "Lançamentos conciliados não podem ser alterados",
            "Algumas alterações podem afetar relatórios"
        ]
    ))
    
    # 7. excluir_lancamento
    tools.append(OmieToolMetadata(
        name="excluir_lancamento",
        display_name="Excluir Lançamento", 
        description="Exclui lançamento com validações de segurança financeira",
        category=ToolCategory.LANCAMENTOS,
        type=ToolType.EXCLUIR,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.MEDIA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/financas/contacorrentelancamentos/",
        omie_call="ExcluirLancCC",
        omie_operation=OMIEOperationType.EXCLUIR,
        tags={"lancamentos", "excluir", "financeiro"},
        required_parameters=[
            {"name": "nCodLanc", "type": "int", "description": "Código do lançamento"},
            {"name": "cCodIntLanc", "type": "str", "description": "Código interno do lançamento"}
        ],
        business_rules=[
            "Operação irreversível",
            "Não excluir lançamentos conciliados",
            "Verificar impacto no saldo"
        ]
    ))
    
    return tools

def create_conta_corrente_tools() -> List[OmieToolMetadata]:
    """Cria metadados para tools de contas correntes"""
    
    tools = []
    
    # 8. incluir_conta_corrente
    tools.append(OmieToolMetadata(
        name="incluir_conta_corrente",
        display_name="Incluir Conta Corrente",
        description="Inclui nova conta corrente no sistema financeiro",
        category=ToolCategory.CONTAS_CORRENTES,
        type=ToolType.INCLUIR,
        complexity=ToolComplexity.INTERMEDIARIA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/contacorrente/",
        omie_call="IncluirContaCorrente",
        omie_operation=OMIEOperationType.INCLUIR,
        tags={"conta_corrente", "financeiro", "incluir", "bancos"},
        required_parameters=[
            {"name": "cCodCCInt", "type": "str", "description": "Código interno da conta"},
            {"name": "tipo_conta_corrente", "type": "str", "description": "Tipo da conta (CX, CC, CA, AD)"},
            {"name": "codigo_banco", "type": "str", "description": "Código do banco"},
            {"name": "descricao", "type": "str", "description": "Descrição da conta"},
            {"name": "saldo_inicial", "type": "float", "description": "Saldo inicial", "default": 0}
        ],
        request_example={
            "cCodCCInt": "MyCC0001",
            "tipo_conta_corrente": "CX",
            "codigo_banco": "999",
            "descricao": "Caixinha",
            "saldo_inicial": 0
        },
        response_example={
            "nCodCC": 3227315558,
            "cCodCCInt": "MyCC0001", 
            "cCodStatus": "0",
            "cDesStatus": "Conta corrente incluída com sucesso!"
        },
        business_rules=[
            "Código interno deve ser único",
            "Tipo de conta deve ser válido (CX=Caixa, CC=Conta Corrente, CA=Cartão, AD=Adiantamento)",
            "Descrição é obrigatória"
        ],
        use_cases=[
            "Cadastrar contas bancárias",
            "Criar caixas para controle",
            "Configurar cartões de crédito"
        ]
    ))
    
    # 9. listar_contas_correntes
    tools.append(OmieToolMetadata(
        name="listar_contas_correntes",
        display_name="Listar Contas Correntes",
        description="Lista contas correntes com detalhes completos",
        category=ToolCategory.CONTAS_CORRENTES,
        type=ToolType.LISTAR,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.ALTA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/contacorrente/",
        omie_call="ListarContasCorrentes",
        omie_operation=OMIEOperationType.LISTAR,
        tags={"conta_corrente", "listar", "financeiro"},
        use_cases=[
            "Visualizar todas as contas cadastradas",
            "Controle de contas ativas",
            "Relatórios financeiros"
        ]
    ))
    
    # 10. listar_resumo_contas_correntes
    tools.append(OmieToolMetadata(
        name="listar_resumo_contas_correntes",
        display_name="Listar Resumo Contas Correntes",
        description="Lista resumo simplificado das contas correntes",
        category=ToolCategory.CONTAS_CORRENTES,
        type=ToolType.LISTAR,
        complexity=ToolComplexity.BASICA,
        priority=ToolPriority.MEDIA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/contacorrente/",
        omie_call="ListarResumoContasCorrentes",
        omie_operation=OMIEOperationType.LISTAR,
        tags={"conta_corrente", "resumo", "dashboard"},
        use_cases=[
            "Dashboard financeiro",
            "Visão geral rápida das contas",
            "Seleção de contas em formulários"
        ]
    ))
    
    # 11. excluir_conta_corrente
    tools.append(OmieToolMetadata(
        name="excluir_conta_corrente",
        display_name="Excluir Conta Corrente",
        description="Exclui conta corrente com validações de segurança",
        category=ToolCategory.CONTAS_CORRENTES,
        type=ToolType.EXCLUIR,
        complexity=ToolComplexity.AVANCADA,
        priority=ToolPriority.BAIXA,
        status=ToolStatus.PLANEJADA,
        omie_endpoint="https://app.omie.com.br/api/v1/geral/contacorrente/",
        omie_call="ExcluirContaCorrente",
        omie_operation=OMIEOperationType.EXCLUIR,
        tags={"conta_corrente", "excluir", "remover"},
        required_parameters=[
            {"name": "nCodCC", "type": "int", "description": "Código da conta"},
            {"name": "cCodCCInt", "type": "str", "description": "Código interno da conta"}
        ],
        business_rules=[
            "Conta não pode ter saldo",
            "Conta não pode ter lançamentos",
            "Operação irreversível"
        ],
        limitations=[
            "Contas com movimentação não podem ser excluídas",
            "Operação irreversível"
        ]
    ))
    
    return tools

# =============================================================================
# SISTEMA DE CLASSIFICAÇÃO ENHANCED
# =============================================================================

class EnhancedToolClassificationSystem:
    """Sistema enhanced de classificação com novas tools"""
    
    def __init__(self):
        self.tools: Dict[str, OmieToolMetadata] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.endpoints: Dict[str, List[str]] = {}
        self.operations: Dict[OMIEOperationType, List[str]] = {}
        
    def register_tool(self, metadata: OmieToolMetadata) -> None:
        """Registra nova tool no sistema"""
        self.tools[metadata.name] = metadata
        
        # Indexar por categoria
        if metadata.category not in self.categories:
            self.categories[metadata.category] = []
        self.categories[metadata.category].append(metadata.name)
        
        # Indexar por endpoint
        if metadata.omie_endpoint not in self.endpoints:
            self.endpoints[metadata.omie_endpoint] = []
        self.endpoints[metadata.omie_endpoint].append(metadata.name)
        
        # Indexar por operação
        if metadata.omie_operation not in self.operations:
            self.operations[metadata.omie_operation] = []
        self.operations[metadata.omie_operation].append(metadata.name)
    
    def get_implementation_roadmap(self) -> Dict[str, Any]:
        """Gera roadmap de implementação baseado em prioridades"""
        
        roadmap = {
            "criticas": [],
            "altas": [],
            "medias": [],
            "baixas": []
        }
        
        for tool in self.tools.values():
            priority_map = {
                ToolPriority.CRITICA: "criticas",
                ToolPriority.ALTA: "altas", 
                ToolPriority.MEDIA: "medias",
                ToolPriority.BAIXA: "baixas"
            }
            
            priority_key = priority_map[tool.priority]
            roadmap[priority_key].append({
                "name": tool.name,
                "display_name": tool.display_name,
                "category": tool.category.value,
                "complexity": tool.complexity.value,
                "estimated_time_ms": tool.estimated_response_time_ms
            })
        
        return roadmap
    
    def generate_test_scenarios(self) -> Dict[str, Any]:
        """Gera cenários de teste para todas as tools"""
        
        scenarios = {}
        
        for tool_name, tool in self.tools.items():
            scenarios[tool_name] = {
                "basic_test": {
                    "description": f"Teste básico da tool {tool.display_name}",
                    "endpoint": tool.omie_endpoint,
                    "method": tool.omie_call,
                    "required_params": tool.required_parameters,
                    "expected_response_time": f"< {tool.estimated_response_time_ms}ms"
                },
                "validation_tests": tool.validation_rules,
                "business_rule_tests": tool.business_rules,
                "error_scenarios": list(tool.error_codes.keys()) if tool.error_codes else []
            }
        
        return scenarios

# =============================================================================
# INSTÂNCIA GLOBAL ENHANCED
# =============================================================================

# Criar sistema enhanced
enhanced_classification = EnhancedToolClassificationSystem()

# Registrar todas as novas tools
for tool in create_projeto_tools():
    enhanced_classification.register_tool(tool)

for tool in create_lancamento_tools():
    enhanced_classification.register_tool(tool)

for tool in create_conta_corrente_tools():
    enhanced_classification.register_tool(tool)

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_implementation_priority_order() -> List[str]:
    """Retorna ordem de implementação baseada em prioridade e dependências"""
    
    roadmap = enhanced_classification.get_implementation_roadmap()
    
    # Ordem: Críticas → Altas → Médias → Baixas
    priority_order = []
    
    for priority in ["criticas", "altas", "medias", "baixas"]:
        for tool in roadmap[priority]:
            priority_order.append(tool["name"])
    
    return priority_order

def export_classification_enhanced() -> str:
    """Exporta classificação enhanced em JSON"""
    
    export_data = {
        "metadata": {
            "total_tools": len(enhanced_classification.tools),
            "generated_at": datetime.now().isoformat(),
            "version": "2.0-enhanced"
        },
        "tools": {},
        "roadmap": enhanced_classification.get_implementation_roadmap(),
        "test_scenarios": enhanced_classification.generate_test_scenarios()
    }
    
    # Serializar tools
    for name, tool in enhanced_classification.tools.items():
        export_data["tools"][name] = {
            "name": tool.name,
            "display_name": tool.display_name,
            "description": tool.description,
            "category": tool.category.value,
            "type": tool.type.value,
            "complexity": tool.complexity.value,
            "priority": tool.priority.value,
            "status": tool.status.value,
            "omie_endpoint": tool.omie_endpoint,
            "omie_call": tool.omie_call,
            "omie_operation": tool.omie_operation.value,
            "tags": list(tool.tags),
            "required_parameters": tool.required_parameters,
            "optional_parameters": tool.optional_parameters,
            "business_rules": tool.business_rules,
            "use_cases": tool.use_cases,
            "estimated_response_time_ms": tool.estimated_response_time_ms
        }
    
    return json.dumps(export_data, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("🏷️ SISTEMA DE CLASSIFICAÇÃO ENHANCED - NOVAS TOOLS OMIE")
    print("=" * 70)
    
    print(f"📊 Total de Tools: {len(enhanced_classification.tools)}")
    
    print("\n📋 Por Categoria:")
    for category, tools in enhanced_classification.categories.items():
        print(f"   {category.value}: {len(tools)} tools")
    
    print("\n🔹 Por Operação Omie:")
    for operation, tools in enhanced_classification.operations.items():
        print(f"   {operation.value}: {len(tools)} tools")
    
    print("\n🎯 Ordem de Implementação:")
    priority_order = get_implementation_priority_order()
    for i, tool_name in enumerate(priority_order[:5], 1):
        tool = enhanced_classification.tools[tool_name]
        print(f"   {i}. {tool.display_name} ({tool.priority.value})")
    
    print(f"\n✅ Sistema enhanced criado com {len(enhanced_classification.tools)} tools")
    print("🔍 Use enhanced_classification para acessar todas as funcionalidades")
    print("📊 Use get_implementation_priority_order() para ordem de implementação")
    print("💾 Use export_classification_enhanced() para exportar dados completos")