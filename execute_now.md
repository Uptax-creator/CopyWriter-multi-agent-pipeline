# 🚀 Instruções de Execução - Omie MCP para Claude Code

## 📋 Passo a Passo

### 1. Salvar os arquivos de contexto

```bash
cd ~/omie-mcp

# Salvar PROJECT_CONTEXT.md
# (copie o conteúdo do artifact PROJECT_CONTEXT.md)

# Salvar TROUBLESHOOTING.md
# (copie o conteúdo do artifact TROUBLESHOOTING.md)

# Salvar setup_context.py
# (copie o conteúdo do artifact setup_context.py)

# Salvar .claude-context
# (copie o conteúdo do artifact .claude-context)

# Salvar prepare_for_claude_code.sh
# (copie o conteúdo do artifact prepare_for_claude_code.sh)
```

### 2. Executar a preparação

```bash
# Tornar executável e rodar
chmod +x prepare_for_claude_code.sh
./prepare_for_claude_code.sh

# OU executar o script Python
python setup_context.py
```

### 3. Instalar Claude Code (se necessário)

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar Claude Code
pip install claude-code

# Verificar instalação
claude-code --version
```

### 4. Iniciar Claude Code

```bash
# No diretório do projeto
cd ~/omie-mcp

# Iniciar Claude Code
claude-code
```

### 5. Primeira mensagem no Claude Code

Cole esta mensagem:

```
Estou trabalhando no projeto Omie MCP Server. 

CONTEXTO: Veja PROJECT_CONTEXT.md e TROUBLESHOOTING.md para histórico completo.

PROBLEMA ATUAL: Erro 500 Bad Request SOAP ao criar cliente no Omie.
- Endpoint: /geral/clientes/
- Call: IncluirCliente
- Resposta: XML/SOAP em vez de JSON

OBJETIVO: 
1. Modularizar o código seguindo a estrutura em PROJECT_CONTEXT.md
2. Resolver o erro 500 mantendo as ferramentas que já funcionam
3. Implementar testes para cada tool

Arquivos de referência estão em ./reference/
Estado atual em ./context/

Por favor, comece criando a estrutura modular do projeto.
```

## 🎯 Resultado Esperado

O Claude Code vai:
1. Criar a estrutura modular de arquivos
2. Separar cada tool em seu próprio módulo
3. Implementar logging detalhado
4. Criar testes individuais
5. Debugar e resolver o erro 500

## 💡 Dicas

- Os arquivos `omie_http_server.py` e `omie_server_json_fixed.py` têm o código atual
- As ferramentas de consulta (categorias, departamentos) estão funcionando
- O problema está específico na criação de cliente
- Já resolvemos o erro 422 JSON com sanitização

## 🔧 Teste Rápido

Enquanto o Claude Code trabalha, você pode testar a API diretamente:

```bash
# Configurar credenciais
export OMIE_APP_KEY="sua_key_real"
export OMIE_APP_SECRET="seu_secret_real"

# Testar
./context/test_api_direct.sh
```

---

**Boa sorte! O Claude Code vai ajudar muito a organizar e resolver o problema!** 🚀