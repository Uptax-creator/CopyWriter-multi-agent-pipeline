include .env
export

test-cliente:
	@echo "🧪 Testando criar cliente..."
	@curl -X POST https://app.omie.com.br/api/v1/geral/clientes/ \
		-H "Content-Type: application/json" \
		-d '{"call":"IncluirCliente","app_key":"$(OMIE_APP_KEY)","app_secret":"$(OMIE_APP_SECRET)","param":[{"razao_social":"TESTE MAKE","cnpj_cpf":"11222333000155","email":"teste@make.com","cliente_fornecedor":"C"}]}' \
		-w "\n\nStatus: %{http_code}\n"

test-categorias:
	@echo "🧪 Testando listar categorias..."
	@curl -X POST https://app.omie.com.br/api/v1/geral/categorias/ \
		-H "Content-Type: application/json" \
		-d '{"call":"ListarCategorias","app_key":"$(OMIE_APP_KEY)","app_secret":"$(OMIE_APP_SECRET)","param":[{"pagina":1,"registros_por_pagina":5}]}' \
		-w "\n\nStatus: %{http_code}\n"

run-server:
	@source venv/bin/activate && python omie_http_server.py

test-all: test-categorias test-cliente