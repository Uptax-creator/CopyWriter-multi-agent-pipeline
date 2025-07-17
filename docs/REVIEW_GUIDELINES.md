# 📋 Guia de Revisão e Políticas do Projeto

## 🎯 Políticas de Desenvolvimento para Omie MCP Server

Este documento define as políticas e diretrizes para desenvolvimento, revisão e manutenção do projeto Omie MCP Server.

## 📚 Índice

- [Políticas de Commit](#políticas-de-commit)
- [Processo de Revisão](#processo-de-revisão)
- [Estrutura de Branches](#estrutura-de-branches)
- [Testes Obrigatórios](#testes-obrigatórios)
- [Documentação](#documentação)
- [Versionamento](#versionamento)
- [Deploy e Release](#deploy-e-release)

## 🔄 Políticas de Commit

### Formato de Commit Messages

```
tipo(escopo): descrição breve

Descrição detalhada (opcional)

- Item específico 1
- Item específico 2

Co-authored-by: Nome <email> (se aplicável)
```

### Tipos de Commit

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Formatação, sem mudança de lógica
- **refactor**: Refatoração de código
- **test**: Adição ou correção de testes
- **chore**: Tarefas de manutenção

### Exemplos

```bash
feat(tools): adicionar ferramenta consultar_produtos
fix(client): corrigir timeout em requisições longas
docs(readme): atualizar instruções de instalação
test(tools): adicionar testes para ferramentas de cliente
refactor(server): reorganizar estrutura de handlers
```

## 🔍 Processo de Revisão

### Checklist Pré-Commit

**Antes de fazer qualquer commit, verificar:**

- [ ] **Código funciona** localmente
- [ ] **Testes passam** (`python scripts/test_all_tools.py`)
- [ ] **Servidor inicia** sem erros (`python scripts/service_manager.py start`)
- [ ] **Documentação atualizada** se necessário
- [ ] **Não há credenciais** expostas no código
- [ ] **Logs estruturados** implementados
- [ ] **Tratamento de erros** adequado

### Checklist Pós-Mudança

**Após implementar mudanças:**

1. **Executar testes completos:**
   ```bash
   python scripts/test_all_tools.py
   ```

2. **Verificar saúde do servidor:**
   ```bash
   python scripts/service_manager.py status
   ```

3. **Validar integração Claude Desktop:**
   ```bash
   python scripts/validate_all.py
   ```

4. **Atualizar documentação:**
   - README.md (se mudanças na API)
   - CHANGELOG.md
   - Documentação de ferramentas

## 🌳 Estrutura de Branches

### Branch Principal
- **`main`**: Código de produção, sempre estável

### Branches de Desenvolvimento
- **`develop`**: Integração de novas features
- **`feature/nome-da-feature`**: Desenvolvimento de funcionalidades
- **`hotfix/nome-do-fix`**: Correções urgentes
- **`release/vX.Y.Z`**: Preparação de releases

### Fluxo de Trabalho

```bash
# 1. Criar branch para feature
git checkout -b feature/nova-ferramenta

# 2. Desenvolver e testar
python scripts/test_all_tools.py

# 3. Commit com formato padrão
git commit -m "feat(tools): adicionar ferramenta nova_ferramenta"

# 4. Push e Pull Request
git push origin feature/nova-ferramenta

# 5. Merge após revisão
git checkout main
git merge feature/nova-ferramenta
```

## 🧪 Testes Obrigatórios

### Antes de Qualquer Commit

1. **Testes unitários básicos:**
   ```bash
   python tests/test_basic.py
   ```

2. **Testes de ferramentas:**
   ```bash
   python scripts/test_all_tools.py
   ```

3. **Validação completa:**
   ```bash
   python scripts/validate_all.py
   ```

### Cobertura Mínima

- **Ferramentas novas**: 100% testadas
- **Alterações existentes**: Testes não devem quebrar
- **Integração**: Claude Desktop deve funcionar

## 📖 Documentação

### Documentos Obrigatórios

- **README.md**: Visão geral e instruções
- **CHANGELOG.md**: Histórico de mudanças
- **API_MAPPING.md**: Mapeamento de endpoints
- **TOOLS.md**: Documentação de ferramentas

### Padrão de Documentação

```markdown
## Nome da Ferramenta

**Descrição**: Breve descrição da funcionalidade

**Parâmetros**:
- `parametro1` (string, obrigatório): Descrição
- `parametro2` (int, opcional): Descrição

**Exemplo de Uso**:
```json
{
  "name": "nome_ferramenta",
  "arguments": {
    "parametro1": "valor"
  }
}
```

**Resposta Esperada**:
```
✅ Operação realizada com sucesso!
Detalhes: ...
```
```

## 📦 Versionamento

### Versionamento Semântico (SemVer)

- **MAJOR.MINOR.PATCH** (ex: 2.1.3)
- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Funcionalidades backward-compatible
- **PATCH**: Correções backward-compatible

### Processo de Versionamento

1. **Atualizar versão** em:
   - `src/config.py`
   - `README.md`
   - `setup.py` (se existir)

2. **Criar tag de release:**
   ```bash
   git tag -a v2.1.0 -m "Release v2.1.0: Adicionar ferramentas de produtos"
   git push origin v2.1.0
   ```

3. **Atualizar CHANGELOG.md**

## 🚀 Deploy e Release

### Checklist de Release

**Antes do Release:**

- [ ] **Todos os testes passam**
- [ ] **Documentação atualizada**
- [ ] **CHANGELOG.md atualizado**
- [ ] **Versão bumped** em todos os arquivos
- [ ] **Backup criado** (`backup/YYYYMMDD/`)
- [ ] **Integração Claude testada**

**Durante o Release:**

1. **Criar branch de release:**
   ```bash
   git checkout -b release/v2.1.0
   ```

2. **Executar validação completa:**
   ```bash
   python scripts/validate_all.py
   ```

3. **Merge para main:**
   ```bash
   git checkout main
   git merge release/v2.1.0
   ```

4. **Tag e push:**
   ```bash
   git tag -a v2.1.0 -m "Release v2.1.0"
   git push origin main --tags
   ```

**Pós-Release:**

- [ ] **GitHub Release** criado
- [ ] **Documentação publicada**
- [ ] **Equipe notificada**
- [ ] **Monitoramento ativo**

## 📊 Monitoramento Pós-Deploy

### Métricas a Acompanhar

- **Uptime do servidor**
- **Tempo de resposta das ferramentas**
- **Taxa de erro das requisições**
- **Uso de recursos (CPU, memória)**

### Comandos de Monitoramento

```bash
# Status do serviço
python scripts/service_manager.py status

# Logs recentes
python scripts/service_manager.py logs

# Teste de saúde
python scripts/test_all_tools.py
```

## 🔒 Segurança

### Políticas de Segurança

- **Jamais commitar credenciais**
- **Usar variables de ambiente** para secrets
- **Validar todas as entradas** de usuário
- **Logs não devem expor** dados sensíveis
- **Tratamento adequado** de erros

### Revisão de Segurança

**Antes de cada release:**

- [ ] **Scan de credenciais** no código
- [ ] **Validação de inputs** implementada
- [ ] **Logs sanitizados**
- [ ] **Dependências atualizadas**

## 🚨 Troubleshooting

### Problemas Comuns

1. **Servidor não inicia**
   ```bash
   python scripts/service_manager.py stop
   python scripts/service_manager.py start
   ```

2. **Testes falhando**
   ```bash
   python scripts/test_all_tools.py
   # Verificar logs para detalhes
   ```

3. **Claude Desktop não conecta**
   ```bash
   python scripts/configure_claude.py
   ```

### Escalação

- **Bugs críticos**: Abrir issue no GitHub imediatamente
- **Problemas de performance**: Coletar logs e métricas
- **Falhas de integração**: Testar com `validate_all.py`

## 📞 Contatos e Responsabilidades

### Responsáveis

- **Maintainer Principal**: [Nome]
- **Reviewers**: [Lista de revisores]
- **Security Lead**: [Nome]

### Canais de Comunicação

- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Urgências**: [Canal de emergência]

---

**📌 Nota**: Este documento deve ser revisado e atualizado a cada release major.

**Última atualização**: 2025-07-15
**Versão do documento**: 1.0.0