#!/usr/bin/env python3
"""
⚡ SISTEMA DE CACHE INTELIGENTE
Performance otimizada para consultas frequentes com TTL dinâmico
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pickle
from pathlib import Path

@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    key: str
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float
    size_bytes: int
    tool_name: str
    
    def is_expired(self) -> bool:
        """Verifica se a entrada está expirada"""
        return time.time() - self.created_at > self.ttl
    
    def is_stale(self, staleness_threshold: float = 0.8) -> bool:
        """Verifica se a entrada está próxima do vencimento"""
        age = time.time() - self.created_at
        return age > (self.ttl * staleness_threshold)
    
    def update_access(self):
        """Atualiza estatísticas de acesso"""
        self.last_accessed = time.time()
        self.access_count += 1

class IntelligentCache:
    """Cache inteligente com TTL dinâmico e otimizações adaptativas"""
    
    def __init__(self, 
                 max_size_mb: int = 100,
                 default_ttl: int = 300,
                 persistence_file: str = None):
        
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.default_ttl = default_ttl
        self.persistence_file = Path(persistence_file) if persistence_file else None
        
        # Métricas de performance
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # TTL dinâmico baseado em padrões de acesso
        self.access_patterns: Dict[str, List[float]] = {}
        
        # Carregar cache persistente se disponível
        self._load_persistent_cache()
    
    def _generate_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Gera chave única para cache baseada na ferramenta e parâmetros"""
        # Serializar parâmetros de forma consistente
        params_str = json.dumps(params, sort_keys=True, default=str)
        combined = f"{tool_name}:{params_str}"
        
        # Hash SHA-256 para chave consistente
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _calculate_size(self, data: Any) -> int:
        """Calcula tamanho aproximado dos dados em bytes"""
        try:
            return len(pickle.dumps(data))
        except:
            return len(str(data).encode('utf-8'))
    
    def _calculate_dynamic_ttl(self, tool_name: str, base_ttl: int = None) -> float:
        """Calcula TTL dinâmico baseado nos padrões de acesso"""
        if base_ttl is None:
            base_ttl = self.default_ttl
        
        if tool_name not in self.access_patterns:
            return base_ttl
        
        accesses = self.access_patterns[tool_name]
        if len(accesses) < 2:
            return base_ttl
        
        # Calcular frequência média de acesso
        time_diffs = [accesses[i] - accesses[i-1] for i in range(1, len(accesses))]
        avg_interval = sum(time_diffs) / len(time_diffs)
        
        # TTL dinâmico: se acesso é frequente, aumentar TTL
        if avg_interval < 60:  # < 1 minuto
            return base_ttl * 2
        elif avg_interval < 300:  # < 5 minutos  
            return base_ttl * 1.5
        elif avg_interval > 1800:  # > 30 minutos
            return base_ttl * 0.5
        
        return base_ttl
    
    def _update_access_pattern(self, tool_name: str):
        """Atualiza padrões de acesso para TTL dinâmico"""
        now = time.time()
        
        if tool_name not in self.access_patterns:
            self.access_patterns[tool_name] = []
        
        self.access_patterns[tool_name].append(now)
        
        # Manter apenas os últimos 10 acessos
        self.access_patterns[tool_name] = self.access_patterns[tool_name][-10:]
    
    def _evict_lru(self):
        """Remove entrada menos recentemente usada"""
        if not self.cache:
            return
        
        # Encontrar entrada com menor last_accessed
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        
        evicted_entry = self.cache.pop(lru_key)
        self.current_size -= evicted_entry.size_bytes
        self.evictions += 1
    
    def _cleanup_expired(self):
        """Remove entradas expiradas"""
        expired_keys = [
            key for key, entry in self.cache.items() 
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            entry = self.cache.pop(key)
            self.current_size -= entry.size_bytes
    
    def _ensure_capacity(self, required_size: int):
        """Garante que há capacidade suficiente no cache"""
        while (self.current_size + required_size > self.max_size_bytes and 
               self.cache):
            self._evict_lru()
    
    async def get(self, tool_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """Recupera dados do cache"""
        key = self._generate_key(tool_name, params)
        
        # Limpar expirados periodicamente
        self._cleanup_expired()
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Verificar se expirado
        if entry.is_expired():
            self.cache.pop(key)
            self.current_size -= entry.size_bytes
            self.misses += 1
            return None
        
        # Atualizar estatísticas de acesso
        entry.update_access()
        self._update_access_pattern(tool_name)
        self.hits += 1
        
        return entry.data
    
    async def set(self, tool_name: str, params: Dict[str, Any], 
                  data: Any, ttl: int = None) -> bool:
        """Armazena dados no cache"""
        key = self._generate_key(tool_name, params)
        
        # Calcular TTL dinâmico
        dynamic_ttl = self._calculate_dynamic_ttl(tool_name, ttl)
        
        # Calcular tamanho dos dados
        size_bytes = self._calculate_size(data)
        
        # Verificar se cabe no cache
        if size_bytes > self.max_size_bytes:
            return False  # Dados muito grandes
        
        # Garantir capacidade
        self._ensure_capacity(size_bytes)
        
        # Remover entrada existente se houver
        if key in self.cache:
            old_entry = self.cache[key]
            self.current_size -= old_entry.size_bytes
        
        # Criar nova entrada
        entry = CacheEntry(
            key=key,
            data=data,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            ttl=dynamic_ttl,
            size_bytes=size_bytes,
            tool_name=tool_name
        )
        
        self.cache[key] = entry
        self.current_size += size_bytes
        
        return True
    
    def invalidate_pattern(self, pattern: str):
        """Invalida entradas que correspondem a um padrão"""
        keys_to_remove = [
            key for key, entry in self.cache.items()
            if pattern in entry.tool_name or pattern in key
        ]
        
        for key in keys_to_remove:
            entry = self.cache.pop(key)
            self.current_size -= entry.size_bytes
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        # Estatísticas por ferramenta
        tool_stats = {}
        for entry in self.cache.values():
            tool_name = entry.tool_name
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "entries": 0,
                    "total_size": 0,
                    "avg_ttl": 0,
                    "total_accesses": 0
                }
            
            tool_stats[tool_name]["entries"] += 1
            tool_stats[tool_name]["total_size"] += entry.size_bytes
            tool_stats[tool_name]["avg_ttl"] += entry.ttl
            tool_stats[tool_name]["total_accesses"] += entry.access_count
        
        # Calcular médias
        for stats in tool_stats.values():
            if stats["entries"] > 0:
                stats["avg_size"] = stats["total_size"] / stats["entries"]
                stats["avg_ttl"] = stats["avg_ttl"] / stats["entries"]
                stats["avg_accesses"] = stats["total_accesses"] / stats["entries"]
        
        return {
            "cache_size": len(self.cache),
            "memory_used_mb": round(self.current_size / 1024 / 1024, 2),
            "memory_limit_mb": round(self.max_size_bytes / 1024 / 1024, 2),
            "memory_usage_percent": round(self.current_size / self.max_size_bytes * 100, 1),
            "hit_rate_percent": round(hit_rate, 1),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "tool_statistics": tool_stats
        }
    
    def get_hot_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna as entradas mais acessadas"""
        sorted_entries = sorted(
            self.cache.values(),
            key=lambda e: e.access_count,
            reverse=True
        )
        
        return [
            {
                "tool_name": entry.tool_name,
                "access_count": entry.access_count,
                "age_seconds": time.time() - entry.created_at,
                "ttl": entry.ttl,
                "size_kb": round(entry.size_bytes / 1024, 1)
            }
            for entry in sorted_entries[:limit]
        ]
    
    async def preload_common_queries(self, preload_config: List[Dict[str, Any]]):
        """Pré-carrega consultas comuns no cache"""
        for config in preload_config:
            tool_name = config.get("tool")
            params = config.get("params", {})
            
            # Aqui seria feita a chamada real à API
            # Por agora, vamos simular
            mock_data = {"preloaded": True, "tool": tool_name}
            await self.set(tool_name, params, mock_data)
    
    def _save_persistent_cache(self):
        """Salva cache no disco"""
        if not self.persistence_file:
            return
        
        try:
            # Salvar apenas entradas não expiradas
            persistent_data = {
                "cache": {
                    key: asdict(entry) for key, entry in self.cache.items()
                    if not entry.is_expired()
                },
                "stats": {
                    "hits": self.hits,
                    "misses": self.misses,
                    "evictions": self.evictions
                },
                "saved_at": time.time()
            }
            
            with open(self.persistence_file, 'wb') as f:
                pickle.dump(persistent_data, f)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def _load_persistent_cache(self):
        """Carrega cache do disco"""
        if not self.persistence_file or not self.persistence_file.exists():
            return
        
        try:
            with open(self.persistence_file, 'rb') as f:
                persistent_data = pickle.load(f)
            
            # Restaurar cache
            for key, entry_data in persistent_data.get("cache", {}).items():
                entry = CacheEntry(**entry_data)
                
                # Apenas carregar se ainda válido
                if not entry.is_expired():
                    self.cache[key] = entry
                    self.current_size += entry.size_bytes
            
            # Restaurar estatísticas
            stats = persistent_data.get("stats", {})
            self.hits = stats.get("hits", 0)
            self.misses = stats.get("misses", 0)
            self.evictions = stats.get("evictions", 0)
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar cache: {e}")
    
    def __del__(self):
        """Salva cache ao destruir objeto"""
        self._save_persistent_cache()

# ============================================================================
# DECORADOR PARA CACHE AUTOMÁTICO
# ============================================================================

class CacheManager:
    """Gerenciador global de cache para ferramentas MCP"""
    
    def __init__(self):
        self.cache = IntelligentCache(
            max_size_mb=50,
            default_ttl=300,
            persistence_file="cache/omie_cache.pkl"
        )
    
    def cached_tool(self, ttl: int = None, cache_key_params: List[str] = None):
        """Decorador para cache automático de ferramentas"""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                # Extrair parâmetros para chave de cache
                if cache_key_params:
                    params = {k: kwargs.get(k) for k in cache_key_params if k in kwargs}
                else:
                    params = kwargs
                
                # Tentar recuperar do cache
                cached_result = await self.cache.get(func.__name__, params)
                if cached_result is not None:
                    return cached_result
                
                # Executar função e cache resultado
                result = await func(*args, **kwargs)
                await self.cache.set(func.__name__, params, result, ttl)
                
                return result
            
            return wrapper
        return decorator

# Instância global do gerenciador de cache
cache_manager = CacheManager()

def main():
    """Teste do sistema de cache"""
    import asyncio
    
    async def test_cache():
        cache = IntelligentCache(max_size_mb=1, default_ttl=5)
        
        # Teste básico
        await cache.set("test_tool", {"param": "value"}, {"data": "test_data"})
        
        result = await cache.get("test_tool", {"param": "value"})
        print(f"Cache result: {result}")
        
        # Estatísticas
        stats = cache.get_stats()
        print(f"Cache stats: {json.dumps(stats, indent=2)}")
        
        # Entradas populares
        hot_entries = cache.get_hot_entries()
        print(f"Hot entries: {json.dumps(hot_entries, indent=2)}")
    
    asyncio.run(test_cache())

if __name__ == "__main__":
    main()