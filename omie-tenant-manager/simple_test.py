"""
Teste super simples
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Teste Simples")

@app.get("/")
def root():
    return {"message": "Funcionando!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Teste simples iniciando...")
    print("📍 Acesse: http://localhost:8004")
    uvicorn.run(app, host="127.0.0.1", port=8004)