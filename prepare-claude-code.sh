#!/bin/bash
# Script para preparar o projeto Omie MCP para o Claude Code

echo "🚀 Preparando projeto Omie MCP para Claude Code..."
echo "=================================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_DIR=~/omie-mcp
cd $PROJECT_DIR || exit 1

# 1. Criar estrutura de diretórios
echo -e "${BLUE}📁 Criando estrutura de diretórios...${NC}"
mkdir -p context
mkdir -p backup
mkdir -p reference

# 2. Fazer backup dos arquivos existentes
echo -e "${BLUE}📦 Fazendo backup dos arquivos atuais...${NC}"
BACKUP_DIR="backup/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Copiar arquivos Python existentes
for file in *.py; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "   ✓ Backup: $file"
    fi
done

# 3. Salvar arquivos de referência
echo -e "${BLUE}📚 Salvando arquivos de referência...${NC}"
if [ -f "omie_http_server.py" ]; then
    cp omie_http_server.py reference/omie_http_server_v2.py
fi
if [ -f "omie_server_json_fixed.py" ]; then
    cp omie_server_json_fixed.py reference/omie_server_json_fixed_v6.py
fi

# 4. Criar arquivo de credenciais template
echo -e "${BLUE}🔑 Criando template de credenciais...${NC}"
cat > .env.example << 'EOF'
# Credenciais Omie
OMIE_APP_KEY=sua_app_key_aqui
OMIE_APP_SECRET=seu_app_secret_aqui

# Configurações do servidor
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
EOF

# 5. Salvar comandos úteis
echo -e "${BLUE}📝 Criando arquivo de comandos úteis...${NC}"
cat > context/COMMANDS.md << 'EOF'
# Comandos Úteis - Omie MCP

## 🚀 Iniciar servidor
```bash
cd ~/omie-mcp
source venv/bin/activate
python omie_http_server.py
```

## 🧪 Testar ferramentas

### Testar Cliente (que está com erro)
```bash
curl -X POST http://localhost:8000/test/cliente \
  -H "Content-Type: application/json" \
  -d '{
    "razao_social": "TESTE CLIENTE",
    "cnpj_cpf": "11222333000144",
    "email": "teste@email.com",
    "tipo_cliente": "cliente"
  }'
```

### Testar Categorias (funcionando)
```bash
curl http://localhost:8000/test/categorias
```

### Ver documentação interativa
```
http://localhost:8000/docs
```

## 🔍 Debug direto na API Omie
```bash
# Configurar credenciais
export OMIE_APP_KEY="sua_key"
export OMIE_APP_SECRET="seu_secret"

# Testar direto
./context/test_api_direct.sh
```

## 📊 Ver logs em tempo real
```bash
# Terminal 1: Servidor
python omie_http_server.py

# Terminal 2: Logs
tail -f logs/omie_mcp.log
```
EOF

# 6. Criar script de teste direto da API
echo -e "${BLUE}🔧 Criando script de teste direto...${NC}"
cat > context/test_api_direct.sh << 'EOF'
#!/bin/bash
# Teste direto da API Omie

# Verificar se as credenciais estão definidas
if [ -z "$OMIE_APP_KEY" ] || [ -z "$OMIE_APP_SECRET" ]; then
    echo "❌ Erro: Configure OMIE_APP_KEY e OMIE_APP_SECRET"
    echo "   export OMIE_APP_KEY='sua_key'"
    echo "   export OMIE_APP_SECRET='seu_secret'"
    exit 1
fi

echo "🧪 Testando API Omie diretamente..."
echo "📍 Endpoint: /geral/clientes/"
echo "🔧 Method: IncluirCliente"
echo ""

# Fazer requisição
curl -X POST https://app.omie.com.br/api/v1/geral/clientes/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "call": "IncluirCliente",
    "app_key": "'$OMIE_APP_KEY'",
    "app_secret": "'$OMIE_APP_SECRET'",
    "param": [{
      "razao_social": "TESTE DIRETO CURL",
      "cnpj_cpf": "55666777000188",
      "email": "teste@curl.com",
      "cliente_fornecedor": "C",
      "inativo": "N"
    }]
  }' \
  -w "\n\n📊 Status HTTP: %{http_code}\n" \
  -v
EOF
chmod +x context/test_api_direct.sh

# 7. Criar resumo do estado atual
echo -e "${BLUE}📋 Criando resumo do estado atual...${NC}"
cat > context/CURRENT_STATE.md << 'EOF'
# Estado Atual - Omie MCP Server

**Data:** $(date)

## 🚨 Problema Principal
- **Erro:** 500 Bad Request SOAP
- **Endpoint:** /geral/clientes/
- **Método:** IncluirCliente
- **Resposta:** XML/SOAP em vez de JSON

## ✅ O que funciona
- Servidor HTTP FastAPI
- Endpoints de consulta (categorias, departamentos)
- Validação e sanitização JSON

## ❌ O que não funciona
- Criar cliente/fornecedor
- Criar contas (bloqueado pelo erro acima)

## 🔍 Diagnóstico
1. JSON está válido (corrigido erro 422)
2. Credenciais estão corretas (outras APIs funcionam)
3. API retorna SOAP/XML indicando erro na requisição
4. Possível campo obrigatório faltando ou formato incorreto

## 🎯 Próximo passo
Modularizar código e testar diretamente com curl
EOF

# 8. Informações finais
echo ""
echo -e "${GREEN}✅ Projeto preparado para Claude Code!${NC}"
echo ""
echo -e "${YELLOW}📋 Arquivos criados:${NC}"
echo "   • PROJECT_CONTEXT.md - Contexto completo do projeto"
echo "   • TROUBLESHOOTING.md - Problemas e soluções"
echo "   • setup_context.py - Script Python de configuração"
echo "   • .claude-context - Configuração para Claude Code"
echo "   • context/ - Diretório com arquivos de referência"
echo "   • $BACKUP_DIR/ - Backup dos arquivos atuais"
echo ""
echo -e "${YELLOW}🚀 Próximos passos:${NC}"
echo "1. Instale o Claude Code (se ainda não tem):"
echo "   pip install claude-code"
echo ""
echo "2. Inicie o Claude Code neste diretório:"
echo "   cd ~/omie-mcp"
echo "   claude-code"
echo ""
echo "3. Primeira mensagem para o Claude Code:"
echo "   'Veja o contexto completo em PROJECT_CONTEXT.md e TROUBLESHOOTING.md."
echo "    Precisamos modularizar o código e resolver o erro 500 SOAP.'"
echo ""
echo -e "${GREEN}Boa sorte! 🍀${NC}"