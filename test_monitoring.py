#!/usr/bin/env python3
"""
Teste do Sistema de Monitoramento Ciclo C
"""

import asyncio
import json
import psutil
from datetime import datetime

def test_system_metrics():
    """Testa coleta de métricas básicas"""
    print("📊 Testando coleta de métricas...")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"   CPU: {cpu_percent}%")
    
    # Memória
    memory = psutil.virtual_memory()
    print(f"   Memória: {memory.percent}% ({memory.available / (1024**3):.1f}GB disponível)")
    
    # Disco
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    print(f"   Disco: {disk_percent:.1f}% ({disk.free / (1024**3):.1f}GB livre)")
    
    # Conexões
    connections = len(psutil.net_connections(kind='inet'))
    print(f"   Conexões ativas: {connections}")
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk_percent,
        "connections": connections,
        "timestamp": datetime.now().isoformat()
    }

def test_health_checks():
    """Testa health checks do sistema"""
    print("🏥 Testando health checks...")
    
    health = {"checks": {}, "timestamp": datetime.now().isoformat()}
    
    # 1. Recursos do sistema
    cpu_ok = psutil.cpu_percent(interval=1) < 80
    memory_ok = psutil.virtual_memory().percent < 85
    disk_ok = (psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100) < 90
    
    health["checks"]["system_resources"] = {
        "cpu_ok": cpu_ok,
        "memory_ok": memory_ok,
        "disk_ok": disk_ok,
        "overall_ok": cpu_ok and memory_ok and disk_ok
    }
    
    print(f"   CPU OK: {cpu_ok}")
    print(f"   Memória OK: {memory_ok}")
    print(f"   Disco OK: {disk_ok}")
    
    # 2. Processos MCP
    mcp_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('mcp' in str(arg).lower() for arg in proc.info['cmdline']):
                mcp_processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    health["checks"]["mcp_processes"] = {
        "count": len(mcp_processes),
        "found": len(mcp_processes) > 0
    }
    
    print(f"   Processos MCP encontrados: {len(mcp_processes)}")
    
    # Status geral
    overall_healthy = (
        health["checks"]["system_resources"]["overall_ok"] and
        health["checks"]["mcp_processes"]["found"]
    )
    
    health["overall_status"] = "healthy" if overall_healthy else "warning"
    print(f"   Status geral: {health['overall_status']}")
    
    return health

def test_alerts():
    """Testa sistema de alertas"""
    print("🚨 Testando sistema de alertas...")
    
    # Thresholds
    thresholds = {
        "cpu_percent": 80,
        "memory_percent": 85,
        "disk_percent": 90
    }
    
    # Métricas atuais
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
    
    alerts = []
    
    if cpu > thresholds["cpu_percent"]:
        alerts.append({
            "type": "cpu_high",
            "severity": "warning",
            "value": cpu,
            "threshold": thresholds["cpu_percent"]
        })
    
    if memory > thresholds["memory_percent"]:
        alerts.append({
            "type": "memory_high",
            "severity": "warning",
            "value": memory,
            "threshold": thresholds["memory_percent"]
        })
    
    if disk > thresholds["disk_percent"]:
        alerts.append({
            "type": "disk_high",
            "severity": "critical",
            "value": disk,
            "threshold": thresholds["disk_percent"]
        })
    
    print(f"   Alertas ativos: {len(alerts)}")
    for alert in alerts:
        print(f"     ⚠️  {alert['type']}: {alert['value']:.1f}% (limite: {alert['threshold']}%)")
    
    if not alerts:
        print("   ✅ Nenhum alerta ativo - sistema OK")
    
    return {
        "alert_count": len(alerts),
        "alerts": alerts,
        "status": "critical" if any(a["severity"] == "critical" for a in alerts) else "warning" if alerts else "ok"
    }

def main():
    """
    Executa todos os testes do sistema de monitoramento
    """
    print("🚀 TESTE SISTEMA DE MONITORAMENTO - CICLO C FASE 1")
    print("=" * 60)
    
    try:
        # 1. Teste de métricas
        metrics = test_system_metrics()
        print("✅ Coleta de métricas: OK\n")
        
        # 2. Teste de health checks
        health = test_health_checks()
        print("✅ Health checks: OK\n")
        
        # 3. Teste de alertas
        alerts = test_alerts()
        print("✅ Sistema de alertas: OK\n")
        
        # Relatório resumido
        print("📊 RELATÓRIO RESUMIDO:")
        print("-" * 30)
        print(f"CPU: {metrics['cpu_percent']:.1f}%")
        print(f"Memória: {metrics['memory_percent']:.1f}%")
        print(f"Disco: {metrics['disk_percent']:.1f}%")
        print(f"Conexões: {metrics['connections']}")
        print(f"Status: {health['overall_status']}")
        print(f"Alertas: {alerts['alert_count']}")
        
        # Status final
        if health['overall_status'] == 'healthy' and alerts['status'] == 'ok':
            print("\n🎉 SISTEMA DE MONITORAMENTO: TOTALMENTE FUNCIONAL!")
        else:
            print("\n⚠️  SISTEMA DE MONITORAMENTO: OPERACIONAL COM AVISOS")
        
        print("\n📝 Próximos passos:")
        print("1. Integrar com FastMCP server")
        print("2. Criar interface web")
        print("3. Configurar notificações")
        print("4. Implementar métricas de negócio")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)