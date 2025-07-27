# 🚀 UPTAX - Guia Completo Azure VPS Setup

> **Setup completo da infraestrutura UPTAX no Azure para homologação**

---

## 🎯 **ESPECIFICAÇÕES VPS RECOMENDADAS**

### **💰 Configuração Custo-Benefício**
```
Tipo: Azure VM Standard B2s
├── CPU: 2 vCPUs
├── RAM: 4GB  
├── Storage: 50GB SSD Premium
├── Network: Standard LB
├── OS: Ubuntu 20.04 LTS
└── Custo estimado: $25-35/mês
```

### **🔧 Portas Necessárias**
```
Inbound Security Rules:
├── SSH: 22 (administração)
├── HTTP: 80 (web access)
├── HTTPS: 443 (secure web)
├── N8N: 5679 (automation)
├── Omie-MCP: 8083 (ERP integration)
├── Nibo-MCP: 8084 (fiscal integration)
└── Monitoring: 8081 (dashboard)
```

---

## 📋 **PASSO A PASSO AZURE PORTAL**

### **STEP 1: Criar Resource Group**
```bash
# No Azure Portal:
1. Resource Groups → Create
2. Name: "uptax-homologation-rg"  
3. Region: "Brazil South" (São Paulo)
4. Click: Create
```

### **STEP 2: Criar Virtual Machine**
```bash
# Azure Portal → Virtual Machines → Create:

BASICS:
├── Resource Group: uptax-homologation-rg
├── VM Name: uptax-homologation-vm
├── Region: Brazil South
├── Image: Ubuntu Server 20.04 LTS - Gen2
├── Size: Standard_B2s (2 vcpus, 4 GiB memory)
├── Authentication: SSH public key
├── Username: uptaxadmin
└── SSH Key: Generate new key pair

DISKS:
├── OS Disk Type: Premium SSD
└── Size: 50GB

NETWORKING:
├── Virtual Network: Create new (uptax-vnet)
├── Subnet: default (10.0.0.0/24)  
├── Public IP: Create new (uptax-public-ip)
├── NIC Security Group: Advanced
└── Configure NSG: Create new
```

### **STEP 3: Configurar Network Security Group**
```bash
# NSG Inbound Rules (Add these):

Rule 1: SSH
├── Source: Any
├── Source port ranges: *
├── Destination: Any  
├── Destination port ranges: 22
├── Protocol: TCP
└── Action: Allow

Rule 2: HTTP
├── Source: Any
├── Destination port ranges: 80
├── Protocol: TCP
└── Action: Allow

Rule 3: HTTPS  
├── Source: Any
├── Destination port ranges: 443
├── Protocol: TCP
└── Action: Allow

Rule 4: N8N
├── Source: Any
├── Destination port ranges: 5679
├── Protocol: TCP
└── Action: Allow

Rule 5: Omie-MCP
├── Source: Any
├── Destination port ranges: 8083
├── Protocol: TCP
└── Action: Allow

Rule 6: Nibo-MCP
├── Source: Any
├── Destination port ranges: 8084
├── Protocol: TCP
└── Action: Allow

Rule 7: Monitoring Dashboard
├── Source: Any
├── Destination port ranges: 8081
├── Protocol: TCP
└── Action: Allow
```

### **STEP 4: Download SSH Key**
```bash
# Azure irá gerar e baixar:
# uptax-homologation-vm_key.pem

# No seu Mac, mover para local seguro:
mkdir ~/.ssh/azure
mv ~/Downloads/uptax-homologation-vm_key.pem ~/.ssh/azure/
chmod 600 ~/.ssh/azure/uptax-homologation-vm_key.pem
```

---

## 🔐 **CONECTAR NO VPS**

### **Obter IP Público**
```bash
# No Azure Portal:
# VM → Overview → Public IP address
# Exemplo: 191.232.123.45
```

### **Conectar via SSH**
```bash
# Do seu Mac:
ssh -i ~/.ssh/azure/uptax-homologation-vm_key.pem uptaxadmin@[SEU_IP_PUBLICO]

# Exemplo:
ssh -i ~/.ssh/azure/uptax-homologation-vm_key.pem uptaxadmin@191.232.123.45
```

---

## ⚙️ **SETUP INICIAL DO SERVIDOR**

### **Update Sistema**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip
```

### **Instalar Docker**
```bash
# Adicionar repositório Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Adicionar usuário ao grupo docker
sudo usermod -aG docker uptaxadmin

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar para aplicar mudanças
sudo reboot
```

### **Instalar Node.js e Python**
```bash
# Conectar novamente após reboot
ssh -i ~/.ssh/azure/uptax-homologation-vm_key.pem uptaxadmin@[SEU_IP_PUBLICO]

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar Python dependencies
sudo apt install -y python3 python3-pip
pip3 install --upgrade pip
```

---

## 📁 **TRANSFER ARQUIVOS UPTAX**

### **Preparar arquivos no Mac**
```bash
# No seu Mac, criar pacote de deploy:
cd /Users/kleberdossantosribeiro/uptaxdev

# Criar pacote compacto
tar -czf uptax-deploy.tar.gz \
  docker-compose.*.yml \
  *.py \
  *.sh \
  *.md \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc'
```

### **Transferir para Azure VPS**
```bash
# Upload via SCP
scp -i ~/.ssh/azure/uptax-homologation-vm_key.pem \
  uptax-deploy.tar.gz \
  uptaxadmin@[SEU_IP_PUBLICO]:~/

# Credentials (CUIDADO - arquivo sensível)
scp -i ~/.ssh/azure/uptax-homologation-vm_key.pem \
  credentials.json \
  uptaxadmin@[SEU_IP_PUBLICO]:~/
```

### **Extrair no VPS**
```bash
# No VPS:
cd ~
tar -xzf uptax-deploy.tar.gz
ls -la

# Configurar permissions
chmod +x *.sh
```

---

## 🚀 **INICIAR SERVIÇOS UPTAX**

### **Configurar Environment**
```bash
# Criar .env com suas credenciais
cat > .env << EOF
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# N8N
N8N_BASIC_AUTH_ACTIVE=false
N8N_HOST=0.0.0.0
N8N_PORT=5679

# MCP Servers
OMIE_APP_KEY=your_omie_key
OMIE_APP_SECRET=your_omie_secret
NIBO_CLIENT_ID=your_nibo_client_id
NIBO_CLIENT_SECRET=your_nibo_secret
EOF
```

### **Iniciar Docker Compose**
```bash
# Verificar Docker funcionando
docker --version
docker-compose --version

# Iniciar serviços
docker-compose -f docker-compose.n8n-dev.yml up -d

# Verificar status
docker ps
```

### **Testar Conectividade**
```bash
# Testar portas localmente
curl http://localhost:5679/healthz    # N8N
curl http://localhost:8083/health     # Omie-MCP
curl http://localhost:8084/health     # Nibo-MCP

# Testar do exterior (seu Mac)
curl http://[SEU_IP_PUBLICO]:5679/healthz
```

---

## 📊 **MONITORAMENTO**

### **Sistema**
```bash
# Resources usage
htop
df -h
free -h

# Docker status
docker stats
docker logs [container_name]
```

### **Services Health**
```bash
# Criar script de monitoring
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "🎯 UPTAX Azure VPS Status"
echo "========================"
echo "⏰ $(date)"
echo ""

echo "📊 SISTEMA:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk: $(df -h / | awk 'NR==2{printf "%s", $5}')"
echo ""

echo "🐳 DOCKER CONTAINERS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "📋 SERVICES HEALTH:"
curl -s http://localhost:5679/healthz > /dev/null && echo "✅ N8N: OK" || echo "❌ N8N: FAIL"
curl -s http://localhost:8083/health > /dev/null && echo "✅ Omie-MCP: OK" || echo "❌ Omie-MCP: FAIL"  
curl -s http://localhost:8084/health > /dev/null && echo "✅ Nibo-MCP: OK" || echo "❌ Nibo-MCP: FAIL"
EOF

chmod +x monitor.sh
./monitor.sh
```

---

## 🔧 **CONFIGURAÇÕES ESPECÍFICAS**

### **Firewall Ubuntu (ufw)**
```bash
# Configurar firewall interno
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5679/tcp  # N8N
sudo ufw allow 8083/tcp  # Omie-MCP
sudo ufw allow 8084/tcp  # Nibo-MCP
sudo ufw allow 8081/tcp  # Monitoring

sudo ufw --force enable
sudo ufw status
```

### **Backup Automático**
```bash
# Script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/uptaxadmin/backups"

mkdir -p $BACKUP_DIR

# Backup containers data
docker-compose -f docker-compose.n8n-dev.yml down
tar -czf $BACKUP_DIR/uptax_backup_$DATE.tar.gz \
  docker-compose.*.yml \
  .env \
  *.py \
  *.sh \
  /var/lib/docker/volumes

docker-compose -f docker-compose.n8n-dev.yml up -d

echo "✅ Backup created: uptax_backup_$DATE.tar.gz"
EOF

chmod +x backup.sh
```

---

## 📞 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **Docker não funciona**
```bash
# Verificar service
sudo systemctl status docker
sudo systemctl start docker

# Verificar permissions
sudo usermod -aG docker $USER
logout # e login novamente
```

#### **Portas bloqueadas**
```bash
# Verificar Azure NSG rules
# Verificar Ubuntu ufw
sudo ufw status

# Testar conectividade
telnet [SEU_IP_PUBLICO] 5679
```

#### **Containers não iniciam**
```bash
# Verificar logs
docker logs [container_name]

# Verificar resources
free -h
df -h

# Restart containers
docker-compose down
docker-compose up -d
```

---

## 💰 **GESTÃO DE CUSTOS**

### **Otimização Azure**
```bash
# Configurar auto-shutdown (economizar $$)
# Azure Portal → VM → Auto-shutdown
# Schedule: 23:00 UTC-3 (2AM local)
# Notification: Yes
```

### **Monitoring Costs**
```bash
# Azure Portal → Cost Management
# Set budget alerts: $50/month
# Daily cost tracking
```

---

## ✅ **CHECKLIST FINAL**

```
PREPARAÇÃO:
□ Resource Group criado
□ VM Standard_B2s provisionada  
□ NSG rules configuradas
□ SSH key baixada

SETUP:
□ Conectado via SSH
□ Sistema atualizado
□ Docker instalado
□ Node.js/Python instalados

DEPLOY:
□ Arquivos UPTAX transferidos
□ Environment configurado
□ Services iniciados
□ Health checks OK

PRODUÇÃO:
□ Monitoring ativo
□ Backup configurado
□ Firewall habilitado
□ Costs monitoring ativo
```

---

**🎯 PRÓXIMOS PASSOS**
1. Criar VM no Azure Portal
2. Conectar via SSH  
3. Executar setup scripts
4. Deploy UPTAX services
5. Iniciar homologação

**Tempo estimado: 2-3 horas para setup completo**