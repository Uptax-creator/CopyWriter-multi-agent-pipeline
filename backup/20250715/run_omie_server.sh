#!/bin/bash

# Script wrapper para executar o servidor Omie MCP com ambiente virtual
# Isso resolve o problema de PATH do Claude Desktop

cd /Users/kleberdossantosribeiro/omie-mcp

# Ativar ambiente virtual
source venv/bin/activate

# Executar servidor
python omie_http_server.py