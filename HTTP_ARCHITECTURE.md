# 🌐 Arquitetura HTTP - Omie MCP Server

## 🎯 **Nova Arquitetura Unificada**

### **Antes: Arquitetura Direta**
```
Claude Desktop → Python Script → Omie API
```
- ❌ Problemas de PATH e dependências
- ❌ Logs misturados com protocolo MCP
- ❌ Difícil de debugar
- ❌ Não reutilizável para outras integrações

### **Depois: Arquitetura HTTP**
```
Claude Desktop → HTTP Client → HTTP Server → Omie API
     ↓
Copilot Studio → HTTP Server → Omie API
     ↓
N8N/Zapier → HTTP Server → Omie API
```
- ✅ Servidor HTTP único e estável
- ✅ Múltiplas integrações usando o mesmo servidor
- ✅ Logs centralizados e limpos
- ✅ Fácil de debugar e manter
- ✅ API REST padrão

## 🔧 **Componentes da Nova Arquitetura**

### 1. **Servidor HTTP (`omie_mcp_http.py`)**
- Servidor FastAPI na porta 3000
- Endpoints MCP padronizados
- Integração direta com Omie API
- Logs centralizados
- Documentação automática

### 2. **Cliente HTTP (`claude_http_client.py`)**
- Cliente específico para Claude Desktop
- Converte protocolo MCP para HTTP
- Comunica com o servidor HTTP
- Processa respostas para o Claude

### 3. **Scripts de Configuração**
- `configure_claude_http.py` - Configura Claude Desktop
- `start_server.py` - Inicia servidor HTTP
- Configuração automática e validação

## 📋 **Endpoints HTTP Disponíveis**

### **MCP Endpoints**
```
POST /mcp/initialize     - Inicializar sessão
GET  /mcp/tools          - Listar ferramentas
POST /mcp/tools/{name}   - Executar ferramenta
```

### **Ferramentas Disponíveis**
```
POST /mcp/tools/consultar_categorias
POST /mcp/tools/consultar_departamentos
POST /mcp/tools/consultar_tipos_documento
POST /mcp/tools/consultar_contas_pagar
POST /mcp/tools/consultar_contas_receber
```

### **Endpoints de Teste**
```
GET /test/categorias      - Teste rápido de categorias
GET /test/departamentos   - Teste rápido de departamentos
GET /test/tipos-documento - Teste rápido de tipos
GET /test/contas-pagar    - Teste rápido de contas a pagar
GET /test/contas-receber  - Teste rápido de contas a receber
```

### **Documentação**
```
GET /docs                 - Documentação automática (Swagger)
GET /health               - Health check
GET /                     - Informações do servidor
```

## 🚀 **Como Usar**

### **Passo 1: Iniciar Servidor HTTP**
```bash
# Terminal 1
python start_server.py
```

### **Passo 2: Configurar Claude Desktop**
```bash
# Terminal 2
python configure_claude_http.py
```

### **Passo 3: Reiniciar Claude Desktop**
- Feche completamente o Claude Desktop
- Abra novamente
- Teste: `"Consulte as categorias do Omie ERP"`

## 💡 **Vantagens da Arquitetura HTTP**

### **1. Unificação**
- ✅ Um único servidor para todas as integrações
- ✅ Mesmo código para Claude, Copilot, N8N, etc.
- ✅ Manutenção centralizada

### **2. Estabilidade**
- ✅ Servidor HTTP mais estável que scripts diretos
- ✅ Retry automático em caso de falha
- ✅ Logs separados do protocolo MCP

### **3. Debugabilidade**
- ✅ Logs HTTP claros e estruturados
- ✅ Endpoints de teste independentes
- ✅ Documentação automática
- ✅ Fácil de testar com curl/Postman

### **4. Escalabilidade**
- ✅ Pode servir múltiplos clientes simultaneamente
- ✅ Cache de respostas possível
- ✅ Rate limiting implementável
- ✅ Métricas e monitoring

### **5. Flexibilidade**
- ✅ Funciona com qualquer cliente HTTP
- ✅ Não depende de ambiente Python específico
- ✅ Deploy em containers Docker
- ✅ Pode rodar em servidor remoto

## 🔧 **Configuração do Claude Desktop**

### **Arquivo gerado:**
```json
{
  "mcpServers": {
    "omie-erp": {
      "command": "python3",
      "args": ["/caminho/para/claude_http_client.py"]
    }
  }
}
```

### **Fluxo de funcionamento:**
1. Claude Desktop inicia `claude_http_client.py`
2. Cliente HTTP conecta ao servidor em `localhost:3000`
3. Servidor HTTP processa requisições Omie
4. Respostas retornam via HTTP para o cliente
5. Cliente converte respostas para protocolo MCP
6. Claude Desktop recebe respostas formatadas

## 🧪 **Testes**

### **Teste do Servidor HTTP**
```bash
# Teste básico
curl http://localhost:3000/health

# Teste de ferramenta
curl -X POST http://localhost:3000/mcp/tools/consultar_categorias \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"pagina": 1}}'
```

### **Teste do Cliente MCP**
```bash
# Testar cliente isoladamente
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python claude_http_client.py
```

### **Teste no Claude Desktop**
```
Liste as categorias do Omie ERP
```

## 📊 **Monitoramento**

### **Logs do Servidor HTTP**
- Logs estruturados no terminal
- Requests HTTP com timestamps
- Erros detalhados com stack traces

### **Logs do Cliente MCP**
- Logs enviados para stderr (não interferem no protocolo)
- Requisições MCP processadas
- Erros de comunicação HTTP

### **Health Check**
```bash
curl http://localhost:3000/health
```

## 🎉 **Resultado Final**

### **Para o Usuário:**
- ✅ Funcionamento idêntico ao anterior
- ✅ Mais estável e confiável
- ✅ Mesmos comandos no Claude Desktop

### **Para o Desenvolvedor:**
- ✅ Código mais limpo e organizado
- ✅ Logs centralizados e claros
- ✅ Fácil de debugar e manter
- ✅ Reutilizável para outras integrações

### **Para Integrações:**
- ✅ API REST padrão
- ✅ Documentação automática
- ✅ Endpoints de teste
- ✅ Compatível com qualquer cliente HTTP

---

**Arquitetura HTTP implementada e pronta para uso!** 🚀