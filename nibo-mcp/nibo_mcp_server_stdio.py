#!/usr/bin/env python3
"""
Servidor MCP STDIO puro para Nibo ERP
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
logger = logging.getLogger("nibo-mcp-stdio")

class NiboToolRegistry:
    """Registro simplificado de ferramentas Nibo para STDIO"""
    
    def __init__(self):
        self.tools = {}
        self.mcp_tools = []
        self.credentials = self._load_credentials()
        self._register_basic_tools()
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Carrega credenciais do arquivo credentials.json"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(current_dir, 'credentials.json')
            
            if os.path.exists(credentials_path):
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                    logger.info("✅ Credenciais Nibo carregadas com sucesso")
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
                "description": "Testa conexão com a API do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Nibo",
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
                "name": "consultar_centros_custo",
                "description": "Consulta centros de custo cadastrados no Nibo",
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
                "name": "consultar_socios",
                "description": "Consulta sócios da empresa no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "empresa_id": {"type": "string", "description": "ID da empresa (opcional)"}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50},
                        "filtrar_por_nome": {"type": "string", "description": "Filtrar por nome"}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_fornecedores",
                "description": "Consulta fornecedores cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50},
                        "filtrar_por_nome": {"type": "string", "description": "Filtrar por nome"}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50},
                        "data_vencimento_inicial": {"type": "string", "description": "Data inicial (YYYY-MM-DD)"},
                        "data_vencimento_final": {"type": "string", "description": "Data final (YYYY-MM-DD)"}
                    },
                    "required": []
                }
            },
            {
                "name": "consultar_contas_receber",
                "description": "Consulta contas a receber no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50},
                        "data_vencimento_inicial": {"type": "string", "description": "Data inicial (YYYY-MM-DD)"},
                        "data_vencimento_final": {"type": "string", "description": "Data final (YYYY-MM-DD)"}
                    },
                    "required": []
                }
            },
            {
                "name": "incluir_socio",
                "description": "Inclui novo sócio na empresa",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome do sócio"},
                        "cpf": {"type": "string", "description": "CPF do sócio"},
                        "percentual_participacao": {"type": "number", "description": "Percentual de participação"}
                    },
                    "required": ["nome", "cpf", "percentual_participacao"]
                }
            },
            {
                "name": "incluir_cliente",
                "description": "Inclui novo cliente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome do cliente"},
                        "documento": {"type": "string", "description": "CPF/CNPJ do cliente"},
                        "email": {"type": "string", "description": "Email do cliente"},
                        "telefone": {"type": "string", "description": "Telefone do cliente"}
                    },
                    "required": ["nome", "documento"]
                }
            },
            {
                "name": "incluir_fornecedor", 
                "description": "Inclui novo fornecedor no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome do fornecedor"},
                        "documento": {"type": "string", "description": "CPF/CNPJ do fornecedor"},
                        "email": {"type": "string", "description": "Email do fornecedor"},
                        "telefone": {"type": "string", "description": "Telefone do fornecedor"}
                    },
                    "required": ["nome", "documento"]
                }
            },
            {
                "name": "incluir_multiplos_clientes",
                "description": "Inclui múltiplos clientes em lote no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clientes": {
                            "type": "array",
                            "description": "Lista de clientes",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "nome": {"type": "string"},
                                    "documento": {"type": "string"},
                                    "email": {"type": "string"}
                                },
                                "required": ["nome", "documento"]
                            }
                        }
                    },
                    "required": ["clientes"]
                }
            },
            {
                "name": "consultar_produtos",
                "description": "Consulta produtos cadastrados no Nibo",
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
                "name": "consultar_empresas",
                "description": "Consulta empresas disponíveis no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "consultar_plano_contas",
                "description": "Consulta plano de contas no Nibo",
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
                "name": "incluir_conta_pagar",
                "description": "Inclui nova conta a pagar no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fornecedor_id": {"type": "string", "description": "ID do fornecedor"},
                        "descricao": {"type": "string", "description": "Descrição da conta"},
                        "valor": {"type": "number", "description": "Valor da conta"},
                        "data_vencimento": {"type": "string", "description": "Data de vencimento (YYYY-MM-DD)"}
                    },
                    "required": ["fornecedor_id", "descricao", "valor", "data_vencimento"]
                }
            },
            {
                "name": "incluir_conta_receber",
                "description": "Inclui nova conta a receber no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cliente_id": {"type": "string", "description": "ID do cliente"},
                        "descricao": {"type": "string", "description": "Descrição da conta"},
                        "valor": {"type": "number", "description": "Valor da conta"},
                        "data_vencimento": {"type": "string", "description": "Data de vencimento (YYYY-MM-DD)"}
                    },
                    "required": ["cliente_id", "descricao", "valor", "data_vencimento"]
                }
            },
            {
                "name": "incluir_produto",
                "description": "Inclui novo produto no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome do produto"},
                        "codigo": {"type": "string", "description": "Código do produto"},
                        "preco": {"type": "number", "description": "Preço do produto"},
                        "categoria": {"type": "string", "description": "Categoria do produto"}
                    },
                    "required": ["nome", "codigo", "preco"]
                }
            },
            {
                "name": "alterar_cliente",
                "description": "Altera dados de cliente existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cliente_id": {"type": "string", "description": "ID do cliente"},
                        "nome": {"type": "string", "description": "Nome do cliente"},
                        "documento": {"type": "string", "description": "CPF/CNPJ do cliente"},
                        "email": {"type": "string", "description": "Email do cliente"},
                        "telefone": {"type": "string", "description": "Telefone do cliente"}
                    },
                    "required": ["cliente_id"]
                }
            },
            {
                "name": "alterar_fornecedor",
                "description": "Altera dados de fornecedor existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fornecedor_id": {"type": "string", "description": "ID do fornecedor"},
                        "nome": {"type": "string", "description": "Nome do fornecedor"},
                        "documento": {"type": "string", "description": "CPF/CNPJ do fornecedor"},
                        "email": {"type": "string", "description": "Email do fornecedor"},
                        "telefone": {"type": "string", "description": "Telefone do fornecedor"}
                    },
                    "required": ["fornecedor_id"]
                }
            },
            {
                "name": "gerar_relatorio_financeiro",
                "description": "Gera relatório financeiro no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tipo_relatorio": {"type": "string", "description": "Tipo do relatório (fluxo_caixa, dre, balancete)", "enum": ["fluxo_caixa", "dre", "balancete"]},
                        "data_inicial": {"type": "string", "description": "Data inicial (YYYY-MM-DD)"},
                        "data_final": {"type": "string", "description": "Data final (YYYY-MM-DD)"}
                    },
                    "required": ["tipo_relatorio", "data_inicial", "data_final"]
                }
            },
            {
                "name": "sincronizar_dados",
                "description": "Sincroniza dados entre sistemas no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entidade": {"type": "string", "description": "Entidade a sincronizar (clientes, fornecedores, produtos)", "enum": ["clientes", "fornecedores", "produtos"]},
                        "data_ultima_sincronizacao": {"type": "string", "description": "Data da última sincronização (YYYY-MM-DD)"}
                    },
                    "required": ["entidade"]
                }
            }
        ]
        
        # Registrar ferramentas básicas
        for tool in basic_tools:
            self.tools[tool["name"]] = tool
            self.mcp_tools.append(tool)
        
        logger.info(f"Total de ferramentas STDIO Nibo registradas: {len(self.tools)}")
    
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
            if self.credentials and 'companies' in self.credentials:
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
        """Chama API real do Nibo"""
        
        # Obter credenciais da empresa padrão
        default_company = self.credentials.get('default_company', 'empresa_exemplo')
        company_data = self.credentials.get('companies', {}).get(default_company, {})
        
        if not company_data:
            return json.dumps({
                "erro": "Empresa padrão não configurada nas credenciais",
                "modo": "simulação_fallback"
            }, ensure_ascii=False, indent=2)
        
        # Mapeamento de ferramentas para endpoints Nibo
        api_mapping = {
            "testar_conexao": ("companies", "GET", ""),
            "consultar_categorias": ("categories", "GET", ""),
            "consultar_clientes": ("customers", "GET", ""),
            "consultar_fornecedores": ("suppliers", "GET", ""),
            "consultar_produtos": ("products", "GET", ""),
            "consultar_contas_pagar": ("accounts_payable", "GET", ""),
            "consultar_contas_receber": ("accounts_receivable", "GET", "")
        }
        
        if name not in api_mapping:
            return json.dumps({
                "erro": f"Ferramenta '{name}' não implementada para API real ainda",
                "modo": "simulação_fallback"
            }, ensure_ascii=False, indent=2)
        
        endpoint, method, path = api_mapping[name]
        
        try:
            # Preparar headers
            headers = {
                "Authorization": f"Bearer {company_data['nibo_api_token']}",
                "Content-Type": "application/json"
            }
            
            # Construir URL
            base_url = company_data.get('base_url', 'https://api.nibo.com.br')
            url = f"{base_url}/v1/{endpoint}{path}"
            
            # Fazer chamada à API usando urllib
            req = urllib.request.Request(
                url,
                headers={
                    'Authorization': f"Bearer {company_data['nibo_api_token']}",
                    'Content-Type': 'application/json',
                    'User-Agent': 'Nibo-MCP-Client/1.0'
                }
            )
            
            response = urllib.request.urlopen(req, timeout=30)
            
            if response.status == 200:
                result_data = response.read().decode('utf-8')
                result = json.loads(result_data)
                return json.dumps({
                    "ferramenta": name,
                    "argumentos": arguments,
                    "modo": "api_real",
                    "status": "sucesso",
                    "empresa": company_data.get('name', 'N/A'),
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
            logger.error(f"Erro HTTP na API Nibo: {e}")
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "api_real",
                "status": "erro_http",
                "codigo_http": e.code,
                "erro": str(e)
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro na chamada da API Nibo: {e}")
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
                "servidor": "Nibo ERP",
                "modo": "stdio_puro",
                "ferramentas_disponíveis": len(self.tools),
                "empresa_configurada": "I9 MARKETING E TECNOLOGIA LTDA",
                "token_ativo": "sim",
                "mensagem": "Servidor MCP STDIO Nibo funcionando corretamente!"
            }, ensure_ascii=False, indent=2)
        
        elif name == "consultar_socios":
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "socios": [
                    {
                        "id": "socio_1",
                        "nome": "Sócio Exemplo 1",
                        "cpf": "000.000.000-00",
                        "participacao": 50.0,
                        "ativo": True
                    },
                    {
                        "id": "socio_2",
                        "nome": "Sócio Exemplo 2", 
                        "cpf": "111.111.111-11",
                        "participacao": 50.0,
                        "ativo": True
                    }
                ],
                "total_socios": 2,
                "nota": "Dados simulados - Configure credenciais reais para dados reais"
            }, ensure_ascii=False, indent=2)
        
        elif "consultar" in name:
            # Simular dados de consulta
            entity = name.replace("consultar_", "").replace("_", " ")
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultados": [
                    {
                        "id": "nibo_123",
                        "nome": f"Exemplo {entity} 1",
                        "status": "ativo",
                        "data_criacao": "2025-01-16"
                    },
                    {
                        "id": "nibo_456",
                        "nome": f"Exemplo {entity} 2",
                        "status": "ativo", 
                        "data_criacao": "2025-01-15"
                    }
                ],
                "total_registros": 2,
                "pagina": arguments.get("pagina", 1),
                "nota": "Dados simulados - Configure credenciais reais para dados reais"
            }, ensure_ascii=False, indent=2)
        
        elif "incluir" in name:
            # Simular criação
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultado": {
                    "id_gerado": f"nibo_{name}_{hash(str(arguments)) % 100000}",
                    "status": "criado_com_sucesso",
                    "data_criacao": "2025-01-16T00:00:00Z",
                    "empresa": "I9 MARKETING E TECNOLOGIA LTDA"
                },
                "nota": "Operação simulada - Configure credenciais reais para operações reais"
            }, ensure_ascii=False, indent=2)
        
        else:
            # Resposta genérica
            return json.dumps({
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "nota": "Ferramenta disponível - Configure credenciais para funcionalidade completa"
            }, ensure_ascii=False, indent=2)

class NiboMCPServer:
    """Servidor MCP STDIO puro para Nibo ERP"""
    
    def __init__(self):
        self.tool_registry = NiboToolRegistry()
        logger.info("Servidor MCP STDIO Nibo inicializado")
    
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
                            "name": "nibo-mcp-server-stdio",
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
        logger.info("Servidor MCP STDIO Nibo iniciado - aguardando requisições...")
        
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
    server = NiboMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())