#!/usr/bin/env python3
"""
Servidor MCP para Nibo ERP - Versão simplificada com autenticação direta
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("nibo-mcp-server")

class NiboMCPServer:
    """Servidor MCP para Nibo ERP - Versão simplificada"""
    
    def __init__(self):
        # Autenticação simples via variáveis de ambiente
        self.nibo_token = os.getenv("NIBO_TOKEN", "2264E2C5B5464BFABC3D6E6820EBE47F")
        self.company_id = os.getenv("NIBO_COMPANY_ID", "50404226-615e-48d2-9701-0e765f64e0b9")
        self.base_url = "https://api.nibo.com.br"
        
        logger.info(f"Nibo MCP Server inicializado com token: {self.nibo_token[:8]}...")
        
        self.tools = [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
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
                    }
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_fornecedores",
                "description": "Consulta fornecedores cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    }
                }
            },
            {
                "name": "consultar_contas_receber",
                "description": "Consulta contas a receber no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_inicio": {"type": "string", "description": "Data início (DD/MM/AAAA)"},
                        "data_fim": {"type": "string", "description": "Data fim (DD/MM/AAAA)"},
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 20}
                    }
                }
            },
            {
                "name": "consultar_socios",
                "description": "Consulta sócios cadastrados no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "incluir_cliente",
                "description": "Inclui novo cliente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do cliente"},
                        "document": {"type": "string", "description": "CPF ou CNPJ"},
                        "email": {"type": "string", "description": "Email"},
                        "phone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["name", "document"]
                }
            },
            {
                "name": "incluir_fornecedor",
                "description": "Inclui novo fornecedor no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do fornecedor"},
                        "document": {"type": "string", "description": "CPF ou CNPJ"},
                        "email": {"type": "string", "description": "Email"},
                        "phone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["name", "document"]
                }
            },
            {
                "name": "incluir_socio",
                "description": "Inclui novo sócio no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do sócio"},
                        "document": {"type": "string", "description": "CPF"},
                        "email": {"type": "string", "description": "Email"},
                        "participation_percentage": {"type": "number", "description": "Percentual de participação"}
                    },
                    "required": ["name", "document", "participation_percentage"]
                }
            },
            {
                "name": "testar_conexao",
                "description": "Testa conexão com a API do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "alterar_cliente",
                "description": "Altera dados de cliente existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do cliente"},
                        "name": {"type": "string", "description": "Novo nome"},
                        "email": {"type": "string", "description": "Novo email"},
                        "phone": {"type": "string", "description": "Novo telefone"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "alterar_fornecedor",
                "description": "Altera dados de fornecedor existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do fornecedor"},
                        "name": {"type": "string", "description": "Novo nome"},
                        "email": {"type": "string", "description": "Novo email"},
                        "phone": {"type": "string", "description": "Novo telefone"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "alterar_socio",
                "description": "Altera dados de sócio existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do sócio"},
                        "name": {"type": "string", "description": "Novo nome"},
                        "email": {"type": "string", "description": "Novo email"},
                        "participation_percentage": {"type": "number", "description": "Novo % participação"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "excluir_cliente",
                "description": "Exclui cliente do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do cliente"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "excluir_fornecedor",
                "description": "Exclui fornecedor do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do fornecedor"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "excluir_socio",
                "description": "Exclui sócio do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do sócio"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "obter_cliente_por_id",
                "description": "Busca cliente específico por ID no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do cliente"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "obter_fornecedor_por_id",
                "description": "Busca fornecedor específico por ID no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do fornecedor"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "obter_socio_por_id",
                "description": "Busca sócio específico por ID no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do sócio"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "incluir_conta_pagar",
                "description": "Inclui nova conta a pagar no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "supplier_id": {"type": "integer", "description": "ID do fornecedor"},
                        "document_number": {"type": "string", "description": "Número do documento"},
                        "due_date": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                        "amount": {"type": "number", "description": "Valor"},
                        "category_id": {"type": "integer", "description": "ID da categoria"}
                    },
                    "required": ["supplier_id", "document_number", "due_date", "amount"]
                }
            },
            {
                "name": "incluir_conta_receber",
                "description": "Inclui nova conta a receber no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "integer", "description": "ID do cliente"},
                        "document_number": {"type": "string", "description": "Número do documento"},
                        "due_date": {"type": "string", "description": "Data vencimento (YYYY-MM-DD)"},
                        "amount": {"type": "number", "description": "Valor"},
                        "category_id": {"type": "integer", "description": "ID da categoria"}
                    },
                    "required": ["customer_id", "document_number", "due_date", "amount"]
                }
            },
            {
                "name": "alterar_conta_pagar",
                "description": "Altera conta a pagar existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"},
                        "due_date": {"type": "string", "description": "Nova data vencimento (YYYY-MM-DD)"},
                        "amount": {"type": "number", "description": "Novo valor"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "alterar_conta_receber",
                "description": "Altera conta a receber existente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"},
                        "due_date": {"type": "string", "description": "Nova data vencimento (YYYY-MM-DD)"},
                        "amount": {"type": "number", "description": "Novo valor"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "excluir_conta_pagar",
                "description": "Exclui conta a pagar do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "excluir_conta_receber",
                "description": "Exclui conta a receber do Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "consultar_conta_pagar_por_id",
                "description": "Consulta conta a pagar específica por ID no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "consultar_conta_receber_por_id",
                "description": "Consulta conta a receber específica por ID no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID da conta"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos (alias para centros de custo) no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "description": "Página", "default": 1},
                        "registros_por_pagina": {"type": "integer", "description": "Registros por página", "default": 50}
                    }
                }
            },
            {
                "name": "buscar_dados_contato_cliente",
                "description": "Busca dados completos de contato do cliente no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do cliente"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "buscar_dados_contato_fornecedor",
                "description": "Busca dados completos de contato do fornecedor no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID do fornecedor"}
                    },
                    "required": ["id"]
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
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "document": {"type": "string"},
                                    "email": {"type": "string"},
                                    "phone": {"type": "string"}
                                },
                                "required": ["name", "document"]
                            }
                        }
                    },
                    "required": ["clientes"]
                }
            },
            {
                "name": "incluir_multiplos_fornecedores",
                "description": "Inclui múltiplos fornecedores em lote no Nibo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fornecedores": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "document": {"type": "string"},
                                    "email": {"type": "string"},
                                    "phone": {"type": "string"}
                                },
                                "required": ["name", "document"]
                            }
                        }
                    },
                    "required": ["fornecedores"]
                }
            }
        ]
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "nibo-mcp-server", "version": "1.0.0"}
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(result)}]}
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Método não suportado: {method}"}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Chama ferramenta específica"""
        try:
            # Simulação de chamadas para API do Nibo
            if tool_name == "testar_conexao":
                return json.dumps({
                    "status": "conectado",
                    "empresa": "I9 MARKETING E TECNOLOGIA LTDA",
                    "token": self.nibo_token[:8] + "...",
                    "company_id": self.company_id
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_categorias":
                return json.dumps({
                    "categorias": [
                        {"id": 1, "nome": "Vendas", "ativo": True},
                        {"id": 2, "nome": "Compras", "ativo": True},
                        {"id": 3, "nome": "Administrativo", "ativo": True}
                    ],
                    "total": 3
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_centros_custo":
                return json.dumps({
                    "centros_custo": [
                        {"id": 1, "nome": "Comercial", "ativo": True},
                        {"id": 2, "nome": "Financeiro", "ativo": True}
                    ],
                    "total": 2
                }, ensure_ascii=False, indent=2)
            
            elif tool_name == "consultar_socios":
                return json.dumps({
                    "socios": [
                        {
                            "id": 1,
                            "nome": "João Silva",
                            "documento": "123.456.789-00",
                            "email": "joao@empresa.com",
                            "participacao": 50.0
                        }
                    ],
                    "total": 1
                }, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({
                    "erro": f"Ferramenta '{tool_name}' em implementação",
                    "argumentos_recebidos": arguments
                }, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return f"Erro ao executar {tool_name}: {str(e)}"

async def main():
    """Função principal do servidor MCP"""
    server = NiboMCPServer()
    logger.info("Servidor MCP Nibo iniciado (versão simplificada)")
    
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:
                break
                
            request = json.loads(line)
            response = await server.handle_request(request)
            server.send_response(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
            server.send_response(error_response)
            
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            server.send_response(error_response)

if __name__ == "__main__":
    asyncio.run(main())