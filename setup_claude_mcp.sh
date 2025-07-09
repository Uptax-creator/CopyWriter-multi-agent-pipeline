#!/bin/bash

# Script para configurar o Omie MCP Server no Claude Desktop
# Versão simplificada com carregamento automático de credenciais

echo "🚀 Configurando Omie MCP Server no Claude Desktop..."

# Criar diretório se não existir
echo "📁 Criando diretório de configuração do Claude..."
mkdir -p ~/Library/Application\ Support/Claude/

# Criar arquivo de configuração
echo "⚙️  Criando configuração MCP..."
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "omie-erp": {
      "command": "python",
      "args": ["/Users/kleberdossantosribeiro/omie-mcp/omie_http_server.py"]
    }
  }
}
EOF

# Verificar se o arquivo foi criado
if [ -f ~/Library/Application\ Support/Claude/claude_desktop_config.json ]; then
    echo "✅ Configuração criada com sucesso!"
    echo "📍 Local: ~/Library/Application Support/Claude/claude_desktop_config.json"
    echo ""
    echo "📋 Conteúdo da configuração:"
    cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
    echo ""
    echo "🔄 PRÓXIMOS PASSOS:"
    echo "1. Feche completamente o Claude Desktop"
    echo "2. Abra novamente o Claude Desktop"
    echo "3. Teste com: 'Consulte as categorias do Omie ERP'"
    echo ""
    echo "🎯 COMANDOS DE TESTE SUGERIDOS:"
    echo "• 'Liste as categorias do Omie ERP'"
    echo "• 'Mostre os departamentos disponíveis'"
    echo "• 'Consulte os tipos de documento'"
    echo "• 'Crie uma conta a pagar para o fornecedor X'"
    echo ""
    echo "💡 NOTA: As credenciais são carregadas automaticamente do arquivo credentials.json"
else
    echo "❌ Erro ao criar configuração!"
    exit 1
fi

# Verificar se credentials.json existe
if [ -f /Users/kleberdossantosribeiro/omie-mcp/credentials.json ]; then
    echo "✅ Arquivo credentials.json encontrado"
else
    echo "⚠️  Arquivo credentials.json não encontrado!"
    echo "   Crie o arquivo com suas credenciais Omie:"
    echo '   {"app_key": "sua_app_key", "app_secret": "seu_app_secret"}'
fi

# Verificar se o servidor Python funciona
echo ""
echo "🧪 Testando servidor Python..."
cd /Users/kleberdossantosribeiro/omie-mcp
python -c "
import sys
sys.path.insert(0, '.')
try:
    from omie_http_server import OMIE_APP_KEY
    print('✅ Servidor Python funcionando!')
    print(f'✅ Credenciais carregadas: {OMIE_APP_KEY[:8]}...****')
except Exception as e:
    print(f'❌ Erro: {e}')
"

echo ""
echo "🎉 Configuração concluída! Reinicie o Claude Desktop para ativar."