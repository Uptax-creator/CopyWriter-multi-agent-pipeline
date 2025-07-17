#!/usr/bin/env python3
"""
Cliente MCP Parametrizado para Claude Desktop
Permite configuração de credenciais via argumentos MCP
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, Optional
import httpx

# Configurar logging apenas para stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("claude-mcp-client-parameterized")

class ParameterizedMCPClient:
    """Cliente MCP com suporte a parametrização de credenciais"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.base_url = self.config.get("server_url", "http://localhost:3000")
        self.omie_credentials = self._load_credentials()
        
    def _load_credentials(self) -> Optional[Dict[str, str]]:
        """Carregar credenciais de múltiplas fontes"""
        credentials = {}
        
        # 1. Prioridade: Parâmetros passados via configuração MCP
        if "omie_app_key" in self.config and "omie_app_secret" in self.config:
            credentials = {
                "app_key": self.config["omie_app_key"],
                "app_secret": self.config["omie_app_secret"]
            }
            logger.info("Credenciais carregadas via configuração MCP")
            
        # 2. Fallback: Variáveis de ambiente
        elif os.getenv("OMIE_APP_KEY") and os.getenv("OMIE_APP_SECRET"):
            credentials = {
                "app_key": os.getenv("OMIE_APP_KEY"),
                "app_secret": os.getenv("OMIE_APP_SECRET")
            }
            logger.info("Credenciais carregadas via variáveis de ambiente")
            
        # 3. Fallback: Arquivo credentials.json
        else:
            try:
                credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
                if os.path.exists(credentials_path):
                    with open(credentials_path, 'r') as f:
                        file_creds = json.load(f)
                        credentials = {
                            "app_key": file_creds.get("app_key"),
                            "app_secret": file_creds.get("app_secret")
                        }
                    logger.info("Credenciais carregadas via arquivo credentials.json")
            except Exception as e:
                logger.error(f"Erro ao carregar credenciais do arquivo: {e}")
        
        if not credentials.get("app_key") or not credentials.get("app_secret"):
            logger.error("Nenhuma credencial válida encontrada!")
            return None
            
        return credentials
        
    async def initialize(self):
        """Inicializar cliente com credenciais"""
        try:
            # Enviar credenciais para o servidor HTTP
            if self.omie_credentials:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{self.base_url}/mcp/initialize",
                        json={"credentials": self.omie_credentials}
                    )
                    return response.json()
            else:
                raise Exception("Credenciais não configuradas")
        except Exception as e:
            logger.error(f"Erro ao inicializar: {e}")
            raise
    
    async def get_tools(self):
        """Obter lista de ferramentas"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/mcp/tools")
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Executar ferramenta"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/mcp/tools/{tool_name}",
                    json={"arguments": arguments}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                
                result = response.json()
                return result.get("content", [{}])[0].get("text", "Erro: resposta inválida")
                
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return f"Erro ao executar {tool_name}: {str(e)}"

class MCPServer:
    """Servidor MCP que atua como proxy para o servidor HTTP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.client = ParameterizedMCPClient(config)
        self.tools = []
        
    async def init_server(self):
        """Inicializar servidor"""
        try:
            # Inicializar cliente HTTP
            await self.client.initialize()
            
            # Obter ferramentas disponíveis
            tools_response = await self.client.get_tools()
            self.tools = tools_response.get("tools", [])
            
            logger.info(f"Servidor inicializado com {len(self.tools)} ferramentas")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar servidor: {e}")
            self.tools = []
    
    def send_response(self, response: Dict):
        """Enviar resposta via stdout"""
        print(json.dumps(response, ensure_ascii=False), flush=True)
    
    async def handle_request(self, request: Dict) -> Dict:
        """Processar requisição MCP"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                await self.init_server()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {"name": "omie-mcp-parameterized-client", "version": "2.0.0"}
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
                
                # Executar ferramenta via HTTP
                result = await self.client.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": result}]}
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

def load_config_from_args():
    """Carregar configuração dos argumentos da linha de comando"""
    config = {}
    
    # Analisar argumentos do sys.argv
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--server-url="):
            config["server_url"] = arg.split("=", 1)[1]
        elif arg.startswith("--omie-app-key="):
            config["omie_app_key"] = arg.split("=", 1)[1]
        elif arg.startswith("--omie-app-secret="):
            config["omie_app_secret"] = arg.split("=", 1)[1]
        elif arg.startswith("--config="):
            # Carregar configuração de arquivo JSON
            config_file = arg.split("=", 1)[1]
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                logger.error(f"Erro ao carregar configuração do arquivo {config_file}: {e}")
    
    return config

async def main():
    """Loop principal do cliente MCP"""
    # Carregar configuração
    config = load_config_from_args()
    
    server = MCPServer(config)
    logger.info("Cliente MCP Parametrizado iniciado")
    
    # Aguardar inicialização
    await asyncio.sleep(0.1)
    
    # Ler requisições da stdin
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            logger.info(f"Requisição recebida: {request.get('method')}")
            
            response = await server.handle_request(request)
            server.send_response(response)
            
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON")
        except KeyboardInterrupt:
            logger.info("Cliente interrompido")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")

if __name__ == "__main__":
    asyncio.run(main())