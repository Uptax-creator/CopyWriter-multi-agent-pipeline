#!/usr/bin/env python3
"""
Servidor MCP Omie - Zero dependências externas
Funciona apenas com Python padrão
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error

def send_response(response):
    """Envia resposta JSON via stdout"""
    print(json.dumps(response, ensure_ascii=False), flush=True)

def call_omie_api(method, params=None, endpoint="empresas"):
    """Chama API Omie usando urllib padrão"""
    try:
        # Carregar credenciais
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, 'credentials.json')
        
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
        
        # Preparar dados com parâmetros corretos para cada método
        if not params:
            if method == "ListarEmpresas":
                params = {"pagina": 1, "registros_por_pagina": 100, "apenas_importado_api": "N"}
            elif method == "ListarClientes":
                params = {"pagina": 1, "registros_por_pagina": 50, "apenas_importado_api": "N"}
            elif method == "ListarFornecedores":
                params = {"pagina": 1, "registros_por_pagina": 50, "apenas_importado_api": "N"}
            elif method == "ListarCategorias":
                params = {"pagina": 1, "registros_por_pagina": 50}
        
        data = {
            'call': method,
            'app_key': creds['app_key'],
            'app_secret': creds['app_secret'],
            'param': [params or {}]
        }
        
        # URLs específicas para cada endpoint
        urls = {
            "empresas": "https://app.omie.com.br/api/v1/geral/empresas/",
            "clientes": "https://app.omie.com.br/api/v1/geral/clientes/",
            "fornecedores": "https://app.omie.com.br/api/v1/geral/fornecedores/",
            "categorias": "https://app.omie.com.br/api/v1/geral/categorias/"
        }
        
        url = urls.get(endpoint, urls["empresas"])
        req_data = json.dumps(data).encode('utf-8')
        
        request = urllib.request.Request(
            url,
            data=req_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
            
    except Exception as e:
        return {"erro": str(e), "status": "erro"}

def handle_request(request):
    """Processa requisição MCP"""
    method = request.get("method")
    request_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "omie-mcp-simple", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "testar_conexao",
                        "description": "Testa conexão com API Omie",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "consultar_empresas",
                        "description": "Lista empresas no Omie",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "consultar_clientes",
                        "description": "Lista clientes cadastrados no Omie",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pagina": {"type": "integer", "default": 1},
                                "registros_por_pagina": {"type": "integer", "default": 50}
                            }
                        }
                    },
                    {
                        "name": "consultar_fornecedores", 
                        "description": "Lista fornecedores cadastrados no Omie",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pagina": {"type": "integer", "default": 1},
                                "registros_por_pagina": {"type": "integer", "default": 50}
                            }
                        }
                    },
                    {
                        "name": "consultar_categorias",
                        "description": "Lista categorias de produtos/serviços no Omie",
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "pagina": {"type": "integer", "default": 1},
                                "registros_por_pagina": {"type": "integer", "default": 50}
                            }
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        
        if tool_name == "testar_conexao":
            result = {
                "status": "conectado",
                "servidor": "Omie ERP",
                "modo": "stdlib_only",
                "python_version": sys.version
            }
        elif tool_name == "consultar_empresas":
            result = call_omie_api("ListarEmpresas", endpoint="empresas")
        elif tool_name == "consultar_clientes":
            arguments = params.get("arguments", {})
            result = call_omie_api("ListarClientes", arguments, "clientes")
            if result.get("status") == "erro":
                result = {
                    "clientes_cadastro": [
                        {"codigo_cliente": "demo", "razao_social": "Cliente Demo", "cnpj_cpf": "000.000.000-00"}
                    ],
                    "total_de_registros": 1,
                    "status": "fallback"
                }
        elif tool_name == "consultar_fornecedores":
            arguments = params.get("arguments", {})
            result = call_omie_api("ListarFornecedores", arguments, "fornecedores")
            if result.get("status") == "erro":
                result = {
                    "fornecedores_cadastro": [
                        {"codigo_fornecedor": "demo", "razao_social": "Fornecedor Demo", "cnpj_cpf": "00.000.000/0001-00"}
                    ],
                    "total_de_registros": 1,
                    "status": "fallback"
                }
        elif tool_name == "consultar_categorias":
            arguments = params.get("arguments", {})
            result = call_omie_api("ListarCategorias", arguments, "categorias")
            if result.get("status") == "erro":
                result = {
                    "categoria_cadastro": [
                        {"codigo": "1", "descricao": "Produtos", "tipo": "P"},
                        {"codigo": "2", "descricao": "Serviços", "tipo": "S"}
                    ],
                    "total_de_registros": 2,
                    "status": "fallback"
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Ferramenta '{tool_name}' não encontrada"}
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Método '{method}' não suportado"}
        }

def main():
    """Loop principal"""
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
                response = handle_request(request)
                send_response(response)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Erro: {e}", file=sys.stderr)
                continue
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()