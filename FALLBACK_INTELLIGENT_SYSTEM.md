# 🔄 **UpTax Intelligent Fallback System**

## 📋 **Visão Geral**

Sistema inteligente de fallback para garantir 99.9% de disponibilidade dos serviços LLM na UpTax AI Platform.

## 🏗️ **Arquitetura do Sistema**

### **Componentes Principais**

```
┌─────────────────────────────────────────────┐
│           🧠 Intelligent Router              │
├─────────────────────────────────────────────┤
│  • Health Monitoring                        │
│  • Performance Analysis                     │
│  • Cost Optimization                        │
│  • Context-Aware Routing                    │
└─────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Primary    │ │  Secondary   │ │  Emergency   │
│   Providers  │ │  Providers   │ │  Providers   │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ • OpenAI     │ │ • Gemini     │ │ • HuggingFace│
│ • Claude     │ │ • Mistral    │ │ • Local LLM  │
│ • GPT-4o     │ │ • Llama      │ │ • Ollama     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🎯 **Funcionalidades Core**

### **1. Health Monitoring**
```python
class HealthMonitor:
    def __init__(self):
        self.providers = {
            "openai": {"status": "healthy", "latency": 450, "error_rate": 0.02},
            "gemini": {"status": "degraded", "latency": 1200, "error_rate": 0.15},
            "huggingface": {"status": "healthy", "latency": 800, "error_rate": 0.05}
        }
    
    async def check_provider_health(self, provider: str) -> Dict:
        """Monitoramento em tempo real da saúde dos providers"""
        return {
            "status": "healthy|degraded|critical|offline",
            "latency_ms": 0,
            "error_rate": 0.0,
            "quota_remaining": 100,
            "last_check": datetime.now()
        }
```

### **2. Intelligent Routing Algorithm**
```python
class IntelligentRouter:
    def __init__(self):
        self.routing_matrix = {
            "task_complexity": {
                "trivial": ["gemini-flash", "gpt-4o-mini", "hf-small"],
                "simple": ["gpt-4o-mini", "gemini-pro", "claude-haiku"],
                "moderate": ["gpt-4o", "claude-sonnet", "gemini-pro"],
                "complex": ["gpt-4o", "claude-sonnet", "o1-preview"],
                "expert": ["o1-preview", "claude-opus", "gpt-4o"],
                "epic": ["o1-preview", "claude-opus"]
            },
            "quality_requirements": {
                "draft": ["gemini-flash", "gpt-4o-mini"],
                "production": ["gpt-4o", "claude-sonnet"],
                "critical": ["o1-preview", "claude-opus"]
            },
            "cost_constraints": {
                "ultra_low": ["hf-models", "gemini-flash"],
                "low": ["gpt-4o-mini", "claude-haiku"],
                "medium": ["gpt-4o", "gemini-pro"],
                "high": ["claude-sonnet", "o1-preview"]
            }
        }
    
    async def select_optimal_provider(self, 
                                    complexity: str, 
                                    quality: str, 
                                    budget: float,
                                    context: Dict) -> str:
        """
        Algoritmo de seleção inteligente baseado em:
        - Complexidade da tarefa
        - Requisitos de qualidade  
        - Restrições de budget
        - Health status dos providers
        - Histórico de performance
        """
        pass
```

### **3. Fallback Cascade Strategy**
```python
class FallbackCascade:
    """
    Sistema de cascata inteligente para fallback
    """
    def __init__(self):
        self.cascade_levels = {
            "level_1_primary": {
                "providers": ["openai", "claude"],
                "criteria": "best_quality",
                "timeout": 30
            },
            "level_2_secondary": {
                "providers": ["gemini", "mistral"],
                "criteria": "balanced",
                "timeout": 45
            },
            "level_3_emergency": {
                "providers": ["huggingface", "local_llm"],
                "criteria": "availability",
                "timeout": 60
            },
            "level_4_last_resort": {
                "providers": ["cached_responses", "template_responses"],
                "criteria": "functionality",
                "timeout": 5
            }
        }
    
    async def execute_with_fallback(self, request: Dict) -> Dict:
        """
        Executa request com fallback automático
        """
        for level, config in self.cascade_levels.items():
            try:
                result = await self._try_providers(request, config)
                if result["success"]:
                    return result
            except Exception as e:
                self.logger.warning(f"Fallback level {level} failed: {e}")
                continue
        
        return {"success": False, "error": "All fallback levels exhausted"}
```

## 🔧 **Implementação Técnica**

### **Arquivo Principal: `uptax_intelligent_fallback.py`**

```python
#!/usr/bin/env python3
"""
🔄 UpTax Intelligent Fallback System
===================================
Sistema inteligente de fallback para providers LLM
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    CRITICAL = "critical"
    OFFLINE = "offline"

class TaskComplexity(Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"
    EPIC = "epic"

@dataclass
class ProviderHealth:
    name: str
    status: ProviderStatus
    latency_ms: float
    error_rate: float
    quota_remaining: int
    last_check: str
    consecutive_failures: int = 0

@dataclass
class FallbackRequest:
    prompt: str
    complexity: TaskComplexity
    quality_requirement: str
    budget_limit: float
    max_tokens: int
    temperature: float
    task_id: Optional[str] = None
    context: Optional[Dict] = None

class UptaxIntelligentFallback:
    """
    🧠 Sistema Inteligente de Fallback para UpTax AI Platform
    
    Funcionalidades:
    - Health monitoring em tempo real
    - Roteamento inteligente baseado em contexto
    - Fallback automático com múltiplos níveis
    - Otimização de custo e performance
    - Análise preditiva de falhas
    """
    
    def __init__(self):
        self.setup_logging()
        self.provider_health = {}
        self.performance_history = {}
        self.fallback_stats = {"total_requests": 0, "fallback_used": 0}
        
        # Importar LLM providers
        from uptax_llm_credentials_manager import UptaxLLMCredentialsManager
        self.credentials_manager = UptaxLLMCredentialsManager()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('IntelligentFallback')
    
    async def initialize(self) -> bool:
        """Inicializar sistema de fallback"""
        try:
            await self.credentials_manager.initialize()
            await self._initialize_health_monitoring()
            self.logger.info("✅ Intelligent Fallback System inicializado")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            return False
    
    async def _initialize_health_monitoring(self):
        """Inicializar monitoramento de saúde dos providers"""
        providers = await self.credentials_manager.list_available_providers()
        
        for provider in providers:
            self.provider_health[provider] = ProviderHealth(
                name=provider,
                status=ProviderStatus.HEALTHY,
                latency_ms=0.0,
                error_rate=0.0,
                quota_remaining=100,
                last_check=datetime.now().isoformat(),
                consecutive_failures=0
            )
    
    async def execute_with_intelligent_fallback(self, request: FallbackRequest) -> Dict[str, Any]:
        """
        Executar request com fallback inteligente
        
        Fluxo:
        1. Selecionar provider otimizado
        2. Tentar execução
        3. Em caso de falha, usar fallback inteligente
        4. Atualizar métricas e aprendizado
        """
        self.fallback_stats["total_requests"] += 1
        
        # 1. Seleção inteligente do provider primário
        primary_provider = await self._select_optimal_provider(request)
        
        # 2. Tentativa primária
        result = await self._try_provider(primary_provider, request)
        if result["success"]:
            await self._update_performance_metrics(primary_provider, result, success=True)
            return result
        
        # 3. Fallback inteligente
        self.fallback_stats["fallback_used"] += 1
        self.logger.warning(f"🔄 Iniciando fallback para {primary_provider}")
        
        fallback_result = await self._execute_fallback_cascade(request, failed_provider=primary_provider)
        
        # 4. Atualizar health status do provider que falhou
        await self._update_provider_health(primary_provider, success=False)
        
        return fallback_result
    
    async def _select_optimal_provider(self, request: FallbackRequest) -> str:
        """Seleção inteligente de provider baseada em múltiplos fatores"""
        
        # Matriz de decisão baseada em complexidade
        complexity_matrix = {
            TaskComplexity.TRIVIAL: ["gemini", "huggingface"],
            TaskComplexity.SIMPLE: ["openai", "gemini"],
            TaskComplexity.MODERATE: ["openai", "anthropic"],
            TaskComplexity.COMPLEX: ["openai", "anthropic"],
            TaskComplexity.EXPERT: ["anthropic", "openai"],
            TaskComplexity.EPIC: ["anthropic", "openai"]
        }
        
        # Providers candidatos baseados na complexidade
        candidates = complexity_matrix.get(request.complexity, ["openai"])
        
        # Filtrar por saúde e performance
        healthy_candidates = []
        for provider in candidates:
            if provider in self.provider_health:
                health = self.provider_health[provider]
                if health.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]:
                    healthy_candidates.append(provider)
        
        if not healthy_candidates:
            # Fallback para qualquer provider saudável
            healthy_candidates = [p for p, h in self.provider_health.items() 
                                if h.status == ProviderStatus.HEALTHY]
        
        # Selecionar melhor candidato baseado em performance histórica
        if healthy_candidates:
            return self._rank_providers_by_performance(healthy_candidates)[0]
        else:
            return "openai"  # Default fallback
    
    def _rank_providers_by_performance(self, providers: List[str]) -> List[str]:
        """Ranquear providers por performance histórica"""
        scores = {}
        
        for provider in providers:
            health = self.provider_health.get(provider)
            if health:
                # Score baseado em latência, error rate e disponibilidade
                latency_score = max(0, 100 - health.latency_ms / 10)  # Lower latency = higher score
                reliability_score = (100 - health.error_rate * 100)
                availability_score = health.quota_remaining
                
                total_score = (latency_score * 0.3 + reliability_score * 0.5 + availability_score * 0.2)
                scores[provider] = total_score
        
        # Ordenar por score (maior primeiro)
        return sorted(providers, key=lambda p: scores.get(p, 0), reverse=True)
    
    async def _try_provider(self, provider: str, request: FallbackRequest) -> Dict[str, Any]:
        """Tentar execução em um provider específico"""
        try:
            start_time = datetime.now()
            
            # Simular execução (em implementação real, chamar o provider real)
            health = self.provider_health.get(provider)
            if health and health.status == ProviderStatus.OFFLINE:
                raise Exception(f"Provider {provider} is offline")
            
            # Simular processamento
            await asyncio.sleep(0.1)  # Simular latência
            
            # Calcular métricas
            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "provider": provider,
                "content": f"Response from {provider} for: {request.prompt[:50]}...",
                "latency_ms": latency,
                "tokens_used": request.max_tokens // 2,  # Estimativa
                "cost": 0.01,  # Estimativa
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": provider,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_fallback_cascade(self, request: FallbackRequest, failed_provider: str) -> Dict[str, Any]:
        """Executar cascata de fallback"""
        
        # Definir níveis de fallback
        available_providers = [p for p in self.provider_health.keys() if p != failed_provider]
        
        for provider in available_providers:
            self.logger.info(f"🔄 Tentando fallback para {provider}")
            
            result = await self._try_provider(provider, request)
            if result["success"]:
                result["fallback_used"] = True
                result["original_provider"] = failed_provider
                await self._update_performance_metrics(provider, result, success=True)
                return result
        
        # Se todos falharam, retornar erro
        return {
            "success": False,
            "error": "All providers failed",
            "fallback_exhausted": True,
            "attempted_providers": [failed_provider] + available_providers
        }
    
    async def _update_provider_health(self, provider: str, success: bool):
        """Atualizar health status de um provider"""
        if provider not in self.provider_health:
            return
        
        health = self.provider_health[provider]
        
        if success:
            health.consecutive_failures = 0
            if health.status == ProviderStatus.DEGRADED:
                health.status = ProviderStatus.HEALTHY
        else:
            health.consecutive_failures += 1
            
            if health.consecutive_failures >= 3:
                health.status = ProviderStatus.CRITICAL
            elif health.consecutive_failures >= 2:
                health.status = ProviderStatus.DEGRADED
        
        health.last_check = datetime.now().isoformat()
    
    async def _update_performance_metrics(self, provider: str, result: Dict, success: bool):
        """Atualizar métricas de performance"""
        if provider not in self.performance_history:
            self.performance_history[provider] = []
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "latency_ms": result.get("latency_ms", 0),
            "tokens_used": result.get("tokens_used", 0),
            "cost": result.get("cost", 0)
        }
        
        self.performance_history[provider].append(metric)
        
        # Manter apenas últimas 100 métricas
        if len(self.performance_history[provider]) > 100:
            self.performance_history[provider] = self.performance_history[provider][-100:]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Obter status completo do sistema"""
        return {
            "provider_health": {name: asdict(health) for name, health in self.provider_health.items()},
            "fallback_stats": self.fallback_stats,
            "performance_summary": await self._get_performance_summary(),
            "recommendations": await self._get_system_recommendations()
        }
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Resumo de performance dos providers"""
        summary = {}
        
        for provider, metrics in self.performance_history.items():
            if metrics:
                recent_metrics = metrics[-10:]  # Últimas 10
                avg_latency = sum(m["latency_ms"] for m in recent_metrics) / len(recent_metrics)
                success_rate = sum(1 for m in recent_metrics if m["success"]) / len(recent_metrics)
                
                summary[provider] = {
                    "avg_latency_ms": avg_latency,
                    "success_rate": success_rate,
                    "total_requests": len(metrics)
                }
        
        return summary
    
    async def _get_system_recommendations(self) -> List[str]:
        """Gerar recomendações do sistema"""
        recommendations = []
        
        # Analisar providers com problemas
        for provider, health in self.provider_health.items():
            if health.status in [ProviderStatus.CRITICAL, ProviderStatus.OFFLINE]:
                recommendations.append(f"🔴 Provider {provider} needs attention: {health.status}")
            elif health.consecutive_failures > 0:
                recommendations.append(f"🟡 Monitor {provider}: {health.consecutive_failures} recent failures")
        
        # Analisar uso de fallback
        if self.fallback_stats["total_requests"] > 0:
            fallback_rate = self.fallback_stats["fallback_used"] / self.fallback_stats["total_requests"]
            if fallback_rate > 0.1:  # > 10%
                recommendations.append(f"⚠️ High fallback rate: {fallback_rate:.1%} - investigate primary providers")
        
        if not recommendations:
            recommendations.append("✅ All systems operating normally")
        
        return recommendations

# Função para teste
async def test_intelligent_fallback():
    """Testar sistema de fallback inteligente"""
    system = UptaxIntelligentFallback()
    
    if await system.initialize():
        print("✅ Sistema de Fallback Inteligente inicializado")
        
        # Testar request
        request = FallbackRequest(
            prompt="Explain quantum computing in simple terms",
            complexity=TaskComplexity.MODERATE,
            quality_requirement="production",
            budget_limit=0.05,
            max_tokens=500,
            temperature=0.7
        )
        
        result = await system.execute_with_intelligent_fallback(request)
        print(f"🔄 Resultado: {result['success']}")
        
        if result["success"]:
            print(f"📝 Provider usado: {result['provider']}")
            print(f"⚡ Latência: {result['latency_ms']:.0f}ms")
            if result.get("fallback_used"):
                print(f"🔄 Fallback usado (original: {result['original_provider']})")
        
        # Status do sistema
        status = await system.get_system_status()
        print(f"📊 Providers saudáveis: {sum(1 for h in status['provider_health'].values() if h['status'] == 'healthy')}")
    else:
        print("❌ Falha na inicialização")

if __name__ == "__main__":
    asyncio.run(test_intelligent_fallback())
```

## 📊 **Métricas e Monitoramento**

### **KPIs do Sistema**
- **Availability**: 99.9% uptime garantido
- **Fallback Rate**: < 5% dos requests
- **Mean Time to Recovery**: < 30 segundos
- **Cost Optimization**: 15-25% economia vs single provider

### **Alertas Automáticos**
- Provider offline > 1 minuto
- Error rate > 10% em 5 minutos
- Latência > 5x baseline
- Quota < 20% remaining

## 🚀 **Roadmap de Implementação**

### **Fase 1: Core System (1-2 semanas)**
- [x] Arquitetura base
- [ ] Health monitoring
- [ ] Basic fallback logic
- [ ] Integration com existing LLM tools

### **Fase 2: Intelligence (2-3 semanas)**
- [ ] Machine learning para provider selection
- [ ] Predictive failure detection
- [ ] Auto-scaling baseado em load
- [ ] Advanced cost optimization

### **Fase 3: Enterprise (4+ semanas)**
- [ ] Multi-tenant support
- [ ] Custom fallback policies
- [ ] Integration com monitoring tools
- [ ] Advanced analytics dashboard

## 💡 **Considerações de Arquitetura**

### **Posicionamento na UpTax Platform**
```
UpTax AI Platform
├── Task Master MCP
├── Budget Tracker  
├── MCP Optimizer
├── 🆕 Intelligent Fallback System ← Nova aplicação
└── Infrastructure Agent
```

### **Integração com Componentes Existentes**
- **Task Master**: Fallback para criação de tarefas
- **Budget Tracker**: Otimização de custo em tempo real
- **MCP Optimizer**: Fallback baseado em complexidade
- **All Tools**: Provider reliability para todas as operações

---

**Status**: 📋 Documentação Completa  
**Próximo Passo**: Implementação do sistema core  
**Prioridade**: 🔴 Alta (Critical for production reliability)