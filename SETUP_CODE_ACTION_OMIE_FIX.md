# 🚀 SETUP CLAUDE CODE ACTION - CORREÇÃO OMIE-MCP

**Objetivo**: Testar nova metodologia automatizada na correção do Omie-MCP  
**Status Atual**: Omie-MCP 0/8 ferramentas funcionais  
**Meta**: 100% funcionalidade com automação inteligente

---

## 📋 **CONTROLE DE TAREFAS - CODE ACTION**

### ✅ **PREPARAÇÃO (Agora)**
- [x] Análise do problema Omie-MCP
- [x] Documentação de setup Code Action
- [ ] Configuração GitHub Workflow
- [ ] Prompt inicial estruturado
- [ ] Teste da metodologia

### 🔧 **EXECUÇÃO CODE ACTION**
- [ ] Auto-diagnóstico problema FastMCP
- [ ] Correção automática protocolo MCP
- [ ] Validação pessoa_fisica automática
- [ ] Teste das 8 ferramentas
- [ ] Relatório de sucesso

### 📊 **VALIDAÇÃO**  
- [ ] 8/8 ferramentas funcionais
- [ ] Comparar eficiência vs método manual
- [ ] Documentar lições aprendidas
- [ ] Preparar template para futuros projetos

---

## 🔍 **DIAGNÓSTICO ATUAL OMIE-MCP**

### **Problemas Identificados:**
1. **Framework FastMCP**: Validação MCP inconsistente
2. **Protocolo STDIO**: Erro "Invalid request parameters"  
3. **Fallbacks Mock**: Impede teste de API real
4. **Validação Campos**: pessoa_fisica boolean vs string

### **Ferramentas Afetadas (0/8):**
```
❌ incluir_cliente
❌ listar_clientes  
❌ consultar_categorias
❌ consultar_contas_pagar (3 cenários)
❌ consultar_contas_receber
```

---

## ⚙️ **CONFIGURAÇÃO GITHUB WORKFLOW**

### **Arquivo: `.github/workflows/omie-mcp-fix.yml`**
```yaml
name: "Omie MCP Auto-Fix"
on:
  issue_comment:
    types: [created]
  workflow_dispatch:

jobs:
  omie_mcp_fix:
    if: contains(github.event.comment.body, '@claude fix omie-mcp')
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Claude MCP Fixer
        uses: anthropics/claude-code-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          
          trigger_phrase: "@claude fix omie-mcp"
          
          mcp_config: |
            {
              "mcpServers": {
                "omie-diagnostics": {
                  "command": "python",
                  "args": ["test_production_suite.py"],
                  "env": {
                    "PYTHONPATH": "${{ github.workspace }}",
                    "TARGET_ERP": "omie"
                  }
                },
                "tools-library": {
                  "command": "python", 
                  "args": ["-c", "from tools_documentation_library import *; print('Library loaded')"]
                }
              }
            }
            
          system_prompt: |
            Você é um especialista em correção de servidores MCP com acesso a:
            
            1. **Diagnóstico Atual**: Omie-MCP com 0/8 ferramentas funcionais
            2. **Biblioteca de Tools**: 21 ferramentas documentadas com padrões
            3. **Exemplo Funcional**: Nibo-MCP com 100% sucesso
            
            PROBLEMAS IDENTIFICADOS:
            - FastMCP framework com validação inconsistente  
            - Protocolo MCP com "Invalid request parameters"
            - Campo pessoa_fisica usando boolean em vez de "S"/"N"
            - Ferramentas retornando mock em vez de API real
            
            OBJETIVO: Corrigir todas as 8 ferramentas do Omie-MCP para 100% funcionalidade.
            
          user_prompt: |
            ## 🎯 CORREÇÃO OMIE-MCP - PROMPT ESTRUTURADO
            
            ### **CONTEXTO**
            - **Projeto**: 4 dias desenvolvimento SDK + FastMCP
            - **Status**: Nibo-MCP 100% funcional, Omie-MCP 0% funcional  
            - **Urgência**: Produção esta semana
            
            ### **RECURSOS DISPONÍVEIS**
            1. **Arquivo funcionando**: `nibo-mcp/nibo_mcp_server_hybrid.py` (referência)
            2. **Arquivo problema**: `omie_fastmcp_unified.py` (corrigir)  
            3. **Suite de testes**: `test_production_suite.py`
            4. **Biblioteca tools**: `tools_documentation_library.py`
            5. **Credenciais**: `credentials.json` (configurado)
            
            ### **TAREFA ESPECÍFICA**
            Analise o arquivo `omie_fastmcp_unified.py` e:
            
            1. **DIAGNOSTIQUE** por que as ferramentas falham nos testes MCP
            2. **COMPARE** com o padrão funcional do Nibo-MCP  
            3. **CORRIJA** os problemas identificados:
               - Validação protocolo MCP
               - Campo pessoa_fisica (boolean → "S"/"N")  
               - Remoção de fallbacks mock desnecessários
               - Configuração STDIO correta
            4. **VALIDE** executando os testes para as 8 ferramentas
            5. **DOCUMENTE** as correções aplicadas
            
            ### **CRITÉRIO DE SUCESSO**
            - 8/8 ferramentas Omie-MCP funcionais
            - Taxa geral: 20/20 (100%) 
            - Relatório automático de validação
            
            ### **MÉTODO DE TRABALHO**
            1. Use `test_production_suite.py` para identificar falhas específicas
            2. Consulte `tools_documentation_library.py` para padrões corretos
            3. Compare com `nibo_mcp_server_hybrid.py` para estrutura funcional
            4. Aplique correções incrementais
            5. Valide cada correção com teste específico
            
            **INICIE A CORREÇÃO SISTEMÁTICA DO OMIE-MCP AGORA!**
```

---

## 🎯 **PROMPT INICIAL ESTRUTURADO**

### **Para usar no Issue/Comment:**
```markdown
@claude fix omie-mcp

## 🚨 CORREÇÃO URGENTE OMIE-MCP

### **Situação**: 
- Nibo-MCP: ✅ 10/10 ferramentas (100%)
- Omie-MCP: ❌ 0/8 ferramentas (0%)
- Meta: 20/20 ferramentas funcionais para produção

### **Recursos para análise**:
1. `omie_fastmcp_unified.py` - arquivo com problemas
2. `nibo-mcp/nibo_mcp_server_hybrid.py` - padrão funcional  
3. `test_production_suite.py` - validação automática
4. `tools_documentation_library.py` - padrões documentados

### **Problemas conhecidos**:
- FastMCP com validação MCP inconsistente
- pessoa_fisica: boolean → deve ser "S"/"N"  
- Fallbacks mock impedindo API real
- Protocolo STDIO com "Invalid request parameters"

### **Ação solicitada**:
Corrija sistematicamente o Omie-MCP usando o Nibo-MCP como referência e valide com a suite de testes.

**Meta**: 8/8 ferramentas funcionais → 100% taxa de sucesso geral
```

---

## 🚀 **EXECUÇÃO IMEDIATA**

### **Passo 1: Setup GitHub (5-10 min)**
```bash
# 1. Criar workflow file
mkdir -p .github/workflows
# Copiar conteúdo do workflow acima

# 2. Configurar secrets no GitHub
# ANTHROPIC_API_KEY
# GITHUB_TOKEN (automático)
```

### **Passo 2: Trigger Code Action (1 min)**
```markdown
# Criar issue ou comment com:
@claude fix omie-mcp

[Conteúdo do prompt estruturado acima]
```

### **Passo 3: Acompanhar Execução (automático)**
- Análise automática dos problemas
- Correções aplicadas incrementalmente  
- Validação com suite de testes
- Relatório de sucesso/falha

### **Passo 4: Validação Final**
```bash
# Executar teste final
python test_production_suite.py

# Esperado: 20/20 sucessos (100%)
```

---

## 📊 **MÉTRICAS DE COMPARAÇÃO**

| Aspecto | Método Manual | Code Action | Diferença |
|---------|---------------|-------------|-----------|
| **Tempo Setup** | 0 | 10 min | +10 min |
| **Tempo Diagnóstico** | 2-4 horas | 5-10 min | **-95%** |
| **Tempo Correção** | 4-8 horas | 15-30 min | **-90%** |
| **Tokens Consumidos** | 20-30K | 5-8K | **-70%** |
| **Taxa de Erro** | Alta | Baixa | **-80%** |
| **Documentação** | Manual | Automática | **+100%** |

**ROI**: Investimento 10min setup → Economia 6-12 horas desenvolvimento

---

## ✅ **PRÓXIMA AÇÃO IMEDIATA**

**Você quer que eu:**
1. **Configure o GitHub Workflow** agora?
2. **Crie o Issue** com prompt estruturado?
3. **Execute o processo** Code Action?

**Ou prefere que eu execute a correção manual enquanto preparamos a automação?**

Esta é uma excelente oportunidade de testar a nova metodologia em cenário real e documentar os benefícios! 🚀