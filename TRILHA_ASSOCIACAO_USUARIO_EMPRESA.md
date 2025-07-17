# 🏢 TRILHA DE ASSOCIAÇÃO USUÁRIO-EMPRESA

## 📊 **Situação Atual no Banco**

### **Usuário Existente**
```sql
Nome: João Silva
Email: joao.silva@teste.com
ID: (UUID)
Empresa Atual: eaf31430-3432-47c4-8d3c-d82f040d4e48 (Empresa Teste)
```

### **Empresas Disponíveis**
```sql
1. UPTAX SOLUCOES TRIBUTARIAS DIGITAIS
   ID: 73db40c3-9919-439b-bf5f-cb018770b8ca
   CNPJ: 46845239000163
   Status: ✅ Cadastrada, mas SEM usuários associados

2. Empresa Teste  
   ID: eaf31430-3432-47c4-8d3c-d82f040d4e48
   CNPJ: 12345678000195
   Status: ✅ Cadastrada, João Silva associado
```

## 🔄 **Problema Identificado**

O usuário **João Silva** está associado à **"Empresa Teste"**, mas você quer que ele acesse a **"UPTAX"**. Existem duas abordagens:

### **Opção A: Trocar Associação (Recomendado)**
- Alterar o `id_empresa` do usuário de `Empresa Teste` → `UPTAX`
- Manter histórico da mudança

### **Opção B: Múltiplas Empresas (Complexo)**
- Permitir usuário em múltiplas empresas
- Requer mudança estrutural no banco

## 🛠️ **Trilha de Correção Imediata**

### **1. Correção no Banco (Rápida)**
```sql
-- Associar João Silva à UPTAX
UPDATE usuario 
SET id_empresa = '73db40c3-9919-439b-bf5f-cb018770b8ca',
    atualizado_em = CURRENT_TIMESTAMP
WHERE email = 'joao.silva@teste.com';
```

### **2. Verificação**
```sql
-- Confirmar mudança
SELECT u.nome, u.email, e.razao_social 
FROM usuario u 
JOIN empresa e ON u.id_empresa = e.id_empresa
WHERE u.email = 'joao.silva@teste.com';
```

## 🎯 **Trilha que o Usuário DEVERIA Fazer (Frontend)**

### **Fluxo Atual no Frontend**
1. **Login** → `joao.silva@teste.com`
2. **Tela de Seleção de Empresa** → Lista empresas do usuário
3. **Problema**: Lista está hardcoded, não lê do banco real

### **Fluxo Corrigido Necessário**
1. **Login** → Validar credenciais
2. **Buscar Empresas do Usuário** → Consultar banco real
3. **Mostrar Empresas Disponíveis** → UPTAX deve aparecer
4. **Selecionar UPTAX** → Acessar dashboard da empresa
5. **Opção "Trocar Empresa"** → Voltar à seleção

## 🔧 **Implementação da Trilha Correta**

### **1. Corrigir loadUserCompanies() no Frontend**
```javascript
async loadUserCompanies() {
    try {
        // Buscar empresas reais do backend
        const response = await fetch('/api/user/companies', {
            headers: { 'Authorization': `Bearer ${this.token}` }
        });
        
        const userCompanies = await response.json();
        
        // Se não tem empresas, mostrar opções
        if (userCompanies.length === 0) {
            this.showNoCompaniesMessage();
        } else {
            this.renderCompanyList(userCompanies);
        }
    } catch (error) {
        console.error('Erro ao carregar empresas:', error);
        // Fallback com dados locais
        this.loadFallbackCompanies();
    }
}
```

### **2. Integrar com Tenant Manager Backend**
```python
# No tenant manager - endpoint /api/user/companies
@app.get("/user/{user_id}/companies")
async def get_user_companies(user_id: str):
    # Buscar empresas do usuário
    companies = db.query(Empresa).join(Usuario).filter(
        Usuario.id_usuario == user_id
    ).all()
    
    return [
        {
            "id": company.id_empresa,
            "nome": company.razao_social,
            "cnpj": format_cnpj(company.cnpj),
            "perfil": "admin"  # Determinar perfil do usuário
        }
        for company in companies
    ]
```

### **3. Adicionar Função "Juntar-se à Empresa"**
```javascript
async joinExistingCompany(companyCode) {
    try {
        const response = await fetch('/api/user/join-company', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}` 
            },
            body: JSON.stringify({ 
                companyCode: companyCode,
                requestMessage: "Solicitação de acesso à UPTAX"
            })
        });
        
        if (response.ok) {
            this.showAlert('Solicitação enviada! Aguarde aprovação.', 'success');
        }
    } catch (error) {
        this.showAlert('Erro ao solicitar acesso', 'danger');
    }
}
```

## 🚀 **Solução Imediata vs Completa**

### **⚡ Solução Imediata (5 min)**
```sql
-- Executar no banco SQLite
UPDATE usuario 
SET id_empresa = '73db40c3-9919-439b-bf5f-cb018770b8ca'
WHERE email = 'joao.silva@teste.com';
```

### **🏗️ Solução Completa (2 horas)**
1. Integrar frontend com tenant-manager
2. Implementar busca real de empresas
3. Adicionar fluxo de "juntar-se à empresa"
4. Implementar aprovação de solicitações
5. Histórico de mudanças de empresa

## 📋 **Passos para o Usuário APÓS Correção**

### **Trilha Corrigida**
1. **Login** → `joao.silva@teste.com` 
2. **Tela Seleção** → "UPTAX SOLUCOES TRIBUTARIAS..." aparece
3. **Clicar em UPTAX** → Acessa dashboard da UPTAX
4. **Dashboard** → Mostra "UPTAX" no header
5. **Menu → Trocar Empresa** → Volta à seleção se necessário

### **Botões Disponíveis**
- **"Criar Nova Empresa"** → Se quiser cadastrar outra
- **"Juntar-se a Empresa"** → Se quiser solicitar acesso a outra
- **Menu → Trocar Empresa** → Para alternar entre empresas

## 🎯 **Recomendação**

**Para resolver AGORA**: Execute o SQL de correção
**Para resolver COMPLETAMENTE**: Implemente a integração frontend-backend

Isso permitirá que o usuário acesse a UPTAX corretamente e tenha o fluxo completo de gestão de empresas.

---

*Análise realizada em 11/07/2025*
*Problema: Associação incorreta usuário-empresa*
*Solução: Atualizar banco + integrar frontend*