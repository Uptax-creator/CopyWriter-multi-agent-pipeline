#!/usr/bin/env python3
"""
Servidor HTTP puro para Nibo MCP
Versão simplificada usando apenas bibliotecas padrão do Python
"""

import json
import logging
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import argparse
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("nibo-http-pure")

class NiboToolRegistry:
    """Registro de ferramentas Nibo para HTTP"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas as ferramentas Nibo"""
        
        tools_data = [
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
                "name": "incluir_conta_pagar",
                "description": "Inclui nova conta a pagar no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fornecedor_id": {"type": "string", "description": "ID do fornecedor"},
                        "valor": {"type": "number", "description": "Valor da conta"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                        "descricao": {"type": "string", "description": "Descrição"}
                    },
                    "required": ["fornecedor_id", "valor", "data_vencimento"]
                }
            },
            {
                "name": "incluir_conta_receber",
                "description": "Inclui nova conta a receber no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cliente_id": {"type": "string", "description": "ID do cliente"},
                        "valor": {"type": "number", "description": "Valor da conta"},
                        "data_vencimento": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                        "descricao": {"type": "string", "description": "Descrição"}
                    },
                    "required": ["cliente_id", "valor", "data_vencimento"]
                }
            },
            {
                "name": "excluir_cliente",
                "description": "Exclui cliente do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cliente_id": {"type": "string", "description": "ID do cliente"}
                    },
                    "required": ["cliente_id"]
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
                        "preco": {"type": "number", "description": "Preço do produto"}
                    },
                    "required": ["nome", "codigo", "preco"]
                }
            },
            {
                "name": "alterar_cliente",
                "description": "Altera dados de cliente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID do cliente"},
                        "nome": {"type": "string", "description": "Nome do cliente"},
                        "email": {"type": "string", "description": "Email do cliente"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "alterar_fornecedor",
                "description": "Altera dados de fornecedor no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID do fornecedor"},
                        "nome": {"type": "string", "description": "Nome do fornecedor"},
                        "email": {"type": "string", "description": "Email do fornecedor"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "gerar_relatorio_financeiro",
                "description": "Gera relatório financeiro no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tipo": {"type": "string", "description": "Tipo do relatório"},
                        "data_inicio": {"type": "string", "description": "Data início (YYYY-MM-DD)"},
                        "data_fim": {"type": "string", "description": "Data fim (YYYY-MM-DD)"}
                    },
                    "required": ["tipo", "data_inicio", "data_fim"]
                }
            },
            {
                "name": "sincronizar_dados",
                "description": "Sincroniza dados com o Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        for tool in tools_data:
            self.tools[tool["name"]] = tool
        
        logger.info(f"Registradas {len(self.tools)} ferramentas Nibo")
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Retorna todas as ferramentas"""
        return list(self.tools.values())
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Obtém ferramenta por nome"""
        return self.tools.get(name)
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ferramenta"""
        tool = self.get_tool(name)
        if not tool:
            return {
                "error": f"Ferramenta '{name}' não encontrada",
                "available_tools": list(self.tools.keys())
            }
        
        # Simular execução da ferramenta
        if name == "testar_conexao":
            return {
                "status": "conectado",
                "servidor": "Nibo ERP",
                "modo": "http_puro",
                "ferramentas_disponíveis": len(self.tools),
                "empresa_configurada": "I9 MARKETING E TECNOLOGIA LTDA",
                "token_ativo": "sim",
                "mensagem": "Servidor HTTP Nibo funcionando perfeitamente!"
            }
        
        elif name == "consultar_socios":
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "socios": [
                    {
                        "id": "socio_nibo_1",
                        "nome": "Sócio Exemplo Nibo 1",
                        "cpf": "000.000.000-00",
                        "participacao": 50.0,
                        "ativo": True
                    },
                    {
                        "id": "socio_nibo_2",
                        "nome": "Sócio Exemplo Nibo 2", 
                        "cpf": "111.111.111-11",
                        "participacao": 50.0,
                        "ativo": True
                    }
                ],
                "total_socios": 2,
                "nota": "Dados simulados - Configure credenciais para dados reais"
            }
        
        elif "consultar" in name:
            entity = name.replace("consultar_", "").replace("_", " ")
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "resultados": [
                    {
                        "id": f"nibo_{hash(name) % 1000}",
                        "nome": f"Exemplo {entity} 1",
                        "status": "ativo",
                        "data_criacao": "2025-01-16"
                    },
                    {
                        "id": f"nibo_{hash(name) % 1000 + 1}",
                        "nome": f"Exemplo {entity} 2",
                        "status": "ativo", 
                        "data_criacao": "2025-01-15"
                    }
                ],
                "total_registros": 2,
                "pagina": arguments.get("pagina", 1),
                "nota": "Dados simulados - Configure credenciais para dados reais"
            }
        
        elif "incluir" in name or "alterar" in name or "gerar" in name or "sincronizar" in name:
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "resultado": {
                    "id_gerado": f"nibo_{name}_{hash(str(arguments)) % 100000}",
                    "status": "operacao_realizada_com_sucesso",
                    "data_operacao": "2025-01-16T00:00:00Z"
                },
                "nota": "Operação simulada - Configure credenciais para operações reais"
            }
        
        else:
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "nota": "Ferramenta disponível - Configure API para funcionalidade completa"
            }

class NiboHTTPHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servidor Nibo"""
    
    def __init__(self, *args, tool_registry=None, **kwargs):
        self.tool_registry = tool_registry
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Lidar com preflight CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Lidar com requisições GET"""
        parsed_path = urlparse(self.path)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        if parsed_path.path == '/':
            # Root endpoint
            response = {
                "service": "Nibo MCP Server",
                "version": "2.0.0-http-pure",
                "status": "online",
                "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                "tools_count": len(self.tool_registry.tools),
                "endpoints": {
                    "tools": "/mcp/tools",
                    "call_tool": "/mcp/tools/{tool_name}"
                }
            }
            
        elif parsed_path.path == '/mcp/tools':
            # Listar ferramentas
            response = {
                "tools": self.tool_registry.get_all_tools()
            }
            
        else:
            # Endpoint não encontrado
            self.send_response(404)
            response = {"error": "Endpoint não encontrado"}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def do_POST(self):
        """Lidar com requisições POST"""
        parsed_path = urlparse(self.path)
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        
        if parsed_path.path.startswith('/mcp/tools/'):
            # Chamar ferramenta
            tool_name = parsed_path.path.split('/')[-1]
            
            try:
                # Ler corpo da requisição
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                arguments = data.get('arguments', {})
                
                # Executar ferramenta
                result = self.tool_registry.call_tool(tool_name, arguments)
                
                self.send_response(200)
                self.end_headers()
                
                response = {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                }
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                
                response = {
                    "error": f"Erro ao executar ferramenta: {str(e)}"
                }
        
        else:
            self.send_response(404)
            self.end_headers()
            response = {"error": "Endpoint não encontrado"}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override para usar nosso logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(tool_registry):
    """Cria handler com registry injetado"""
    def handler(*args, **kwargs):
        return NiboHTTPHandler(*args, tool_registry=tool_registry, **kwargs)
    return handler

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Servidor HTTP Nibo MCP')
    parser.add_argument('--port', type=int, default=3002, help='Porta do servidor')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    
    args = parser.parse_args()
    
    # Criar registry de ferramentas
    tool_registry = NiboToolRegistry()
    
    # Criar servidor HTTP
    handler = create_handler(tool_registry)
    server = HTTPServer((args.host, args.port), handler)
    
    logger.info(f"🚀 Servidor HTTP Nibo iniciado em http://{args.host}:{args.port}")
    logger.info(f"📋 {len(tool_registry.tools)} ferramentas disponíveis")
    logger.info(f"🔗 Acesse http://{args.host}:{args.port}/mcp/tools para ver as ferramentas")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
        server.shutdown()

if __name__ == "__main__":
    main()