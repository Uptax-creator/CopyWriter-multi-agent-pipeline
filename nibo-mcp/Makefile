# Makefile para Nibo MCP Server v2.0
# Comandos úteis para gerenciar o serviço

.PHONY: help install test diagnose start monitor clean

# Configurações
PYTHON = python3
SCRIPTS_DIR = scripts

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(BLUE)Nibo MCP Server v2.0 - Comandos Disponíveis:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)  %-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Exemplos de uso:$(NC)"
	@echo "  make install     # Instalar dependências"
	@echo "  make test        # Testar todas as ferramentas"
	@echo "  make diagnose    # Diagnóstico completo"
	@echo "  make start       # Iniciar serviço"

install: ## Instala dependências
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	$(PYTHON) -m pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas$(NC)"

test-connection: ## Testa conectividade básica
	@echo "$(BLUE)🌐 Testando conectividade...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/test_connection.py

test: ## Executa teste completo de todas as ferramentas
	@echo "$(BLUE)🧪 Testando todas as ferramentas...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/test_all_tools_v2.py

diagnose: ## Executa diagnóstico completo do sistema
	@echo "$(BLUE)🔍 Executando diagnóstico completo...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/diagnose_nibo_service.py

start: ## Inicia o servidor MCP com verificações
	@echo "$(BLUE)🚀 Iniciando Nibo MCP Server...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/start_nibo_service.py

monitor: ## Inicia monitor de saúde contínuo
	@echo "$(BLUE)📊 Iniciando monitor de saúde...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/health_monitor.py

monitor-once: ## Executa uma verificação de saúde
	@echo "$(BLUE)🔍 Verificação única de saúde...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/health_monitor.py --once

server: ## Inicia apenas o servidor MCP (sem verificações)
	@echo "$(BLUE)🖥️  Iniciando servidor MCP...$(NC)"
	$(PYTHON) nibo_mcp_server.py

validate: ## Valida estrutura do projeto
	@echo "$(BLUE)✅ Validando estrutura do projeto...$(NC)"
	@test -f credentials.json || (echo "$(RED)❌ credentials.json não encontrado$(NC)" && exit 1)
	@test -f nibo_mcp_server.py || (echo "$(RED)❌ nibo_mcp_server.py não encontrado$(NC)" && exit 1)
	@test -d src/core || (echo "$(RED)❌ Diretório src/core não encontrado$(NC)" && exit 1)
	@test -d src/tools || (echo "$(RED)❌ Diretório src/tools não encontrado$(NC)" && exit 1)
	@echo "$(GREEN)✅ Estrutura do projeto válida$(NC)"

check-credentials: ## Verifica se credenciais estão configuradas
	@echo "$(BLUE)🔐 Verificando credenciais...$(NC)"
	@$(PYTHON) -c "import json; creds = json.load(open('credentials.json')); print('✅ Credenciais válidas') if creds.get('companies') else exit(1)" || (echo "$(RED)❌ Credenciais inválidas$(NC)" && exit 1)

quick-check: validate check-credentials test-connection ## Verificação rápida completa
	@echo "$(GREEN)🎉 Verificação rápida concluída com sucesso!$(NC)"

full-check: quick-check diagnose test ## Verificação completa (demora mais)
	@echo "$(GREEN)🎉 Verificação completa concluída com sucesso!$(NC)"

clean: ## Remove arquivos temporários e logs
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(NC)"
	@rm -f *.log
	@rm -f *_report_*.json
	@rm -f service_status.json
	@rm -rf __pycache__/
	@rm -rf src/__pycache__/
	@rm -rf src/core/__pycache__/
	@rm -rf src/tools/__pycache__/
	@rm -rf src/utils/__pycache__/
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"

logs: ## Mostra logs recentes
	@echo "$(BLUE)📋 Logs recentes:$(NC)"
	@if [ -f health_monitor.log ]; then \
		echo "$(YELLOW)Health Monitor (últimas 10 linhas):$(NC)"; \
		tail -10 health_monitor.log; \
		echo ""; \
	fi
	@if ls *_report_*.json 1> /dev/null 2>&1; then \
		echo "$(YELLOW)Relatórios disponíveis:$(NC)"; \
		ls -la *_report_*.json; \
	fi

status: ## Mostra status atual do serviço
	@echo "$(BLUE)📊 Status do Nibo MCP Server:$(NC)"
	@if [ -f service_status.json ]; then \
		$(PYTHON) -c "import json; status = json.load(open('service_status.json')); print(f\"Status: {status.get('status', 'unknown')}\"); print(f\"Iniciado: {status.get('started_at', 'unknown')}\"); print(f\"Versão: {status.get('version', 'unknown')}\")"; \
	else \
		echo "$(YELLOW)⚠️  Arquivo de status não encontrado$(NC)"; \
	fi

dev-setup: install validate check-credentials ## Configuração para desenvolvimento
	@echo "$(GREEN)🛠️  Ambiente de desenvolvimento configurado!$(NC)"
	@echo "$(YELLOW)Próximos passos:$(NC)"
	@echo "  1. make test-connection  # Testar conectividade"
	@echo "  2. make diagnose         # Diagnóstico completo"
	@echo "  3. make start            # Iniciar serviço"

prod-setup: dev-setup full-check ## Configuração para produção
	@echo "$(GREEN)🚀 Ambiente de produção validado!$(NC)"
	@echo "$(YELLOW)Para monitoramento contínuo:$(NC)"
	@echo "  make monitor &           # Monitor em background"

# Comandos de desenvolvimento
lint: ## Executa linting do código (se pylint instalado)
	@if command -v pylint >/dev/null 2>&1; then \
		echo "$(BLUE)🔍 Executando pylint...$(NC)"; \
		pylint src/ --disable=all --enable=E,W; \
	else \
		echo "$(YELLOW)⚠️  pylint não instalado$(NC)"; \
	fi

format: ## Formata código (se black instalado)
	@if command -v black >/dev/null 2>&1; then \
		echo "$(BLUE)🎨 Formatando código...$(NC)"; \
		black src/ scripts/; \
	else \
		echo "$(YELLOW)⚠️  black não instalado$(NC)"; \
	fi

# Comandos de debug
debug-api: ## Debug de conectividade com API
	@echo "$(BLUE)🐛 Debug de API...$(NC)"
	@$(PYTHON) -c "import asyncio; from src.core.config import NiboConfig; from src.core.nibo_client import NiboClient; config = NiboConfig(); client = NiboClient(config); print('Config:', config.get_current_company_info()); result = asyncio.run(client.testar_conexao()); print('Result:', result)"

debug-tools: ## Debug básico das ferramentas
	@echo "$(BLUE)🐛 Debug de ferramentas...$(NC)"
	@$(PYTHON) -c "from src.tools.consultas import NiboConsultas; from src.core.nibo_client import NiboClient; from src.core.config import NiboConfig; import asyncio; config = NiboConfig(); client = NiboClient(config); consultas = NiboConsultas(client); result = asyncio.run(consultas.consultar_categorias(registros_por_pagina=1)); print('Categorias:', len(result.get('items', [])))"

# Comandos de informação
version: ## Mostra versão e informações
	@echo "$(BLUE)Nibo MCP Server v2.0$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Diretório: $(shell pwd)"
	@echo "Ferramentas: 31 implementadas"

list-tools: ## Lista todas as ferramentas disponíveis
	@echo "$(BLUE)🛠️  Ferramentas Implementadas (31):$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 Consultas (7):$(NC)"
	@echo "  consultar_categorias, consultar_centros_custo, consultar_clientes"
	@echo "  consultar_fornecedores, consultar_contas_pagar, consultar_contas_receber, consultar_socios"
	@echo ""
	@echo "$(YELLOW)👥 CRUD Clientes/Fornecedores (8):$(NC)"
	@echo "  incluir_cliente, alterar_cliente, excluir_cliente, obter_cliente_por_id"
	@echo "  incluir_fornecedor, alterar_fornecedor, excluir_fornecedor, obter_fornecedor_por_id"
	@echo ""
	@echo "$(YELLOW)💰 CRUD Financeiro (6):$(NC)"
	@echo "  incluir_conta_pagar, alterar_conta_pagar, excluir_conta_pagar"
	@echo "  incluir_conta_receber, alterar_conta_receber, excluir_conta_receber"
	@echo ""
	@echo "$(YELLOW)🆕 CRUD Sócios (5):$(NC)"
	@echo "  consultar_socios, incluir_socio, alterar_socio, excluir_socio, obter_socio_por_id"
	@echo ""
	@echo "$(YELLOW)⚙️  Gerenciamento (4):$(NC)"
	@echo "  listar_empresas, selecionar_empresa, info_empresa_atual, testar_conexao"
	@echo ""
	@echo "$(YELLOW)🔄 Compatibilidade (1):$(NC)"
	@echo "  consultar_departamentos (alias para consultar_centros_custo)"