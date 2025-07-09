# Projeto Omie MCP Server

## Contexto
Servidor MCP HTTP para integração com Omie ERP.

## Problema Atual
- Erro 500 Bad Request SOAP ao criar cliente
- Endpoint: /geral/clientes/
- Call: IncluirCliente

## Arquivos Importantes
- PROJECT_CONTEXT.md - Contexto completo
- TROUBLESHOOTING.md - Problemas e soluções
- omie_http_server.py - Servidor atual
- omie_server_json_fixed.py - Versão com correções

## Objetivo
1. Modularizar código
2. Resolver erro 500
3. Manter tools funcionais