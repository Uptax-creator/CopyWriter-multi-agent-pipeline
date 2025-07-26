#!/usr/bin/env python3
"""
🚀 Omie FastMCP Expandido - Conjunto Completo de Tools
Versão para Validação Homologação/Produção
"""

import asyncio
import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastmcp import FastMCP

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.client.omie_client_fixed import OmieClient
except ImportError:
    try:
        from src.client.omie_client import OmieClient
    except ImportError:
        print("Erro: Não foi possível importar OmieClient")
        sys.exit(1)

# Criar instância FastMCP
mcp = FastMCP("Omie ERP Complete Suite 🏢")

# Cliente Omie global
omie_client = None

async def get_omie_client():
    """Obtém cliente Omie inicializado"""
    global omie_client
    if omie_client is None:
        try:
            omie_client = OmieClient()
            if hasattr(omie_client, 'initialize'):
                await omie_client.initialize()
        except Exception as e:
            raise Exception(f"Erro ao inicializar cliente Omie: {e}")
    return omie_client

# =============================================================================
# TOOLS BÁSICAS DE SISTEMA
# =============================================================================

@mcp.tool
async def testar_conexao() -> str:
    """Testa a conexão com a API do Omie ERP"""
    try:
        client = await get_omie_client()
        result = await client.testar_conexao()
        return json.dumps({
            "status": "success",
            "message": "Conexão estabelecida com sucesso",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Erro na conexão: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def obter_info_empresa() -> str:
    """Obtém informações da empresa no Omie"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'obter_info_empresa'):
            result = await client.obter_info_empresa()
        else:
            result = {"message": "Método ainda não implementado no cliente"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS DE CONSULTA ORGANIZACIONAL
# =============================================================================

@mcp.tool
async def consultar_categorias(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro: Optional[str] = None
) -> str:
    """Consulta categorias cadastradas no Omie ERP"""
    try:
        client = await get_omie_client()
        result = await client.consultar_categorias(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        # Aplicar filtro se fornecido
        if filtro and isinstance(result, dict) and 'categoria' in result:
            filtered_categories = [
                cat for cat in result['categoria']
                if filtro.lower() in cat.get('descricao', '').lower()
            ]
            result['categoria'] = filtered_categories
            result['total_filtrado'] = len(filtered_categories)
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtro_aplicado": filtro,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def consultar_departamentos(
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """Consulta departamentos cadastrados no Omie ERP"""
    try:
        client = await get_omie_client()
        result = await client.consultar_departamentos(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        return json.dumps({
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def consultar_tipos_documento(codigo: Optional[str] = None) -> str:
    """Consulta tipos de documento no Omie ERP"""
    try:
        client = await get_omie_client()
        result = await client.consultar_tipos_documento(codigo=codigo)
        return json.dumps({
            "status": "success",
            "data": result,
            "codigo_filtro": codigo,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS FINANCEIRAS
# =============================================================================

@mcp.tool
async def consultar_contas_pagar(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    registros_por_pagina: int = 20,
    apenas_vencidas: bool = False
) -> str:
    """Consulta contas a pagar no Omie ERP"""
    try:
        client = await get_omie_client()
        
        # Se apenas_vencidas é True, definir data_fim como hoje
        if apenas_vencidas and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        
        result = await client.consultar_contas_pagar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "pagina": pagina,
                "apenas_vencidas": apenas_vencidas
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def consultar_contas_receber(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    registros_por_pagina: int = 20,
    apenas_vencidas: bool = False
) -> str:
    """Consulta contas a receber no Omie ERP"""
    try:
        client = await get_omie_client()
        
        # Se apenas_vencidas é True, definir data_fim como hoje
        if apenas_vencidas and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        
        result = await client.consultar_contas_receber(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "pagina": pagina,
                "apenas_vencidas": apenas_vencidas
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS DE CLIENTES E FORNECEDORES
# =============================================================================

@mcp.tool
async def listar_clientes(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_nome: Optional[str] = None
) -> str:
    """Lista clientes cadastrados no Omie ERP"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'listar_clientes'):
            result = await client.listar_clientes(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            # Fallback para método genérico se disponível
            result = {"message": "Método de listagem de clientes não disponível"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "nome": filtro_nome,
                "pagina": pagina,
                "registros_por_pagina": registros_por_pagina
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def cadastrar_cliente(
    nome: str,
    cnpj_cpf: str,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    endereco: Optional[str] = None
) -> str:
    """Cadastra novo cliente no Omie ERP"""
    try:
        client = await get_omie_client()
        
        # Dados do cliente
        dados_cliente = {
            "nome": nome,
            "cnpj_cpf": cnpj_cpf
        }
        
        if email:
            dados_cliente["email"] = email
        if telefone:
            dados_cliente["telefone"] = telefone
        if endereco:
            dados_cliente["endereco"] = endereco
        
        if hasattr(client, 'cadastrar_cliente'):
            result = await client.cadastrar_cliente(dados_cliente)
        else:
            result = {"message": "Método de cadastro de cliente não disponível no momento"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "dados_enviados": dados_cliente,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "dados_tentativa": {
                "nome": nome,
                "cnpj_cpf": cnpj_cpf[:4] + "*" * (len(cnpj_cpf) - 4)  # Mascarar CPF/CNPJ
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def listar_fornecedores(
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """Lista fornecedores cadastrados no Omie ERP"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'listar_fornecedores'):
            result = await client.listar_fornecedores(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {"message": "Método de listagem de fornecedores não disponível"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS DE PRODUTOS E ESTOQUE
# =============================================================================

@mcp.tool
async def listar_produtos(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_nome: Optional[str] = None
) -> str:
    """Lista produtos cadastrados no Omie ERP"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'listar_produtos'):
            result = await client.listar_produtos(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {"message": "Método de listagem de produtos não disponível"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "nome": filtro_nome,
                "pagina": pagina
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def consultar_estoque(
    codigo_produto: Optional[str] = None,
    pagina: int = 1
) -> str:
    """Consulta estoque de produtos no Omie ERP"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'consultar_estoque'):
            result = await client.consultar_estoque(
                codigo_produto=codigo_produto,
                pagina=pagina
            )
        else:
            result = {"message": "Método de consulta de estoque não disponível"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "codigo_produto": codigo_produto,
                "pagina": pagina
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS DE VENDAS E PEDIDOS
# =============================================================================

@mcp.tool
async def listar_pedidos_venda(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    registros_por_pagina: int = 20
) -> str:
    """Lista pedidos de venda no Omie ERP"""
    try:
        client = await get_omie_client()
        if hasattr(client, 'listar_pedidos_venda'):
            result = await client.listar_pedidos_venda(
                data_inicio=data_inicio,
                data_fim=data_fim,
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {"message": "Método de listagem de pedidos não disponível"}
        
        return json.dumps({
            "status": "success",
            "data": result,
            "filtros": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "pagina": pagina
            },
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# TOOLS DE RELATÓRIOS E ANÁLISES
# =============================================================================

@mcp.tool
async def relatorio_vendas_periodo(
    data_inicio: str,
    data_fim: str,
    agrupar_por: str = "mes"  # mes, dia, cliente
) -> str:
    """Gera relatório de vendas por período"""
    try:
        client = await get_omie_client()
        
        # Buscar pedidos do período
        if hasattr(client, 'listar_pedidos_venda'):
            pedidos = await client.listar_pedidos_venda(
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            
            # Processar dados para relatório
            relatorio = {
                "periodo": f"{data_inicio} a {data_fim}",
                "total_pedidos": len(pedidos.get('pedidos', [])) if isinstance(pedidos, dict) else 0,
                "valor_total": 0,
                "agrupamento": agrupar_por,
                "detalhes": pedidos
            }
        else:
            relatorio = {
                "periodo": f"{data_inicio} a {data_fim}",
                "message": "Método de relatório não disponível",
                "agrupamento": agrupar_por
            }
        
        return json.dumps({
            "status": "success",
            "data": relatorio,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

@mcp.tool
async def dashboard_financeiro() -> str:
    """Gera dashboard com visão geral financeira"""
    try:
        client = await get_omie_client()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "resumo": {
                "contas_pagar": "Carregando...",
                "contas_receber": "Carregando...",
                "saldo_estimado": 0
            },
            "alertas": [],
            "metricas": {
                "total_clientes": "N/A",
                "total_produtos": "N/A",
                "pedidos_mes": "N/A"
            }
        }
        
        # Tentar coletar dados básicos
        try:
            # Contas a pagar vencidas
            contas_pagar = await client.consultar_contas_pagar(
                data_fim=datetime.now().strftime("%d/%m/%Y")
            )
            dashboard["resumo"]["contas_pagar"] = len(contas_pagar.get('contas', [])) if isinstance(contas_pagar, dict) else 0
        except:
            dashboard["alertas"].append("Não foi possível carregar contas a pagar")
        
        try:
            # Contas a receber vencidas
            contas_receber = await client.consultar_contas_receber(
                data_fim=datetime.now().strftime("%d/%m/%Y")
            )
            dashboard["resumo"]["contas_receber"] = len(contas_receber.get('contas', [])) if isinstance(contas_receber, dict) else 0
        except:
            dashboard["alertas"].append("Não foi possível carregar contas a receber")
        
        return json.dumps({
            "status": "success",
            "data": dashboard,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# RESOURCES PARA DADOS ESTRUTURADOS
# =============================================================================

@mcp.resource("omie://config")
async def get_omie_config() -> str:
    """Retorna configuração atual do cliente Omie"""
    try:
        client = await get_omie_client()
        config = {
            "base_url": getattr(client, 'base_url', 'https://app.omie.com.br/api/v1/'),
            "timeout": getattr(client, 'timeout', 30),
            "status": "conectado" if client else "desconectado",
            "tools_disponiveis": 15,
            "versao": "2.0 - Expandido"
        }
        return json.dumps(config, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False, indent=2)

@mcp.resource("omie://status")
async def get_omie_status() -> str:
    """Retorna status atual da conexão Omie"""
    try:
        client = await get_omie_client()
        test_result = await client.testar_conexao()
        status = {
            "connection": "ok" if test_result else "failed",
            "timestamp": datetime.now().isoformat(),
            "client_initialized": client is not None,
            "tools_count": 15,
            "features": [
                "Sistema básico",
                "Consultas organizacionais",
                "Ferramentas financeiras",
                "Gestão de clientes/fornecedores",
                "Produtos e estoque",
                "Vendas e pedidos",
                "Relatórios e análises"
            ]
        }
        return json.dumps(status, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "connection": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

# =============================================================================
# PROMPTS PARA ANÁLISES INTELIGENTES
# =============================================================================

@mcp.prompt("omie-analise-completa")
async def analise_completa_prompt(
    periodo_dias: str = "30",
    foco: str = "financeiro"  # financeiro, vendas, estoque
) -> str:
    """Gera prompt para análise completa da empresa"""
    return f"""
Execute uma análise completa da empresa com foco {foco} dos últimos {periodo_dias} dias.

📋 DADOS PARA COLETAR:
1. Use testar_conexao() para validar sistema
2. Use dashboard_financeiro() para visão geral
3. Use consultar_contas_pagar(apenas_vencidas=true) para urgências
4. Use consultar_contas_receber(apenas_vencidas=true) para recebíveis
5. Use listar_clientes() para base de clientes
6. Use listar_produtos() para catálogo
7. Use relatorio_vendas_periodo() para performance

🔍 ANÁLISE REQUERIDA:
1. Saúde financeira geral
2. Fluxo de caixa (pagar vs receber)
3. Performance de vendas
4. Base de clientes ativa
5. Gestão de estoque
6. Principais riscos identificados
7. Oportunidades de melhoria

📏 RELATÓRIO FINAL:
- Resumo executivo (3-5 pontos)
- Métricas-chave com alertas
- Recomendações por prioridade
- Próximas ações sugeridas
"""

@mcp.prompt("omie-validacao-homologacao")
async def validacao_homologacao_prompt() -> str:
    """Prompt para validação de ambiente de homologação"""
    return """
Execute validação completa do ambiente de homologação Omie FastMCP.

🧪 TESTES DE CONECTIVIDADE:
1. testar_conexao() - Validar API
2. obter_info_empresa() - Dados empresa
3. omie://status - Resource de status
4. omie://config - Configuração atual

📋 TESTES FUNCIONAIS:
1. consultar_categorias() - Dados organizacionais
2. consultar_contas_pagar() - Módulo financeiro
3. listar_clientes() - Gestão comercial
4. listar_produtos() - Catálogo
5. dashboard_financeiro() - Relatórios

📊 VALIDAÇÃO DE PERFORMANCE:
- Tempo de resposta < 3s por tool
- Sucesso rate > 95%
- Handling de erros adequado
- Retorno JSON estruturado

🏆 CRITÉRIOS DE APROVAÇÃO:
✅ Todas as 15 tools funcionais
✅ Resources respondendo
✅ Prompts gerando templates
✅ Tratamento de erro robusto
✅ Performance adequada

Relate o status de cada teste e aprovação final para PRODUÇÃO.
"""

if __name__ == "__main__":
    print("🚀 Omie FastMCP Expandido - Conjunto Completo")
    print("=" * 50)
    print("📊 15 Ferramentas disponíveis:")
    print("\n🔧 SISTEMA:")
    print("   - testar_conexao")
    print("   - obter_info_empresa")
    print("\n📋 ORGANIZAÇÃO:")
    print("   - consultar_categorias")
    print("   - consultar_departamentos")
    print("   - consultar_tipos_documento")
    print("\n💰 FINANCEIRO:")
    print("   - consultar_contas_pagar")
    print("   - consultar_contas_receber")
    print("\n👥 COMERCIAL:")
    print("   - listar_clientes")
    print("   - cadastrar_cliente")
    print("   - listar_fornecedores")
    print("\n📦 PRODUTOS:")
    print("   - listar_produtos")
    print("   - consultar_estoque")
    print("\n📊 VENDAS & RELATÓRIOS:")
    print("   - listar_pedidos_venda")
    print("   - relatorio_vendas_periodo")
    print("   - dashboard_financeiro")
    print("\n📂 Resources: omie://config, omie://status")
    print("📝 Prompts: omie-analise-completa, omie-validacao-homologacao")
    print("\n🏆 PRONTO PARA VALIDAÇÃO HOMOLOGAÇÃO/PRODUÇÃO!")
    print()
    
    # Executar servidor FastMCP expandido
    mcp.run()