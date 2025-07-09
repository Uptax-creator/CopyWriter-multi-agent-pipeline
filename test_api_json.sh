#!/bin/bash

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com: brew install jq"
    exit 1
fi

# Ler credenciais do JSON
APP_KEY=$(jq -r '.app_key' credentials.json)
APP_SECRET=$(jq -r '.app_secret' credentials.json)

echo "🧪 Testando com credenciais do JSON..."

curl -X POST https://app.omie.com.br/api/v1/geral/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "call": "IncluirCliente",
    "app_key": "'$APP_KEY'",
    "app_secret": "'$APP_SECRET'",
    "param": [{
      "razao_social": "TESTE JSON CREDS",
      "cnpj_cpf": "11222333000155",
      "email": "teste@json.com",
      "cliente_fornecedor": "C"
    }]
  }' -v
