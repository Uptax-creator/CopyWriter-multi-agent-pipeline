# 🚀 ROADMAP - Nibo MCP v2.0

## 📋 **Funcionalidades Planejadas**

### **🔴 PRIORIDADE ALTA**

#### **1. Implementar Operações DELETE no Omie-MCP**
**Problema:** Omie não possui funcionalidades de exclusão (DELETE)
**Solução:** Implementar exclusão via API do Omie para padronizar com Nibo

**Ferramentas a implementar:**
- ✅ `excluir_cliente` 
- ✅ `excluir_fornecedor`
- ✅ `excluir_conta_pagar` 
- ✅ `excluir_conta_receber`

**Impacto:** Paridade completa entre Omie-MCP e Nibo-MCP

---

#### **2. Gestão de Sócios no Nibo-MCP**
**Problema:** Nibo possui entidade "Sócios" que não existe no Omie
**Solução:** Implementar CRUD completo para Sócios

**Ferramentas a implementar:**
- 🆕 `consultar_socios` (GET /partners)
- 🆕 `incluir_socio` (POST /partners)
- 🆕 `alterar_socio` (PUT /partners/{id})
- 🆕 `excluir_socio` (DELETE /partners/{id})

**Benefit:** Funcionalidade exclusiva do Nibo aproveitada

---

#### **3. Padronização de Nomenclaturas**
**Problema:** Terminologias diferentes entre plataformas
**Solução:** Criar camada de abstração unificada

**Mapeamentos:**
```
Omie "Departamentos" → Nibo "Centros de Custo"
Omie "consultar_departamentos" → Nibo "consultar_centros_custo"
```

**Implementação:**
- Alias para compatibilidade backward
- Documentação de equivalências
- Helpers de conversão

---

### **🟡 PRIORIDADE MÉDIA**

#### **4. Funcionalidades Avançadas de Consulta**

**4.1 Filtros Avançados**
- 🆕 Filtro por intervalo de datas
- 🆕 Filtro por valores (min/max)
- 🆕 Filtro por status (ativo/inativo)
- 🆕 Busca full-text

**4.2 Ordenação e Paginação Inteligente**
- 🆕 Auto-detecção de campos ordenáveis
- 🆕 Paginação otimizada
- 🆕 Cache de consultas frequentes

**4.3 Agregações e Relatórios**
- 🆕 `obter_resumo_financeiro`
- 🆕 `calcular_totais_por_categoria`
- 🆕 `gerar_relatorio_vencimentos`

---

#### **5. Operações em Lote (Batch)**

**5.1 Criação em Lote**
- 🆕 `incluir_multiplos_clientes`
- 🆕 `incluir_multiplas_contas`

**5.2 Atualização em Lote**
- 🆕 `alterar_multiplos_registros`
- 🆕 `aplicar_desconto_em_lote`

**5.3 Exclusão em Lote**
- 🆕 `excluir_multiplos_registros`
- 🆕 `excluir_por_filtro`

---

### **🟢 PRIORIDADE BAIXA**

#### **6. Funcionalidades de Auditoria**
- 🆕 `consultar_historico_alteracoes`
- 🆕 `obter_log_acessos`
- 🆕 `gerar_relatorio_auditoria`

#### **7. Integrações Avançadas**
- 🆕 Webhooks para eventos
- 🆕 Sincronização automática
- 🆕 Export/Import de dados

#### **8. Performance e Cache**
- 🆕 Cache distribuído
- 🆕 Consultas assíncronas
- 🆕 Otimização de queries

---

## 📊 **Matriz de Funcionalidades**

### **CRUD Completo por Entidade**

| **Entidade** | **GET** | **POST** | **PUT** | **DELETE** | **Omie** | **Nibo** |
|--------------|---------|----------|---------|------------|----------|----------|
| **Clientes** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ |
| **Fornecedores** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ |
| **Contas Pagar** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ |
| **Contas Receber** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ |
| **Sócios** | ❌ | ❌ | ❌ | ❌ | ❌ | 🆕 |
| **Categorias** | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Centros Custo** | ✅ | ❌ | ❌ | ❌ | ✅* | ✅ |

*Omie: "Departamentos"

### **Funcionalidades Exclusivas**

| **Funcionalidade** | **Omie** | **Nibo** | **Status** |
|--------------------|----------|----------|------------|
| **Tipos de Documento** | ✅ | ❌ | Omie-only |
| **Gestão de Sócios** | ❌ | ✅ | Nibo-only |
| **Operações DELETE** | ❌ | ✅ | Implementar no Omie |
| **Multi-Empresa** | ❌ | ✅ | Nibo-advanced |

---

## 🎯 **Metas da v2.0**

### **Objetivo Principal**
**Alcançar 100% de paridade funcional entre Omie-MCP e Nibo-MCP**

### **KPIs de Sucesso**
- ✅ **30 ferramentas** totais (vs 20 atuais)
- ✅ **CRUD completo** para todas as entidades
- ✅ **Zero diferenças** de funcionalidade
- ✅ **Compatibilidade total** entre plataformas

### **Timeline Estimado**
- **Sprint 1** (2 semanas): DELETE operations no Omie
- **Sprint 2** (2 semanas): Gestão de Sócios no Nibo  
- **Sprint 3** (1 semana): Padronização e testes
- **Sprint 4** (1 semana): Documentação e release

---

## 🔧 **Implementação Técnica**

### **Padrão de Desenvolvimento**
```python
# Exemplo: Nova ferramenta de Sócios
class NiboSocios:
    async def consultar_socios(self, **params) -> Dict:
        """GET /partners"""
        
    async def incluir_socio(self, dados_socio: Dict) -> Dict:
        """POST /partners"""
        
    async def alterar_socio(self, socio_id: str, dados: Dict) -> Dict:
        """PUT /partners/{id}"""
        
    async def excluir_socio(self, socio_id: str) -> Dict:
        """DELETE /partners/{id}"""
```

### **Testes Automatizados**
- Unit tests para cada ferramenta
- Integration tests com APIs reais
- Performance tests para operações em lote
- Compatibility tests entre plataformas

---

## 📝 **Notas de Desenvolvimento**

### **Considerações Técnicas**
1. **Versionamento**: Manter compatibilidade com v1.0
2. **Configuração**: Flags de feature para ativar/desativar funcionalidades
3. **Documentação**: Atualizar docs automaticamente
4. **Monitoramento**: Métricas de uso das novas funcionalidades

### **Riscos e Mitigações**
1. **API Limits**: Implementar rate limiting
2. **Breaking Changes**: Versionamento semântico rigoroso
3. **Performance**: Cache inteligente para operações pesadas
4. **Security**: Validação extra para operações DELETE

---

*Última atualização: 2025-01-11*
*Versão atual: 1.0.0*
*Próxima versão: 2.0.0*