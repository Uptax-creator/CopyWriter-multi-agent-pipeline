# 🌐 Unified MCP Server - Omie + Nibo

## 📋 Visão Geral

Sistema unificado que integra **Omie-MCP** (20 ferramentas) e **Nibo-MCP** (31 ferramentas) em uma única interface MCP.

## 🎯 Características

### **🔧 Ferramentas Unificadas**
- **Total**: 51 ferramentas (20 Omie + 31 Nibo)
- **Nomenclatura**: Padronizada entre plataformas
- **Compatibilidade**: Aliases para termos diferentes
- **Funcionalidades**: CRUD completo para todas as entidades

### **🏗️ Arquitetura**
```
unified-mcp/
├── unified_mcp_server.py       # Servidor principal
├── src/
│   ├── adapters/              # Adaptadores de plataforma
│   │   ├── omie_adapter.py
│   │   └── nibo_adapter.py
│   ├── mappers/               # Mapeamento de dados
│   │   ├── universal_mapper.py
│   │   └── field_mapper.py
│   └── utils/                 # Utilitários
│       ├── compatibility.py
│       └── validator.py
└── config/
    └── tool_mapping.json      # Mapeamento de ferramentas
```

### **🎨 Funcionalidades Exclusivas**

#### **Omie-MCP**
- `consultar_tipos_documento` - Lista tipos de documento
- `consultar_departamentos` - Lista departamentos (terminologia Omie)

#### **Nibo-MCP**
- `consultar_socios` - Gestão de sócios (exclusivo)
- `incluir_multiplos_clientes` - Operações em lote
- `incluir_multiplos_fornecedores` - Operações em lote

### **🔄 Mapeamentos de Compatibilidade**

| **Conceito** | **Omie** | **Nibo** | **Universal** |
|-------------|----------|----------|---------------|
| Estrutura organizacional | departamentos | centros_custo | departments |
| Identificador | codigo_cliente | id | entity_id |
| Documento | cnpj_cpf | document | document_number |
| Data | DD/MM/AAAA | YYYY-MM-DD | ISO 8601 |

## 🚀 Vantagens

1. **Interface única** para ambas as plataformas
2. **Nomenclatura padronizada** entre ERPs
3. **Funcionalidades combinadas** (51 ferramentas)
4. **Compatibilidade total** com código existente
5. **Preparação** para futuras integrações

## 📊 Estatísticas

- **Ferramentas Omie**: 20
- **Ferramentas Nibo**: 31
- **Total Unificado**: 51
- **Aliases de Compatibilidade**: 12
- **Mapeamentos de Campo**: 25

## 🔧 Configuração

```json
{
  "mcpServers": {
    "unified-erp": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/unified-mcp/unified_mcp_server.py"],
      "env": {
        "OMIE_APP_KEY": "your_omie_key",
        "OMIE_APP_SECRET": "your_omie_secret",
        "NIBO_TOKEN": "your_nibo_token",
        "NIBO_COMPANY_ID": "your_nibo_company_id"
      }
    }
  }
}
```

---

*Desenvolvido para o projeto Uptax Manager*