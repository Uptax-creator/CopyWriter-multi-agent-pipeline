#!/bin/bash

# Script para parar servidor MCP
# Arquivo: stop_server.sh

echo "🛑 Parando Omie MCP Server..."

# Verificar se há processos rodando
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "📋 Processos encontrados na porta 3000:"
    lsof -i :3000
    
    # Parar processos
    PID=$(lsof -ti :3000)
    if [ ! -z "$PID" ]; then
        echo "🛑 Parando processo $PID..."
        kill -9 $PID
        echo "✅ Processo parado"
    fi
else
    echo "ℹ️  Nenhum processo rodando na porta 3000"
fi

# Verificar porta 3001 também
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "📋 Processos encontrados na porta 3001:"
    lsof -i :3001
    
    # Parar processos
    PID=$(lsof -ti :3001)
    if [ ! -z "$PID" ]; then
        echo "🛑 Parando processo $PID..."
        kill -9 $PID
        echo "✅ Processo parado"
    fi
fi

# Verificar processos Python do MCP
echo "🔍 Verificando processos Python MCP..."
PYTHON_PIDS=$(ps aux | grep "omie_mcp_server" | grep -v grep | awk '{print $2}')

if [ ! -z "$PYTHON_PIDS" ]; then
    echo "🛑 Parando processos Python MCP: $PYTHON_PIDS"
    echo $PYTHON_PIDS | xargs kill -9
    echo "✅ Processos Python MCP parados"
else
    echo "ℹ️  Nenhum processo Python MCP encontrado"
fi

echo "🎉 Servidor MCP parado com sucesso!"