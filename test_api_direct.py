#!/usr/bin/env python3
import os
import json
import httpx
from dotenv import load_dotenv

# Tenta carregar do .env
load_dotenv()

APP_KEY = os.getenv("OMIE_APP_KEY")
APP_SECRET = os.getenv("OMIE_APP_SECRET")

# Se não encontrou, tenta pegar do credentials.json
if not APP_KEY or not APP_SECRET:
    cred_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    if os.path.exists(cred_path):
        with open(cred_path) as f:
            creds = json.load(f)
            APP_KEY = creds.get("app_key")
            APP_SECRET = creds.get("app_secret")

if not APP_KEY or not APP_SECRET:
    print("❌ Configure OMIE_APP_KEY e OMIE_APP_SECRET no arquivo .env ou credentials.json")
    exit(1)

print(f"🔑 Usando credenciais carregadas!")
print(f"🔑 App Key: {APP_KEY[:8]}...****")

# Dados de teste
payload = {
    "call": "IncluirCliente",
    "app_key": APP_KEY,
    "app_secret": APP_SECRET,
    "param": [{
        "razao_social": "TESTE PYTHON DIRETO",
        "cnpj_cpf": "11222333000155",
        "email": "teste@python.com",
        "cliente_fornecedor": "C",
        "inativo": "N"
    }]
}

print("📡 Enviando requisição...")
print(json.dumps(payload["param"][0], indent=2))

# Fazer requisição
response = httpx.post(
    "https://app.omie.com.br/api/v1/geral/clientes/",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=30.0
)

print(f"\n📊 Status: {response.status_code}")
print(f"📄 Resposta: {response.text[:500]}")

# Salvar resposta completa
with open("test_response.json", "w") as f:
    f.write(response.text)
    print(f"\n💾 Resposta completa salva em test_response.json")
