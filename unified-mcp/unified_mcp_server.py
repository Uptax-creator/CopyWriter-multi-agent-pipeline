#!/usr/bin/env python3
"""
Servidor MCP Unificado - Omie + Nibo
Combina funcionalidades de ambas as plataformas em uma interface única
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("unified-mcp-server")

# Importar adaptadores
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.adapters.omie_adapter import OmieAdapter
from src.adapters.nibo_adapter import NiboAdapter
from src.mappers.universal_mapper import UniversalMapper

class UnifiedMCPServer:
    """Servidor MCP Unificado para Omie e Nibo"""
    
    def __init__(self):
        self.omie_adapter = OmieAdapter()
        self.nibo_adapter = NiboAdapter()
        self.universal_mapper = UniversalMapper()
        
        # Configurar credenciais
        self.omie_credentials = {
            "app_key": os.getenv("OMIE_APP_KEY", "2687508979155"),
            "app_secret": os.getenv("OMIE_APP_SECRET", "23ae858794e1cd879232c81105604b1f")
        }
        
        self.nibo_credentials = {
            "token": os.getenv("NIBO_TOKEN", "2264E2C5B5464BFABC3D6E6820EBE47F"),
            "company_id": os.getenv("NIBO_COMPANY_ID", "50404226-615e-48d2-9701-0e765f64e0b9")
        }
        
        logger.info("Servidor MCP Unificado inicializado")
        logger.info(f"Omie: {self.omie_credentials['app_key'][:8]}...")
        logger.info(f"Nibo: {self.nibo_credentials['token'][:8]}...")
        
        self.tools = self.create_unified_tools()
    
    def create_unified_tools(self) -> List[Dict[str, Any]]:
        """Cria lista unificada de ferramentas"""
        
        tools = []
        
        # Ferramentas universais (disponíveis em ambas as plataformas)
        universal_tools = [
            {
                "name": "consultar_categorias",
                "description": "Consulta categorias cadastradas (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_clientes",
                "description": "Consulta clientes cadastrados (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_fornecedores",
                "description": "Consulta fornecedores cadastrados (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_contas_pagar",
                "description": "Consulta contas a pagar (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "data_inicio": {"type": "string", "description": "Data início (formato universal)"},
                        "data_fim": {"type": "string", "description": "Data fim (formato universal)"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 20}
                    }
                }
            },
            {
                "name": "consultar_contas_receber",
                "description": "Consulta contas a receber (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "data_inicio": {"type": "string", "description": "Data início (formato universal)"},
                        "data_fim": {"type": "string", "description": "Data fim (formato universal)"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 20}
                    }
                }
            },
            {
                "name": "incluir_cliente",
                "description": "Inclui cliente (formato universal - Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "name": {"type": "string", "description": "Nome/Razão social"},
                        "document": {"type": "string", "description": "CPF/CNPJ"},
                        "email": {"type": "string", "description": "Email"},
                        "phone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["name", "document"]
                }
            },
            {
                "name": "incluir_fornecedor",
                "description": "Inclui fornecedor (formato universal - Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "name": {"type": "string", "description": "Nome/Razão social"},
                        "document": {"type": "string", "description": "CPF/CNPJ"},
                        "email": {"type": "string", "description": "Email"},
                        "phone": {"type": "string", "description": "Telefone"}
                    },
                    "required": ["name", "document"]
                }
            }
        ]
        
        # Ferramentas com alias de compatibilidade
        compatibility_tools = [
            {
                "name": "consultar_departamentos",
                "description": "Consulta departamentos/centros de custo (Omie: departamentos, Nibo: centros_custo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            },
            {
                "name": "consultar_centros_custo",
                "description": "Consulta centros de custo/departamentos (Nibo: centros_custo, Omie: departamentos)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"},
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            }
        ]
        
        # Ferramentas exclusivas do Omie
        omie_exclusive_tools = [
            {
                "name": "consultar_tipos_documento",
                "description": "Consulta tipos de documento (Exclusivo Omie)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string", "description": "Código do tipo documento (opcional)"}
                    }
                }
            }
        ]
        
        # Ferramentas exclusivas do Nibo
        nibo_exclusive_tools = [
            {
                "name": "consultar_socios",
                "description": "Consulta sócios cadastrados (Exclusivo Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pagina": {"type": "integer", "default": 1},
                        "registros_por_pagina": {"type": "integer", "default": 50}
                    }
                }
            },
            {
                "name": "incluir_socio",
                "description": "Inclui novo sócio (Exclusivo Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nome do sócio"},
                        "document": {"type": "string", "description": "CPF"},
                        "email": {"type": "string", "description": "Email"},
                        "participation_percentage": {"type": "number", "description": "% participação"}
                    },
                    "required": ["name", "document", "participation_percentage"]
                }
            },
            {
                "name": "incluir_multiplos_clientes",
                "description": "Inclui múltiplos clientes em lote (Exclusivo Nibo)",
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
            }
        ]
        
        # Ferramenta de teste
        test_tools = [
            {
                "name": "testar_conexao_unificada",
                "description": "Testa conexão com ambas as plataformas (Omie + Nibo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["omie", "nibo", "both"], "default": "both"}
                    }
                }
            }
        ]
        
        # Combinar todas as ferramentas
        tools.extend(universal_tools)
        tools.extend(compatibility_tools)
        tools.extend(omie_exclusive_tools)
        tools.extend(nibo_exclusive_tools)
        tools.extend(test_tools)
        
        return tools
    
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
                        "serverInfo": {
                            "name": "unified-mcp-server",
                            "version": "1.0.0",
                            "description": "Servidor MCP Unificado (Omie + Nibo)"
                        }
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
                
                result = await self.call_unified_tool(tool_name, arguments)
                
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
    
    async def call_unified_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Chama ferramenta unificada"""
        try:
            platform = arguments.get("platform", "both")
            
            # Remover parâmetro platform dos argumentos
            clean_arguments = {k: v for k, v in arguments.items() if k != "platform"}
            
            # Ferramentas de teste
            if tool_name == "testar_conexao_unificada":
                return await self.test_unified_connection(platform)
            
            # Ferramentas exclusivas do Omie
            if tool_name in ["consultar_tipos_documento"]:
                omie_result = await self.omie_adapter.call_tool(tool_name, clean_arguments)
                return json.dumps(omie_result, ensure_ascii=False, indent=2)
            
            # Ferramentas exclusivas do Nibo
            if tool_name in ["consultar_socios", "incluir_socio", "incluir_multiplos_clientes"]:
                nibo_result = await self.nibo_adapter.call_tool(tool_name, clean_arguments)
                return json.dumps(nibo_result, ensure_ascii=False, indent=2)
            
            # Ferramentas universais
            if platform == "both":
                return await self.call_both_platforms(tool_name, clean_arguments)
            elif platform == "omie":
                omie_result = await self.omie_adapter.call_tool(tool_name, clean_arguments)
                return json.dumps(omie_result, ensure_ascii=False, indent=2)
            elif platform == "nibo":
                nibo_result = await self.nibo_adapter.call_tool(tool_name, clean_arguments)
                return json.dumps(nibo_result, ensure_ascii=False, indent=2)
            
            return json.dumps({"error": f"Ferramenta {tool_name} não encontrada"}, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
    
    async def call_both_platforms(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Chama ferramenta em ambas as plataformas e mescla resultados"""
        
        # Executar em paralelo
        omie_task = asyncio.create_task(self.omie_adapter.call_tool(tool_name, arguments))
        nibo_task = asyncio.create_task(self.nibo_adapter.call_tool(tool_name, arguments))
        
        omie_result, nibo_result = await asyncio.gather(omie_task, nibo_task, return_exceptions=True)
        
        # Processar resultados
        if isinstance(omie_result, Exception):
            omie_result = {"error": str(omie_result)}
        if isinstance(nibo_result, Exception):
            nibo_result = {"error": str(nibo_result)}
        
        # Determinar tipo de entidade
        entity_type = self.get_entity_type(tool_name)
        
        # Mesclar resultados
        merged_result = self.universal_mapper.merge_results(omie_result, nibo_result, entity_type)
        
        # Adicionar nota de compatibilidade se necessário
        compatibility_note = self.universal_mapper.get_compatibility_note(tool_name)
        if compatibility_note:
            merged_result["compatibility_note"] = compatibility_note
        
        return json.dumps(merged_result, ensure_ascii=False, indent=2)
    
    def get_entity_type(self, tool_name: str) -> str:
        """Determina tipo de entidade baseado no nome da ferramenta"""
        
        if "cliente" in tool_name:
            return "cliente"
        elif "fornecedor" in tool_name:
            return "fornecedor"
        elif "categoria" in tool_name:
            return "categoria"
        elif "departamento" in tool_name or "centro" in tool_name:
            return "departamento"
        elif "conta" in tool_name:
            return "conta"
        elif "socio" in tool_name:
            return "socio"
        
        return "generic"
    
    async def test_unified_connection(self, platform: str) -> str:
        """Testa conexão com plataformas"""
        
        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "platform_tests": {}
        }
        
        if platform in ["omie", "both"]:
            try:
                omie_result = await self.omie_adapter.call_tool("testar_conexao", {})
                results["platform_tests"]["omie"] = {
                    "status": "success",
                    "credentials": f"{self.omie_credentials['app_key'][:8]}...",
                    "result": omie_result
                }
            except Exception as e:
                results["platform_tests"]["omie"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        if platform in ["nibo", "both"]:
            try:
                nibo_result = await self.nibo_adapter.call_tool("testar_conexao", {})
                results["platform_tests"]["nibo"] = {
                    "status": "success",
                    "credentials": f"{self.nibo_credentials['token'][:8]}...",
                    "result": nibo_result
                }
            except Exception as e:
                results["platform_tests"]["nibo"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return json.dumps(results, ensure_ascii=False, indent=2)

async def main():
    """Função principal do servidor MCP unificado"""
    server = UnifiedMCPServer()
    logger.info("Servidor MCP Unificado iniciado")
    logger.info(f"Total de ferramentas: {len(server.tools)}")
    
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