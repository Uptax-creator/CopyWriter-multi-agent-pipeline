# 🧪 ROTEIRO COMPLETO DE TESTES PARA HOMOLOGAÇÃO OMIE MCP

## 📋 Objetivo
Validar todas as ferramentas implementadas nos **Conjuntos 1 e 2** antes da liberação para produção, garantindo qualidade, performance e confiabilidade.

## 🎯 Escopo dos Testes

### **Conjunto 1 Enhanced** (3 tools)
- ✅ consultar_categorias
- ✅ listar_clientes (com nova API)
- ✅ consultar_contas_pagar

### **Conjunto 2 Complete** (8 tools)
- 🏗️ **Projetos**: incluir_projeto, listar_projetos, excluir_projeto
- 💰 **Lançamentos**: incluir_lancamento, listar_lancamentos
- 🏦 **Contas Correntes**: incluir_conta_corrente, listar_contas_correntes, listar_resumo_contas_correntes

### **Sistema de Database** 
- 🗄️ Rastreamento de processos
- 📊 Métricas de performance
- 🚨 Sistema de alertas

---

## 🚀 FASE 1: TESTES DE CONECTIVIDADE

### 1.1 Teste de Inicialização
```bash
# Iniciar servidor do Conjunto 1
python omie_fastmcp_conjunto_1_enhanced.py

# Verificar recursos disponíveis
curl -X GET "omie://database/status"
curl -X GET "omie://metrics/summary"
curl -X GET "omie://alerts/active"
```

**✅ Critérios de Sucesso:**
- Servidor inicia sem erros
- Database conecta com PostgreSQL e Redis
- Resources respondem com status "healthy"

### 1.2 Teste de Conectividade API Omie
```python
# Teste através da tool testar_conexao()
await testar_conexao()
```

**✅ Critérios de Sucesso:**
- Conexão estabelecida com API Omie
- Tempo de resposta < 2s
- Credenciais válidas

---

## 🔍 FASE 2: TESTES FUNCIONAIS CONJUNTO 1

### 2.1 Teste: consultar_categorias()

#### Cenário 1: Consulta Básica
```python
resultado = await consultar_categorias(
    pagina=1,
    registros_por_pagina=10
)
```

**✅ Validações:**
- Retorna JSON estruturado
- Campo "execution_id" presente
- Campo "data" com categorias
- Performance < 3s

#### Cenário 2: Filtros Avançados
```python
resultado = await consultar_categorias(
    filtro_descricao="receita",
    apenas_ativas=True
)
```

**✅ Validações:**
- Filtro por descrição funciona
- Apenas categorias ativas retornadas
- Campo "total_filtrado" correto

#### Cenário 3: Teste de Erro
```python
resultado = await consultar_categorias(pagina=-1)
```

**✅ Validações:**
- Erro tratado adequadamente
- Mensagem de erro clara
- Status "error" no retorno

### 2.2 Teste: listar_clientes()

#### Cenário 1: Nova Estrutura API
```python
resultado = await listar_clientes(
    pagina=1,
    registros_por_pagina=50
)
```

**✅ Validações:**
- Endpoint "/geral/clientes/" utilizado
- Campo "clientes_cadastro" presente
- Estrutura conforme documentação
- Tags "cliente" aplicadas

#### Cenário 2: Filtros Combinados
```python
resultado = await listar_clientes(
    filtro_nome="silva",
    filtro_cidade="são paulo",
    apenas_ativos=True
)
```

**✅ Validações:**
- Filtros aplicados corretamente
- Apenas clientes ativos
- Performance adequada

### 2.3 Teste: consultar_contas_pagar()

#### Cenário 1: Contas Vencidas
```python
resultado = await consultar_contas_pagar(
    status="vencido",
    data_fim="20/07/2025"
)
```

**✅ Validações:**
- Apenas contas vencidas retornadas
- Data calculada automaticamente
- Alerta criado se > 10 contas vencidas

#### Cenário 2: Contas a Vencer
```python
resultado = await consultar_contas_pagar(
    status="a_vencer",
    data_inicio="21/07/2025"
)
```

**✅ Validações:**
- Apenas contas futuras
- Filtro de status correto
- Transações canceladas ignoradas

---

## 🔧 FASE 3: TESTES FUNCIONAIS CONJUNTO 2

### 3.1 Grupo: Projetos

#### Teste 1: incluir_projeto()
```python
# Cenário de Sucesso
resultado = await incluir_projeto(
    codint="PROJ_001",
    nome="Projeto Teste Homologação",
    inativo="N"
)
```

**✅ Validações:**
- Projeto criado com sucesso
- Código único gerado
- Status "0" retornado
- Execution_id registrado

#### Teste 2: Código Duplicado (deve falhar)
```python
resultado = await incluir_projeto(
    codint="PROJ_001",  # Mesmo código
    nome="Projeto Duplicado"
)
```

**✅ Validações:**
- Erro de código duplicado
- Mensagem clara de falha
- Process marcado como "failed"

#### Teste 3: listar_projetos()
```python
resultado = await listar_projetos(
    pagina=1,
    registros_por_pagina=20
)
```

**✅ Validações:**
- Projeto criado aparece na lista
- Paginação funcionando
- Formato de resposta correto

#### Teste 4: excluir_projeto()
```python
resultado = await excluir_projeto(
    codint="PROJ_001"
)
```

**✅ Validações:**
- Projeto excluído com sucesso
- Validações de segurança aplicadas
- Não aparece mais na listagem

### 3.2 Grupo: Lançamentos

#### Teste 5: incluir_lancamento()
```python
resultado = await incluir_lancamento(
    cod_int_lanc="LANC_001",
    cod_conta_corrente=3154514643,
    data_lancamento="20/07/2025",
    valor_lancamento=1500.00,
    cod_categoria="1.01.02",
    tipo_lancamento="DIN",
    observacao="Teste de lançamento"
)
```

**✅ Validações:**
- Estrutura conforme documentação
- Validação de data formato DD/MM/AAAA
- Valor deve ser > 0
- Execution_id registrado

#### Teste 6: Data Inválida (deve falhar)
```python
resultado = await incluir_lancamento(
    cod_int_lanc="LANC_002",
    data_lancamento="2025-07-20"  # Formato inválido
)
```

**✅ Validações:**
- Erro de formato de data
- Mensagem explicativa
- Validação antes da API

#### Teste 7: listar_lancamentos()
```python
resultado = await listar_lancamentos(
    pagina=1,
    registros_por_pagina=10
)
```

**✅ Validações:**
- Lançamento criado aparece
- Estrutura "listaLancamentos"
- Informações detalhadas presentes

### 3.3 Grupo: Contas Correntes

#### Teste 8: incluir_conta_corrente()
```python
resultado = await incluir_conta_corrente(
    cod_int_conta="TESTE_001",
    tipo_conta="CX",
    codigo_banco="999",
    descricao="Caixa Teste Homologação",
    saldo_inicial=1000.00
)
```

**✅ Validações:**
- Conta criada com sucesso
- Tipo de conta validado (CX, CC, CA, AD)
- Saldo inicial registrado
- Código único gerado

#### Teste 9: Tipo Inválido (deve falhar)
```python
resultado = await incluir_conta_corrente(
    cod_int_conta="TESTE_002",
    tipo_conta="XX",  # Tipo inválido
    codigo_banco="999",
    descricao="Conta Inválida"
)
```

**✅ Validações:**
- Erro de tipo inválido
- Mensagem lista tipos válidos
- Validação antes da API

#### Teste 10: listar_contas_correntes()
```python
resultado = await listar_contas_correntes()
```

**✅ Validações:**
- Conta criada aparece na lista
- Detalhes completos presentes
- Paginação funcional

#### Teste 11: listar_resumo_contas_correntes()
```python
resultado = await listar_resumo_contas_correntes()
```

**✅ Validações:**
- Formato resumido correto
- Apenas campos essenciais
- Performance melhor que listagem completa

---

## 📊 FASE 4: TESTES DE PERFORMANCE

### 4.1 Teste de Carga
```python
import asyncio
import time

async def teste_carga():
    start_time = time.time()
    
    # Executar 10 operações simultâneas
    tasks = []
    for i in range(10):
        tasks.append(consultar_categorias())
    
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    print(f"10 operações em {duration:.2f}s")
    return duration < 10  # Deve completar em < 10s
```

**✅ Critérios:**
- 10 operações em < 10s
- Todas respondem com sucesso
- Database não trava

### 4.2 Teste de Timeout
```python
# Simular operação lenta
resultado = await incluir_projeto(
    codint="TIMEOUT_TEST",
    nome="A" * 1000  # Nome muito longo
)
```

**✅ Validações:**
- Timeout adequado (< 30s)
- Alerta criado para operações lentas
- Process marcado corretamente

---

## 🗄️ FASE 5: TESTES DE DATABASE

### 5.1 Teste de Rastreamento
```python
# Verificar se todos os processos são registrados
health = await omie_db.health_check()
processes = await omie_db.process_controller.get_active_processes()
```

**✅ Validações:**
- Todos os execution_ids registrados
- PostgreSQL e Redis funcionando
- Métricas sendo coletadas

### 5.2 Teste de Métricas
```python
# Após executar várias tools
summary = await omie_db.metrics_collector.get_performance_summary(hours=1)
```

**✅ Validações:**
- Métricas de cada endpoint coletadas
- Tempo de resposta registrado
- Taxa de sucesso calculada

### 5.3 Teste de Alertas
```python
# Forçar condição de alerta (muitas contas vencidas)
resultado = await consultar_contas_pagar(status="vencido")
```

**✅ Validações:**
- Alerta criado automaticamente
- Severidade apropriada
- Detalhes no context_data

---

## 🚨 FASE 6: TESTES DE ERRO E RECUPERAÇÃO

### 6.1 Teste de Resiliência
```python
# Desconectar Redis temporariamente
# Executar operações
# Reconectar Redis
```

**✅ Validações:**
- Aplicação continua funcionando
- Fallback para modo sem cache
- Reconexão automática

### 6.2 Teste de Dados Inválidos
```python
# Testar com dados maliciosos
resultado = await incluir_projeto(
    codint="'; DROP TABLE projects; --",
    nome="<script>alert('xss')</script>"
)
```

**✅ Validações:**
- Dados sanitizados
- SQL injection bloqueado
- XSS prevenido

---

## 📋 FASE 7: VALIDAÇÃO FINAL

### 7.1 Checklist de Homologação

#### ✅ Funcionalidade
- [ ] Todas as 11 tools funcionam
- [ ] Validações de entrada implementadas
- [ ] Códigos de erro apropriados
- [ ] Estruturas de dados corretas

#### ✅ Performance
- [ ] Tempo de resposta < 3s por tool
- [ ] Suporte a 10 operações simultâneas
- [ ] Database responsivo
- [ ] Métricas coletadas

#### ✅ Segurança
- [ ] Dados sensíveis protegidos
- [ ] Validação de entrada completa
- [ ] SQL injection prevenido
- [ ] Rate limiting funcional

#### ✅ Rastreabilidade
- [ ] Todos os processos registrados
- [ ] Execution_ids únicos
- [ ] Métricas precisas
- [ ] Alertas automáticos

#### ✅ Documentação
- [ ] APIs documentadas
- [ ] Exemplos funcionais
- [ ] Casos de erro cobertos
- [ ] Performance baselined

### 7.2 Critérios de Aprovação

**🟢 APROVADO PARA PRODUÇÃO**
- 100% dos testes funcionais passando
- Performance dentro dos limites
- 0 alertas críticos
- Database estável
- Documentação completa

**🟡 APROVADO COM RESSALVAS**
- 95% dos testes passando
- Performance aceitável
- Alertas não-críticos apenas
- Correções menores necessárias

**🔴 REPROVADO**
- < 95% dos testes passando
- Performance inadequada
- Alertas críticos presentes
- Falhas de segurança

---

## 🎯 EXECUÇÃO DOS TESTES

### Comando Unificado
```bash
# Executar suite completa de testes
python test_homologacao_complete.py --conjunto=all --verbose

# Executar apenas Conjunto 1
python test_homologacao_complete.py --conjunto=1

# Executar apenas Conjunto 2  
python test_homologacao_complete.py --conjunto=2

# Executar apenas testes de performance
python test_homologacao_complete.py --performance-only
```

### Relatório Esperado
```
🧪 RELATÓRIO DE HOMOLOGAÇÃO OMIE MCP
===========================================

📊 RESUMO GERAL:
- Total de testes: 47
- Sucessos: 47 (100%)
- Falhas: 0 (0%)
- Warnings: 2

⏱️ PERFORMANCE:
- Tempo médio de resposta: 1.2s
- Operações simultâneas: 10 OK
- Database responsivo: ✅

🎯 APROVAÇÃO: ✅ LIBERADO PARA PRODUÇÃO
```

Este roteiro garante que todas as ferramentas estejam **totalmente validadas e prontas para uso em produção**, com qualidade, performance e confiabilidade comprovadas.