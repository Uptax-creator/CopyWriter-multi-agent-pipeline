#!/usr/bin/env python3
"""
Teste do frontend corrigido
"""

import webbrowser
import time
import subprocess
import os

def main():
    print("🧪 TESTE FRONTEND CORRIGIDO")
    print("="*50)
    
    # Ir para o diretório correto
    os.chdir('/Users/kleberdossantosribeiro/omie-mcp/omie-dashboard-v2')
    
    print("📂 Diretório:", os.getcwd())
    
    # Verificar se os arquivos existem
    files_to_check = [
        'index.html',
        'js/auth.js', 
        'js/validation.js',
        'js/app.js'
    ]
    
    print("\n📁 Verificando arquivos...")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - FALTANDO")
            return
    
    # Iniciar servidor
    print("\n🌐 Iniciando servidor HTTP...")
    try:
        print("🔗 URL: http://localhost:8003")
        print("\n📋 CHECKLIST DE TESTE:")
        print("1. ✅ Página carrega sem erros no console")
        print("2. ✅ Botão 'Configurar Nova Aplicação' funciona")
        print("3. ✅ Formulário de empresa abre")
        print("4. ✅ Campo de telefone não gera erro JavaScript")
        print("5. ✅ Validação de email duplicado funciona")
        print("6. ✅ Validação de CNPJ único funciona")
        print("\n💡 TESTE ESPECÍFICO:")
        print("- Tente cadastrar email: joao.silva@teste.com (deve dar erro)")
        print("- Tente cadastrar CNPJ: 46845239000163 (deve dar erro)")
        print("\n⏹️  Pressione Ctrl+C para parar")
        
        # Abrir navegador
        webbrowser.open('http://localhost:8003')
        
        # Iniciar servidor
        subprocess.run(['python', '-m', 'http.server', '8003'])
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()