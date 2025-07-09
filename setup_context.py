"""
Script para configurar contexto do projeto
"""
import os

# Credenciais
OMIE_APP_KEY = "suas_credenciais"
OMIE_APP_SECRET = "seu_secret"

# Estado atual do projeto
PROJECT_STATE = {
    "tools_working": ["listar_categorias", "listar_departamentos"],
    "tools_failing": ["criar_cliente"],
    "current_error": "500 Bad Request SOAP",
    "last_attempt": "ultra_clean_string sanitization"
}

# Salvar contexto
with open(".project_state.json", "w") as f:
    json.dump(PROJECT_STATE, f, indent=2)