#!/bin/bash

# Script para iniciar servidor MCP com verificação de porta
# Arquivo: start_server.sh

echo "🚀 Iniciando Omie MCP Server..."

# Verificar se a porta 3000 está em uso
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Porta 3000 já está em uso"
    
    # Mostrar qual processo está usando
    echo "📋 Processo atual:"
    lsof -i :3000
    
    # Perguntar se quer parar o processo
    read -p "❓ Deseja parar o processo existente? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Parando processo existente..."
        PID=$(lsof -ti :3000)
        if [ ! -z "$PID" ]; then
            kill -9 $PID
            echo "✅ Processo $PID parado"
            sleep 2
        fi
    else
        echo "🔄 Tentando porta alternativa 3001..."
        PORT=3001
    fi
else
    echo "✅ Porta 3000 disponível"
    PORT=3000
fi

# Iniciar servidor
echo "🌟 Iniciando servidor na porta $PORT..."
python omie_mcp_server_hybrid.py --mode http --port $PORT

echo "🎉 Servidor iniciado com sucesso!"
echo "🌐 Acesse: http://localhost:$PORT"
echo "📊 Teste: curl http://localhost:$PORT/test/testar_conexao"