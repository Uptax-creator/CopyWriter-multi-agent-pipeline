#!/usr/bin/env python3
"""
Script para iniciar a aplicação completa
"""

import subprocess
import time
import webbrowser
import os
import signal
import sys

def kill_existing_processes():
    """Matar processos existentes nas portas"""
    print("🔄 Limpando processos existentes...")
    
    # Matar processos nas portas 8001 e 8003
    os.system("lsof -ti:8001 | xargs kill -9 2>/dev/null")
    os.system("lsof -ti:8003 | xargs kill -9 2>/dev/null")
    time.sleep(2)

def start_backend():
    """Iniciar backend FastAPI"""
    print("🚀 Iniciando backend (porta 8001)...")
    
    # Ir para diretório do backend
    backend_dir = "/Users/kleberdossantosribeiro/omie-mcp/omie-tenant-manager"
    os.chdir(backend_dir)
    
    # Iniciar backend em background
    backend_process = subprocess.Popen([
        "python", "-m", "uvicorn", "src.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001", 
        "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Aguardar backend inicializar
    print("⏳ Aguardando backend inicializar...")
    time.sleep(5)
    
    # Verificar se backend está rodando
    import requests
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend iniciado com sucesso!")
            return backend_process
        else:
            print("❌ Backend não respondeu corretamente")
            return None
    except:
        print("❌ Erro ao conectar com backend")
        return None

def start_frontend():
    """Iniciar frontend"""
    print("🌐 Iniciando frontend (porta 8003)...")
    
    # Ir para diretório do frontend
    frontend_dir = "/Users/kleberdossantosribeiro/omie-mcp/omie-dashboard-v2"
    os.chdir(frontend_dir)
    
    # Iniciar frontend em background
    frontend_process = subprocess.Popen([
        "python", "-m", "http.server", "8003"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(2)
    print("✅ Frontend iniciado com sucesso!")
    
    return frontend_process

def open_browser():
    """Abrir navegador"""
    print("🌐 Abrindo navegador...")
    webbrowser.open('http://localhost:8003')

def show_info():
    """Mostrar informações da aplicação"""
    print("\n" + "="*60)
    print("🎉 APLICAÇÃO INICIADA COM SUCESSO!")
    print("="*60)
    
    print("\n📍 ENDEREÇOS:")
    print("🌐 Frontend: http://localhost:8003")
    print("🔧 Backend:  http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    
    print("\n🔐 CREDENCIAIS DE TESTE:")
    print("📧 joao.silva@teste.com / 123456")
    print("📧 kleber.ribeiro@uptax.net / uptax2024")
    
    print("\n🧪 FUNCIONALIDADES ATIVAS:")
    print("✅ Login/registro com backend")
    print("✅ Validações em tempo real")
    print("✅ Gestão de empresas")
    print("✅ Campo de senha com visualização")
    print("✅ Fallback automático se backend falhar")
    
    print("\n⚠️  PARA PARAR A APLICAÇÃO:")
    print("🔴 Pressione Ctrl+C")
    
    print("\n💡 DICA:")
    print("Abra Developer Tools (F12) no navegador para ver os logs de integração")
    print("="*60)

def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    print("\n\n🛑 Parando aplicação...")
    
    # Matar processos
    os.system("lsof -ti:8001 | xargs kill -9 2>/dev/null")
    os.system("lsof -ti:8003 | xargs kill -9 2>/dev/null")
    
    print("👋 Aplicação parada com sucesso!")
    sys.exit(0)

def main():
    print("🚀 INICIANDO APLICAÇÃO OMIE TENANT MANAGER")
    print("="*50)
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 1. Limpar processos existentes
        kill_existing_processes()
        
        # 2. Iniciar backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Falha ao iniciar backend")
            return
        
        # 3. Iniciar frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Falha ao iniciar frontend")
            return
        
        # 4. Abrir navegador
        open_browser()
        
        # 5. Mostrar informações
        show_info()
        
        # 6. Manter processos rodando
        print("\n🔄 Aplicação rodando... (Ctrl+C para parar)")
        
        # Loop infinito para manter script ativo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    main()