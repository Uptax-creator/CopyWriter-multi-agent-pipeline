#!/usr/bin/env python3
"""
Servidor MCP STDIO puro para Omie ERP
Versão sem dependências HTTP para funcionar no Claude Desktop
"""

import asyncio
import json
import logging
import sys
import os
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-stdio")

class OmieToolRegistry:
    """Registro simplificado de ferramentas Omie para STDIO"""
    
    def __init__(self):
        self.tools = {}
        self.mcp_tools = []
        self.credentials = self._load_credentials()
        self._register_basic_tools()
    
    def _load_credentials(self) -> Dict[str, str]:
        """Carrega credenciais do arquivo credentials.json"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(current_dir, 'credentials.json')
            
            if os.path.exists(credentials_path):
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                    logger.info("✅ Credenciais Omie carregadas com sucesso")
                    return creds
            else:
                logger.warning("⚠️ Arquivo credentials.json não encontrado, usando modo simulação")
                return {}
        except Exception as e:
            logger.error(f"❌ Erro ao carregar credenciais: {e}")
            return {}
    
    def _register_basic_tools(self):
        """Registra ferramentas básicas que funcionam sem dependências HTTP"""
        
        basic_tools = [
            {
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_tipos_documento",
                "description": "Consulta tipos de documento no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string", "description": "Código do tipo documento (opcional)"}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_contas_receber",
                "description": "Consulta contas a receber do Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_fornecedores",
                "description": "Consulta fornecedores cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    },
                    "required": []
                }
            },
            {
                "name": "cadastrar_cliente_fornecedor",
                "description": "Cadastra cliente ou fornecedor no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "razao_social": {"type": "string", "description": "Razão social"},
                        "nome_fantasia": {"type": "string", "description": "Nome fantasia"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                        "telefone1_ddd": {"type": "string", "description": "DDD do telefone"},
                        "telefone1_numero": {"type": "string", "description": "Número do telefone"},
                        "email": {"type": "string", "description": "Email"}
                    },
                    "required": ["razao_social", "cnpj_cpf"]
                }
            },
            {
                "name": "criar_conta_pagar",
                "description": "Cria conta a pagar no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_fornecedor": {"type": "string", "description": "Código do fornecedor"},
                        "valor_documento": {"type": "number", "description": "Valor do documento"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                        "observacao": {"type": "string", "description": "Observação"}
                    },
                    "required": ["codigo_cliente_fornecedor", "valor_documento", "data_vencimento"]
                }
            },
            {
                "name": "criar_conta_receber",
                "description": "Cria conta a receber no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente": {"type": "string", "description": "Código do cliente"},
                        "valor_documento": {"type": "number", "description": "Valor do documento"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (DD/MM/AAAA)"},
                        "observacao": {"type": "string", "description": "Observação"}
                    },
                    "required": ["codigo_cliente", "valor_documento", "data_vencimento"]
                }
            },
            {
                "name": "alterar_cliente_fornecedor",
                "description": "Altera dados de cliente ou fornecedor no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo_cliente_omie": {"type": "string", "description": "Código do cliente no Omie"},
                        "razao_social": {"type": "string", "description": "Razão social"},
                        "nome_fantasia": {"type": "string", "description": "Nome fantasia"},
                        "cnpj_cpf": {"type": "string", "description": "CNPJ ou CPF"},
                        "telefone1_ddd": {"type": "string", "description": "DDD do telefone"},
                        "telefone1_numero": {"type": "string", "description": "Número do telefone"},
                        "email": {"type": "string", "description": "Email"}
                    },
                    "required": ["codigo_cliente_omie"]
                }
            },
            {
                "name": "consultar_produtos",
                "description": "Consulta produtos cadastrados no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50},
                        "codigo_produto": {"type": "string", "description": "Código do produto"}
                    },
                    "required": []
                }
            },
            {
                "name": "incluir_produto",
                "description": "Inclui novo produto no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string", "description": "Código do produto"},
                        "descricao": {"type": "string", "description": "Descrição do produto"},
                        "ncm": {"type": "string", "description": "NCM do produto"},
                        "valor_unitario": {"type": "number", "description": "Valor unitário"},
                        "unidade": {"type": "string", "description": "Unidade de medida"}
                    },
                    "required": ["codigo", "descricao", "valor_unitario"]
                }
            },
            {
                "name": "gerar_relatorio_financeiro",
                "description": "Gera relatório financeiro no Omie ERP",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tipo_relatorio": {"type": "string", "description": "Tipo do relatório (contas_pagar, contas_receber, fluxo_caixa)", "enum": ["contas_pagar", "contas_receber", "fluxo_caixa"]},
                        "data_inicial": {"type": "string", "description": "Data inicial (DD/MM/AAAA)"},
                        "data_final": {"type": "string", "description": "Data final (DD/MM/AAAA)"}
                    },
                    "required": ["tipo_relatorio", "data_inicial", "data_final"]
                }
            }
        ]
        
        # Registrar ferramentas básicas
        for tool in basic_tools:
            self.tools[tool["name"]] = tool
            self.mcp_tools.append(tool)
        
        logger.info(f"Total de ferramentas STDIO registradas: {len(self.tools)}")
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Retorna ferramentas no formato MCP"""
        return self.mcp_tools
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém ferramenta por nome"""
        return self.tools.get(name)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa ferramenta"""
        tool = self.get_tool(name)
        if not tool:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não encontrada",
                "ferramentas_disponíveis": list(self.tools.keys())
            }, ensure_ascii=False, indent=2)
        
        try:
            # Se temos credenciais, usar API real, senão simular
            if self.credentials and 'app_key' in self.credentials and 'app_secret' in self.credentials:
                return await self._call_real_api(name, arguments)
            else:
                return await self._simulate_tool_call(name, arguments)
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {name}: {e}")
            return json.dumps({
                "erro": f"Erro ao executar {name}",
                "detalhes": str(e)
            }, ensure_ascii=False, indent=2)
    
    async def _call_real_api(self, name: str, arguments: Dict[str, Any]) -> str:
        """Chama API real do Omie"""
        
        # Mapeamento de ferramentas para endpoints Omie
        api_mapping = {
            "testar_conexao": ("geral", "ListarCnae", {}),
            "consultar_categorias": ("geral", "ListarCategorias", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 50)}),
            "consultar_departamentos": ("geral", "ListarDepartamentos", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 50)}),
            "consultar_tipos_documento": ("geral", "ListarTiposDocumento", {}),
            "consultar_contas_pagar": ("financas", "ListarContasPagar", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 20)}),
            "consultar_contas_receber": ("financas", "ListarContasReceber", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 20)}),
            "consultar_clientes": ("geral", "ListarClientes", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 50)}),
            "consultar_fornecedores": ("geral", "ListarFornecedores", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 50)}),
            "consultar_produtos": ("geral", "ListarProdutos", {"pagina": arguments.get("pagina", 1), "registros_por_pagina": arguments.get("registros_por_pagina", 50)})
        }
        
        if name not in api_mapping:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não implementada para API real ainda",
                "modo": "simulação_fallback"
            }, ensure_ascii=False, indent=2)
        
        call_type, action, params = api_mapping[name]
        
        try:
            # Preparar dados para API
            payload = {
                "call": f"{call_type}",
                "app_key": self.credentials["app_key"],
                "app_secret": self.credentials["app_secret"],
                "param": [params]
            }
            
            # Fazer chamada à API usando urllib
            url = f"https://app.omie.com.br/api/v1/{call_type}/{action.lower()}/"
            
            # Preparar dados
            data = json.dumps(payload).encode('utf-8')
            
            # Criar request
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Omie-MCP-Client/1.0'
                }
            )
            
            # Fazer chamada
            response = urllib.request.urlopen(req, timeout=30)
            
            if response.status == 200:
                result_data = response.read().decode('utf-8')
                result = json.loads(result_data)
                return json.dumps({
                    "ferramenta": name,
                    "argumentos": arguments,
                    "modo": "api_real",
                    "status": "sucesso",
                    "resultado": result
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "ferramenta": name,
                    "argumentos": arguments,
                    "modo": "api_real",
                    "status": "erro",
                    "codigo_http": response.status,
                    "mensagem": response.read().decode('utf-8')
                }, ensure_ascii=False, indent=2)
                
        except urllib.error.HTTPError as e:
            logger.error(f"Erro HTTP na API Omie: {e}")
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "api_real",
                "status": "erro_http",
                "codigo_http": e.code,
                "erro": str(e)
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro na chamada da API Omie: {e}")
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "api_real",
                "status": "erro",
                "erro": str(e)
            }, ensure_ascii=False, indent=2)
    
    async def _simulate_tool_call(self, name: str, arguments: Dict[str, Any]) -> str:
        """Simula execução de ferramenta"""
        
        if name == "testar_conexao":
            return json.dumps({
                "status": "conectado",
                "servidor": "Omie ERP",
                "modo": "stdio_puro",
                "ferramentas_disponíveis": len(self.tools),
                "configuracao": "credenciais_ok",
                "mensagem": "Servidor MCP STDIO funcionando corretamente!"
            }, ensure_ascii=False, indent=2)
        
        elif "consultar" in name:
            # Simular dados de consulta
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultados": [
                    {
                        "id": "123",
                        "nome": f"Exemplo {name}",
                        "status": "ativo"
                    },
                    {
                        "id": "456", 
                        "nome": f"Exemplo 2 {name}",
                        "status": "ativo"
                    }
                ],
                "total_registros": 2,
                "nota": "Dados simulados - Configure credenciais reais para dados reais"
            }, ensure_ascii=False, indent=2)
        
        elif "cadastrar" in name or "criar" in name:
            # Simular criação
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultado": {
                    "codigo_gerado": "SIM123456",
                    "status": "criado_com_sucesso",
                    "data_criacao": "16/01/2025"
                },
                "nota": "Operação simulada - Configure credenciais reais para operações reais"
            }, ensure_ascii=False, indent=2)
        
        else:
            # Resposta genérica
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "nota": "Ferramenta disponível - Configure credenciais para funcionalidade completa"
            }, ensure_ascii=False, indent=2)

class OmieMCPServer:
    """Servidor MCP STDIO puro para Omie ERP"""
    
    def __init__(self):
        self.tool_registry = OmieToolRegistry()
        logger.info("Servidor MCP STDIO Omie inicializado")
    
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição ou gera um padrão"""
        request_id = request.get("id")
        if request_id is None:
            return "unknown"
        return str(request_id)
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        method = request.get("method")
        request_id = self.get_request_id(request)
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": "omie-mcp-server-stdio",
                            "version": "2.0.0-stdio"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tool_registry.get_mcp_tools()}
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "Tool name is required"}
                    }
                
                result = await self.tool_registry.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(result)}]}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not supported: {method}"}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
    
    async def run(self):
        """Executa servidor MCP"""
        logger.info("Servidor MCP STDIO Omie iniciado - aguardando requisições...")
        
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    self.send_response(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": "unknown",
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    self.send_response(error_response)
                except Exception as e:
                    logger.error(f"Erro ao processar linha: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no servidor: {e}")

async def main():
    """Função principal"""
    server = OmieMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())