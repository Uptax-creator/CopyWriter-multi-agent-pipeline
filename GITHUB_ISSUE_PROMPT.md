# 🚨 ISSUE: Correção Omie-MCP via Claude Code Action

**Status**: 🔴 CRÍTICO - Produção aguardando  
**Metodologia**: Nova abordagem Code Action (teste piloto)  
**Meta**: 0/8 → 8/8 ferramentas funcionais

---

## 📋 **SITUAÇÃO ATUAL**

### **Métricas de Funcionalidade**
- **Nibo-MCP**: ✅ 10/10 ferramentas (100% funcional)
- **Omie-MCP**: ❌ 0/8 ferramentas (0% funcional)  
- **Taxa Geral**: 60% (12/20) → Meta: 100% (20/20)

### **Desenvolvimento**
- **Tempo Investido**: 4 dias intensivos
- **Framework**: SDK + FastMCP  
- **Prazo Produção**: Esta semana
- **Abordagem**: Testando automação Code Action

---

## 🔍 **DIAGNÓSTICO TÉCNICO**

### **Problemas Identificados**
1. **Framework FastMCP**: Validação MCP protocol inconsistente
2. **STDIO Communication**: "Invalid request parameters" em tools/list
3. **Data Validation**: `pessoa_fisica: boolean` → deve ser `"S"/"N"`
4. **Mock Fallbacks**: Try/catch sempre retorna dados simulados
5. **API Integration**: Chamadas reais bloqueadas por fallbacks

### **Ferramentas Afetadas (0/8 funcionais)**
```
❌ incluir_cliente - CRUD essencial
❌ listar_clientes - Paginação crítica  
❌ consultar_categorias - Dados base
❌ consultar_contas_pagar - Financeiro (3 cenários)
❌ consultar_contas_receber - Financeiro  
```

### **Comparação com Funcional (Nibo-MCP)**
| Aspecto | Nibo-MCP (✅) | Omie-MCP (❌) |
|---------|---------------|---------------|
| **Framework** | MCP Padrão | FastMCP |
| **Protocolo** | STDIO OK | Invalid Params |
| **Validação** | String "S"/"N" | Boolean |
| **API Calls** | Diretas | Mock Fallback |

---

## 🎯 **PROMPT PARA CODE ACTION**

@claude fix omie-mcp

### **CONTEXTO DE PRODUÇÃO**
- **Urgência**: Sistema deve entrar em produção esta semana
- **Situação**: Nibo-MCP 100% funcional, Omie-MCP 0% funcional
- **Recursos**: 4 dias desenvolvimento, experiência acumulada
- **Metodologia**: Teste piloto Code Action vs correção manual

### **RECURSOS DISPONÍVEIS PARA ANÁLISE**
1. **📂 Arquivo Problema**: `omie_fastmcp_unified.py` 
   - Framework: FastMCP 2.10.6
   - Status: 0/8 ferramentas funcionais
   - Issue: Protocolo MCP + validação dados

2. **📂 Arquivo Referência**: `nibo-mcp/nibo_mcp_server_hybrid.py`
   - Framework: MCP Padrão  
   - Status: 10/10 ferramentas funcionais
   - Exemplo: Implementação correta

3. **🧪 Suite Validação**: `test_production_suite.py`
   - Testa 20 ferramentas (10 Nibo + 8 Omie)
   - Relatório detalhado por categoria
   - Métricas de performance

4. **📚 Biblioteca Tools**: `tools_documentation_library.py`
   - 21 ferramentas documentadas
   - Padrões de implementação
   - Cenários de teste

5. **🔑 Configuração**: `credentials.json`
   - Credenciais Omie configuradas
   - Base URL: https://app.omie.com.br/api/v1
   - Autenticação: app_key + app_secret

### **CORREÇÕES CRÍTICAS NECESSÁRIAS**

#### **1. Validação Campo pessoa_fisica**
```python
# ❌ ATUAL (CAUSA ERRO 500)  
"pessoa_fisica": len(cnpj_cpf.replace(...)) == 11

# ✅ CORREÇÃO NECESSÁRIA
"pessoa_fisica": "S" if len(cnpj_cpf.replace(...)) == 11 else "N"
```

#### **2. Protocolo MCP FastMCP**  
```python
# Problema: "Invalid request parameters" 
# Investigar: Por que FastMCP falha na validação?
# Comparar: Como Nibo-MCP inicializa vs Omie-MCP?
```

#### **3. Remoção Fallbacks Mock**
```python  
# Identificar padrões como:
try:
    result = await client._make_request(...)
except:
    # ❌ MOCK - impede teste real da API
    result = {"mock": "data"}

# ✅ CORRIGIR: Permitir erro para debug real
```

### **METODOLOGIA DE CORREÇÃO**

1. **COMPARE** estruturas Omie vs Nibo
   - Framework differences
   - Initialization patterns  
   - Error handling approaches

2. **EXECUTE** diagnóstico detalhado
   ```bash
   python test_production_suite.py
   ```

3. **IDENTIFIQUE** falhas específicas
   - MCP protocol validation
   - API parameter formatting
   - Authentication flow

4. **APLIQUE** correções incrementais
   - Fix pessoa_fisica validation
   - Remove unnecessary mock fallbacks
   - Align with Nibo-MCP patterns

5. **VALIDE** cada correção
   - Test individual tools
   - Monitor progress 0/8 → 8/8
   - Generate success metrics

### **CRITÉRIOS DE SUCESSO**
- ✅ **8/8 ferramentas Omie-MCP funcionais**  
- ✅ **Taxa geral: 100% (20/20)**
- ✅ **Tempo resposta: <1000ms** 
- ✅ **Relatório automático de validação**
- ✅ **Documentação das correções**

### **ENTREGÁVEIS ESPERADOS**
1. **Arquivo corrigido**: `omie_fastmcp_unified.py`
2. **Relatório detalhado**: Correções aplicadas
3. **Validação completa**: 8/8 tools funcionais  
4. **Comparação metodológica**: Code Action vs Manual
5. **Template**: Para futuros projetos MCP

---

## ⏱️ **CRONOGRAMA EXECUÇÃO**

| Fase | Tempo Esperado | Ação |
|------|----------------|------|
| **Diagnóstico** | 5-10 min | Análise automática problemas |
| **Correção** | 15-30 min | Aplicação fixes sistemática |  
| **Validação** | 5-10 min | Teste suite completa |
| **Relatório** | 2-5 min | Documentação automática |
| **TOTAL** | **~30-55 min** | **vs 4-8h manual** |

---

## 🚀 **EXECUÇÃO CODE ACTION**

**Trigger**: @claude fix omie-mcp  
**Workflow**: `.github/workflows/omie-mcp-fix.yml`  
**Monitoramento**: Actions tab no GitHub  
**Resultado**: Comment automático neste issue

---

**INICIE A CORREÇÃO SISTEMÁTICA AGORA!**
**Produção aguarda - metodologia Code Action em teste piloto** 🎯