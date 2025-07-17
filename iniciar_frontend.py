#!/usr/bin/env python3
"""
Script simples para iniciar o frontend
"""
import os
import subprocess
import sys

def main():
    print("🌐 Iniciando Frontend...")
    
    # Verificar se estamos no diretório correto
    current_dir = os.getcwd()
    print(f"📂 Diretório atual: {current_dir}")
    
    # Tentar diferentes portas
    portas = [8003, 8004, 8005, 8006, 8007]
    
    for porta in portas:
        try:
            print(f"🔄 Tentando porta {porta}...")
            
            # Verificar se a porta está livre
            result = subprocess.run(['lsof', '-i', f':{porta}'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"❌ Porta {porta} ocupada")
                continue
            
            print(f"✅ Porta {porta} livre!")
            print(f"🚀 Iniciando servidor na porta {porta}")
            print(f"🔗 Acesse: http://localhost:{porta}")
            print("⏹️  Pressione Ctrl+C para parar")
            
            # Iniciar servidor
            subprocess.run(['python', '-m', 'http.server', str(porta)])
            break
            
        except KeyboardInterrupt:
            print("\n👋 Servidor parado pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro na porta {porta}: {e}")
            continue
    
    else:
        print("❌ Todas as portas testadas estão ocupadas")
        print("💡 Tente manualmente:")
        print("   python -m http.server 8008")

if __name__ == "__main__":
    main()