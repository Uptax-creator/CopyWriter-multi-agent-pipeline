#!/usr/bin/env python3
"""
Teste do frontend - Iniciar servidor local
"""

import webbrowser
import http.server
import socketserver
import os
import threading
import time

def iniciar_servidor():
    """Iniciar servidor HTTP para o frontend"""
    # Mudar para o diretório do frontend
    os.chdir('/Users/kleberdossantosribeiro/omie-mcp/omie-dashboard-v2')
    
    PORT = 8001
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"🌐 Iniciando servidor frontend na porta {PORT}...")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ Servidor rodando em: http://localhost:{PORT}")
            print(f"📂 Diretório: {os.getcwd()}")
            
            # Aguardar um pouco e abrir o navegador
            def abrir_navegador():
                time.sleep(2)
                print("🔗 Abrindo navegador...")
                webbrowser.open(f'http://localhost:{PORT}')
            
            threading.Thread(target=abrir_navegador, daemon=True).start()
            
            print("\n🎯 FRONTEND PRONTO!")
            print("📋 Checklist de teste:")
            print("   - [ ] Tela de boas-vindas carrega")
            print("   - [ ] Botão 'Configurar Nova Aplicação' funciona")
            print("   - [ ] Formulário de empresa abre")
            print("   - [ ] Campos CNPJ/telefone com máscara")
            print("   - [ ] Navegação entre telas")
            print("   - [ ] Layout responsivo")
            print("   - [ ] Densidade 100% (sem zoom)")
            print("\n⏹️  Pressione Ctrl+C para parar o servidor")
            
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️  Porta {PORT} já está em uso")
            print("🔄 Tentando porta alternativa...")
            
            # Tentar porta alternativa
            for port in range(8002, 8010):
                try:
                    with socketserver.TCPServer(("", port), Handler) as httpd:
                        print(f"✅ Servidor rodando em: http://localhost:{port}")
                        webbrowser.open(f'http://localhost:{port}')
                        httpd.serve_forever()
                        break
                except OSError:
                    continue
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    iniciar_servidor()