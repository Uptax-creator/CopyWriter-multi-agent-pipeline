# 📚 Documentação - Omie MCP Ecosystem

## 🎯 Visão Geral

Esta documentação cobre todo o ecossistema de servidores MCP para integração com ERPs, incluindo arquitetura, padrões de nomenclatura, políticas de governança e guias de implementação.

## 📁 Estrutura da Documentação

### 🏗️ Arquitetura
- **[Comparação de Arquiteturas](ARCHITECTURE_COMPARISON.md)** - Análise detalhada dos modelos unificado vs independente
- **[Plano de Arquitetura Independente](INDEPENDENT_ARCHITECTURE_PLAN.md)** - Estratégia de implementação do modelo distribuído
- **[Políticas de Governança Distribuída](DISTRIBUTED_GOVERNANCE_POLICIES.md)** - Políticas de segurança, deploy e monitoramento

### 🔧 Desenvolvimento
- **[Diretrizes de Revisão](REVIEW_GUIDELINES.md)** - Padrões para revisão de código e documentação
- **[Estrutura GitHub](GITHUB_STRUCTURE_PROPOSAL.md)** - Proposta de organização do repositório GitHub

### 🌐 Padrões de Nomenclatura
- **[Padrão Universal de Nomenclatura](UNIVERSAL_NAMING_STANDARD.md)** - Especificação completa do sistema de nomenclatura
- **[Estratégia de Nomenclatura ERP](ERP_UNIVERSAL_NAMING_STRATEGY.md)** - Estratégia de implementação entre ERPs

### 🔗 Integração
- **[Mapeamento de APIs](API_MAPPING.md)** - Mapeamento entre diferentes APIs de ERP
- **[Documentação de Ferramentas](TOOLS.md)** - Documentação completa das ferramentas disponíveis

## 🚀 Guias de Início Rápido

### Para Desenvolvedores
1. Leia a [Comparação de Arquiteturas](ARCHITECTURE_COMPARISON.md) para entender o modelo
2. Consulte o [Plano de Arquitetura Independente](INDEPENDENT_ARCHITECTURE_PLAN.md) para implementação
3. Siga as [Diretrizes de Revisão](REVIEW_GUIDELINES.md) para padrões de código

### Para Integradores
1. Consulte o [Padrão Universal de Nomenclatura](UNIVERSAL_NAMING_STANDARD.md)
2. Veja o [Mapeamento de APIs](API_MAPPING.md) para seu ERP específico
3. Use a [Documentação de Ferramentas](TOOLS.md) como referência

### Para Administradores
1. Revise as [Políticas de Governança Distribuída](DISTRIBUTED_GOVERNANCE_POLICIES.md)
2. Configure seguindo a [Estrutura GitHub](GITHUB_STRUCTURE_PROPOSAL.md)
3. Implemente os processos de segurança e monitoramento

## 📊 Status da Documentação

| Documento | Status | Última Atualização |
|-----------|--------|-------------------|
| ARCHITECTURE_COMPARISON.md | ✅ Completo | 2024-07-15 |
| INDEPENDENT_ARCHITECTURE_PLAN.md | ✅ Completo | 2024-07-15 |
| DISTRIBUTED_GOVERNANCE_POLICIES.md | ✅ Completo | 2024-07-15 |
| UNIVERSAL_NAMING_STANDARD.md | ✅ Completo | 2024-07-15 |
| GITHUB_STRUCTURE_PROPOSAL.md | ✅ Completo | 2024-07-15 |
| REVIEW_GUIDELINES.md | ✅ Completo | 2024-07-15 |
| API_MAPPING.md | ✅ Completo | 2024-07-09 |
| TOOLS.md | ✅ Completo | 2024-07-09 |

## 🔍 Buscar na Documentação

### Por Categoria
- **Arquitetura**: Comparação, Plano Independente, Governança
- **Desenvolvimento**: Diretrizes, GitHub, Ferramentas
- **Integração**: Nomenclatura, APIs, Mapeamento
- **Operação**: Políticas, Segurança, Deploy

### Por ERP
- **Omie**: Todas as seções aplicáveis
- **Nibo**: Todas as seções aplicáveis
- **SAP**: Nomenclatura, Arquitetura, Governança
- **Oracle**: Nomenclatura, Arquitetura, Governança
- **Dynamics**: Nomenclatura, Arquitetura, Governança
- **QuickBooks**: Nomenclatura, Arquitetura, Governança

## 📝 Contribuindo com a Documentação

### Padrões de Escrita
- Use emojis para melhor visualização
- Organize com títulos claros
- Inclua exemplos práticos
- Mantenha linguagem técnica mas acessível

### Processo de Atualização
1. Crie branch para mudanças
2. Siga as diretrizes de revisão
3. Submeta pull request
4. Aguarde revisão e aprovação

### Templates Disponíveis
- Template de análise técnica
- Template de guia de implementação
- Template de documentação de API
- Template de política de segurança

## 🔗 Links Úteis

### Repositórios
- [Omie MCP Server](../omie-mcp/)
- [Nibo MCP Server](../nibo-mcp/)
- [Biblioteca Comum](../common/)

### Ferramentas
- [Validador de Nomenclatura](../scripts/validate_naming.py)
- [Gerador de Documentação](../scripts/generate_docs.py)
- [Testes de Integração](../scripts/test_integration.py)

### Recursos Externos
- [Documentação MCP](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [FastAPI](https://fastapi.tiangolo.com/)

## ❓ Suporte

### Para Dúvidas sobre Documentação
- Crie uma [issue](https://github.com/kleberdossantosribeiro/omie-mcp/issues) com label `documentation`
- Envie email para: docs@uptax.com

### Para Contribuições
- Leia o [guia de contribuição](../CONTRIBUTING.md)
- Participe das [discussões](https://github.com/kleberdossantosribeiro/omie-mcp/discussions)

### Para Problemas Técnicos
- Consulte o [guia de troubleshooting](../TROUBLESHOOTING.md)
- Abra uma [issue](https://github.com/kleberdossantosribeiro/omie-mcp/issues) com label `bug`

---

**Esta documentação é mantida pela comunidade e atualizada continuamente para refletir as melhores práticas do ecossistema MCP.**