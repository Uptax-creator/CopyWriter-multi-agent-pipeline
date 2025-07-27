# 🔧 UPTAX - Guia Completo de Configuração MCP Servers

> **Documentação completa para configuração de todos os MCP servers da plataforma UPTAX**

---

## 🎯 **OVERVIEW DO SISTEMA MCP**

### **📊 MCP Servers Configurados**
```
UPTAX MCP ECOSYSTEM
├── 🗄️ Supabase MCP (Database & Vector)
├── 🔄 N8N MCP Standard (Automation)
├── 🤖 Senior Developer Agent MCP
├── 📚 Documentation Agent MCP
├── 🏗️ Infrastructure Agent MCP
└── 🎭 Agent Orchestrator MCP
```

### **🔐 Segurança e Boas Práticas**
- **Desenvolvimento Only**: Nunca conectar em produção
- **Read-Only Mode**: Sempre usar modo somente leitura quando possível
- **Project Scoped**: Limitar acesso a projetos específicos
- **Credential Management**: Usar unified credentials manager
- **Backup Configs**: Manter backups das configurações

---

## 🗄️ **SUPABASE MCP SERVER**

### **📋 Configuração Básica**

#### **🔑 1. Obter Credenciais**
```bash
# 1. Acesse Supabase Dashboard
# 2. Vá em Settings > API
# 3. Copie o Project Reference ID
# 4. Vá em Account > Access Tokens
# 5. Crie Personal Access Token
```

#### **⚙️ 2. Configuração Claude Desktop**
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=YOUR_PROJECT_REF"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "YOUR_PERSONAL_ACCESS_TOKEN"
      }
    }
  }
}
```

#### **🔒 3. Configuração Segura (Recomendada)**
```json
{
  "mcpServers": {
    "supabase-dev": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=${SUPABASE_PROJECT_REF}"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}",
        "SUPABASE_PROJECT_REF": "${SUPABASE_PROJECT_REF}"
      }
    }
  }
}
```

### **🛠️ Funcionalidades Disponíveis**
- **📊 Database Queries**: Consultas SQL no banco de dados
- **📋 Table Management**: Listar e inspecionar tabelas
- **🔍 Data Analysis**: Análise de dados e estruturas
- **📈 Metrics & Analytics**: Métricas de performance
- **🔐 Row Level Security**: Consultar políticas RLS

### **💡 Casos de Uso CEO**
```
"Quantos usuários temos ativo no sistema?"
"Qual o crescimento de receita nos últimos 3 meses?"
"Mostre a performance das integrações ERP"
"Analise os dados de uso do dashboard CEO"
```

---

## 🔄 **N8N MCP SERVER**

### **📋 Configuração N8N-DEV (Docker)**

#### **⚙️ 1. Configuração Claude Desktop**
```json
{
  "mcpServers": {
    "n8n-dev": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/n8n_mcp_server_standard.py"
      ],
      "env": {
        "N8N_API_KEY": "${N8N_DEV_API_KEY}",
        "N8N_BASE_URL": "http://localhost:5679",
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev",
        "PYTHONUNBUFFERED": "1"
      },
      "timeout": 30000,
      "restart": true
    }
  }
}
```

#### **🐳 2. Configuração Docker N8N**
```yaml
# docker-compose.n8n-dev.yml
version: '3.8'
services:
  n8n-dev:
    image: n8nio/n8n:latest
    container_name: n8n-dev
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_METRICS=true
      - WEBHOOK_URL=http://localhost:5679/
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
```

#### **🔧 3. Integração com Supabase**
```python
# n8n_supabase_integration.py
class N8NSupabaseIntegration:
    def __init__(self):
        self.n8n_client = N8NClient("http://localhost:5679")
        self.supabase_client = SupabaseClient()
    
    def create_data_sync_workflow(self):
        """Criar workflow para sincronizar dados N8N → Supabase"""
        workflow = {
            "name": "CEO Data Sync",
            "nodes": [
                {
                    "name": "Trigger",
                    "type": "n8n-nodes-base.cron",
                    "parameters": {"triggerTimes": {"hour": 8, "minute": 0}}
                },
                {
                    "name": "Get N8N Metrics",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"url": "http://localhost:5679/rest/executions"}
                },
                {
                    "name": "Store in Supabase",
                    "type": "n8n-nodes-base.supabase",
                    "parameters": {
                        "operation": "insert",
                        "table": "ceo_metrics"
                    }
                }
            ]
        }
        return self.n8n_client.create_workflow(workflow)
```

---

## 🤖 **AGENTS MCP SERVERS**

### **👨‍💻 Senior Developer Agent**
```json
{
  "mcpServers": {
    "senior-developer": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/senior_developer_agent_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev",
        "AGENT_MODE": "senior_developer",
        "LOG_LEVEL": "INFO"
      },
      "timeout": 60000,
      "restart": true
    }
  }
}
```

**Funcionalidades:**
- Consultas arquiteturais
- Code review automatizado
- Recomendações técnicas
- Análise de performance

### **📚 Documentation Agent**
```json
{
  "mcpServers": {
    "documentation": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/documentation_agent_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev",
        "DOCS_OUTPUT_PATH": "/Users/kleberdossantosribeiro/uptaxdev/docs",
        "AUTO_GENERATE": "true"
      },
      "timeout": 45000,
      "restart": true
    }
  }
}
```

**Funcionalidades:**
- Geração automática de documentação
- Atualização de README files
- API documentation
- Business case updates

### **🏗️ Infrastructure Agent**
```json
{
  "mcpServers": {
    "infrastructure": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/infrastructure_agent_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev",
        "DOCKER_HOST": "unix:///var/run/docker.sock",
        "MONITORING_ENABLED": "true"
      },
      "timeout": 30000,
      "restart": true
    }
  }
}
```

**Funcionalidades:**
- Health checks automatizados
- Docker management
- Performance monitoring
- System recovery

---

## 🔧 **CONFIGURAÇÃO UNIFICADA**

### **📄 Claude Desktop Config Completo**
```json
{
  "mcpServers": {
    "supabase-dev": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=${SUPABASE_PROJECT_REF}"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
      }
    },
    "n8n-dev": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/n8n_mcp_server_standard.py"
      ],
      "env": {
        "N8N_API_KEY": "${N8N_DEV_API_KEY}",
        "N8N_BASE_URL": "http://localhost:5679",
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev",
        "PYTHONUNBUFFERED": "1"
      },
      "timeout": 30000,
      "restart": true
    },
    "senior-developer": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/senior_developer_agent_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev"
      },
      "timeout": 60000,
      "restart": true
    },
    "infrastructure": {
      "command": "python3",
      "args": [
        "/Users/kleberdossantosribeiro/uptaxdev/infrastructure_agent_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/kleberdossantosribeiro/uptaxdev"
      },
      "timeout": 30000,
      "restart": true
    }
  }
}
```

---

## 🔐 **GERENCIAMENTO DE CREDENCIAIS**

### **📋 Unified Credentials Structure**
```json
{
  "version": "3.1_with_supabase",
  "description": "UPTAX Unified Credentials with Supabase MCP",
  "credentials": {
    "supabase": {
      "project_ref": "YOUR_PROJECT_REF_HERE",
      "access_token": "YOUR_PERSONAL_ACCESS_TOKEN",
      "database_url": "postgresql://postgres:[password]@db.[ref].supabase.co:6543/postgres",
      "anon_key": "YOUR_ANON_KEY",
      "service_role_key": "YOUR_SERVICE_ROLE_KEY"
    },
    "n8n": {
      "dev": {
        "url": "http://localhost:5679",
        "api_key": "YOUR_N8N_DEV_API_KEY",
        "webhook_url": "http://localhost:5679/webhook/"
      },
      "prod": {
        "url": "https://uptax-n8n.easypanel.host",
        "api_key": "YOUR_N8N_PROD_API_KEY",
        "webhook_url": "https://uptax-n8n.easypanel.host/webhook/"
      }
    },
    "openai": {
      "api_key": "YOUR_OPENAI_API_KEY",
      "organization": "YOUR_ORG_ID"
    }
  }
}
```

### **🔒 Script de Configuração Segura**
```python
#!/usr/bin/env python3
"""
Setup seguro das credenciais MCP
"""
import os
import json
from pathlib import Path

def setup_mcp_credentials():
    """Configure MCP credentials securely"""
    
    # Load unified credentials
    with open('credentials.json', 'r') as f:
        creds = json.load(f)
    
    # Set environment variables
    os.environ['SUPABASE_PROJECT_REF'] = creds['supabase']['project_ref']
    os.environ['SUPABASE_ACCESS_TOKEN'] = creds['supabase']['access_token']
    os.environ['N8N_DEV_API_KEY'] = creds['n8n']['dev']['api_key']
    
    # Update Claude Desktop config
    claude_config_path = Path.home() / 'Library/Application Support/Claude/claude_desktop_config.json'
    
    with open(claude_config_path, 'r') as f:
        claude_config = json.load(f)
    
    # Add Supabase MCP server
    claude_config['mcpServers']['supabase-dev'] = {
        "command": "npx",
        "args": [
            "-y",
            "@supabase/mcp-server-supabase@latest",
            "--read-only",
            f"--project-ref={creds['supabase']['project_ref']}"
        ],
        "env": {
            "SUPABASE_ACCESS_TOKEN": creds['supabase']['access_token']
        }
    }
    
    # Save updated config
    with open(claude_config_path, 'w') as f:
        json.dump(claude_config, f, indent=2)
    
    print("✅ MCP credentials configured successfully!")

if __name__ == "__main__":
    setup_mcp_credentials()
```

---

## 🧪 **TESTES E VALIDAÇÃO**

### **📊 Test Suite MCP Servers**
```python
#!/usr/bin/env python3
"""
Test all MCP server connections
"""
import asyncio
import json
import subprocess

async def test_mcp_servers():
    """Test all configured MCP servers"""
    
    servers = [
        "supabase-dev",
        "n8n-dev", 
        "senior-developer",
        "infrastructure"
    ]
    
    results = {}
    
    for server in servers:
        try:
            # Test server connection
            result = await test_server_connection(server)
            results[server] = {"status": "✅ Active", "response_time": result}
        except Exception as e:
            results[server] = {"status": "❌ Error", "error": str(e)}
    
    return results

def generate_test_report(results):
    """Generate MCP test report"""
    report = "# 🧪 MCP Servers Test Report\n\n"
    
    for server, result in results.items():
        report += f"## {server}\n"
        report += f"- **Status**: {result['status']}\n"
        if 'response_time' in result:
            report += f"- **Response Time**: {result['response_time']}ms\n"
        if 'error' in result:
            report += f"- **Error**: {result['error']}\n"
        report += "\n"
    
    return report

if __name__ == "__main__":
    results = asyncio.run(test_mcp_servers())
    report = generate_test_report(results)
    print(report)
```

---

## 🎯 **CASOS DE USO CEO**

### **🧠 Queries Inteligentes com Supabase + N8N**

#### **Análise de Performance**
```
CEO: "Como está a performance da plataforma hoje?"

Supabase MCP Response:
📊 Database Metrics:
- Active connections: 15/20
- Query response time: avg 45ms
- Table sizes: ceo_tasks (1.2k rows), metrics (5.8k rows)

N8N MCP Response:  
🔄 Automation Status:
- Active workflows: 8/10
- Success rate: 98.5% (last 24h)
- Failed executions: 2 (non-critical)
```

#### **Business Intelligence**
```
CEO: "Quantas tarefas foram criadas esta semana?"

Supabase Query via MCP:
SELECT COUNT(*) as task_count, 
       AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) as avg_completion_hours
FROM ceo_tasks 
WHERE created_at >= NOW() - INTERVAL '7 days';

Result: 23 tasks created, avg completion time 2.5 hours
```

### **🔄 Automação Inteligente**
```
CEO: "Crie um workflow para monitorar métricas semanais"

N8N MCP Response:
✅ Workflow created: "CEO Weekly Metrics"
- Trigger: Every Monday 8 AM
- Action 1: Query Supabase for weekly data
- Action 2: Generate executive summary
- Action 3: Send to CEO dashboard
- Status: Active and scheduled
```

---

## 🚀 **DEPLOYMENT E PRODUÇÃO**

### **📋 Checklist Pré-Deploy**
- [ ] ✅ Supabase MCP configurado e testado
- [ ] ✅ N8N-DEV funcionando com Docker
- [ ] ✅ Agents MCP ativos e responsivos
- [ ] ✅ Credentials unificadas e seguras
- [ ] ✅ Backup de configurações realizado
- [ ] ✅ Testes end-to-end executados
- [ ] ✅ Monitoring ativo em todos os servers

### **🔧 Comandos de Deploy**
```bash
# 1. Setup credentials
python3 setup_mcp_credentials.py

# 2. Start N8N Docker
docker-compose -f docker-compose.n8n-dev.yml up -d

# 3. Test all connections
python3 test_mcp_servers.py

# 4. Validate CEO workflows
python3 validate_ceo_workflows.py

# 5. Start monitoring
python3 monitoring_dashboard.py
```

---

## 📞 **SUPORTE E TROUBLESHOOTING**

### **🚨 Problemas Comuns**
1. **Supabase MCP não conecta**
   - Verificar project_ref e access_token
   - Confirmar permissões de leitura
   - Testar conectividade de rede

2. **N8N MCP timeout**
   - Verificar se Docker container está rodando
   - Confirmar porta 5679 disponível
   - Restart do container N8N

3. **Agents MCP não respondem**
   - Verificar PYTHONPATH configurado
   - Confirmar arquivos Python existem
   - Check logs do Claude Desktop

### **🔧 Comandos de Debug**
```bash
# Test Supabase connection
npx @supabase/mcp-server-supabase@latest --project-ref=YOUR_REF

# Test N8N Docker
docker logs n8n-dev

# Test Python agents
python3 -c "import sys; print(sys.path)"

# Claude Desktop logs
tail -f ~/Library/Logs/Claude/claude-desktop.log
```

---

**🔧 MCP SERVERS CONFIGURATION GUIDE**  
**Complete Setup for UPTAX AI-First Platform**  
**Ready for CEO Vertical Agent Integration**