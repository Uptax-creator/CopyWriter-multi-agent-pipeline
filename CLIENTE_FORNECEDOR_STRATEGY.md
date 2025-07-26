# 🏷️ ESTRATÉGIA CLIENTE vs FORNECEDOR NO OMIE

## 📋 Descoberta Importante

### Unificação de Cadastro
No Omie ERP, **cliente e fornecedor compartilham o mesmo cadastro base**. A diferenciação acontece através de **tags** aplicadas no momento do cadastro:

- **Tag "cliente"** → Para relacionamentos comerciais de venda
- **Tag "fornecedor"** → Para relacionamentos comerciais de compra  
- **Ambas as tags** → Uma mesma empresa pode ser cliente E fornecedor

## 🔧 Implementação Necessária

### 1. Modificação nas Tools de Cadastro

#### **cadastrar_cliente()** 
```python
# Adicionar automaticamente tag "cliente"
dados_cliente = {
    "nome": nome,
    "cnpj_cpf": cnpj_cpf,
    "tags": ["cliente"]  # ← TAG OBRIGATÓRIA
}
```

#### **cadastrar_fornecedor()** 
```python
# Adicionar automaticamente tag "fornecedor"  
dados_fornecedor = {
    "nome": nome,
    "cnpj_cpf": cnpj_cpf,
    "tags": ["fornecedor"]  # ← TAG OBRIGATÓRIA
}
```

#### **cadastrar_cliente_fornecedor()** 
```python
# Para empresas que são ambos
dados_hibrido = {
    "nome": nome,
    "cnpj_cpf": cnpj_cpf,
    "tags": ["cliente", "fornecedor"]  # ← AMBAS AS TAGS
}
```

### 2. Filtros Inteligentes nas Consultas

#### **listar_clientes()** - Filtrar por tag "cliente"
#### **listar_fornecedores()** - Filtrar por tag "fornecedor"  
#### **listar_clientes_fornecedores()** - Sem filtro de tag

## 🎯 Impacto nas Tools Existentes

### Tools a Modificar:
1. **listar_clientes** → Adicionar filtro por tag "cliente"
2. **listar_fornecedores** → Adicionar filtro por tag "fornecedor"
3. **cadastrar_cliente** → Adicionar tag automática

### Tools a Criar:
1. **cadastrar_fornecedor** → Nova tool com tag "fornecedor"
2. **cadastrar_cliente_fornecedor** → Tool híbrida
3. **converter_cliente_para_fornecedor** → Gestão de tags
4. **consultar_tags_entidade** → Verificar tags de uma entidade

## 📊 Benefícios da Estratégia

### ✅ Vantagens:
- **Consistência**: Evita duplicação de cadastros
- **Flexibilidade**: Mesma empresa pode ter múltiplos relacionamentos
- **Rastreabilidade**: Tags permitem histórico de relacionamento
- **Integridade**: Dados unificados, relacionamentos flexíveis

### ⚠️  Cuidados:
- **Validação**: Sempre verificar tags antes de operações
- **Filtros**: Consultas devem considerar tags apropriadas
- **Migração**: Dados existentes podem precisar de ajuste de tags

## 🔄 Fluxo de Implementação

1. **Fase 1**: Modificar tools existentes com tags
2. **Fase 2**: Criar tools específicas para fornecedores  
3. **Fase 3**: Implementar tools de gestão de tags
4. **Fase 4**: Validar e testar todos os cenários

Esta estratégia garante que o sistema seja **robusto, flexível e alinhado com a arquitetura do Omie ERP**.