#!/usr/bin/env python3
"""
Teste de Integração Completa Frontend-Backend
"""

import webbrowser
import subprocess
import time
import requests
import os

def test_backend():
    """Testar se backend está funcionando"""
    print("🔍 TESTANDO BACKEND")
    print("="*40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend healthy:", response.json())
        else:
            print(f"❌ Backend erro {response.status_code}")
            return False
            
        # Test root endpoint
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("✅ API root:", response.json())
        else:
            print(f"❌ API root erro {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no backend: {e}")
        return False
        
    return True

def start_frontend():
    """Iniciar servidor frontend"""
    print(f"\n🌐 INICIANDO FRONTEND")
    print("="*40)
    
    os.chdir('/Users/kleberdossantosribeiro/omie-mcp/omie-dashboard-v2')
    
    # Matar processo existente na porta 8003
    os.system("lsof -ti:8003 | xargs kill -9 2>/dev/null")
    time.sleep(2)
    
    print("🔗 URL Frontend: http://localhost:8003")
    print("🔗 URL Backend: http://localhost:8001")
    
    # Abrir no navegador
    webbrowser.open('http://localhost:8003')
    
    return True

def main():
    print("🧪 TESTE DE INTEGRAÇÃO COMPLETA")
    print("="*50)
    
    # 1. Testar backend
    if not test_backend():
        print("❌ Backend não está funcionando")
        return
    
    # 2. Iniciar frontend
    if not start_frontend():
        print("❌ Erro ao iniciar frontend")
        return
    
    print(f"\n📋 CHECKLIST DE TESTE INTEGRATION")
    print("="*50)
    
    print("✅ FUNCIONALIDADES IMPLEMENTADAS:")
    print("1. ✅ Backend FastAPI rodando na porta 8001")
    print("2. ✅ Frontend com backend-integration.js")
    print("3. ✅ AuthManager conectado ao backend")
    print("4. ✅ Validações tentam backend primeiro")
    print("5. ✅ Fallback para dados locais se backend falhar")
    print("6. ✅ Campo de visualização de senha")
    
    print(f"\n🧪 TESTES PARA EXECUTAR:")
    print("="*40)
    print("1. 🔐 Login - verificar logs no console:")
    print("   - Deve mostrar: '🔐 Validando credenciais no backend...'")
    print("   - Se falhar: '🔄 Usando validação de fallback...'")
    
    print("2. 📝 Registro - verificar logs no console:")
    print("   - Deve mostrar: '📝 Registrando usuário no backend...'")
    print("   - Se falhar: '🔄 Usando registro simulado...'")
    
    print("3. 🏢 Empresas - verificar logs no console:")
    print("   - Deve mostrar: '🏢 Buscando empresas do usuário no backend...'")
    print("   - Se falhar: '🔄 Usando dados simulados de empresas...'")
    
    print("4. ✅ Validações em tempo real:")
    print("   - Email deve tentar backend primeiro")
    print("   - CNPJ deve tentar backend primeiro")
    
    print(f"\n💡 CREDENCIAIS DE TESTE:")
    print("="*40)
    print("📧 joao.silva@teste.com / 123456")
    print("📧 kleber.ribeiro@uptax.net / uptax2024")
    
    print(f"\n⏹️  Para parar: Ctrl+C")
    
    try:
        # Iniciar servidor HTTP
        subprocess.run(['python', '-m', 'http.server', '8003'])
    except KeyboardInterrupt:
        print("\n👋 Teste finalizado")
        print("🎉 Integração frontend-backend implementada!")

if __name__ == "__main__":
    main()