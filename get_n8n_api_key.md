# 🔑 Como Obter N8N API Key

## **Opção 1: Via Interface N8N (Recomendado)**

1. Acesse: http://localhost:5678
2. Clique no seu avatar/perfil (canto superior direito)
3. Vá em **"Personal Settings"** ou **"Settings"**
4. Procure seção **"API Keys"** ou **"Personal Access Tokens"**
5. Click **"Create API Key"** ou **"Generate Token"**
6. Nome: `MCP Integration`
7. Copy a key gerada

## **Opção 2: Via Terminal (Se disponível)**

```bash
# Se N8N tem CLI para API keys
n8n user:create-api-key --name "MCP Integration"
```

## **Opção 3: Configuração Manual**

Se não conseguir encontrar nas settings, vamos configurar:

1. **Parar N8N**:
```bash
pkill -f n8n
```

2. **Iniciar com API habilitada**:
```bash
N8N_API_KEY_ENABLED=true n8n start --port 5678
```

## **🔒 COMO ENVIAR A KEY DE FORMA SEGURA**

### **Método 1: Via Arquivo Local**
```bash
# Criar arquivo temporário com a key
echo "sua_api_key_aqui" > /tmp/n8n_api_key.txt

# Eu leio o arquivo
cat /tmp/n8n_api_key.txt

# Você deleta o arquivo
rm /tmp/n8n_api_key.txt
```

### **Método 2: Via Variável de Ambiente**
```bash
# Definir temporariamente
export N8N_API_KEY="sua_api_key_aqui"

# Eu uso a variável
echo $N8N_API_KEY
```

### **Método 3: Hash/Substring**
Se for muito longa, você pode me enviar apenas:
- Primeiros 8 caracteres: `n8n_abcd...`
- Últimos 4 caracteres: `...xyz1`
- Eu assumo o formato completo

## **📋 PRÓXIMOS PASSOS**

Após obter a API key:

1. **Configurar Claude Desktop**
2. **Testar conexão N8N-MCP** 
3. **Criar workflows via MCP**
4. **Executar testes automatizados**

**Qual método prefere para obter/enviar a API key?**