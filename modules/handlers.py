"""
Handlers para as ferramentas MCP do Omie ERP
"""

import json
import logging
from datetime import datetime
from typing import Dict
from .omie_client import OmieClient
from .validators import OmieValidators


logger = logging.getLogger("omie-mcp-complete")


class OmieHandlers:
    """Handlers para as ferramentas MCP do Omie ERP"""
    
    def __init__(self, omie_client: OmieClient):
        self.omie_client = omie_client
        self.validators = OmieValidators(omie_client)
    
    # ========== HANDLERS DE CLIENTES/FORNECEDORES ==========
    
    async def handle_cadastrar_cliente_fornecedor(self, args: Dict) -> str:
        """Handler para cadastrar cliente/fornecedor"""
        
        # Gerar código único de integração
        import time
        codigo_integracao = f"MCP-{int(time.time())}"
        
        # Mapear tipos
        tipo_map = {"cliente": "C", "fornecedor": "F", "ambos": "A"}
        
        dados_omie = {
            "codigo_cliente_integracao": codigo_integracao,
            "razao_social": args["razao_social"],
            "cnpj_cpf": args["cnpj_cpf"],
            "email": args["email"],
            "nome_fantasia": args.get("nome_fantasia", ""),
            "telefone1_ddd": args.get("telefone1_ddd", ""),
            "telefone1_numero": args.get("telefone1_numero", ""),
            "endereco": args.get("endereco", ""),
            "cidade": args.get("cidade", ""),
            "estado": args.get("estado", ""),
            "cep": args.get("cep", "")
        }
        
        resultado = await self.omie_client.cadastrar_cliente_fornecedor(dados_omie)
        
        if "codigo_cliente_omie" in resultado:
            return f"""✅ Cliente/Fornecedor cadastrado com sucesso!

📋 Detalhes:
• Código Omie: {resultado['codigo_cliente_omie']}
• Código Integração: {codigo_integracao}
• Razão Social: {args['razao_social']}
• CNPJ/CPF: {args['cnpj_cpf']}
• E-mail: {args['email']}
• Tipo: {args['tipo_cliente']}

🔗 Disponível no módulo Geral > Clientes/Fornecedores do Omie ERP"""
        else:
            return f"✅ Cadastrado! Resposta: {json.dumps(resultado, ensure_ascii=False, indent=2)}"
    
    # ========== HANDLERS DE CONSULTA ==========
    
    async def handle_consultar_categorias(self, args: Dict) -> str:
        """Handler para consultar categorias"""
        
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 50)
        }
        
        resultado = await self.omie_client.consultar_categorias(params)
        
        categorias = resultado.get("categoria_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if categorias:
            lista_categorias = []
            for categoria in categorias:
                codigo = categoria.get("codigo", "N/A")
                descricao = categoria.get("descricao", "N/A")
                lista_categorias.append(f"• {codigo} - {descricao}")
            
            return f"""📋 Categorias encontradas: {total}

{chr(10).join(lista_categorias)}

💡 Use os códigos acima para criar contas a pagar/receber"""
        else:
            return "❌ Nenhuma categoria encontrada"
    
    async def handle_consultar_departamentos(self, args: Dict) -> str:
        """Handler para consultar departamentos"""
        
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 50)
        }
        
        resultado = await self.omie_client.consultar_departamentos(params)
        
        departamentos = resultado.get("departamentos", [])
        total = resultado.get("total_de_registros", 0)
        
        if departamentos:
            lista_departamentos = []
            for departamento in departamentos:
                codigo = departamento.get("codigo", "N/A")
                descricao = departamento.get("descricao", "N/A")
                estrutura = departamento.get("estrutura", "N/A")
                inativo = departamento.get("inativo", "N")
                status = "🔴 Inativo" if inativo == "S" else "🟢 Ativo"
                lista_departamentos.append(f"• {codigo} - {descricao} ({estrutura}) {status}")
            
            return f"""🏢 Departamentos encontrados: {total}

{chr(10).join(lista_departamentos)}

💡 Use os códigos acima para distribuir custos nas contas"""
        else:
            return "❌ Nenhum departamento encontrado"
    
    async def handle_consultar_tipos_documento(self, args: Dict) -> str:
        """Handler para consultar tipos de documentos"""
        
        resultado = await self.omie_client.consultar_tipos_documento({})
        
        tipos = resultado.get("tipo_documento_cadastro", [])
        
        if tipos:
            lista_tipos = []
            for tipo in tipos:
                codigo = tipo.get("codigo", "N/A")
                descricao = tipo.get("descricao", "N/A")
                lista_tipos.append(f"• {codigo} - {descricao}")
            
            return f"""📄 Tipos de documentos encontrados: {len(tipos)}

{chr(10).join(lista_tipos)}

💡 Use os códigos acima para classificar documentos"""
        else:
            return "❌ Nenhum tipo de documento encontrado"
    
    # ========== HANDLERS DE CONTAS A PAGAR ==========
    
    async def handle_consultar_contas_pagar(self, args: Dict) -> str:
        """Handler para consultar contas a pagar"""
        
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 20)
        }
        
        # Adicionar filtros se fornecidos
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await self.omie_client.consultar_contas_pagar(params)
        
        contas = resultado.get("conta_pagar_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"""💰 Contas a Pagar encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💵 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}

📊 Filtros aplicados:
{f"• Fornecedor: {args.get('codigo_cliente_fornecedor', 'Todos')}" if args.get('codigo_cliente_fornecedor') else "• Fornecedor: Todos"}
{f"• Período: {args.get('data_inicio', 'N/A')} a {args.get('data_fim', 'N/A')}" if args.get('data_inicio') else "• Período: Todos"}"""
        else:
            return "❌ Nenhuma conta a pagar encontrada com os filtros especificados"
    
    # ========== HANDLERS DE CONTAS A RECEBER ==========
    
    async def handle_consultar_contas_receber(self, args: Dict) -> str:
        """Handler para consultar contas a receber"""
        
        params = {
            "pagina": args.get("pagina", 1),
            "registros_por_pagina": args.get("registros_por_pagina", 20)
        }
        
        # Adicionar filtros se fornecidos
        if args.get("codigo_cliente_fornecedor"):
            params["codigo_cliente_fornecedor"] = args["codigo_cliente_fornecedor"]
        
        if args.get("data_inicio") and args.get("data_fim"):
            params["data_de"] = args["data_inicio"]
            params["data_ate"] = args["data_fim"]
        
        resultado = await self.omie_client.consultar_contas_receber(params)
        
        contas = resultado.get("conta_receber_cadastro", [])
        total = resultado.get("total_de_registros", 0)
        
        if contas:
            lista_contas = []
            total_valor = 0
            
            for conta in contas[:10]:
                numero_doc = conta.get("numero_documento", "N/A")
                valor = conta.get("valor_documento", 0)
                vencimento = conta.get("data_vencimento", "N/A")
                status = conta.get("status_titulo", "N/A")
                
                total_valor += valor
                lista_contas.append(f"• Doc: {numero_doc} | R$ {valor:,.2f} | Venc: {vencimento} | Status: {status}")
            
            return f"""💵 Contas a Receber encontradas: {total}

📋 Lista de contas:
{chr(10).join(lista_contas)}

💰 Total (10 primeiras): R$ {total_valor:,.2f}
{f"(Mostrando 10 de {total})" if total > 10 else ""}

📊 Filtros aplicados:
{f"• Cliente: {args.get('codigo_cliente_fornecedor', 'Todos')}" if args.get('codigo_cliente_fornecedor') else "• Cliente: Todos"}
{f"• Período: {args.get('data_inicio', 'N/A')} a {args.get('data_fim', 'N/A')}" if args.get('data_inicio') else "• Período: Todos"}"""
        else:
            return "❌ Nenhuma conta a receber encontrada com os filtros especificados"