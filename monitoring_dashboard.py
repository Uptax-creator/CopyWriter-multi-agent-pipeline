#!/usr/bin/env python3
"""
🔍 Dashboard de Monitoramento Avançado - Ciclo C Fase 1
Monitoramento em tempo real do sistema Omie FastMCP
"""

import asyncio
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastmcp import FastMCP
import httpx
from pathlib import Path

# Servidor de Monitoramento
monitoring = FastMCP("Omie Monitoring Dashboard 📊")

# Configurações
CONFIG = {
    "alert_thresholds": {
        "cpu_percent": 80,
        "memory_percent": 85,
        "disk_percent": 90,
        "response_time_ms": 5000
    },
    "check_interval": 30,  # segundos
    "history_retention": 24  # horas
}

# Armazenamento em memória para métricas históricas
metrics_history: List[Dict[str, Any]] = []

@monitoring.tool
async def get_system_metrics() -> str:
    """
    Coleta métricas completas do sistema em tempo real
    
    Returns:
        str: Métricas do sistema em formato JSON
    """
    try:
        # Métricas básicas do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Métricas de processo
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Conexões ativas
        connections = len(psutil.net_connections(kind='inet'))
        
        # Timestamp
        timestamp = datetime.now().isoformat()
        
        metrics = {
            "timestamp": timestamp,
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent,
                    "free_gb": round(memory.free / (1024**3), 2)
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": round((disk.used / disk.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "connections": connections
            },
            "process": {
                "memory_rss_mb": round(process_memory.rss / (1024**2), 2),
                "memory_vms_mb": round(process_memory.vms / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            },
            "alerts": await check_alerts(cpu_percent, memory.percent, disk.used/disk.total*100)
        }
        
        # Adicionar ao histórico
        global metrics_history
        metrics_history.append(metrics)
        
        # Manter apenas as últimas 24 horas
        cutoff_time = datetime.now() - timedelta(hours=CONFIG["history_retention"])
        metrics_history = [
            m for m in metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        return json.dumps(metrics, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"Erro ao coletar métricas: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

@monitoring.tool
async def health_check_complete() -> str:
    """
    Health check completo do sistema Omie FastMCP
    
    Returns:
        str: Status detalhado de saúde do sistema
    """
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {}
        }
        
        # 1. Teste de conectividade Omie API
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://app.omie.com.br/api/v1/")
                health_status["checks"]["omie_api"] = {
                    "status": "ok" if response.status_code < 400 else "error",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code
                }
        except Exception as e:
            health_status["checks"]["omie_api"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 2. Verificação de recursos do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        health_status["checks"]["system_resources"] = {
            "cpu_ok": cpu_percent < CONFIG["alert_thresholds"]["cpu_percent"],
            "memory_ok": memory_percent < CONFIG["alert_thresholds"]["memory_percent"],
            "disk_ok": disk_percent < CONFIG["alert_thresholds"]["disk_percent"],
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent
        }
        
        # 3. Verificação de arquivos críticos
        critical_files = [
            "credentials.json",
            "omie_fastmcp_example.py",
            "claude_desktop_config_final.json"
        ]
        
        health_status["checks"]["critical_files"] = {}
        for file in critical_files:
            file_path = Path(file)
            health_status["checks"]["critical_files"][file] = {
                "exists": file_path.exists(),
                "size_bytes": file_path.stat().st_size if file_path.exists() else 0
            }
        
        # 4. Verificação de processos MCP
        mcp_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('mcp' in str(arg).lower() for arg in proc.info['cmdline']):
                    mcp_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": " ".join(proc.info['cmdline'][:3])  # Primeiros 3 args
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        health_status["checks"]["mcp_processes"] = {
            "count": len(mcp_processes),
            "processes": mcp_processes
        }
        
        # Determinar status geral
        all_checks_ok = (
            health_status["checks"]["omie_api"].get("status") == "ok" and
            health_status["checks"]["system_resources"]["cpu_ok"] and
            health_status["checks"]["system_resources"]["memory_ok"] and
            health_status["checks"]["system_resources"]["disk_ok"] and
            len(mcp_processes) > 0
        )
        
        health_status["overall_status"] = "healthy" if all_checks_ok else "warning"
        
        return json.dumps(health_status, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"Erro no health check: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error"
        }, indent=2)

@monitoring.tool
async def get_metrics_history(hours: int = 1) -> str:
    """
    Retorna histórico de métricas para análise de tendências
    
    Args:
        hours: Número de horas de histórico a retornar
        
    Returns:
        str: Histórico de métricas em formato JSON
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_history = [
            m for m in metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # Estatísticas resumidas
        if filtered_history:
            cpu_values = [m["system"]["cpu_percent"] for m in filtered_history]
            memory_values = [m["system"]["memory"]["percent_used"] for m in filtered_history]
            
            summary = {
                "period_hours": hours,
                "data_points": len(filtered_history),
                "summary_stats": {
                    "cpu": {
                        "avg": round(sum(cpu_values) / len(cpu_values), 2),
                        "max": max(cpu_values),
                        "min": min(cpu_values)
                    },
                    "memory": {
                        "avg": round(sum(memory_values) / len(memory_values), 2),
                        "max": max(memory_values),
                        "min": min(memory_values)
                    }
                },
                "data": filtered_history[-50:]  # Últimos 50 pontos para não sobrecarregar
            }
        else:
            summary = {
                "period_hours": hours,
                "data_points": 0,
                "message": "Nenhum dado disponível para o período solicitado",
                "data": []
            }
        
        return json.dumps(summary, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"Erro ao buscar histórico: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

async def check_alerts(cpu: float, memory: float, disk: float) -> List[Dict[str, Any]]:
    """
    Verifica condições de alerta baseadas nos thresholds configurados
    
    Args:
        cpu: Percentual de uso da CPU
        memory: Percentual de uso da memória
        disk: Percentual de uso do disco
        
    Returns:
        List[Dict]: Lista de alertas ativos
    """
    alerts = []
    thresholds = CONFIG["alert_thresholds"]
    
    if cpu > thresholds["cpu_percent"]:
        alerts.append({
            "type": "cpu_high",
            "severity": "warning",
            "message": f"CPU usage high: {cpu}% (threshold: {thresholds['cpu_percent']}%)",
            "value": cpu,
            "threshold": thresholds["cpu_percent"]
        })
    
    if memory > thresholds["memory_percent"]:
        alerts.append({
            "type": "memory_high",
            "severity": "warning",
            "message": f"Memory usage high: {memory}% (threshold: {thresholds['memory_percent']}%)",
            "value": memory,
            "threshold": thresholds["memory_percent"]
        })
    
    if disk > thresholds["disk_percent"]:
        alerts.append({
            "type": "disk_high",
            "severity": "critical",
            "message": f"Disk usage high: {disk}% (threshold: {thresholds['disk_percent']}%)",
            "value": disk,
            "threshold": thresholds["disk_percent"]
        })
    
    return alerts

@monitoring.tool
async def configure_alerts(
    cpu_threshold: int = 80,
    memory_threshold: int = 85,
    disk_threshold: int = 90,
    response_time_threshold: int = 5000
) -> str:
    """
    Configura thresholds para os alertas do sistema
    
    Args:
        cpu_threshold: Threshold CPU em %
        memory_threshold: Threshold memória em %
        disk_threshold: Threshold disco em %
        response_time_threshold: Threshold tempo resposta em ms
        
    Returns:
        str: Confirmação da configuração
    """
    global CONFIG
    
    CONFIG["alert_thresholds"] = {
        "cpu_percent": cpu_threshold,
        "memory_percent": memory_threshold,
        "disk_percent": disk_threshold,
        "response_time_ms": response_time_threshold
    }
    
    return json.dumps({
        "message": "Alert thresholds updated successfully",
        "new_config": CONFIG["alert_thresholds"],
        "timestamp": datetime.now().isoformat()
    }, indent=2)

# Recursos para dados estruturados
@monitoring.resource("monitoring://dashboard")
async def dashboard_data() -> str:
    """
    Dados estruturados para dashboard de monitoramento
    
    Returns:
        str: Dados do dashboard em formato JSON
    """
    try:
        # Métricas atuais
        current_metrics = await get_system_metrics()
        metrics_data = json.loads(current_metrics)
        
        # Health check
        health_data = json.loads(await health_check_complete())
        
        # Últimas 2 horas de histórico
        history_data = json.loads(await get_metrics_history(2))
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "status": health_data.get("overall_status", "unknown"),
            "current_metrics": metrics_data,
            "health_check": health_data,
            "trends": history_data,
            "alerts_active": len(metrics_data.get("alerts", [])),
            "uptime_hours": round(time.time() - psutil.boot_time()) / 3600
        }
        
        return json.dumps(dashboard, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"Erro ao gerar dados do dashboard: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

@monitoring.resource("monitoring://alerts")
async def active_alerts() -> str:
    """
    Lista de alertas ativos no sistema
    
    Returns:
        str: Alertas ativos em formato JSON
    """
    try:
        # Coletar métricas atuais para verificar alertas
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        alerts = await check_alerts(cpu_percent, memory_percent, disk_percent)
        
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts,
            "status": "critical" if any(a["severity"] == "critical" for a in alerts) else "warning" if alerts else "ok"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Erro ao buscar alertas: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

# Prompt para análise de performance
@monitoring.prompt("performance-analysis")
async def performance_analysis_prompt(period_hours: str = "1") -> str:
    """
    Template para análise de performance do sistema
    
    Args:
        period_hours: Período em horas para análise
        
    Returns:
        str: Prompt formatado para análise
    """
    return f"""
Analise o desempenho do sistema Omie FastMCP nas últimas {period_hours} horas.

📊 DADOS PARA ANÁLISE:
1. Use get_metrics_history({period_hours}) para obter dados históricos
2. Use health_check_complete() para status atual
3. Use monitoring://dashboard para visão geral
4. Use monitoring://alerts para alertas ativos

🔍 ANÁLISE REQUERIDA:
1. Identifique tendências de CPU, memória e disco
2. Detecte picos de uso anômalos
3. Avalie performance da API Omie
4. Verifique alertas ativos e sua frequência
5. Sugira otimizações específicas

📋 RELATÓRIO:
- Resumo executivo da performance
- Principais métricas e tendências
- Problemas identificados e impacto
- Recomendações de ação imediata
- Sugestões de melhoria de longo prazo
"""

if __name__ == "__main__":
    print("🔍 Dashboard de Monitoramento Omie FastMCP")
    print("📊 Ferramentas disponíveis:")
    print("   - get_system_metrics: Métricas em tempo real")
    print("   - health_check_complete: Health check completo")
    print("   - get_metrics_history: Histórico de métricas")
    print("   - configure_alerts: Configurar alertas")
    print("📂 Recursos disponíveis:")
    print("   - monitoring://dashboard: Dados dashboard")
    print("   - monitoring://alerts: Alertas ativos")
    print("📝 Prompts disponíveis:")
    print("   - performance-analysis: Análise de performance")
    print()
    
    # Executar servidor de monitoramento
    monitoring.run()