"""
Rate Limiter para evitar erro 529 Overloaded da API Anthropic
"""

import asyncio
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate Limiter para controlar requisições e evitar sobrecarga da API
    """
    
    def __init__(self, requests_per_minute: int = 20, min_delay: float = 1.0):
        self.requests_per_minute = requests_per_minute
        self.min_delay = min_delay
        self.request_times = []
        self.last_request_time = 0
        
    async def wait_if_needed(self):
        """
        Aguarda se necessário para respeitar rate limits
        """
        current_time = time.time()
        
        # Limpar requisições antigas (mais de 1 minuto)
        cutoff_time = current_time - 60
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # Verificar se excedeu limite por minuto
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limit atingido. Aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Verificar delay mínimo entre requisições
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logger.debug(f"Aguardando delay mínimo: {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Registrar nova requisição
        self.request_times.append(time.time())
        self.last_request_time = time.time()

class ExponentialBackoff:
    """
    Backoff exponencial para retry em caso de erro 529
    """
    
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0, multiplier: float = 2.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.current_delay = initial_delay
        
    async def wait(self):
        """
        Aguarda com backoff exponencial
        """
        await asyncio.sleep(self.current_delay)
        self.current_delay = min(self.current_delay * self.multiplier, self.max_delay)
        
    def reset(self):
        """
        Reset do delay para valor inicial
        """
        self.current_delay = self.initial_delay

async def handle_api_request(func, *args, max_retries: int = 3, **kwargs):
    """
    Wrapper para requisições da API com retry automático em caso de erro 529
    """
    rate_limiter = RateLimiter()
    backoff = ExponentialBackoff()
    
    for attempt in range(max_retries + 1):
        try:
            await rate_limiter.wait_if_needed()
            result = await func(*args, **kwargs)
            backoff.reset()  # Reset em caso de sucesso
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Verificar se é erro 529 ou overloaded
            if "529" in error_msg or "overloaded" in error_msg:
                if attempt < max_retries:
                    logger.warning(f"Erro 529 detectado. Tentativa {attempt + 1}/{max_retries + 1}. Aguardando backoff...")
                    await backoff.wait()
                    continue
                else:
                    logger.error(f"Máximo de tentativas atingido para erro 529: {e}")
                    raise
            else:
                # Outro tipo de erro, não faz retry
                raise
    
    raise Exception("Máximo de tentativas atingido")

# Rate limiter global
global_rate_limiter = RateLimiter(requests_per_minute=15, min_delay=2.0)