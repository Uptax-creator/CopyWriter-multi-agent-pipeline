# 🔗 Integração Tenant Manager ↔ MCP Server

## 🎯 **Como funciona a integração**

### **📊 Fluxo Completo:**
```
1. Cliente se cadastra no Tenant Manager
2. Recebe credenciais do sistema (APP_KEY/SECRET)
3. Cadastra credenciais Omie da empresa
4. Claude/Copilot usa MCP Server 
5. MCP Server consulta Tenant Manager para obter credenciais Omie
6. MCP Server usa credenciais corretas para cada empresa
```

## 🏗️ **Estrutura Atual**

### **🔧 Tenant Manager (Porta 8001)**
- **Função**: Gerenciar empresas, usuários e aplicações
- **Dados**: Credenciais Omie por empresa
- **API**: REST com autenticação JWT

### **⚡ MCP Server (Porta 8000)**  
- **Função**: Fornecer tools para Claude/Copilot
- **Integração**: Busca credenciais no Tenant Manager
- **Protocolo**: HTTP MCP + REST

## 🔄 **Integração Necessária**

### **1. Endpoint de Consulta de Credenciais**

**No Tenant Manager, adicionar:**

```python
@router.get("/credenciais/{empresa_cnpj}")
async def obter_credenciais_empresa(
    empresa_cnpj: str,
    app_key: str,  # Credencial da aplicação (Claude, etc.)
    db: Session = Depends(get_db)
):
    """Obter credenciais Omie de uma empresa para uma aplicação"""
    
    # 1. Validar APP_KEY da aplicação
    aplicacao = db.query(Aplicacao).filter(
        Aplicacao.app_key == app_key,
        Aplicacao.ativo == True
    ).first()
    
    if not aplicacao:
        raise HTTPException(404, "Aplicação não encontrada")
    
    # 2. Buscar empresa por CNPJ
    empresa = db.query(Empresa).filter(
        Empresa.cnpj == empresa_cnpj,
        Empresa.ativo == True
    ).first()
    
    if not empresa:
        raise HTTPException(404, "Empresa não encontrada")
    
    # 3. Buscar aplicação da empresa
    app_cliente = db.query(AplicacaoCliente).filter(
        AplicacaoCliente.id_empresa == empresa.id_empresa,
        AplicacaoCliente.id_aplicacao == aplicacao.id_aplicacao,
        AplicacaoCliente.ativo == True
    ).first()
    
    if not app_cliente:
        raise HTTPException(404, "Empresa não vinculada à aplicação")
    
    # 4. Retornar credenciais Omie
    return {
        "omie_app_key": app_cliente.omie_app_key,
        "omie_app_secret": decrypt_password(app_cliente.omie_app_secret_hash),
        "config_omie": app_cliente.config_omie_json,
        "empresa": {
            "razao_social": empresa.razao_social,
            "cnpj": empresa.cnpj
        }
    }
```

### **2. Modificação no MCP Server**

**No arquivo `src/client/omie_client.py`:**

```python
import aiohttp
from typing import Optional, Dict

class TenantManagerClient:
    def __init__(self, tenant_url: str, app_key: str, app_secret: str):
        self.tenant_url = tenant_url
        self.app_key = app_key
        self.app_secret = app_secret
        self._token = None
    
    async def get_token(self):
        """Obter token de autenticação"""
        if self._token:
            return self._token
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.tenant_url}/auth/token",
                json={
                    "app_key": self.app_key,
                    "app_secret": self.app_secret
                }
            ) as response:
                data = await response.json()
                self._token = data["access_token"]
                return self._token
    
    async def get_empresa_credentials(self, cnpj: str) -> Dict:
        """Obter credenciais Omie de uma empresa"""
        token = await self.get_token()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.tenant_url}/credenciais/{cnpj}",
                headers={"Authorization": f"Bearer {token}"},
                params={"app_key": self.app_key}
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Erro ao obter credenciais: {response.status}")

class OmieClient:
    def __init__(self, tenant_manager: TenantManagerClient):
        self.tenant_manager = tenant_manager
        self._credentials_cache = {}
    
    async def get_credentials_for_cnpj(self, cnpj: str):
        """Obter credenciais para um CNPJ específico"""
        if cnpj in self._credentials_cache:
            return self._credentials_cache[cnpj]
        
        creds = await self.tenant_manager.get_empresa_credentials(cnpj)
        self._credentials_cache[cnpj] = creds
        return creds
    
    async def make_request(self, cnpj: str, endpoint: str, call: str, param: Dict):
        """Fazer requisição com credenciais específicas da empresa"""
        credentials = await self.get_credentials_for_cnpj(cnpj)
        
        payload = [{
            "call": call,
            "app_key": credentials["omie_app_key"],
            "app_secret": credentials["omie_app_secret"],
            "param": [param]
        }]
        
        # Resto da implementação...
```

### **3. Configuração das Tools**

**No MCP Server, cada tool recebe o CNPJ:**

```python
async def incluir_cliente(cnpj_empresa: str, dados_cliente: Dict):
    """Tool para incluir cliente"""
    
    # 1. Obter credenciais da empresa
    credentials = await omie_client.get_credentials_for_cnpj(cnpj_empresa)
    
    # 2. Usar configurações específicas da empresa
    config = credentials.get("config_omie", {})
    
    # 3. Aplicar departamento padrão se configurado
    if "departamento_padrao" in config:
        dados_cliente["codigo_departamento"] = config["departamento_padrao"]
    
    # 4. Fazer requisição
    return await omie_client.make_request(
        cnpj_empresa, 
        "/geral/clientes/", 
        "IncluirCliente", 
        dados_cliente
    )
```

## 🚀 **Implementação Prática**

### **Passo 1: Adicionar endpoint de credenciais**
```python
# No router aplicacoes.py
@router.get("/credenciais/{empresa_cnpj}")
async def obter_credenciais_empresa(...)
```

### **Passo 2: Criar cliente do Tenant Manager**
```python
# No MCP Server
tenant_client = TenantManagerClient(
    tenant_url="http://localhost:8001",
    app_key="chave_do_claude",
    app_secret="secret_do_claude"
)
```

### **Passo 3: Modificar todas as tools**
```python
# Cada tool recebe o CNPJ da empresa
# E busca credenciais dinamicamente
```

## 📋 **Vantagens da Integração**

### ✅ **Benefícios:**
1. **Multi-tenant real**: Cada empresa usa suas credenciais
2. **Segurança**: Credenciais centralizadas e criptografadas
3. **Configuração**: Cada empresa pode ter configs específicas
4. **Auditoria**: Logs de qual empresa usou qual tool
5. **Escalabilidade**: Adicionar empresas sem modificar código

### ⚡ **Performance:**
- Cache de credenciais no MCP Server
- Tokens JWT com expiração
- Conexões HTTP keep-alive

## 🔧 **Configuração Claude Desktop**

```json
{
  "mcpServers": {
    "omie-multi-tenant": {
      "command": "python",
      "args": ["/path/to/omie-mcp-server/src/server.py"],
      "env": {
        "TENANT_MANAGER_URL": "http://localhost:8001",
        "TENANT_APP_KEY": "sua_app_key_claude",
        "TENANT_APP_SECRET": "seu_app_secret_claude"
      }
    }
  }
}
```

## 🎯 **Exemplo de Uso**

### **1. Claude pergunta:**
> "Crie um cliente para a empresa CNPJ 12.345.678/0001-90"

### **2. MCP Server:**
1. Recebe CNPJ: `12345678000190`
2. Consulta Tenant Manager
3. Obtém credenciais Omie da empresa
4. Usa departamento padrão configurado
5. Cria cliente no Omie
6. Retorna resultado para Claude

### **3. Resultado:**
- ✅ Cliente criado com credenciais corretas
- ✅ Auditoria registrada
- ✅ Configurações aplicadas

## 📊 **Próximos Passos**

### **Implementação:**
1. ✅ Estrutura do banco atualizada
2. ⏳ Endpoint de credenciais
3. ⏳ Cliente do Tenant Manager
4. ⏳ Modificação das tools
5. ⏳ Testes integrados

**Esta integração torna o sistema verdadeiramente multi-tenant!** 🚀