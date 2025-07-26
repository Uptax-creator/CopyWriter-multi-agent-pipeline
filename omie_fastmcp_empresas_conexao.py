#!/usr/bin/env python3
"""
🎯 OMIE FASTMCP - FERRAMENTAS DE CONEXÃO E EMPRESAS
Implementa teste de conexão e listagem de empresas ativas
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
    from src.client.omie_client import OmieClient
except ImportError:
    print("Erro: Não foi possível importar OmieClient")
    sys.exit(1)

# Criar instância FastMCP
mcp = FastMCP("Omie ERP - Conexão e Empresas 🔌🏢")

# Instância global
omie_client = None

async def initialize_system():
    """Inicializa cliente Omie"""
    global omie_client
    if omie_client is None:
        omie_client = OmieClient()
    return omie_client

async def get_omie_client():
    """Obtém cliente Omie inicializado"""
    return await initialize_system()

def format_response(status: str, data: Any, **kwargs) -> str:
    """Formatar resposta padronizada"""
    response = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "data": data,
        **kwargs
    }
    
    return json.dumps(response, ensure_ascii=False, indent=2, default=str)

@mcp.tool()
async def teste_conexao() -> str:
    """
    Testa a conectividade com a API Omie ERP
    
    Implementação baseada no projeto anterior homologado.
    Realiza uma consulta simples para verificar conectividade.
    
    Returns:
        String com resultado do teste de conexão
        
    Examples:
        - teste_conexao() - "✅ Conexão com API Omie funcionando"
    """
    try:
        client = await get_omie_client()
        
        print("🔌 Testando conexão com API Omie...")
        
        # Usar a mesma estratégia do projeto anterior: testar com listar_clientes
        resultado = await client.listar_clientes({"pagina": 1, "registros_por_pagina": 1})
        
        if resultado:
            return "✅ Conexão com API Omie funcionando"
        else:
            return "❌ Erro na conexão: resposta vazia"
            
    except Exception as e:
        return f"❌ Erro na conexão: {str(e)}"

@mcp.tool()
async def listar_empresas_ativas() -> str:
    """
    Lista empresas ativas no Omie ERP
    
    Implementação baseada no projeto anterior homologado.
    Tenta acessar informações da empresa via API Omie.
    
    Returns:
        String com informações das empresas ativas
        
    Examples:
        - listar_empresas_ativas() - Lista empresas cadastradas
    """
    try:
        client = await get_omie_client()
        
        print("🏢 Consultando empresas ativas...")
        
        # Tentar endpoint de empresas
        try:
            resultado = await client._make_request("geral/empresas", "ListarEmpresas", {})
            
            if resultado:
                return f"🏢 Empresas encontradas: {len(resultado) if isinstance(resultado, list) else 1}\n\n📋 Dados: {str(resultado)[:500]}..."
            else:
                return "⚠️ Nenhuma empresa encontrada"
                
        except Exception as e:
            # Fallback: informações básicas
            test_result = await client.consultar_categorias({"pagina": 1, "registros_por_pagina": 1})
            if test_result:
                return "🏢 Empresa ativa detectada\n\n📋 API conectada e operacional\n💡 Para informações detalhadas, verificar permissões específicas"
            else:
                return f"❌ Erro ao consultar empresas: {str(e)[:100]}"
        
    except Exception as e:
        return f"❌ Erro ao listar empresas: {str(e)}"

@mcp.tool() 
async def dados_empresa_ativa() -> str:
    """
    Obtém dados detalhados da empresa ativa no Omie ERP
    
    Implementação baseada no projeto anterior homologado.
    Consulta informações específicas da empresa em uso.
    
    Returns:
        String com dados da empresa ativa
        
    Examples:
        - dados_empresa_ativa() - Mostra informações detalhadas da empresa
    """
    try:
        client = await get_omie_client()
        
        print("📊 Consultando dados da empresa ativa...")
        
        # Tentar diferentes endpoints para informações da empresa
        endpoints_empresa = [
            {"endpoint": "geral/empresas", "call": "ListarEmpresas"},
            {"endpoint": "geral/informacoes", "call": "InformacoesEmpresa"},
            {"endpoint": "geral/empresa", "call": "ConsultarEmpresa"}
        ]
        
        for endpoint_info in endpoints_empresa:
            try:
                resultado = await client._make_request(
                    endpoint_info["endpoint"], 
                    endpoint_info["call"], 
                    {}
                )
                
                if resultado:
                    # Processar dados da empresa
                    if isinstance(resultado, list) and len(resultado) > 0:
                        empresa = resultado[0]
                    elif isinstance(resultado, dict):
                        empresa = resultado
                    else:
                        continue
                    
                    # Formatar informações
                    info_empresa = []
                    info_empresa.append("📋 DADOS DA EMPRESA ATIVA")
                    info_empresa.append("=" * 30)
                    
                    # Informações básicas
                    if empresa.get("razao_social"):
                        info_empresa.append(f"🏢 Razão Social: {empresa['razao_social']}")
                    if empresa.get("nome_fantasia"):
                        info_empresa.append(f"🏪 Nome Fantasia: {empresa['nome_fantasia']}")
                    if empresa.get("cnpj_cpf") or empresa.get("cnpj"):
                        cnpj = empresa.get("cnpj_cpf", empresa.get("cnpj", ""))
                        info_empresa.append(f"📄 CNPJ: {cnpj}")
                    if empresa.get("inscricao_estadual"):
                        info_empresa.append(f"🆔 IE: {empresa['inscricao_estadual']}")
                    
                    # Informações de contato
                    if empresa.get("email"):
                        info_empresa.append(f"📧 Email: {empresa['email']}")
                    if empresa.get("telefone1_ddd") and empresa.get("telefone1_numero"):
                        tel = f"({empresa['telefone1_ddd']}) {empresa['telefone1_numero']}"
                        info_empresa.append(f"📞 Telefone: {tel}")
                    
                    # Endereço
                    endereco_parts = []
                    if empresa.get("endereco"):
                        endereco_parts.append(empresa["endereco"])
                    if empresa.get("endereco_numero"):
                        endereco_parts.append(empresa["endereco_numero"])
                    if empresa.get("bairro"):
                        endereco_parts.append(empresa["bairro"])
                    if empresa.get("cidade") and empresa.get("estado"):
                        endereco_parts.append(f"{empresa['cidade']}/{empresa['estado']}")
                    
                    if endereco_parts:
                        info_empresa.append(f"📍 Endereço: {', '.join(endereco_parts)}")
                    
                    # Status e outras informações
                    status = "ATIVA" if empresa.get("inativo", "N") == "N" else "INATIVA"
                    info_empresa.append(f"✅ Status: {status}")
                    
                    if empresa.get("regime_tributario"):
                        info_empresa.append(f"💼 Regime: {empresa['regime_tributario']}")
                    
                    return "\n".join(info_empresa)
                
            except Exception:
                continue
        
        # Fallback: informações básicas via teste
        try:
            test_result = await client.consultar_categorias({"pagina": 1, "registros_por_pagina": 1})
            if test_result:
                return "📋 DADOS DA EMPRESA ATIVA\n" + \
                       "=" * 30 + "\n" + \
                       "🏢 Empresa: Conectada e Operacional\n" + \
                       "✅ Status: ATIVA\n" + \
                       "📊 API: Funcionando\n\n" + \
                       "💡 Para dados detalhados, verificar permissões de acesso específicas"
            else:
                return "❌ Não foi possível obter dados da empresa"
                
        except Exception as e:
            return f"❌ Erro ao obter dados da empresa: {str(e)[:100]}"
        
    except Exception as e:
        return f"❌ Erro ao consultar dados da empresa: {str(e)}"

@mcp.tool()
async def status_sistema_omie() -> str:
    """
    Retorna status geral do sistema Omie ERP
    
    Combina teste de conexão e informações básicas da empresa
    para fornecer um panorama geral do sistema.
    
    Returns:
        JSON com status geral, conectividade e informações básicas
    """
    try:
        print("📊 Verificando status geral do sistema Omie...")
        
        start_time = datetime.now()
        
        # Executar testes em paralelo seria ideal, mas para simplicidade vamos fazer sequencial
        conexao_result = await teste_conexao()
        empresas_result = await listar_empresas_ativas()
        
        # Parse dos resultados JSON
        import json
        conexao_data = json.loads(conexao_result)
        empresas_data = json.loads(empresas_result)
        
        # Determinar status geral
        conexao_ok = conexao_data.get("status") == "success"
        empresas_ok = empresas_data.get("status") in ["success", "partial_success"]
        
        overall_status = "operational" if conexao_ok and empresas_ok else "issues_detected"
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return format_response(
            overall_status,
            {
                "connectivity": {
                    "status": "OK" if conexao_ok else "ISSUES",
                    "latency_ms": conexao_data.get("data", {}).get("connection_test", {}).get("latency_ms", 0)
                },
                "companies": {
                    "status": "OK" if empresas_ok else "LIMITED",
                    "active_companies": empresas_data.get("total_empresas_ativas", 0)
                },
                "system_health": {
                    "overall": "HEALTHY" if overall_status == "operational" else "DEGRADED",
                    "api_responsive": conexao_ok,
                    "data_accessible": empresas_ok
                }
            },
            total_execution_time_ms=round(total_time, 2),
            recommendations=[
                "Sistema operacional - todas as verificações OK" if overall_status == "operational"
                else "Algumas limitações detectadas - verificar logs específicos",
                "Conectividade adequada para uso em produção" if conexao_ok
                else "Problemas de conectividade requerem atenção"
            ]
        )
        
    except Exception as e:
        return format_response(
            "error",
            f"Erro ao verificar status do sistema: {str(e)}",
            error_type=type(e).__name__
        )

# Executar servidor se chamado diretamente
if __name__ == "__main__":
    print("🎯 OMIE FASTMCP - CONEXÃO E EMPRESAS")
    print("=" * 50)
    print("📊 Tools disponíveis:")
    print("   1. teste_conexao - Verifica conectividade com API Omie")
    print("   2. listar_empresas_ativas - Lista empresas ativas")
    print("   3. status_sistema_omie - Status geral do sistema")
    print()
    print("🚀 Iniciando servidor MCP...")
    
    mcp.run()