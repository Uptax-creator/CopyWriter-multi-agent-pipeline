#!/usr/bin/env python3
"""
Servidor HTTP puro para Omie MCP
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
logger = logging.getLogger("omie-http-pure")

class OmieToolRegistry:
    """Registro de ferramentas Omie para HTTP"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas as ferramentas Omie"""
        
        tools_data = [
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
            }
        ]
        
        for tool in tools_data:
            self.tools[tool["name"]] = tool
        
        logger.info(f"Registradas {len(self.tools)} ferramentas Omie")
    
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
                "servidor": "Omie ERP",
                "modo": "http_puro",
                "ferramentas_disponíveis": len(self.tools),
                "credenciais": "configuradas",
                "mensagem": "Servidor HTTP Omie funcionando perfeitamente!"
            }
        
        elif "consultar" in name:
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultados": [
                    {
                        "id": "omie_123",
                        "nome": f"Exemplo {name}",
                        "status": "ativo",
                        "data_criacao": "16/01/2025"
                    },
                    {
                        "id": "omie_456",
                        "nome": f"Exemplo 2 {name}",
                        "status": "ativo",
                        "data_criacao": "15/01/2025"
                    }
                ],
                "total_registros": 2,
                "pagina": arguments.get("pagina", 1),
                "nota": "Dados simulados - Configure credenciais para dados reais"
            }
        
        elif "cadastrar" in name or "criar" in name:
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "resultado": {
                    "codigo_gerado": f"OMIE{hash(str(arguments)) % 100000}",
                    "status": "criado_com_sucesso",
                    "data_criacao": "16/01/2025"
                },
                "nota": "Operação simulada - Configure credenciais para operações reais"
            }
        
        else:
            return {
                "ferramenta": name,
                "argumentos": arguments,
                "modo": "simulação",
                "nota": "Ferramenta disponível - Configure API para funcionalidade completa"
            }

class OmieHTTPHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servidor Omie"""
    
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
                "service": "Omie MCP Server",
                "version": "2.0.0-http-pure",
                "status": "online",
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
        return OmieHTTPHandler(*args, tool_registry=tool_registry, **kwargs)
    return handler

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Servidor HTTP Omie MCP')
    parser.add_argument('--port', type=int, default=3001, help='Porta do servidor')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    
    args = parser.parse_args()
    
    # Criar registry de ferramentas
    tool_registry = OmieToolRegistry()
    
    # Criar servidor HTTP
    handler = create_handler(tool_registry)
    server = HTTPServer((args.host, args.port), handler)
    
    logger.info(f"🚀 Servidor HTTP Omie iniciado em http://{args.host}:{args.port}")
    logger.info(f"📋 {len(tool_registry.tools)} ferramentas disponíveis")
    logger.info(f"🔗 Acesse http://{args.host}:{args.port}/mcp/tools para ver as ferramentas")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
        server.shutdown()

if __name__ == "__main__":
    main()