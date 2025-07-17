# 📋 Guia do Usuário - Omie Tenant Manager

## 🎯 **O que é esta aplicação?**

O Omie Tenant Manager é um sistema para gerenciar **empresas**, **usuários** e **aplicações** que usam o Omie ERP. 

**Imagine que você tem:**
- 🏢 **Várias empresas** como clientes
- 👥 **Usuários** de cada empresa  
- 📱 **Aplicações** (Claude, Copilot, N8N) que precisam acessar o Omie

Este sistema organiza tudo isso de forma segura e controlada.

---

## 🚀 **Como usar - Passo a Passo**

### **Passo 1: Acessar a aplicação** 🌐

1. **Abra seu navegador** (Chrome, Safari, Firefox)
2. **Digite o endereço**: `http://localhost:8001/docs`
3. **Você verá uma tela** com vários botões e seções

### **Passo 2: Entender a tela** 👀

Na tela você verá **4 seções principais:**

#### 🔐 **Autenticação**
- Para criar credenciais de aplicações
- Para fazer login e obter tokens

#### 🏢 **Empresas** 
- Cadastrar clientes (empresas)
- Ver lista de empresas
- Editar dados das empresas

#### 👥 **Usuários**
- Cadastrar usuários de cada empresa
- Vincular usuários às empresas
- Gerenciar acessos

#### 📱 **Aplicações**
- Criar aplicações (Claude, Copilot, etc.)
- Gerar credenciais seguras
- Vincular empresas às aplicações

---

## 📝 **Fluxo Completo de Uso**

### **1️⃣ Criar uma Aplicação**

**O que fazer:**
1. **Clique em "Aplicações"** na tela
2. **Clique em "POST /aplicacoes/"**
3. **Clique em "Try it out"**
4. **Digite** uma descrição para sua aplicação:
   ```json
   {
     "descricao": "Claude Desktop para Empresa X"
   }
   ```
5. **Clique em "Execute"**

**O que acontece:**
- Sistema cria **APP_KEY** e **APP_SECRET**
- ⚠️ **IMPORTANTE**: Copie e guarde o APP_SECRET em local seguro!

### **2️⃣ Obter Token de Acesso**

**O que fazer:**
1. **Clique em "Autenticação"**
2. **Clique em "POST /auth/token"**
3. **Clique em "Try it out"**
4. **Cole suas credenciais**:
   ```json
   {
     "app_key": "sua_app_key_aqui",
     "app_secret": "seu_app_secret_aqui"
   }
   ```
5. **Clique em "Execute"**

**O que acontece:**
- Sistema gera um **token de acesso**
- ⚠️ **IMPORTANTE**: Copie este token!

### **3️⃣ Usar o Token (Autorização)**

**O que fazer:**
1. **No topo da página**, clique em **"Authorize"**
2. **Digite**: `Bearer seu_token_aqui`
3. **Clique em "Authorize"**

**O que acontece:**
- Agora você pode usar **todos os endpoints** da API

### **4️⃣ Cadastrar uma Empresa**

**O que fazer:**
1. **Clique em "Empresas"**
2. **Clique em "POST /empresas/"**
3. **Clique em "Try it out"**
4. **Preencha os dados**:
   ```json
   {
     "razao_social": "Empresa Exemplo LTDA",
     "cnpj": "12345678000195",
     "email_contato": "contato@empresa.com",
     "telefone_contato": "(11) 99999-9999"
   }
   ```
5. **Clique em "Execute"**

### **5️⃣ Cadastrar Usuários**

**O que fazer:**
1. **Clique em "Usuários"**
2. **Clique em "POST /usuarios/"**
3. **Preencha os dados**:
   ```json
   {
     "nome": "João",
     "sobrenome": "Silva",
     "email": "joao.silva@empresa.com",
     "telefone": "(11) 88888-8888",
     "id_empresa": "cole_o_id_da_empresa_aqui"
   }
   ```

### **6️⃣ Vincular Empresa à Aplicação**

**O que fazer:**
1. **Clique em "Aplicações"**
2. **Clique em "POST /aplicacoes/vincular"**
3. **Preencha com credenciais do Omie**:
   ```json
   {
     "id_empresa": "id_da_empresa",
     "id_aplicacao": "id_da_aplicacao",
     "omie_app_key": "credencial_omie_da_empresa",
     "omie_app_secret": "secret_omie_da_empresa",
     "config_especifica": {
       "departamento_padrao": "001",
       "categoria_padrao": "1.01.01"
     }
   }
   ```

---

## 🔍 **Como consultar dados**

### **Ver todas as empresas:**
1. **Clique em "GET /empresas/"**
2. **Clique em "Try it out"**
3. **Clique em "Execute"**

### **Buscar empresa específica:**
1. **Clique em "GET /empresas/{empresa_id}"**
2. **Digite o ID da empresa**
3. **Execute**

### **Ver usuários de uma empresa:**
1. **Clique em "GET /empresas/{empresa_id}/usuarios"**
2. **Digite o ID da empresa**
3. **Execute**

---

## ⚠️ **Dicas Importantes**

### 🔐 **Segurança:**
- **NUNCA compartilhe** APP_SECRET ou tokens
- **Guarde credenciais** em local seguro
- **Tokens expiram** em 24 horas

### 📝 **CNPJ:**
- Digite **apenas números**: `12345678000195`
- Sistema valida automaticamente

### 📧 **Email:**
- Deve ser **único** no sistema
- Usado para identificar usuários

### 🆔 **IDs:**
- **Copie sempre** os IDs retornados
- Necessários para vincular dados

---

## 🛠️ **Resolvendo Problemas**

### **❌ Error 401 - Unauthorized**
**Problema:** Token inválido ou expirado
**Solução:** Obter novo token no endpoint `/auth/token`

### **❌ Error 400 - Bad Request**
**Problema:** Dados incorretos ou incompletos
**Solução:** Verificar JSON e campos obrigatórios

### **❌ Error 404 - Not Found**
**Problema:** ID não existe
**Solução:** Verificar se o ID está correto

### **❌ CNPJ já cadastrado**
**Problema:** Empresa já existe
**Solução:** Usar outro CNPJ ou atualizar existente

---

## 📊 **Endpoints mais usados**

| Ação | Endpoint | Método |
|------|----------|---------|
| Criar aplicação | `/aplicacoes/` | POST |
| Obter token | `/auth/token` | POST |
| Listar empresas | `/empresas/` | GET |
| Criar empresa | `/empresas/` | POST |
| Criar usuário | `/usuarios/` | POST |
| Vincular empresa+app | `/aplicacoes/vincular` | POST |
| Health check | `/health` | GET |

---

## 🎯 **Exemplo Prático Completo**

**Cenário:** Cadastrar a empresa "Tech LTDA" e usuário "Maria"

### **1. Criar aplicação:**
```json
{"descricao": "Claude para Tech LTDA"}
```
**Resultado:** `app_key: ABC123`, `app_secret: XYZ789`

### **2. Obter token:**
```json
{"app_key": "ABC123", "app_secret": "XYZ789"}
```
**Resultado:** `token: eyJ0eXAi...`

### **3. Cadastrar empresa:**
```json
{
  "razao_social": "Tech LTDA",
  "cnpj": "11222333000144",
  "email_contato": "contato@tech.com"
}
```
**Resultado:** `id_empresa: 456-789-012`

### **4. Cadastrar usuário:**
```json
{
  "nome": "Maria",
  "sobrenome": "Santos",
  "email": "maria@tech.com",
  "id_empresa": "456-789-012"
}
```

**🎉 Pronto! Empresa e usuário cadastrados com sucesso!**

---

## 📞 **Precisa de ajuda?**

- 📧 **Email**: Para dúvidas técnicas
- 📱 **WhatsApp**: Para suporte urgente
- 📹 **Call**: Reunião para treinamento

**Este guia cobre 95% do uso diário da aplicação!** 🚀