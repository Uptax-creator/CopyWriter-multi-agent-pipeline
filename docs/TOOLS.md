# 🛠️ Documentação das Ferramentas

Este documento descreve todas as ferramentas disponíveis no Omie MCP Server.

## 📋 Índice

- [Ferramentas de Consulta](#ferramentas-de-consulta)
- [Ferramentas de Cliente/Fornecedor](#ferramentas-de-clientefornecedor)
- [Ferramentas de Contas a Pagar](#ferramentas-de-contas-a-pagar)
- [Ferramentas de Contas a Receber](#ferramentas-de-contas-a-receber)
- [Validações](#validações)
- [Exemplos de Uso](#exemplos-de-uso)

## 🔍 Ferramentas de Consulta

### consultar_categorias

**Descrição**: Consulta as categorias cadastradas no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_codigo` (string, opcional): Filtrar por código da categoria
- `filtrar_por_descricao` (string, opcional): Filtrar por descrição da categoria

**Exemplo de uso**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 10,
  "filtrar_por_codigo": "1.01"
}
```

### consultar_departamentos

**Descrição**: Consulta os departamentos cadastrados no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_codigo` (string, opcional): Filtrar por código do departamento
- `filtrar_por_descricao` (string, opcional): Filtrar por descrição do departamento

**Exemplo de uso**:
```json
{
  "pagina": 1,
  "registros_por_pagina": 20
}
```

### consultar_tipos_documento

**Descrição**: Consulta os tipos de documento cadastrados no Omie ERP.

**Parâmetros**:
- `filtrar_por_codigo` (string, opcional): Filtrar por código do tipo de documento
- `filtrar_por_descricao` (string, opcional): Filtrar por descrição do tipo de documento

**Exemplo de uso**:
```json
{
  "filtrar_por_codigo": "99999"
}
```

### consultar_clientes

**Descrição**: Consulta os clientes cadastrados no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_nome` (string, opcional): Filtrar por nome do cliente
- `cnpj_cpf` (string, opcional): Filtrar por CNPJ/CPF do cliente
- `codigo_cliente_omie` (string, opcional): Filtrar por código do cliente no Omie

**Exemplo de uso**:
```json
{
  "cnpj_cpf": "12.345.678/0001-90"
}
```

### consultar_fornecedores

**Descrição**: Consulta os fornecedores cadastrados no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_nome` (string, opcional): Filtrar por nome do fornecedor
- `cnpj_cpf` (string, opcional): Filtrar por CNPJ/CPF do fornecedor
- `codigo_fornecedor_omie` (string, opcional): Filtrar por código do fornecedor no Omie

**Exemplo de uso**:
```json
{
  "filtrar_por_nome": "Fornecedor Teste"
}
```

### consultar_contas_pagar

**Descrição**: Consulta as contas a pagar cadastradas no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_codigo_lancamento` (string, opcional): Filtrar por código do lançamento
- `filtrar_por_fornecedor` (string, opcional): Filtrar por código do fornecedor
- `filtrar_por_data_inicial` (string, opcional): Filtrar por data inicial (DD/MM/YYYY)
- `filtrar_por_data_final` (string, opcional): Filtrar por data final (DD/MM/YYYY)

**Exemplo de uso**:
```json
{
  "filtrar_por_data_inicial": "01/01/2024",
  "filtrar_por_data_final": "31/12/2024"
}
```

### consultar_contas_receber

**Descrição**: Consulta as contas a receber cadastradas no Omie ERP.

**Parâmetros**:
- `pagina` (int, opcional): Número da página (padrão: 1)
- `registros_por_pagina` (int, opcional): Registros por página (padrão: 50, máximo: 500)
- `filtrar_por_codigo_lancamento` (string, opcional): Filtrar por código do lançamento
- `filtrar_por_cliente` (string, opcional): Filtrar por código do cliente
- `filtrar_por_data_inicial` (string, opcional): Filtrar por data inicial (DD/MM/YYYY)
- `filtrar_por_data_final` (string, opcional): Filtrar por data final (DD/MM/YYYY)

**Exemplo de uso**:
```json
{
  "filtrar_por_cliente": "12345678"
}
```

## 👥 Ferramentas de Cliente/Fornecedor

### incluir_cliente

**Descrição**: Inclui um novo cliente no Omie ERP.

**Parâmetros obrigatórios**:
- `cnpj_cpf` (string): CNPJ ou CPF do cliente
- `razao_social` (string): Razão social do cliente

**Parâmetros opcionais**:
- `nome_fantasia` (string): Nome fantasia do cliente
- `email` (string): Email do cliente
- `telefone` (string): Telefone do cliente
- `codigo_cliente_integracao` (string): Código de integração do cliente

**Exemplo de uso**:
```json
{
  "cnpj_cpf": "12.345.678/0001-90",
  "razao_social": "Empresa Teste Ltda",
  "nome_fantasia": "Teste",
  "email": "contato@teste.com",
  "telefone": "(11) 99999-9999"
}
```

### incluir_fornecedor

**Descrição**: Inclui um novo fornecedor no Omie ERP.

**Parâmetros obrigatórios**:
- `cnpj_cpf` (string): CNPJ ou CPF do fornecedor
- `razao_social` (string): Razão social do fornecedor

**Parâmetros opcionais**:
- `nome_fantasia` (string): Nome fantasia do fornecedor
- `email` (string): Email do fornecedor
- `telefone` (string): Telefone do fornecedor
- `codigo_fornecedor_integracao` (string): Código de integração do fornecedor

**Exemplo de uso**:
```json
{
  "cnpj_cpf": "98.765.432/0001-10",
  "razao_social": "Fornecedor ABC S.A.",
  "email": "vendas@fornecedor.com"
}
```

### alterar_cliente

**Descrição**: Altera um cliente existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_cliente_omie` (string): Código do cliente no Omie

**Parâmetros opcionais**:
- `cnpj_cpf` (string): CNPJ ou CPF do cliente
- `razao_social` (string): Razão social do cliente
- `nome_fantasia` (string): Nome fantasia do cliente
- `email` (string): Email do cliente
- `telefone` (string): Telefone do cliente

**Exemplo de uso**:
```json
{
  "codigo_cliente_omie": "12345678",
  "email": "novo@email.com",
  "telefone": "(11) 88888-8888"
}
```

### alterar_fornecedor

**Descrição**: Altera um fornecedor existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_fornecedor_omie` (string): Código do fornecedor no Omie

**Parâmetros opcionais**:
- `cnpj_cpf` (string): CNPJ ou CPF do fornecedor
- `razao_social` (string): Razão social do fornecedor
- `nome_fantasia` (string): Nome fantasia do fornecedor
- `email` (string): Email do fornecedor
- `telefone` (string): Telefone do fornecedor

**Exemplo de uso**:
```json
{
  "codigo_fornecedor_omie": "87654321",
  "razao_social": "Fornecedor XYZ Ltda"
}
```

## 💰 Ferramentas de Contas a Pagar

### incluir_conta_pagar

**Descrição**: Inclui uma nova conta a pagar no Omie ERP.

**Parâmetros obrigatórios**:
- `cnpj_fornecedor` (string): CNPJ do fornecedor
- `data_vencimento` (string): Data de vencimento (DD/MM/YYYY)
- `valor_documento` (number): Valor do documento
- `codigo_categoria` (string): Código da categoria

**Parâmetros opcionais**:
- `observacao` (string): Observação sobre a conta
- `numero_documento` (string): Número do documento
- `codigo_departamento` (string): Código do departamento
- `codigo_lancamento_integracao` (string): Código de integração do lançamento

**Exemplo de uso**:
```json
{
  "cnpj_fornecedor": "98.765.432/0001-10",
  "data_vencimento": "31/12/2024",
  "valor_documento": 1500.00,
  "codigo_categoria": "1.01",
  "numero_documento": "NF-001",
  "observacao": "Pagamento de fornecedor"
}
```

### alterar_conta_pagar

**Descrição**: Altera uma conta a pagar existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_lancamento_omie` (string): Código do lançamento no Omie

**Parâmetros opcionais**:
- `data_vencimento` (string): Data de vencimento (DD/MM/YYYY)
- `valor_documento` (number): Valor do documento
- `codigo_categoria` (string): Código da categoria
- `observacao` (string): Observação sobre a conta
- `numero_documento` (string): Número do documento
- `codigo_departamento` (string): Código do departamento

**Exemplo de uso**:
```json
{
  "codigo_lancamento_omie": "12345678",
  "valor_documento": 1800.00,
  "observacao": "Valor atualizado"
}
```

### excluir_conta_pagar

**Descrição**: Exclui uma conta a pagar existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_lancamento_omie` (string): Código do lançamento no Omie

**Exemplo de uso**:
```json
{
  "codigo_lancamento_omie": "12345678"
}
```

## 💵 Ferramentas de Contas a Receber

### incluir_conta_receber

**Descrição**: Inclui uma nova conta a receber no Omie ERP.

**Parâmetros obrigatórios**:
- `cnpj_cliente` (string): CNPJ do cliente
- `data_vencimento` (string): Data de vencimento (DD/MM/YYYY)
- `valor_documento` (number): Valor do documento
- `codigo_categoria` (string): Código da categoria

**Parâmetros opcionais**:
- `observacao` (string): Observação sobre a conta
- `numero_documento` (string): Número do documento
- `codigo_departamento` (string): Código do departamento
- `codigo_lancamento_integracao` (string): Código de integração do lançamento

**Exemplo de uso**:
```json
{
  "cnpj_cliente": "12.345.678/0001-90",
  "data_vencimento": "15/01/2025",
  "valor_documento": 2500.00,
  "codigo_categoria": "2.01",
  "numero_documento": "NF-002"
}
```

### alterar_conta_receber

**Descrição**: Altera uma conta a receber existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_lancamento_omie` (string): Código do lançamento no Omie

**Parâmetros opcionais**:
- `data_vencimento` (string): Data de vencimento (DD/MM/YYYY)
- `valor_documento` (number): Valor do documento
- `codigo_categoria` (string): Código da categoria
- `observacao` (string): Observação sobre a conta
- `numero_documento` (string): Número do documento
- `codigo_departamento` (string): Código do departamento

**Exemplo de uso**:
```json
{
  "codigo_lancamento_omie": "87654321",
  "data_vencimento": "20/01/2025",
  "valor_documento": 3000.00
}
```

### excluir_conta_receber

**Descrição**: Exclui uma conta a receber existente no Omie ERP.

**Parâmetros obrigatórios**:
- `codigo_lancamento_omie` (string): Código do lançamento no Omie

**Exemplo de uso**:
```json
{
  "codigo_lancamento_omie": "87654321"
}
```

## ✅ Validações

O sistema implementa as seguintes validações:

### Validação de Documentos
- **CNPJ**: Validação completa com dígitos verificadores
- **CPF**: Validação completa com dígitos verificadores
- **Email**: Validação de formato RFC 5322
- **Telefone**: Validação de formato brasileiro
- **CEP**: Validação de formato (8 dígitos)

### Validação de Códigos
- **Categorias**: Verifica se o código existe no Omie
- **Departamentos**: Verifica se o código existe no Omie
- **Tipos de Documento**: Verifica se o código existe no Omie

### Validação de Valores
- **Valores monetários**: Deve ser um número positivo
- **Datas**: Formato DD/MM/YYYY
- **Percentuais**: Entre 0 e 100

## 📋 Exemplos de Uso

### Fluxo Completo: Criar Cliente e Conta a Receber

```bash
# 1. Consultar categorias disponíveis
python scripts/test_tool.py consultar_categorias

# 2. Incluir novo cliente
python scripts/test_tool.py incluir_cliente '{
  "cnpj_cpf": "12.345.678/0001-90",
  "razao_social": "Cliente Teste Ltda",
  "email": "contato@cliente.com"
}'

# 3. Criar conta a receber
python scripts/test_tool.py incluir_conta_receber '{
  "cnpj_cliente": "12.345.678/0001-90",
  "data_vencimento": "31/01/2025",
  "valor_documento": 5000.00,
  "codigo_categoria": "2.01",
  "numero_documento": "NF-001"
}'
```

### Fluxo Completo: Criar Fornecedor e Conta a Pagar

```bash
# 1. Consultar departamentos disponíveis
python scripts/test_tool.py consultar_departamentos

# 2. Incluir novo fornecedor
python scripts/test_tool.py incluir_fornecedor '{
  "cnpj_cpf": "98.765.432/0001-10",
  "razao_social": "Fornecedor ABC S.A.",
  "telefone": "(11) 99999-9999"
}'

# 3. Criar conta a pagar com departamento
python scripts/test_tool.py incluir_conta_pagar '{
  "cnpj_fornecedor": "98.765.432/0001-10",
  "data_vencimento": "28/02/2025",
  "valor_documento": 3500.00,
  "codigo_categoria": "1.01",
  "codigo_departamento": "001",
  "numero_documento": "NF-456"
}'
```

---

Para mais informações sobre o uso das ferramentas, consulte o [README.md](../README.md) principal.