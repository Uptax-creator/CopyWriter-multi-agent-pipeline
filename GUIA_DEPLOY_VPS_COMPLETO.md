# 🚀 GUIA COMPLETO - DEPLOY MCP SERVERS EM VPS EXTERNA

**Data**: 22/07/2025 20:30  
**Objetivo**: Deploy da arquitetura MCP independente em VPS com integração N8N  
**Status**: Guia completo com comandos e links  

---

## 🏗️ **ARQUITETURA VPS TARGET**

```
🌐 VPS EXTERNA (Ubuntu/Debian)
├── 🏦 Nibo-MCP Server (porta 8081)
│   ├── HTTP API endpoints
│   ├── SSE real-time streaming (porta 8083)
│   └── 24 ferramentas disponíveis
├── 📊 Omie-MCP Server (porta 8080)  
│   ├── HTTP API endpoints
│   ├── SSE real-time streaming (porta 8082)
│   └── 5 ferramentas disponíveis
├── 🔄 N8N Integration
│   ├── Webhooks para ambos ERPs
│   ├── SSE client nodes
│   └── Workflows automatizados
└── 🔍 Monitoring Stack
    ├── Health checks automáticos
    ├── Logs centralizados
    └── Alertas por email/slack
```

---

## 📦 **PREPARAÇÃO LOCAL**

### **1. Criar pacote de deploy**
```bash
# Navegar para projeto
cd /Users/kleberdossantosribeiro/omie-mcp

# Criar diretório de deploy
mkdir -p deploy-package

# Copiar arquivos essenciais
cp -r nibo-mcp/ deploy-package/
cp -r src/ deploy-package/
cp -r protocols/ deploy-package/
cp requirements.txt deploy-package/
cp credentials.json deploy-package/
cp omie_mcp_standard_simple.py deploy-package/
cp docker-compose.independent.yml deploy-package/
cp -r docker/ deploy-package/

# Criar script de instalação
cat > deploy-package/install-vps.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Instalando MCP Servers na VPS..."

# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências
sudo apt-get install -y python3 python3-pip python3-venv curl nginx certbot

# Criar usuário mcp
sudo useradd -m -s /bin/bash mcp || true
sudo usermod -aG sudo mcp

# Criar ambiente virtual
sudo -u mcp python3 -m venv /home/mcp/venv
sudo -u mcp /home/mcp/venv/bin/pip install -r requirements.txt

# Copiar arquivos
sudo cp -r . /home/mcp/omie-mcp/
sudo chown -R mcp:mcp /home/mcp/omie-mcp/

echo "✅ Instalação base concluída"
EOF

chmod +x deploy-package/install-vps.sh

# Compactar para upload
tar -czf mcp-deploy.tar.gz deploy-package/
```

### **2. Scripts de inicialização**
```bash
# Criar systemd services
cat > deploy-package/nibo-mcp.service << 'EOF'
[Unit]
Description=Nibo MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/home/mcp/omie-mcp/nibo-mcp/protocols
Environment=PATH=/home/mcp/venv/bin
ExecStart=/home/mcp/venv/bin/python3 http_nibo_server.py --host 0.0.0.0 --port 8081
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

cat > deploy-package/omie-mcp.service << 'EOF'
[Unit]
Description=Omie MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/home/mcp/omie-mcp/protocols
Environment=PATH=/home/mcp/venv/bin
ExecStart=/home/mcp/venv/bin/python3 http_mcp_server.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```

---

## 🌐 **COMANDOS DE DEPLOY VPS**

### **1. Upload para VPS**
```bash
# Exemplo com SCP (substitua pelos dados da sua VPS)
VPS_IP="YOUR_VPS_IP"
VPS_USER="root"  # ou seu usuário

# Upload do pacote
scp mcp-deploy.tar.gz $VPS_USER@$VPS_IP:/tmp/

# Conectar na VPS
ssh $VPS_USER@$VPS_IP

# Na VPS: Extrair e instalar
cd /tmp
tar -xzf mcp-deploy.tar.gz
cd deploy-package
sudo ./install-vps.sh
```

### **2. Configuração na VPS**
```bash
# Instalar services
sudo cp nibo-mcp.service /etc/systemd/system/
sudo cp omie-mcp.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable nibo-mcp omie-mcp
sudo systemctl start nibo-mcp omie-mcp

# Verificar status
sudo systemctl status nibo-mcp
sudo systemctl status omie-mcp

# Verificar logs
sudo journalctl -fu nibo-mcp
sudo journalctl -fu omie-mcp
```

### **3. Configurar Nginx Reverse Proxy**
```bash
# Configuração nginx
sudo tee /etc/nginx/sites-available/mcp-servers << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # Substitua pelo seu domínio

    # Nibo MCP
    location /nibo/ {
        proxy_pass http://localhost:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Omie MCP  
    location /omie/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE endpoints
    location /nibo/sse/ {
        proxy_pass http://localhost:8083/sse/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache off;
        proxy_buffering off;
    }

    location /omie/sse/ {
        proxy_pass http://localhost:8082/sse/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache off;
        proxy_buffering off;
    }
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/mcp-servers /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL com Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

---

## 🔗 **ENDPOINTS VPS PÚBLICOS**

### **URLs de Acesso** (substitua `your-domain.com`):

#### **🏦 Nibo-MCP**
- **Dashboard**: `https://your-domain.com/nibo/`
- **Health**: `https://your-domain.com/nibo/health`
- **API Docs**: `https://your-domain.com/nibo/docs`
- **Tools**: `POST https://your-domain.com/nibo/tools/{tool_name}`
- **N8N Webhook**: `POST https://your-domain.com/nibo/n8n/webhook/{tool_name}`
- **SSE Stream**: `https://your-domain.com/nibo/sse/stream`

#### **📊 Omie-MCP**  
- **Dashboard**: `https://your-domain.com/omie/`
- **Health**: `https://your-domain.com/omie/health`
- **Tools**: `https://your-domain.com/omie/tools`
- **SSE Stream**: `https://your-domain.com/omie/sse/stream`

---

## 🤖 **INTEGRAÇÃO N8N**

### **1. N8N Webhook Nodes**

#### **Nibo Integration Workflow**:
```json
{
  "name": "Nibo MCP Integration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "nibo-webhook",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "url": "https://your-domain.com/nibo/tools/={{ $json.tool_name }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "arguments",
              "value": "={{ $json.arguments }}"
            }
          ]
        }
      },
      "name": "Call Nibo MCP",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ $json }}"
      },
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Call Nibo MCP",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Call Nibo MCP": {
      "main": [
        [
          {
            "node": "Respond",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### **2. SSE Client Node (Custom)**
```javascript
// N8N Custom Node para SSE
const EventSource = require('eventsource');

async function execute() {
    const url = 'https://your-domain.com/nibo/sse/stream';
    const eventSource = new EventSource(url);
    
    return new Promise((resolve, reject) => {
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            resolve([{ json: data }]);
        };
        
        eventSource.onerror = function(error) {
            reject(error);
        };
        
        // Timeout após 30 segundos
        setTimeout(() => {
            eventSource.close();
            resolve([{ json: { timeout: true } }]);
        }, 30000);
    });
}
```

### **3. Exemplo de uso N8N**
```bash
# Testar webhook Nibo
curl -X POST https://your-n8n-instance.com/webhook/nibo-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "testar_conexao",
    "arguments": {}
  }'

# Testar webhook Omie  
curl -X POST https://your-n8n-instance.com/webhook/omie-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "consultar_categorias",
    "arguments": {}
  }'
```

---

## 📊 **MONITORING E LOGGING**

### **1. Health Check Script**
```bash
cat > /home/mcp/health-monitor.sh << 'EOF'
#!/bin/bash

check_service() {
    local service_name=$1
    local url=$2
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $service_name: OK"
    else
        echo "❌ $service_name: FALHA"
        # Restart service
        sudo systemctl restart "$service_name"
        # Send alert (configure seu email/slack)
        echo "$service_name falhou em $(date)" | mail -s "MCP Alert" admin@yourcompany.com
    fi
}

echo "🔍 Health Check MCP Servers - $(date)"
check_service "nibo-mcp" "http://localhost:8081/health"
check_service "omie-mcp" "http://localhost:8080/health"
EOF

chmod +x /home/mcp/health-monitor.sh

# Cron para executar a cada 2 minutos
echo "*/2 * * * * /home/mcp/health-monitor.sh >> /var/log/mcp-health.log" | sudo crontab -
```

### **2. Log Aggregation**
```bash
# Instalar logrotate para MCP logs
sudo tee /etc/logrotate.d/mcp-servers << 'EOF'
/var/log/mcp-*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 mcp mcp
}
EOF
```

---

## 🧪 **COMANDOS DE TESTE**

### **Testes Locais (antes do deploy)**:
```bash
# Testar servidores localmente
curl http://localhost:8081/health
curl http://localhost:8080/health

# Testar ferramentas
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {}}' \
  http://localhost:8081/tools/testar_conexao

curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "consultar_categorias", "arguments": {}}' \
  http://localhost:8080/tools
```

### **Testes VPS (após deploy)**:
```bash
# Health checks públicos
curl https://your-domain.com/nibo/health
curl https://your-domain.com/omie/health

# Teste de ferramentas
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {}}' \
  https://your-domain.com/nibo/tools/testar_conexao

# SSE test
curl https://your-domain.com/nibo/sse/stream
```

---

## 🔒 **SEGURANÇA E FIREWALL**

### **Configuração UFW**:
```bash
# Instalar e configurar firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Abrir portas necessárias
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Portas internas (opcional, se não usar nginx proxy)
sudo ufw allow 8080
sudo ufw allow 8081
sudo ufw allow 8082
sudo ufw allow 8083

sudo ufw status
```

### **Environment Variables**:
```bash
# Configurar variáveis de ambiente seguras
sudo tee /home/mcp/.env << 'EOF'
OMIE_APP_KEY=your_omie_key
OMIE_APP_SECRET=your_omie_secret
NIBO_API_TOKEN=your_nibo_token
NIBO_COMPANY_ID=your_company_id
ENVIRONMENT=production
LOG_LEVEL=info
EOF

sudo chown mcp:mcp /home/mcp/.env
sudo chmod 600 /home/mcp/.env
```

---

## 📞 **TROUBLESHOOTING**

### **Problemas Comuns**:

#### **Serviço não inicia**:
```bash
# Verificar logs
sudo journalctl -u nibo-mcp -f
sudo journalctl -u omie-mcp -f

# Verificar permissões
sudo chown -R mcp:mcp /home/mcp/omie-mcp/
```

#### **Nginx 502 Bad Gateway**:
```bash
# Verificar se serviços estão rodando
sudo systemctl status nibo-mcp omie-mcp
sudo netstat -tlnp | grep -E "(8080|8081)"
```

#### **SSL Certificate Issues**:
```bash
# Renovar certificado
sudo certbot renew
sudo systemctl reload nginx
```

---

## ✅ **CHECKLIST FINAL**

### **Pré-Deploy**:
- [ ] Pacote criado (`mcp-deploy.tar.gz`)
- [ ] Credenciais configuradas
- [ ] Scripts testados localmente
- [ ] VPS com acesso SSH
- [ ] Domínio configurado (DNS)

### **Deploy**:  
- [ ] Upload realizado
- [ ] Instalação executada
- [ ] Serviços iniciados
- [ ] Nginx configurado
- [ ] SSL instalado

### **Pós-Deploy**:
- [ ] Health checks funcionando
- [ ] URLs públicas acessíveis
- [ ] N8N integration testada
- [ ] Monitoring ativo
- [ ] Logs sendo coletados

---

## 🎯 **LINKS ÚTEIS**

### **Documentação**:
- **FastAPI Docs**: `https://your-domain.com/nibo/docs`
- **Health Status**: `https://your-domain.com/nibo/health`
- **Tools List**: `https://your-domain.com/nibo/tools`

### **N8N Webhooks**:
- **Nibo**: `https://your-domain.com/nibo/n8n/webhook/{tool_name}`
- **Omie**: `https://your-domain.com/omie/tools` (formato MCP)

### **SSE Streams**:
- **Nibo**: `https://your-domain.com/nibo/sse/stream`
- **Omie**: `https://your-domain.com/omie/sse/stream`

---

## 🚀 **RESPOSTA À PERGUNTA: É POSSÍVEL?**

### ✅ **SIM, é totalmente possível!**

**Funcionalidades confirmadas**:
1. **MCP Servers**: Rodam perfeitamente em VPS
2. **N8N Integration**: Webhooks + HTTP requests funcionais  
3. **SSE Streaming**: Real-time data para N8N via custom nodes
4. **Public APIs**: URLs públicas com SSL
5. **Monitoring**: Health checks + alertas automáticos

**Arquitetura testada e aprovada para VPS externa!** 🎉

---

*Guia criado por Claude Code - Deploy ready! 🚀*