# 🏗️ Plano de Arquitetura Independente - MCP Servers

## 📋 Estratégia de Implementação

Baseado na análise comparativa, implementaremos o **modelo independente com biblioteca comum** para otimizar flexibilidade, manutenibilidade e custos.

## 🎯 Estrutura Proposta

```
erp-mcp-ecosystem/
├── common/                     # Biblioteca comum (compartilhada)
│   ├── __init__.py
│   ├── auth/                   # Autenticação padronizada
│   │   ├── __init__.py
│   │   ├── base_auth.py        # Classe base de autenticação
│   │   ├── token_manager.py    # Gerenciamento de tokens
│   │   └── credential_store.py # Armazenamento seguro
│   ├── tools/                  # Ferramentas base
│   │   ├── __init__.py
│   │   ├── base_tool.py        # Classe base para ferramentas
│   │   ├── validators.py       # Validações comuns
│   │   └── formatters.py       # Formatação de dados
│   ├── naming/                 # Nomenclatura universal
│   │   ├── __init__.py
│   │   ├── universal_names.py  # Mapeamento de nomes
│   │   ├── field_mappings.py   # Mapeamento de campos
│   │   └── aliases.py          # Sistema de aliases
│   ├── utils/                  # Utilitários comuns
│   │   ├── __init__.py
│   │   ├── http_client.py      # Cliente HTTP padrão
│   │   ├── date_utils.py       # Utilitários de data
│   │   ├── document_utils.py   # Validação CPF/CNPJ
│   │   └── currency_utils.py   # Utilitários monetários
│   ├── mcp/                    # Base MCP
│   │   ├── __init__.py
│   │   ├── base_server.py      # Servidor MCP base
│   │   ├── protocol.py         # Protocolo JSON-RPC
│   │   └── error_handler.py    # Tratamento de erros
│   └── config/                 # Configurações
│       ├── __init__.py
│       ├── base_config.py      # Configuração base
│       └── logging_config.py   # Configuração de logs
├── omie-mcp/                   # Servidor independente Omie
│   ├── __init__.py
│   ├── server.py               # Servidor MCP específico
│   ├── client/                 # Cliente Omie
│   │   ├── __init__.py
│   │   ├── omie_client.py      # Cliente HTTP Omie
│   │   └── endpoints.py        # Endpoints da API
│   ├── tools/                  # Ferramentas específicas
│   │   ├── __init__.py
│   │   ├── clientes.py         # Ferramentas de clientes
│   │   ├── fornecedores.py     # Ferramentas de fornecedores
│   │   ├── categorias.py       # Ferramentas de categorias
│   │   ├── contas.py           # Ferramentas de contas
│   │   └── departamentos.py    # Ferramentas de departamentos
│   ├── config/                 # Configuração específica
│   │   ├── __init__.py
│   │   └── omie_config.py      # Config Omie
│   └── requirements.txt        # Dependências específicas
├── nibo-mcp/                   # Servidor independente Nibo
│   ├── __init__.py
│   ├── server.py               # Servidor MCP específico
│   ├── client/                 # Cliente Nibo
│   │   ├── __init__.py
│   │   ├── nibo_client.py      # Cliente HTTP Nibo
│   │   └── endpoints.py        # Endpoints da API
│   ├── tools/                  # Ferramentas específicas
│   │   ├── __init__.py
│   │   ├── clientes.py         # Ferramentas de clientes
│   │   ├── fornecedores.py     # Ferramentas de fornecedores
│   │   ├── categorias.py       # Ferramentas de categorias
│   │   ├── contas.py           # Ferramentas de contas
│   │   ├── centros_custo.py    # Ferramentas de centros custo
│   │   └── socios.py           # Ferramentas de sócios
│   ├── config/                 # Configuração específica
│   │   ├── __init__.py
│   │   └── nibo_config.py      # Config Nibo
│   └── requirements.txt        # Dependências específicas
├── sap-mcp/                    # Servidor independente SAP
│   ├── __init__.py
│   ├── server.py               # Servidor MCP específico
│   ├── client/                 # Cliente SAP
│   │   ├── __init__.py
│   │   ├── sap_client.py       # Cliente SAP
│   │   └── endpoints.py        # Endpoints SAP
│   ├── tools/                  # Ferramentas específicas
│   │   ├── __init__.py
│   │   ├── customers.py        # Ferramentas de clientes
│   │   ├── vendors.py          # Ferramentas de fornecedores
│   │   ├── materials.py        # Ferramentas de materiais
│   │   └── accounts.py         # Ferramentas de contas
│   ├── config/                 # Configuração específica
│   │   ├── __init__.py
│   │   └── sap_config.py       # Config SAP
│   └── requirements.txt        # Dependências específicas
├── scripts/                    # Scripts de automação
│   ├── create_erp_server.py    # Gerador de novos servidores
│   ├── validate_naming.py      # Validador de nomenclatura
│   ├── test_all_servers.py     # Testes integrados
│   └── deploy.py               # Script de deploy
├── tests/                      # Testes integrados
│   ├── __init__.py
│   ├── test_common/            # Testes biblioteca comum
│   ├── test_omie/              # Testes específicos Omie
│   ├── test_nibo/              # Testes específicos Nibo
│   └── test_integration/       # Testes de integração
├── docs/                       # Documentação
│   ├── ARCHITECTURE.md         # Arquitetura geral
│   ├── NAMING_STANDARD.md      # Padrão de nomenclatura
│   ├── DEVELOPMENT_GUIDE.md    # Guia de desenvolvimento
│   └── DEPLOYMENT_GUIDE.md     # Guia de deploy
├── config/                     # Configurações globais
│   ├── naming_mappings.json    # Mapeamentos de nomenclatura
│   └── erp_definitions.json    # Definições de ERPs
└── requirements.txt            # Dependências comuns
```

## 🔧 Implementação da Biblioteca Comum

### 1. Autenticação Padronizada

```python
# common/auth/base_auth.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAuth(ABC):
    """Classe base para autenticação em ERPs"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.token = None
        self.expires_at = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Autentica com o ERP"""
        pass
    
    @abstractmethod
    async def refresh_token(self) -> bool:
        """Renova token de autenticação"""
        pass
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        pass
```

### 2. Servidor MCP Base

```python
# common/mcp/base_server.py
import asyncio
import json
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseMCPServer(ABC):
    """Classe base para servidores MCP"""
    
    def __init__(self, server_name: str, version: str):
        self.server_name = server_name
        self.version = version
        self.logger = logging.getLogger(server_name)
        self.tools = self.get_tools()
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna lista de ferramentas disponíveis"""
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executa ferramenta específica"""
        pass
    
    def send_response(self, response: Dict[str, Any]) -> None:
        """Envia resposta MCP via stdout"""
        response_json = json.dumps(response, ensure_ascii=False)
        print(response_json, flush=True)
```

### 3. Nomenclatura Universal

```python
# common/naming/universal_names.py
from typing import Dict, Any, Optional

class UniversalNaming:
    """Gerenciador de nomenclatura universal"""
    
    def __init__(self, mappings_file: str = None):
        self.mappings = self.load_mappings(mappings_file)
    
    def get_universal_name(self, platform: str, native_name: str) -> str:
        """Converte nome nativo para universal"""
        platform_mappings = self.mappings.get(platform, {})
        return platform_mappings.get(native_name, native_name)
    
    def get_native_name(self, platform: str, universal_name: str) -> str:
        """Converte nome universal para nativo"""
        reverse_mappings = self.get_reverse_mappings(platform)
        return reverse_mappings.get(universal_name, universal_name)
    
    def map_parameters(self, platform: str, universal_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia parâmetros universais para formato nativo"""
        mapped_params = {}
        for key, value in universal_params.items():
            native_key = self.get_native_name(platform, key)
            mapped_params[native_key] = value
        return mapped_params
```

## 🚀 Migração Passo a Passo

### **Fase 1: Preparação da Biblioteca Comum**

1. **Criar estrutura base**
   ```bash
   mkdir -p erp-mcp-ecosystem/common/{auth,tools,naming,utils,mcp,config}
   ```

2. **Implementar classes base**
   - BaseAuth para autenticação
   - BaseMCPServer para servidores
   - UniversalNaming para nomenclatura
   - BaseConfig para configuração

3. **Migrar utilitários comuns**
   - Validadores de documento
   - Formatadores de data
   - Cliente HTTP base

### **Fase 2: Migração do Omie-MCP**

1. **Criar servidor independente**
   ```bash
   mkdir -p erp-mcp-ecosystem/omie-mcp/{client,tools,config}
   ```

2. **Migrar ferramentas existentes**
   - Adaptar para usar biblioteca comum
   - Implementar nomenclatura universal
   - Configurar autenticação padrão

3. **Testes de compatibilidade**
   - Validar funcionamento com Claude Desktop
   - Verificar todas as 20 ferramentas
   - Testar autenticação e rate limiting

### **Fase 3: Migração do Nibo-MCP**

1. **Criar servidor independente**
   ```bash
   mkdir -p erp-mcp-ecosystem/nibo-mcp/{client,tools,config}
   ```

2. **Migrar ferramentas existentes**
   - Adaptar para usar biblioteca comum
   - Implementar nomenclatura universal
   - Configurar autenticação padrão

3. **Preservar funcionalidades exclusivas**
   - Ferramentas de sócios
   - Operações em lote
   - Funcionalidades específicas do Nibo

### **Fase 4: Preparação para Novos ERPs**

1. **Criar templates**
   - Template de servidor MCP
   - Template de cliente ERP
   - Template de ferramentas

2. **Documentação**
   - Guia de desenvolvimento
   - Padrões de nomenclatura
   - Exemplos de implementação

## 📊 Benefícios da Nova Arquitetura

### **1. Flexibilidade**
- ✅ Clientes ativam apenas ERPs necessários
- ✅ Escalabilidade independente por ERP
- ✅ Falhas isoladas não afetam outros ERPs

### **2. Manutenibilidade**
- ✅ Código simples e focado por ERP
- ✅ Biblioteca comum reduz duplicação
- ✅ Testes isolados e específicos

### **3. Desenvolvimento**
- ✅ Equipes podem especializar por ERP
- ✅ Novos ERPs seguem padrão estabelecido
- ✅ Nomenclatura universal facilita integração

### **4. Operacional**
- ✅ Deploy independente por ERP
- ✅ Monitoramento específico
- ✅ Logs isolados por plataforma

## 🎯 Resultados Esperados

1. **Redução de Complexidade**: Cada servidor é simples e focado
2. **Maior Confiabilidade**: Falhas isoladas não propagam
3. **Facilidade de Manutenção**: Mudanças não afetam outros ERPs
4. **Escalabilidade**: Recursos alocados por demanda
5. **Experiência do Cliente**: Ativação seletiva por ERP

## 📋 Próximos Passos

1. **Implementar biblioteca comum**
2. **Migrar Omie-MCP para nova estrutura**
3. **Migrar Nibo-MCP para nova estrutura**
4. **Criar templates para novos ERPs**
5. **Documentar padrões e processos**

---

**Esta arquitetura posiciona o Uptax Manager como líder em padronização de integração ERP, oferecendo flexibilidade máxima para clientes e simplicidade máxima para desenvolvedores.**