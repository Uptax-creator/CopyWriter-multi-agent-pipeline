# 🌐 Padrão Universal de Nomenclatura - Uptax Manager

## 📋 Objetivo

Criar um padrão universal de nomenclatura para ferramentas MCP que funcione consistentemente entre **todos os ERPs** (Omie, Nibo, SAP, Oracle, Dynamics, QuickBooks).

## 🎯 Princípios do Padrão

### **1. Estrutura Padronizada**
```
{action}_{entity}_{modifier}?
```

**Exemplos:**
- `get_customers_list`
- `create_invoice_item`
- `update_vendor_data`
- `delete_payment_record`

### **2. Ações Universais**
| **Ação** | **Descrição** | **Equivalentes** |
|----------|---------------|------------------|
| `get` | Consultar/Listar | consultar, listar, obter |
| `create` | Criar/Incluir | criar, incluir, adicionar |
| `update` | Atualizar/Alterar | atualizar, alterar, modificar |
| `delete` | Excluir/Remover | excluir, remover, deletar |
| `search` | Buscar/Pesquisar | buscar, pesquisar, filtrar |

### **3. Entidades Universais**
| **Entidade** | **Descrição** | **Omie** | **Nibo** | **SAP** | **Oracle** |
|-------------|---------------|----------|----------|---------|------------|
| `customers` | Clientes | clientes | clients | BP_CUSTOMER | CUSTOMER |
| `vendors` | Fornecedores | fornecedores | suppliers | BP_VENDOR | SUPPLIER |
| `invoices` | Faturas | faturas | invoices | INVOICE | INVOICE |
| `products` | Produtos | produtos | items | MATERIAL | ITEM |
| `accounts` | Contas | contas | accounts | GL_ACCOUNT | ACCOUNT |
| `payments` | Pagamentos | pagamentos | payments | PAYMENT | PAYMENT |
| `categories` | Categorias | categorias | categories | CATEGORY | CATEGORY |
| `departments` | Departamentos | departamentos | centros_custo | COST_CENTER | DEPARTMENT |
| `partners` | Sócios | - | socios | PARTNER | PARTNER |

### **4. Modificadores Opcionais**
| **Modificador** | **Descrição** | **Exemplo** |
|----------------|---------------|-------------|
| `_list` | Lista paginada | `get_customers_list` |
| `_by_id` | Por identificador | `get_customer_by_id` |
| `_by_document` | Por documento | `get_customer_by_document` |
| `_bulk` | Operação em lote | `create_customers_bulk` |
| `_detailed` | Com detalhes | `get_invoice_detailed` |

## 🔄 Mapeamento de Compatibilidade

### **Sistema de Aliases**
```json
{
  "universal_name": "get_customers_list",
  "aliases": {
    "omie": "consultar_clientes",
    "nibo": "consultar_clientes",
    "sap": "GET_CUSTOMER_LIST",
    "oracle": "list_customers",
    "dynamics": "GetCustomers",
    "quickbooks": "query_customers"
  }
}
```

### **Campos Padronizados**
```json
{
  "customer": {
    "id": "entity_id",
    "name": "entity_name",
    "document": "document_number",
    "email": "email_address",
    "phone": "phone_number",
    "address": "address_info",
    "created_at": "creation_date",
    "updated_at": "modification_date"
  }
}
```

## 📊 Implementação por Plataforma

### **Omie → Universal**
```python
# Atual
consultar_clientes(pagina=1, registros_por_pagina=50)

# Universal
get_customers_list(page=1, limit=50)
```

### **Nibo → Universal**
```python
# Atual
consultar_clientes(pagina=1, registros_por_pagina=50)

# Universal
get_customers_list(page=1, limit=50)
```

### **SAP → Universal**
```python
# Atual
GET_CUSTOMER_LIST(SKIP=0, TOP=50)

# Universal
get_customers_list(page=1, limit=50)
```

## 🎨 Exemplos Práticos

### **1. Consulta de Clientes**
```python
# Universal
get_customers_list(page=1, limit=50, active_only=True)

# Mapeia para:
# Omie: consultar_clientes(pagina=1, registros_por_pagina=50)
# Nibo: consultar_clientes(pagina=1, registros_por_pagina=50)
# SAP: GET_CUSTOMER_LIST(SKIP=0, TOP=50, ACTIVE='X')
```

### **2. Criação de Fornecedor**
```python
# Universal
create_vendor({
  "name": "Fornecedor Teste",
  "document": "12345678000195",
  "email": "contato@fornecedor.com"
})

# Mapeia para:
# Omie: incluir_fornecedor(razao_social="...", cnpj_cpf="...", email="...")
# Nibo: incluir_fornecedor(name="...", document="...", email="...")
# SAP: CREATE_VENDOR(NAME="...", TAX_ID="...", EMAIL="...")
```

### **3. Compatibilidade Departamentos**
```python
# Universal (com alias automático)
get_departments_list()

# Mapeia para:
# Omie: consultar_departamentos()
# Nibo: consultar_centros_custo()
# SAP: GET_COST_CENTERS()
```

## 🛠️ Ferramentas de Desenvolvimento

### **Gerador de Mapeamentos**
```python
def generate_mapping(universal_name: str, platforms: dict) -> dict:
    """Gera mapeamento automático entre plataformas"""
    return {
        "universal": universal_name,
        "mappings": platforms,
        "generated_at": datetime.now().isoformat()
    }
```

### **Validador de Compatibilidade**
```python
def validate_compatibility(tool_name: str, platforms: list) -> dict:
    """Valida compatibilidade entre plataformas"""
    results = {}
    for platform in platforms:
        results[platform] = check_tool_support(tool_name, platform)
    return results
```

## 🎯 Benefícios

### **1. Para Desenvolvedores**
- **Uma API** para todos os ERPs
- **Documentação unificada**
- **Manutenção simplificada**

### **2. Para Usuários**
- **Experiência consistente**
- **Migração facilitada** entre ERPs
- **Aprendizado único**

### **3. Para Empresas**
- **Redução de custos** de integração
- **Flexibilidade** de escolha de ERP
- **Futuro-proof** para novas plataformas

## 🚀 Roadmap de Implementação

### **Fase 1: Núcleo (Omie + Nibo)**
- [x] Mapeamento básico
- [x] Ferramentas universais
- [x] Sistema de aliases

### **Fase 2: Expansão (SAP + Oracle)**
- [ ] Conectores SAP
- [ ] Conectores Oracle
- [ ] Testes de integração

### **Fase 3: Completude (Dynamics + QuickBooks)**
- [ ] Conectores Dynamics
- [ ] Conectores QuickBooks
- [ ] Validação completa

### **Fase 4: Otimização**
- [ ] Performance tuning
- [ ] Cache distribuído
- [ ] Monitoramento

## 📝 Especificação Técnica

### **Formato de Resposta Universal**
```json
{
  "data": [...],
  "metadata": {
    "platform": "omie",
    "total_count": 100,
    "page": 1,
    "page_size": 50,
    "has_next": true
  },
  "compatibility": {
    "universal_name": "get_customers_list",
    "platform_name": "consultar_clientes",
    "mapped_fields": {...}
  }
}
```

### **Tratamento de Erros**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Campo obrigatório não informado",
    "platform": "omie",
    "universal_field": "document_number",
    "platform_field": "cnpj_cpf"
  }
}
```

---

**Este padrão posiciona Uptax Manager como pioneiro em padronização ERP, criando um novo padrão de mercado para integrações.**