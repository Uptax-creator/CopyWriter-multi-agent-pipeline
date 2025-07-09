# 🔗 Mapeamento da API Omie

Este documento documenta o mapeamento entre as ferramentas MCP e os endpoints da API Omie.

## 📋 Índice

- [Endpoints de Consulta](#endpoints-de-consulta)
- [Endpoints de CRUD](#endpoints-de-crud)
- [Estruturas de Dados](#estruturas-de-dados)
- [Campos Obrigatórios](#campos-obrigatórios)
- [Troubleshooting](#troubleshooting)

## 🔍 Endpoints de Consulta

### Categorias

**Ferramenta MCP**: `consultar_categorias`  
**Endpoint Omie**: `/geral/categorias/`  
**Método**: `ListarCategorias`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_codigo": "opcional",
  "filtrar_por_descricao": "opcional"
}
```

**Resposta**:
```json
{
  "categoria_cadastro": [
    {
      "codigo": "1.01",
      "descricao": "Receita de Vendas",
      "codigo_pai": "1"
    }
  ],
  "total_de_registros": 100,
  "total_de_paginas": 5
}
```

### Departamentos

**Ferramenta MCP**: `consultar_departamentos`  
**Endpoint Omie**: `/geral/departamentos/`  
**Método**: `ListarDepartamentos`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_codigo": "opcional",
  "filtrar_por_descricao": "opcional"
}
```

**Resposta**:
```json
{
  "departamentos": [
    {
      "codigo": "001",
      "descricao": "Administrativo",
      "inativo": "N"
    }
  ],
  "total_de_registros": 50,
  "total_de_paginas": 2
}
```

### Tipos de Documento

**Ferramenta MCP**: `consultar_tipos_documento`  
**Endpoint Omie**: `/geral/tpdoc/`  
**Método**: `PesquisarTipoDocumento`

**Parâmetros**:
```json
{
  "filtrar_por_codigo": "opcional",
  "filtrar_por_descricao": "opcional"
}
```

**Resposta**:
```json
{
  "tipos_documento_cadastro": [
    {
      "codigo": "99999",
      "descricao": "Outros",
      "tipo": "P"
    }
  ]
}
```

### Clientes

**Ferramenta MCP**: `consultar_clientes`  
**Endpoint Omie**: `/geral/clientes/`  
**Método**: `ListarClientes`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_nome": "opcional",
  "cnpj_cpf": "opcional",
  "codigo_cliente_omie": "opcional"
}
```

**Resposta**:
```json
{
  "clientes_cadastro": [
    {
      "codigo_cliente_omie": "12345678",
      "codigo_cliente_integracao": "CLI_001",
      "cnpj_cpf": "12.345.678/0001-90",
      "razao_social": "Cliente Teste Ltda",
      "nome_fantasia": "Teste",
      "email": "contato@teste.com",
      "telefone1_numero": "(11) 99999-9999"
    }
  ],
  "total_de_registros": 200,
  "total_de_paginas": 10
}
```

### Fornecedores

**Ferramenta MCP**: `consultar_fornecedores`  
**Endpoint Omie**: `/geral/fornecedores/`  
**Método**: `ListarFornecedores`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_nome": "opcional",
  "cnpj_cpf": "opcional",
  "codigo_fornecedor_omie": "opcional"
}
```

**Resposta**:
```json
{
  "fornecedor_cadastro": [
    {
      "codigo_fornecedor_omie": "87654321",
      "codigo_fornecedor_integracao": "FOR_001",
      "cnpj_cpf": "98.765.432/0001-10",
      "razao_social": "Fornecedor ABC S.A.",
      "nome_fantasia": "ABC",
      "email": "vendas@abc.com",
      "telefone1_numero": "(11) 88888-8888"
    }
  ],
  "total_de_registros": 150,
  "total_de_paginas": 8
}
```

### Contas a Pagar

**Ferramenta MCP**: `consultar_contas_pagar`  
**Endpoint Omie**: `/financas/contapagar/`  
**Método**: `ListarContasPagar`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_codigo_lancamento": "opcional",
  "filtrar_por_fornecedor": "opcional",
  "filtrar_por_data_inicial": "opcional",
  "filtrar_por_data_final": "opcional"
}
```

**Resposta**:
```json
{
  "conta_pagar_cadastro": [
    {
      "codigo_lancamento_omie": "123456789",
      "codigo_lancamento_integracao": "CP_001",
      "codigo_fornecedor_omie": "87654321",
      "data_vencimento": "31/12/2024",
      "valor_documento": 1500.00,
      "codigo_categoria": "1.01",
      "observacao": "Pagamento fornecedor",
      "numero_documento": "NF-001"
    }
  ],
  "total_de_registros": 300,
  "total_de_paginas": 15
}
```

### Contas a Receber

**Ferramenta MCP**: `consultar_contas_receber`  
**Endpoint Omie**: `/financas/contareceber/`  
**Método**: `ListarContasReceber`

**Parâmetros**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 50,
  "filtrar_por_codigo_lancamento": "opcional",
  "filtrar_por_cliente": "opcional",
  "filtrar_por_data_inicial": "opcional",
  "filtrar_por_data_final": "opcional"
}
```

**Resposta**:
```json
{
  "conta_receber_cadastro": [
    {
      "codigo_lancamento_omie": "987654321",
      "codigo_lancamento_integracao": "CR_001",
      "codigo_cliente_omie": "12345678",
      "data_vencimento": "15/01/2025",
      "valor_documento": 2500.00,
      "codigo_categoria": "2.01",
      "observacao": "Recebimento cliente",
      "numero_documento": "NF-002"
    }
  ],
  "total_de_registros": 400,
  "total_de_paginas": 20
}
```

## 🔧 Endpoints de CRUD

### Cliente

#### Incluir Cliente

**Ferramenta MCP**: `incluir_cliente`  
**Endpoint Omie**: `/geral/clientes/`  
**Método**: `IncluirCliente`

**Payload**:
```json
{
  "cnpj_cpf": "12.345.678/0001-90",
  "razao_social": "Cliente Teste Ltda",
  "nome_fantasia": "Teste",
  "email": "contato@teste.com",
  "telefone1_numero": "(11) 99999-9999",
  "codigo_cliente_integracao": "CLI_001"
}
```

**Resposta**:
```json
{
  "codigo_cliente_omie": "12345678",
  "codigo_cliente_integracao": "CLI_001",
  "codigo_status": "0",
  "descricao_status": "Cliente incluído com sucesso"
}
```

#### Alterar Cliente

**Ferramenta MCP**: `alterar_cliente`  
**Endpoint Omie**: `/geral/clientes/`  
**Método**: `AlterarCliente`

**Payload**:
```json
{
  "codigo_cliente_omie": "12345678",
  "razao_social": "Cliente Teste Alterado Ltda",
  "email": "novo@email.com"
}
```

**Resposta**:
```json
{
  "codigo_cliente_omie": "12345678",
  "codigo_cliente_integracao": "CLI_001",
  "codigo_status": "0",
  "descricao_status": "Cliente alterado com sucesso"
}
```

### Fornecedor

#### Incluir Fornecedor

**Ferramenta MCP**: `incluir_fornecedor`  
**Endpoint Omie**: `/geral/fornecedores/`  
**Método**: `IncluirFornecedor`

**Payload**:
```json
{
  "cnpj_cpf": "98.765.432/0001-10",
  "razao_social": "Fornecedor ABC S.A.",
  "nome_fantasia": "ABC",
  "email": "vendas@abc.com",
  "telefone1_numero": "(11) 88888-8888",
  "codigo_fornecedor_integracao": "FOR_001"
}
```

**Resposta**:
```json
{
  "codigo_fornecedor_omie": "87654321",
  "codigo_fornecedor_integracao": "FOR_001",
  "codigo_status": "0",
  "descricao_status": "Fornecedor incluído com sucesso"
}
```

#### Alterar Fornecedor

**Ferramenta MCP**: `alterar_fornecedor`  
**Endpoint Omie**: `/geral/fornecedores/`  
**Método**: `AlterarFornecedor`

**Payload**:
```json
{
  "codigo_fornecedor_omie": "87654321",
  "razao_social": "Fornecedor ABC Alterado S.A.",
  "email": "novo@abc.com"
}
```

**Resposta**:
```json
{
  "codigo_fornecedor_omie": "87654321",
  "codigo_fornecedor_integracao": "FOR_001",
  "codigo_status": "0",
  "descricao_status": "Fornecedor alterado com sucesso"
}
```

### Contas a Pagar

#### Incluir Conta a Pagar

**Ferramenta MCP**: `incluir_conta_pagar`  
**Endpoint Omie**: `/financas/contapagar/`  
**Método**: `IncluirContaPagar`

**Payload**:
```json
{
  "codigo_fornecedor_omie": "87654321",
  "data_vencimento": "31/12/2024",
  "valor_documento": 1500.00,
  "codigo_categoria": "1.01",
  "observacao": "Pagamento fornecedor",
  "numero_documento": "NF-001",
  "codigo_lancamento_integracao": "CP_001",
  "distribuicao": [
    {
      "cCodDep": "001",
      "nPerc": 100.0,
      "nValor": 1500.00
    }
  ]
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "123456789",
  "codigo_lancamento_integracao": "CP_001",
  "codigo_status": "0",
  "descricao_status": "Conta a pagar incluída com sucesso"
}
```

#### Alterar Conta a Pagar

**Ferramenta MCP**: `alterar_conta_pagar`  
**Endpoint Omie**: `/financas/contapagar/`  
**Método**: `AlterarContaPagar`

**Payload**:
```json
{
  "codigo_lancamento_omie": "123456789",
  "valor_documento": 1800.00,
  "observacao": "Valor atualizado"
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "123456789",
  "codigo_lancamento_integracao": "CP_001",
  "codigo_status": "0",
  "descricao_status": "Conta a pagar alterada com sucesso"
}
```

#### Excluir Conta a Pagar

**Ferramenta MCP**: `excluir_conta_pagar`  
**Endpoint Omie**: `/financas/contapagar/`  
**Método**: `ExcluirContaPagar`

**Payload**:
```json
{
  "codigo_lancamento_omie": "123456789"
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "123456789",
  "codigo_status": "0",
  "descricao_status": "Conta a pagar excluída com sucesso"
}
```

### Contas a Receber

#### Incluir Conta a Receber

**Ferramenta MCP**: `incluir_conta_receber`  
**Endpoint Omie**: `/financas/contareceber/`  
**Método**: `IncluirContaReceber`

**Payload**:
```json
{
  "codigo_cliente_omie": "12345678",
  "data_vencimento": "15/01/2025",
  "valor_documento": 2500.00,
  "codigo_categoria": "2.01",
  "observacao": "Recebimento cliente",
  "numero_documento": "NF-002",
  "codigo_lancamento_integracao": "CR_001",
  "distribuicao": [
    {
      "cCodDep": "001",
      "nPerc": 100.0,
      "nValor": 2500.00
    }
  ]
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "987654321",
  "codigo_lancamento_integracao": "CR_001",
  "codigo_status": "0",
  "descricao_status": "Conta a receber incluída com sucesso"
}
```

#### Alterar Conta a Receber

**Ferramenta MCP**: `alterar_conta_receber`  
**Endpoint Omie**: `/financas/contareceber/`  
**Método**: `AlterarContaReceber`

**Payload**:
```json
{
  "codigo_lancamento_omie": "987654321",
  "data_vencimento": "20/01/2025",
  "valor_documento": 3000.00
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "987654321",
  "codigo_lancamento_integracao": "CR_001",
  "codigo_status": "0",
  "descricao_status": "Conta a receber alterada com sucesso"
}
```

#### Excluir Conta a Receber

**Ferramenta MCP**: `excluir_conta_receber`  
**Endpoint Omie**: `/financas/contareceber/`  
**Método**: `ExcluirContaReceber`

**Payload**:
```json
{
  "codigo_lancamento_omie": "987654321"
}
```

**Resposta**:
```json
{
  "codigo_lancamento_omie": "987654321",
  "codigo_status": "0",
  "descricao_status": "Conta a receber excluída com sucesso"
}
```

## 📊 Estruturas de Dados

### Distribuição de Departamentos

Para contas a pagar e receber, a distribuição por departamento segue a estrutura:

```json
{
  "distribuicao": [
    {
      "cCodDep": "001",     // Código do departamento
      "nPerc": 100.0,       // Percentual (0-100)
      "nValor": 1500.00     // Valor (opcional)
    }
  ]
}
```

### Endereço

```json
{
  "logradouro": "Rua das Flores, 123",
  "numero": "123",
  "complemento": "Sala 101",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01234-567"
}
```

## ⚠️ Campos Obrigatórios

### Cliente/Fornecedor
- `cnpj_cpf` (obrigatório para inclusão)
- `razao_social` (obrigatório para inclusão)
- `codigo_cliente_omie` ou `codigo_fornecedor_omie` (obrigatório para alteração)

### Contas a Pagar/Receber
- `codigo_fornecedor_omie` ou `codigo_cliente_omie` (obrigatório para inclusão)
- `data_vencimento` (obrigatório para inclusão)
- `valor_documento` (obrigatório para inclusão)
- `codigo_categoria` (obrigatório para inclusão)
- `codigo_lancamento_omie` (obrigatório para alteração/exclusão)

## 🔍 Troubleshooting

### Erros Comuns

#### Erro 500: cliente_fornecedor not part of structure
**Solução**: Removido campo inexistente `cliente_fornecedor` dos payloads.

#### Erro 422: JSON parsing error
**Solução**: Implementada sanitização de strings para remover caracteres problemáticos.

#### Erro: Código de categoria não encontrado
**Solução**: Implementada validação prévia dos códigos antes de enviar para a API.

#### Erro: Departamento não encontrado
**Solução**: Implementada validação e estrutura correta `distribuicao` para departamentos.

### Campos Removidos/Corrigidos

- ❌ `cliente_fornecedor` (não existe na API)
- ✅ `codigo_cliente_integracao` (adicionado)
- ✅ `codigo_fornecedor_integracao` (adicionado)
- ✅ `distribuicao` (estrutura correta para departamentos)

### Validações Implementadas

- ✅ CNPJ/CPF com dígitos verificadores
- ✅ Email com formato RFC 5322
- ✅ Telefone com formato brasileiro
- ✅ Data no formato DD/MM/YYYY
- ✅ Valores monetários positivos
- ✅ Códigos de categoria, departamento e tipo de documento

---

Para mais informações sobre troubleshooting, consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md).