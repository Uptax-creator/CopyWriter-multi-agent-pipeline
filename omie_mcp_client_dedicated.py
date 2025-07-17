#!/usr/bin/env python3
"""
Cliente MCP Dedicado para Omie ERP
Versão robusta com autenticação e roteamento correto
"""

import asyncio
import json
import logging
import sys
import argparse
import requests
from typing import Dict, Any, Optional
import time
from urllib.parse import urljoin

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("omie-mcp-client")

class OmieMCPClient:
    """Cliente MCP dedicado para Omie com autenticação robusta"""
    
    def __init__(self, server_url: str, server_name: str, api_key: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.server_name = server_name
        self.api_key = api_key
        self.session = requests.Session()
        
        # Configurar headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'OmieMCPClient/{server_name}',
            'Connection': 'close',
            'Accept': 'application/json'
        })
        
        # Desabilitar verificação SSL para desenvolvimento
        self.session.verify = False
        
        # Adicionar autenticação se fornecida
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
            
        logger.info(f"Cliente MCP Omie inicializado para {server_name} em {server_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Faz requisição HTTP com tratamento de erros"""
        url = urljoin(self.server_url + '/', endpoint.lstrip('/'))
        
        try:
            logger.debug(f"Fazendo requisição {method} para {url}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Método HTTP {method} não suportado")
            
            logger.debug(f"Resposta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise Exception(f"Endpoint não encontrado: {endpoint}")
            elif response.status_code == 401:
                raise Exception("Não autorizado - verificar credenciais")
            elif response.status_code == 500:
                raise Exception(f"Erro interno do servidor: {response.text}")
            else:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectTimeout:
            raise Exception(f"Timeout de conexão com {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Erro de conexão com {url}")
        except requests.exceptions.RequestException as e:
            # Tentar extrair conteúdo mesmo com erro
            if hasattr(e, 'response') and e.response is not None:
                try:
                    content = e.response.text
                    if content:
                        logger.warning(f"Conteúdo da resposta com erro: {content[:200]}...")
                        # Tentar fazer parse do JSON mesmo com erro de conexão
                        return json.loads(content)
                except:
                    pass
            raise Exception(f"Erro na requisição: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            logger.error(f"Conteúdo da resposta: {response.text[:200]}...")
            raise Exception("Resposta inválida do servidor (não é JSON)")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Obtém informações do servidor"""
        return self._make_request('GET', '/')
    
    def list_tools(self) -> Dict[str, Any]:
        """Lista ferramentas disponíveis"""
        return self._make_request('GET', '/mcp/tools')
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Chama uma ferramenta específica"""
        if arguments is None:
            arguments = {}
            
        endpoint = f'/mcp/tools/{tool_name}'
        payload = {'arguments': arguments}
        
        return self._make_request('POST', endpoint, payload)
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com o servidor"""
        try:
            # Primeiro testa informações básicas
            info = self.get_server_info()
            logger.info(f"Servidor: {info.get('service', 'N/A')} v{info.get('version', 'N/A')}")
            
            # Depois lista ferramentas
            tools = self.list_tools()
            logger.info(f"Ferramentas disponíveis: {tools.get('tools_count', 0)}")
            
            # Finalmente testa uma ferramenta
            result = self.call_tool('testar_conexao')
            
            return {
                'status': 'success',
                'server_info': info,
                'tools_count': tools.get('tools_count', 0),
                'test_result': result
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de conexão: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

class MCPStdioHandler:
    """Manipula protocolo MCP via STDIO"""
    
    def __init__(self, client: OmieMCPClient):
        self.client = client
        self.request_id_counter = 0
        
    def get_request_id(self, request: Dict[str, Any]) -> str:
        """Obtém ID da requisição"""
        return str(request.get("id", "unknown"))
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta via STDIO"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
        logger.debug(f"Resposta enviada: {response_json}")
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição de inicialização"""
        request_id = self.get_request_id(request)
        
        try:
            # Testar conexão com servidor
            test_result = self.client.test_connection()
            
            if test_result['status'] == 'success':
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": self.client.server_name,
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
            else:
                raise Exception(test_result['error'])
                
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro na inicialização: {str(e)}"
                }
            }
    
    async def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Lista ferramentas disponíveis"""
        request_id = self.get_request_id(request)
        
        try:
            tools_data = self.client.list_tools()
            tools = tools_data.get("tools", [])
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro ao listar ferramentas: {str(e)}"
                }
            }
    
    async def handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Chama ferramenta específica"""
        request_id = self.get_request_id(request)
        
        try:
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": "Nome da ferramenta é obrigatório"}
                }
            
            # Chamar ferramenta
            result = self.client.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Erro ao executar ferramenta: {str(e)}"
                }
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> None:
        """Processa requisição MCP"""
        method = request.get("method")
        
        if method == "initialize":
            response = await self.handle_initialize(request)
        elif method == "tools/list":
            response = await self.handle_list_tools(request)
        elif method == "tools/call":
            response = await self.handle_tool_call(request)
        else:
            response = {
                "jsonrpc": "2.0",
                "id": self.get_request_id(request),
                "error": {
                    "code": -32601,
                    "message": f"Método não suportado: {method}"
                }
            }
        
        self.send_response(response)
    
    async def run(self) -> None:
        """Executa cliente MCP via STDIO"""
        logger.info("Cliente MCP Omie iniciado (STDIO)")
        
        try:
            while True:
                try:
                    line = input()
                    if not line.strip():
                        continue
                    
                    request = json.loads(line)
                    await self.handle_request(request)
                    
                except EOFError:
                    logger.info("EOF recebido, encerrando cliente")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    continue
                except KeyboardInterrupt:
                    logger.info("Interrompido pelo usuário")
                    break
                except Exception as e:
                    logger.error(f"Erro inesperado: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Erro crítico no cliente: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Cliente MCP dedicado para Omie ERP')
    parser.add_argument('--server-url', required=True, help='URL do servidor MCP')
    parser.add_argument('--server-name', required=True, help='Nome do servidor')
    parser.add_argument('--api-key', help='Chave de API para autenticação')
    parser.add_argument('--test', action='store_true', help='Apenas testar conexão')
    
    args = parser.parse_args()
    
    # Criar cliente
    client = OmieMCPClient(
        server_url=args.server_url,
        server_name=args.server_name,
        api_key=args.api_key
    )
    
    if args.test:
        # Apenas testar conexão
        result = client.test_connection()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['status'] == 'success' else 1)
    
    # Executar cliente MCP
    handler = MCPStdioHandler(client)
    asyncio.run(handler.run())

if __name__ == "__main__":
    main()