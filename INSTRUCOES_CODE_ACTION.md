# 🤖 INSTRUÇÕES PARA EXECUTAR CODE ACTION

## **PASSO 1: Configurar Secrets no GitHub**
1. Ir para: **Settings → Secrets and variables → Actions**
2. Adicionar: **ANTHROPIC_API_KEY** = sua_chave_claude_api

## **PASSO 2: Criar Issue**
1. **Título**: `🚨 Correção Omie-MCP via Code Action (Teste Piloto)`
2. **Descrição**: Copiar conteúdo de `GITHUB_ISSUE_PROMPT.md`

## **PASSO 3: Trigger Code Action**
**Comentar no Issue**:
```
@claude fix omie-mcp

Status: Omie-MCP 0/8 funcionais → Meta: 8/8 funcionais
Metodologia: Teste piloto Code Action vs Manual
Deadline: Produção esta semana

Arquivos para análise:
- omie_fastmcp_unified.py (problema)
- nibo-mcp/nibo_mcp_server_hybrid.py (referência funcional)
- test_production_suite.py (validação)

Problemas identificados:
1. FastMCP: "Invalid request parameters"
2. pessoa_fisica: boolean → "S"/"N" 
3. Mock fallbacks bloqueando API real

INICIAR CORREÇÃO SISTEMÁTICA AGORA!
```

## **CRONÔMETRO CODE ACTION**: ⏱️ 
- **Início**: [registrar quando comentar]
- **Progresso**: Acompanhar em Actions
- **Fim**: [registrar quando completar]
- **Total**: [calcular duração]