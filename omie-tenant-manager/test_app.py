#!/usr/bin/env python3
"""
Teste simples da aplicação
"""

import uvicorn
from src.main import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    print("📍 Acesse: http://localhost:8003/docs")
    print("❤️ Health: http://localhost:8003/health")
    print("🔄 Use Ctrl+C para parar")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8003,
        log_level="info"
    )