#!/bin/bash

# 🚀 Script de Instalação do Omie MCP HTTP Server
# Este script automatiza a instalação e configuração do projeto

set -e  # Sair em caso de erro

echo "🚀 Iniciando instalação do Omie MCP HTTP Server..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se o diretório do projeto existe
PROJECT_DIR="$HOME/omie-mcp"

if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Criando diretório do projeto: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
else
    print_success "Diretório do projeto já existe: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Verificar e criar ambiente virtual
if [ ! -d "venv" ]; then
    print_status "Criando ambiente virtual Python..."
    python3 -m venv venv
    print_success "Ambiente virtual criado!"
else
    print_success "Ambiente virtual já existe!"
fi

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
print_status "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências básicas
print_status "Instalando dependências básicas..."
pip install httpx pydantic mcp

# Instalar dependências do servidor HTTP
print_status "Instalando dependências do servidor HTTP (FastAPI, Uvicorn)..."
pip install fastapi uvicorn

# Verificar instalações
print_status "Verificando instalações..."
echo "Dependências instaladas:"
pip list | grep -E "(fastapi|uvicorn|pydantic|httpx|mcp)" || true

# Verificar se as credenciais estão configuradas
print_warning "IMPORTANTE: Configure suas credenciais do Omie!"
echo ""
echo "1. Obtenha suas credenciais em: https://app.omie.com.br/"
echo "2. Configure as variáveis de ambiente:"
echo "   export OMIE_APP_KEY='sua_app_key'"
echo "   export OMIE_APP_SECRET='seu_app_secret'"
echo ""

# Verificar se o arquivo do servidor existe
if [ ! -f "omie_http_server.py" ]; then
    print_warning "Arquivo omie_http_server.py não encontrado!"
    print_status "Copie o código do servidor HTTP para: $PROJECT_DIR/omie_http_server.py"
else
    print_success "Arquivo omie_http_server.py encontrado!"
fi

# Verificar permissões de execução
if [ -f "omie_http_server.py" ]; then
    chmod +x omie_http_server.py
    print_success "Permissões de execução configuradas!"
fi

# Criar script de teste
print_status "Criando script de teste..."
cat > test_server.sh << 'EOF'
#!/bin/bash
cd ~/omie-mcp
source venv/bin/activate

echo "🧪 Testando servidor HTTP..."
echo "Certifique-se de que as credenciais estão configuradas:"
echo "export OMIE_APP_KEY='sua_app_key'"
echo "export OMIE_APP_SECRET='seu_app_secret'"
echo ""

if [ -z "$OMIE_APP_KEY" ] || [ -z "$OMIE_APP_SECRET" ]; then
    echo "❌ ERRO: Credenciais não configuradas!"
    echo "Configure as variáveis de ambiente antes de executar o servidor."
    exit 1
fi

echo "🚀 Iniciando servidor..."
python omie_http_server.py
EOF

chmod +x test_server.sh
print_success "Script de teste criado: test_server.sh"

# Informações finais
echo ""
print_success "🎉 Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas credenciais:"
echo "   export OMIE_APP_KEY='sua_app_key'"
echo "   export OMIE_APP_SECRET='seu_app_secret'"
echo ""
echo "2. Copie o código do servidor para: $PROJECT_DIR/omie_http_server.py"
echo ""
echo "3. Teste o servidor:"
echo "   cd $PROJECT_DIR"
echo "   ./test_server.sh"
echo ""
echo "4. Configure o Claude Desktop:"
echo "   - Edite: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "   - Use a configuração fornecida no projeto"
echo ""
echo "🔗 URLs de teste (após iniciar o servidor):"
echo "   • Status: http://localhost:8000"
echo "   • Docs: http://localhost:8000/docs"
echo "   • Health: http://localhost:8000/health"
echo ""
print_success "Instalação finalizada com sucesso! 🚀"