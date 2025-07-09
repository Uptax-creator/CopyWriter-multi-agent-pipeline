"""
Configuração de logging para o Omie MCP Server
"""

import logging
import sys
from typing import Optional
from src.config import config

def setup_logger(name: str = "omie-mcp", level: Optional[str] = None) -> logging.Logger:
    """Configurar logger com formatação consistente"""
    
    # Determinar nível de log
    log_level = level or config.log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para stderr (não interfere com stdout MCP)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Configurar loggers de bibliotecas externas
    if config.debug:
        # Em modo debug, mostrar logs detalhados
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)
    else:
        # Em produção, reduzir verbosidade
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    return logger

# Logger global
logger = setup_logger()