# 🛡️ Políticas de Governança Distribuída - MCP Servers

## 📋 Visão Geral

O modelo de servidores MCP distribuídos permite implementar políticas independentes para cada ERP, aumentando **controle**, **segurança**, **monitoramento** e **suporte**.

## 🔐 Políticas de Segurança

### **1. Autenticação Independente**

```yaml
# erp-mcp-ecosystem/omie-mcp/config/security.yaml
security:
  authentication:
    type: "token_based"
    token_rotation: "24h"
    max_failures: 3
    lockout_duration: "15m"
    encryption: "AES-256"
  
  authorization:
    rbac_enabled: true
    default_role: "readonly"
    admin_approval: true
  
  audit:
    log_all_requests: true
    log_sensitive_data: false
    retention_days: 90
```

### **2. Isolamento de Credenciais**

```python
# common/auth/secure_credentials.py
import os
from cryptography.fernet import Fernet
from typing import Dict, Any

class SecureCredentialStore:
    """Armazenamento seguro de credenciais por ERP"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.key_file = f"/secure/keys/{erp_name}_key.key"
        self.credentials_file = f"/secure/credentials/{erp_name}_creds.enc"
        self.cipher = self.load_cipher()
    
    def store_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Armazena credenciais criptografadas"""
        try:
            encrypted_data = self.cipher.encrypt(
                json.dumps(credentials).encode()
            )
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Log de auditoria (sem dados sensíveis)
            self.audit_log(f"Credentials stored for {self.erp_name}")
            return True
            
        except Exception as e:
            self.audit_log(f"Failed to store credentials: {str(e)}")
            return False
    
    def audit_log(self, message: str) -> None:
        """Log de auditoria de segurança"""
        timestamp = datetime.now().isoformat()
        with open(f"/var/log/security/{self.erp_name}_security.log", 'a') as f:
            f.write(f"{timestamp} - {message}\n")
```

### **3. Controle de Acesso Granular**

```python
# common/auth/rbac.py
from enum import Enum
from typing import Set, Dict, Any

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class Role(Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"

class RBACManager:
    """Controle de acesso baseado em papéis"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.role_permissions = {
            Role.VIEWER: {Permission.READ},
            Role.OPERATOR: {Permission.READ, Permission.WRITE},
            Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN}
        }
    
    def check_permission(self, user_role: Role, required_permission: Permission) -> bool:
        """Verifica se usuário tem permissão"""
        user_permissions = self.role_permissions.get(user_role, set())
        has_permission = required_permission in user_permissions
        
        # Log de auditoria
        self.audit_access(user_role, required_permission, has_permission)
        
        return has_permission
    
    def audit_access(self, role: Role, permission: Permission, granted: bool) -> None:
        """Log de auditoria de acesso"""
        timestamp = datetime.now().isoformat()
        status = "GRANTED" if granted else "DENIED"
        
        with open(f"/var/log/access/{self.erp_name}_access.log", 'a') as f:
            f.write(f"{timestamp} - {status} - {role.value} - {permission.value}\n")
```

## 🏗️ Políticas de Criação

### **1. Template Padronizado**

```python
# scripts/create_erp_server.py
import os
import shutil
from typing import Dict, Any

class ERPServerGenerator:
    """Gerador de servidores MCP para novos ERPs"""
    
    def __init__(self, template_path: str = "templates/erp-server"):
        self.template_path = template_path
        
    def create_server(self, erp_config: Dict[str, Any]) -> bool:
        """Cria novo servidor MCP a partir do template"""
        
        erp_name = erp_config['name'].lower()
        server_path = f"erp-mcp-ecosystem/{erp_name}-mcp"
        
        # 1. Copiar template
        shutil.copytree(self.template_path, server_path)
        
        # 2. Personalizar configurações
        self.customize_config(server_path, erp_config)
        
        # 3. Gerar ferramentas base
        self.generate_tools(server_path, erp_config)
        
        # 4. Configurar autenticação
        self.setup_authentication(server_path, erp_config)
        
        # 5. Configurar testes
        self.setup_tests(server_path, erp_config)
        
        # 6. Configurar deploy
        self.setup_deployment(server_path, erp_config)
        
        return True
        
    def customize_config(self, server_path: str, config: Dict[str, Any]) -> None:
        """Personaliza configurações do servidor"""
        
        # Substituir placeholders no template
        config_file = f"{server_path}/config/server_config.py"
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        content = content.replace("{{ERP_NAME}}", config['name'])
        content = content.replace("{{ERP_URL}}", config['api_url'])
        content = content.replace("{{AUTH_TYPE}}", config['auth_type'])
        
        with open(config_file, 'w') as f:
            f.write(content)
```

### **2. Validação de Padrões**

```python
# scripts/validate_server.py
import json
import os
from typing import List, Dict, Any

class ServerValidator:
    """Valida conformidade com padrões estabelecidos"""
    
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.errors = []
        self.warnings = []
    
    def validate_structure(self) -> bool:
        """Valida estrutura de diretórios"""
        required_dirs = [
            "client", "tools", "config", "tests"
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(f"{self.server_path}/{dir_name}"):
                self.errors.append(f"Missing required directory: {dir_name}")
        
        return len(self.errors) == 0
    
    def validate_naming_convention(self) -> bool:
        """Valida convenções de nomenclatura"""
        # Verificar se todas as ferramentas seguem padrão universal
        tools_file = f"{self.server_path}/tools/__init__.py"
        
        with open(tools_file, 'r') as f:
            content = f.read()
        
        # Verificar padrões de nomenclatura
        invalid_patterns = ["camelCase", "PascalCase"]
        
        for pattern in invalid_patterns:
            if pattern in content:
                self.warnings.append(f"Inconsistent naming pattern: {pattern}")
        
        return len(self.warnings) == 0
    
    def validate_security(self) -> bool:
        """Valida configurações de segurança"""
        security_file = f"{self.server_path}/config/security.yaml"
        
        if not os.path.exists(security_file):
            self.errors.append("Missing security configuration")
            return False
        
        with open(security_file, 'r') as f:
            security_config = yaml.safe_load(f)
        
        # Verificar configurações obrigatórias
        required_security = [
            "authentication", "authorization", "audit"
        ]
        
        for req in required_security:
            if req not in security_config:
                self.errors.append(f"Missing security config: {req}")
        
        return len(self.errors) == 0
```

## 🔍 Políticas de Monitoramento

### **1. Métricas Específicas por ERP**

```python
# common/monitoring/metrics.py
import time
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ERPMetrics:
    """Métricas específicas por ERP"""
    erp_name: str
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    avg_response_time: float = 0.0
    active_connections: int = 0
    rate_limit_hits: int = 0
    
class MetricsCollector:
    """Coletor de métricas por ERP"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.metrics = ERPMetrics(erp_name)
        self.response_times = []
        
    def record_request(self, success: bool, response_time: float) -> None:
        """Registra métrica de requisição"""
        self.metrics.requests_total += 1
        
        if success:
            self.metrics.requests_success += 1
        else:
            self.metrics.requests_failed += 1
        
        self.response_times.append(response_time)
        self.metrics.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Enviar para sistema de monitoramento
        self.send_to_monitoring_system()
    
    def send_to_monitoring_system(self) -> None:
        """Envia métricas para sistema de monitoramento"""
        # Integração com Prometheus, Grafana, etc.
        pass
```

### **2. Alertas Configuráveis**

```yaml
# erp-mcp-ecosystem/omie-mcp/config/alerts.yaml
alerts:
  response_time:
    threshold: 2.0  # segundos
    severity: "warning"
    
  error_rate:
    threshold: 0.05  # 5%
    severity: "critical"
    
  rate_limit:
    threshold: 10  # hits por minuto
    severity: "warning"
    
  authentication_failures:
    threshold: 5  # falhas consecutivas
    severity: "critical"
    
  disk_space:
    threshold: 0.90  # 90%
    severity: "warning"
    
notifications:
  - type: "email"
    recipients: ["admin@uptax.com"]
    severity: ["critical"]
    
  - type: "slack"
    webhook: "https://hooks.slack.com/..."
    severity: ["warning", "critical"]
```

## 🧪 Políticas de Testes

### **1. Testes Automatizados por ERP**

```python
# tests/test_framework.py
import pytest
import asyncio
from typing import Dict, Any, List

class ERPTestFramework:
    """Framework de testes específico por ERP"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.test_results = []
        
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Executa testes de integração"""
        
        test_suite = [
            self.test_authentication,
            self.test_basic_operations,
            self.test_error_handling,
            self.test_rate_limiting,
            self.test_data_validation
        ]
        
        results = {}
        
        for test in test_suite:
            try:
                result = await test()
                results[test.__name__] = {
                    "status": "passed",
                    "result": result
                }
            except Exception as e:
                results[test.__name__] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    async def test_authentication(self) -> Dict[str, Any]:
        """Testa autenticação"""
        # Implementar testes específicos de autenticação
        pass
    
    async def test_basic_operations(self) -> Dict[str, Any]:
        """Testa operações básicas CRUD"""
        # Implementar testes de operações básicas
        pass
```

### **2. Testes de Carga Específicos**

```python
# tests/load_testing.py
import asyncio
import aiohttp
from typing import Dict, Any

class LoadTester:
    """Testes de carga específicos por ERP"""
    
    def __init__(self, erp_name: str, base_url: str):
        self.erp_name = erp_name
        self.base_url = base_url
        
    async def run_load_test(self, concurrent_users: int = 100, duration: int = 60) -> Dict[str, Any]:
        """Executa teste de carga"""
        
        start_time = time.time()
        tasks = []
        
        # Criar usuários simulados
        for i in range(concurrent_users):
            task = asyncio.create_task(self.simulate_user_activity())
            tasks.append(task)
        
        # Executar por duração especificada
        await asyncio.sleep(duration)
        
        # Cancelar tarefas
        for task in tasks:
            task.cancel()
        
        # Coletar resultados
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.analyze_results(results, duration)
```

## 🚀 Políticas de Deploy

### **1. Pipeline de Deploy Independente**

```yaml
# .github/workflows/deploy-omie.yml
name: Deploy Omie MCP Server

on:
  push:
    paths:
      - 'omie-mcp/**'
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Tests
        run: |
          cd omie-mcp
          python -m pytest tests/
          
      - name: Security Scan
        run: |
          cd omie-mcp
          bandit -r . -f json -o security-report.json
          
      - name: Validate Configuration
        run: |
          cd omie-mcp
          python scripts/validate_config.py
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Deploy to Production
        run: |
          docker build -t omie-mcp:${{ github.sha }} .
          docker tag omie-mcp:${{ github.sha }} omie-mcp:latest
          docker push omie-mcp:latest
          
      - name: Health Check
        run: |
          sleep 30
          curl -f http://omie-mcp.production.uptax.com/health
```

### **2. Rollback Automático**

```python
# scripts/deploy_manager.py
import docker
import time
from typing import Dict, Any

class DeployManager:
    """Gerenciador de deploy com rollback automático"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.docker_client = docker.from_env()
        
    def deploy(self, image_tag: str) -> bool:
        """Deploy com health check e rollback automático"""
        
        try:
            # 1. Backup da versão atual
            current_container = self.get_current_container()
            backup_image = f"{self.erp_name}-mcp:backup-{int(time.time())}"
            
            if current_container:
                current_container.commit(backup_image)
            
            # 2. Deploy nova versão
            new_container = self.docker_client.containers.run(
                f"{self.erp_name}-mcp:{image_tag}",
                detach=True,
                name=f"{self.erp_name}-mcp-new"
            )
            
            # 3. Health check
            if self.health_check(new_container):
                # Sucesso: trocar containers
                if current_container:
                    current_container.stop()
                    current_container.remove()
                
                new_container.rename(f"{self.erp_name}-mcp")
                return True
            else:
                # Falha: rollback
                new_container.stop()
                new_container.remove()
                self.rollback(backup_image)
                return False
                
        except Exception as e:
            self.log_error(f"Deploy failed: {str(e)}")
            return False
    
    def health_check(self, container) -> bool:
        """Verifica saúde do container"""
        max_attempts = 30
        
        for attempt in range(max_attempts):
            try:
                # Verificar se container está rodando
                container.reload()
                if container.status != 'running':
                    return False
                
                # Verificar endpoint de health
                response = requests.get(f"http://localhost:8080/health")
                if response.status_code == 200:
                    return True
                    
            except Exception:
                pass
            
            time.sleep(2)
        
        return False
```

## 📊 Ambiente de Produção

### **1. Isolamento de Recursos**

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  omie-mcp:
    image: omie-mcp:latest
    container_name: omie-mcp-prod
    restart: unless-stopped
    
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
    
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - MAX_CONNECTIONS=100
      
    volumes:
      - ./logs/omie:/var/log/omie
      - ./config/omie:/etc/omie
      
    networks:
      - omie-network
      
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      
  nibo-mcp:
    image: nibo-mcp:latest
    container_name: nibo-mcp-prod
    restart: unless-stopped
    
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
    
    networks:
      - nibo-network

networks:
  omie-network:
    driver: bridge
  nibo-network:
    driver: bridge
```

### **2. Backup e Recuperação**

```python
# scripts/backup_manager.py
import shutil
import os
from datetime import datetime, timedelta

class BackupManager:
    """Gerenciador de backup por ERP"""
    
    def __init__(self, erp_name: str):
        self.erp_name = erp_name
        self.backup_path = f"/backups/{erp_name}"
        
    def create_backup(self) -> str:
        """Cria backup completo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.erp_name}_{timestamp}"
        backup_full_path = f"{self.backup_path}/{backup_name}"
        
        # Backup de arquivos
        shutil.copytree(f"/app/{self.erp_name}-mcp", backup_full_path)
        
        # Backup de configurações
        shutil.copytree(f"/etc/{self.erp_name}", f"{backup_full_path}/config")
        
        # Backup de logs
        shutil.copytree(f"/var/log/{self.erp_name}", f"{backup_full_path}/logs")
        
        return backup_name
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restaura backup"""
        backup_full_path = f"{self.backup_path}/{backup_name}"
        
        if not os.path.exists(backup_full_path):
            return False
        
        # Parar serviço
        os.system(f"docker stop {self.erp_name}-mcp")
        
        # Restaurar arquivos
        shutil.rmtree(f"/app/{self.erp_name}-mcp")
        shutil.copytree(backup_full_path, f"/app/{self.erp_name}-mcp")
        
        # Reiniciar serviço
        os.system(f"docker start {self.erp_name}-mcp")
        
        return True
    
    def cleanup_old_backups(self, retention_days: int = 30) -> None:
        """Remove backups antigos"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for backup in os.listdir(self.backup_path):
            backup_path = os.path.join(self.backup_path, backup)
            backup_time = os.path.getctime(backup_path)
            
            if datetime.fromtimestamp(backup_time) < cutoff_date:
                shutil.rmtree(backup_path)
```

## 🎯 Benefícios da Governança Distribuída

### **1. Controle Granular**
- ✅ Políticas específicas por ERP
- ✅ Configurações independentes
- ✅ Versionamento isolado

### **2. Segurança Aprimorada**
- ✅ Isolamento de credenciais
- ✅ Controle de acesso específico
- ✅ Auditoria detalhada

### **3. Monitoramento Eficiente**
- ✅ Métricas específicas
- ✅ Alertas configuráveis
- ✅ Troubleshooting isolado

### **4. Suporte Especializado**
- ✅ Logs específicos por ERP
- ✅ Equipes especializadas
- ✅ Resolução rápida de problemas

---

**Esta estrutura de governança distribuída garante máxima flexibilidade, segurança e controle para o ecossistema de MCP servers.**