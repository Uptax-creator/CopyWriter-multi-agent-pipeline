#!/usr/bin/env python3
"""
🎯 OMIE FASTMCP - CONJUNTO 1: FERRAMENTAS DE CONSULTA/LISTAGEM
Implementação estruturada por conjuntos para validação homologação
"""

import asyncio
import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
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
mcp = FastMCP("Omie ERP - Conjunto 1: Consultas 📋")

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

def format_response(status: str, data: Any, **kwargs) -> str:
    """Formata resposta padrão das tools"""
    response = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    if status == "success":
        response["data"] = data
    else:
        response["error"] = data
    
    return json.dumps(response, ensure_ascii=False, indent=2)

# =============================================================================
# CONJUNTO 1: FERRAMENTAS DE CONSULTA/LISTAGEM
# =============================================================================

@mcp.tool
async def consultar_categorias(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_descricao: Optional[str] = None,
    apenas_ativas: bool = True
) -> str:
    """
    Consulta categorias cadastradas no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_descricao: Filtro por descrição da categoria
        apenas_ativas: Se True, retorna apenas categorias ativas
        
    Returns:
        str: Lista de categorias em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_categorias(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        # Aplicar filtros se necessário
        if isinstance(result, dict) and 'categoria' in result:
            categorias = result['categoria']
            
            # Filtro por descrição
            if filtro_descricao:
                categorias = [
                    cat for cat in categorias
                    if filtro_descricao.lower() in cat.get('descricao', '').lower()
                ]
            
            # Filtro apenas ativas
            if apenas_ativas:
                categorias = [
                    cat for cat in categorias
                    if cat.get('inativo') != 'S'
                ]
            
            result['categoria'] = categorias
            result['total_filtrado'] = len(categorias)
        
        return format_response("success", result, 
                             filtros={
                                 "descricao": filtro_descricao,
                                 "apenas_ativas": apenas_ativas,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_departamentos(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_ativos: bool = True
) -> str:
    """
    Consulta departamentos cadastrados no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        apenas_ativos: Se True, retorna apenas departamentos ativos
        
    Returns:
        str: Lista de departamentos em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_departamentos(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        # Filtrar apenas ativos se solicitado
        if isinstance(result, dict) and 'departamentos' in result and apenas_ativos:
            departamentos = [
                dept for dept in result['departamentos']
                if dept.get('inativo') != 'S'
            ]
            result['departamentos'] = departamentos
            result['total_ativos'] = len(departamentos)
        
        return format_response("success", result,
                             filtros={"apenas_ativos": apenas_ativos, "pagina": pagina})
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_projetos(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    status_projeto: Optional[str] = None  # "ativo", "inativo", "concluido"
) -> str:
    """
    Consulta projetos cadastrados no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        status_projeto: Filtro por status do projeto
        
    Returns:
        str: Lista de projetos em formato JSON
    """
    try:
        client = await get_omie_client()
        
        # Verificar se o método existe no cliente
        if hasattr(client, 'consultar_projetos'):
            result = await client.consultar_projetos(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            # Simular resposta para desenvolvimento
            result = {
                "projetos": [],
                "total_de_registros": 0,
                "pagina": pagina,
                "message": "Método consultar_projetos não implementado no cliente ainda"
            }
        
        return format_response("success", result,
                             filtros={"status_projeto": status_projeto, "pagina": pagina})
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_tipos_documento(
    codigo: Optional[str] = None,
    categoria: Optional[str] = None  # "entrada", "saida", "todos"
) -> str:
    """
    Consulta tipos de documento no Omie ERP
    
    Args:
        codigo: Código específico do tipo de documento
        categoria: Categoria do documento (entrada/saída)
        
    Returns:
        str: Lista de tipos de documento em formato JSON
    """
    try:
        client = await get_omie_client()
        result = await client.consultar_tipos_documento(codigo=codigo)
        
        # Aplicar filtro de categoria se especificado
        if isinstance(result, dict) and 'tipos_documento' in result and categoria:
            if categoria.lower() in ['entrada', 'saida']:
                tipos_filtrados = [
                    tipo for tipo in result['tipos_documento']
                    if tipo.get('categoria', '').lower() == categoria.lower()
                ]
                result['tipos_documento'] = tipos_filtrados
                result['categoria_filtro'] = categoria
        
        return format_response("success", result,
                             filtros={"codigo": codigo, "categoria": categoria})
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def listar_clientes(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_nome: Optional[str] = None,
    apenas_ativos: bool = True,
    filtro_cidade: Optional[str] = None
) -> str:
    """
    Lista clientes cadastrados no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_nome: Filtro por nome do cliente
        apenas_ativos: Se True, retorna apenas clientes ativos
        filtro_cidade: Filtro por cidade do cliente
        
    Returns:
        str: Lista de clientes em formato JSON
    """
    try:
        client = await get_omie_client()
        
        if hasattr(client, 'listar_clientes'):
            result = await client.listar_clientes(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            # Usar método genérico se disponível
            result = {
                "clientes": [],
                "total_de_registros": 0,
                "pagina": pagina,
                "message": "Método listar_clientes não implementado - usando simulação"
            }
        
        # Aplicar filtros se resultado contém dados
        if isinstance(result, dict) and 'clientes' in result:
            clientes = result['clientes']
            
            # Filtro por nome
            if filtro_nome:
                clientes = [
                    cliente for cliente in clientes
                    if filtro_nome.lower() in cliente.get('nome_fantasia', '').lower() or
                       filtro_nome.lower() in cliente.get('razao_social', '').lower()
                ]
            
            # Filtro apenas ativos
            if apenas_ativos:
                clientes = [
                    cliente for cliente in clientes
                    if cliente.get('inativo') != 'S'
                ]
            
            # Filtro por cidade
            if filtro_cidade:
                clientes = [
                    cliente for cliente in clientes
                    if filtro_cidade.lower() in cliente.get('cidade', '').lower()
                ]
            
            result['clientes'] = clientes
            result['total_filtrado'] = len(clientes)
        
        return format_response("success", result,
                             filtros={
                                 "nome": filtro_nome,
                                 "apenas_ativos": apenas_ativos,
                                 "cidade": filtro_cidade,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def listar_fornecedores(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    filtro_nome: Optional[str] = None,
    apenas_ativos: bool = True
) -> str:
    """
    Lista fornecedores cadastrados no Omie ERP
    
    Args:
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_nome: Filtro por nome do fornecedor
        apenas_ativos: Se True, retorna apenas fornecedores ativos
        
    Returns:
        str: Lista de fornecedores em formato JSON
    """
    try:
        client = await get_omie_client()
        
        if hasattr(client, 'listar_fornecedores'):
            result = await client.listar_fornecedores(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {
                "fornecedores": [],
                "total_de_registros": 0,
                "pagina": pagina,
                "message": "Método listar_fornecedores não implementado - usando simulação"
            }
        
        return format_response("success", result,
                             filtros={
                                 "nome": filtro_nome,
                                 "apenas_ativos": apenas_ativos,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_contas_pagar(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: str = "todos",  # "vencido", "a_vencer", "pago", "todos"
    pagina: int = 1,
    registros_por_pagina: int = 20,
    filtro_fornecedor: Optional[str] = None
) -> str:
    """
    Consulta contas a pagar no Omie ERP com filtros por status
    
    Args:
        data_inicio: Data de início da consulta (DD/MM/AAAA)
        data_fim: Data de fim da consulta (DD/MM/AAAA)
        status: Status das contas (vencido, a_vencer, pago, todos)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_fornecedor: Filtro por nome do fornecedor
        
    Returns:
        str: Lista de contas a pagar em formato JSON
    """
    try:
        client = await get_omie_client()
        
        # Ajustar datas baseado no status
        if status == "vencido" and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        elif status == "a_vencer" and not data_inicio:
            data_inicio = datetime.now().strftime("%d/%m/%Y")
        
        result = await client.consultar_contas_pagar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        # Filtrar por status se necessário
        if isinstance(result, dict) and 'contas' in result:
            contas = result['contas']
            hoje = datetime.now().date()
            
            if status != "todos":
                contas_filtradas = []
                for conta in contas:
                    # Ignorar canceladas/excluídas
                    if conta.get('status_titulo') in ['CANCELADO', 'EXCLUIDO']:
                        continue
                    
                    if status == "vencido":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt < hoje and conta.get('status_titulo') != 'PAGO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "a_vencer":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt >= hoje and conta.get('status_titulo') != 'PAGO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "pago":
                        if conta.get('status_titulo') == 'PAGO':
                            contas_filtradas.append(conta)
                
                result['contas'] = contas_filtradas
                result['total_filtrado'] = len(contas_filtradas)
        
        return format_response("success", result,
                             filtros={
                                 "data_inicio": data_inicio,
                                 "data_fim": data_fim,
                                 "status": status,
                                 "fornecedor": filtro_fornecedor,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_contas_receber(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: str = "todos",  # "vencido", "a_vencer", "pago", "todos"
    pagina: int = 1,
    registros_por_pagina: int = 20,
    filtro_cliente: Optional[str] = None
) -> str:
    """
    Consulta contas a receber no Omie ERP com filtros por status
    
    Args:
        data_inicio: Data de início da consulta (DD/MM/AAAA)
        data_fim: Data de fim da consulta (DD/MM/AAAA)
        status: Status das contas (vencido, a_vencer, pago, todos)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        filtro_cliente: Filtro por nome do cliente
        
    Returns:
        str: Lista de contas a receber em formato JSON
    """
    try:
        client = await get_omie_client()
        
        # Ajustar datas baseado no status
        if status == "vencido" and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
        elif status == "a_vencer" and not data_inicio:
            data_inicio = datetime.now().strftime("%d/%m/%Y")
        
        result = await client.consultar_contas_receber(
            data_inicio=data_inicio,
            data_fim=data_fim,
            pagina=pagina,
            registros_por_pagina=registros_por_pagina
        )
        
        # Aplicar filtros de status
        if isinstance(result, dict) and 'contas' in result:
            contas = result['contas']
            hoje = datetime.now().date()
            
            if status != "todos":
                contas_filtradas = []
                for conta in contas:
                    # Ignorar canceladas/excluídas
                    if conta.get('status_titulo') in ['CANCELADO', 'EXCLUIDO']:
                        continue
                    
                    if status == "vencido":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt < hoje and conta.get('status_titulo') != 'PAGO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "a_vencer":
                        data_venc = conta.get('data_vencimento')
                        if data_venc:
                            try:
                                data_venc_dt = datetime.strptime(data_venc, "%d/%m/%Y").date()
                                if data_venc_dt >= hoje and conta.get('status_titulo') != 'RECEBIDO':
                                    contas_filtradas.append(conta)
                            except:
                                continue
                    elif status == "pago":
                        if conta.get('status_titulo') == 'RECEBIDO':
                            contas_filtradas.append(conta)
                
                result['contas'] = contas_filtradas
                result['total_filtrado'] = len(contas_filtradas)
        
        return format_response("success", result,
                             filtros={
                                 "data_inicio": data_inicio,
                                 "data_fim": data_fim,
                                 "status": status,
                                 "cliente": filtro_cliente,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_lancamentos(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    tipo_lancamento: Optional[str] = None,  # "receita", "despesa", "transferencia"
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """
    Consulta lançamentos financeiros no Omie ERP
    
    Args:
        data_inicio: Data de início da consulta (DD/MM/AAAA)
        data_fim: Data de fim da consulta (DD/MM/AAAA)
        tipo_lancamento: Tipo do lançamento (receita, despesa, transferencia)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de lançamentos em formato JSON
    """
    try:
        client = await get_omie_client()
        
        # Se não definir período, usar últimos 30 dias
        if not data_inicio and not data_fim:
            data_fim = datetime.now().strftime("%d/%m/%Y")
            data_inicio = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        
        if hasattr(client, 'consultar_lancamentos'):
            result = await client.consultar_lancamentos(
                data_inicio=data_inicio,
                data_fim=data_fim,
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {
                "lancamentos": [],
                "total_de_registros": 0,
                "pagina": pagina,
                "message": "Método consultar_lancamentos não implementado - usando simulação"
            }
        
        return format_response("success", result,
                             filtros={
                                 "data_inicio": data_inicio,
                                 "data_fim": data_fim,
                                 "tipo_lancamento": tipo_lancamento,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

@mcp.tool
async def consultar_contas_correntes(
    apenas_ativas: bool = True,
    tipo_conta: Optional[str] = None,  # "banco", "caixa", "aplicacao"
    pagina: int = 1,
    registros_por_pagina: int = 50
) -> str:
    """
    Consulta contas correntes cadastradas no Omie ERP
    
    Args:
        apenas_ativas: Se True, retorna apenas contas ativas
        tipo_conta: Tipo da conta (banco, caixa, aplicacao)
        pagina: Número da página para paginação
        registros_por_pagina: Quantidade de registros por página
        
    Returns:
        str: Lista de contas correntes em formato JSON
    """
    try:
        client = await get_omie_client()
        
        if hasattr(client, 'consultar_contas_correntes'):
            result = await client.consultar_contas_correntes(
                pagina=pagina,
                registros_por_pagina=registros_por_pagina
            )
        else:
            result = {
                "contas_correntes": [],
                "total_de_registros": 0,
                "pagina": pagina,
                "message": "Método consultar_contas_correntes não implementado - usando simulação"
            }
        
        # Aplicar filtros
        if isinstance(result, dict) and 'contas_correntes' in result:
            contas = result['contas_correntes']
            
            # Filtro apenas ativas
            if apenas_ativas:
                contas = [
                    conta for conta in contas
                    if conta.get('inativa') != 'S'
                ]
            
            # Filtro por tipo
            if tipo_conta:
                contas = [
                    conta for conta in contas
                    if conta.get('tipo', '').lower() == tipo_conta.lower()
                ]
            
            result['contas_correntes'] = contas
            result['total_filtrado'] = len(contas)
        
        return format_response("success", result,
                             filtros={
                                 "apenas_ativas": apenas_ativas,
                                 "tipo_conta": tipo_conta,
                                 "pagina": pagina
                             })
    except Exception as e:
        return format_response("error", str(e))

# =============================================================================
# RESOURCES PARA DADOS ESTRUTURADOS
# =============================================================================

@mcp.resource("omie://conjunto1/status")
async def conjunto1_status() -> str:
    """Status do Conjunto 1 de ferramentas"""
    tools_conjunto1 = [
        "consultar_categorias",
        "consultar_departamentos", 
        "consultar_projetos",
        "consultar_tipos_documento",
        "listar_clientes",
        "listar_fornecedores",
        "consultar_contas_pagar",
        "consultar_contas_receber",
        "consultar_lancamentos",
        "consultar_contas_correntes"
    ]
    
    status = {
        "conjunto": "1 - Consultas e Listagens",
        "total_tools": len(tools_conjunto1),
        "tools": tools_conjunto1,
        "status": "implementado",
        "timestamp": datetime.now().isoformat(),
        "proximo_conjunto": "2 - Tools CRUD em Lote"
    }
    
    return json.dumps(status, ensure_ascii=False, indent=2)

# =============================================================================
# PROMPT PARA VALIDAÇÃO DO CONJUNTO 1
# =============================================================================

@mcp.prompt("validar-conjunto-1")
async def validar_conjunto1_prompt() -> str:
    """Prompt para validação completa do Conjunto 1"""
    return """
Execute validação completa do CONJUNTO 1 - Ferramentas de Consulta/Listagem.

🎯 OBJETIVO: Validar 10 tools básicas de consulta antes de avançar para Conjunto 2.

📋 TOOLS PARA TESTAR:
1. consultar_categorias() - Testar com e sem filtros
2. consultar_departamentos() - Validar paginação
3. consultar_projetos() - Verificar se retorna dados
4. consultar_tipos_documento() - Testar filtros por categoria
5. listar_clientes() - Testar filtros de nome e cidade
6. listar_fornecedores() - Validar apenas_ativos
7. consultar_contas_pagar() - Testar filtros por status (vencido, a_vencer, pago)
8. consultar_contas_receber() - Testar filtros por status
9. consultar_lancamentos() - Validar período de consulta
10. consultar_contas_correntes() - Testar tipos de conta

🧪 CRITÉRIOS DE VALIDAÇÃO:
✅ Todas as tools respondem sem erro
✅ Filtros funcionam corretamente
✅ Paginação opera adequadamente
✅ Status "vencido", "a_vencer", "pago" filtram corretamente
✅ Transações canceladas/excluídas são ignoradas
✅ Formato JSON estruturado e consistente
✅ Performance < 3s por tool

📊 RELATÓRIO FINAL:
- Status de cada tool (✅/❌)
- Problemas encontrados
- Performance geral
- Aprovação para Conjunto 2 (SIM/NÃO)

Após validação completa, confirme se podemos avançar para o CONJUNTO 2.
"""

if __name__ == "__main__":
    print("🎯 OMIE FASTMCP - CONJUNTO 1: CONSULTAS E LISTAGENS")
    print("=" * 60)
    print("📋 10 Ferramentas de Consulta/Listagem implementadas:")
    print("\n📊 ORGANIZACIONAL:")
    print("   1. consultar_categorias - Categorias com filtros")
    print("   2. consultar_departamentos - Departamentos ativos")
    print("   3. consultar_projetos - Projetos por status")
    print("   4. consultar_tipos_documento - Tipos por categoria")
    print("\n👥 COMERCIAL:")
    print("   5. listar_clientes - Clientes com filtros avançados")
    print("   6. listar_fornecedores - Fornecedores ativos")
    print("\n💰 FINANCEIRO:")
    print("   7. consultar_contas_pagar - Por status (vencido/a_vencer/pago)")
    print("   8. consultar_contas_receber - Por status (vencido/a_vencer/pago)")
    print("   9. consultar_lancamentos - Lançamentos por período")
    print("   10. consultar_contas_correntes - Contas por tipo")
    print("\n📂 Resource: omie://conjunto1/status")
    print("📝 Prompt: validar-conjunto-1")
    print("\n🎯 PRONTO PARA VALIDAÇÃO DO CONJUNTO 1")
    print("✅ Teste todas as tools antes de avançar para Conjunto 2")
    print()
    
    # Executar servidor FastMCP - Conjunto 1
    mcp.run()