#!/usr/bin/env python3
"""
🔧 SCRIPT DE CORREÇÃO E RE-EXECUÇÃO DA HOMOLOGAÇÃO
Instala dependências e executa homologação novamente
"""

import subprocess
import sys
import asyncio
from datetime import datetime

def print_step(step: str):
    """Imprime passo formatado"""
    print(f"\n🔧 {step}")
    print("-" * 50)

def print_result(success: bool, message: str):
    """Imprime resultado formatado"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def install_dependencies():
    """Instala dependências necessárias"""
    print_step("Instalando dependências")
    
    try:
        # Instalar aioredis
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "aioredis"
        ], capture_output=True, text=True, check=True)
        
        print_result(True, "aioredis instalado com sucesso")
        
        # Instalar outras dependências se necessário
        dependencies = ["asyncpg", "fastmcp", "psutil"]
        
        for dep in dependencies:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True)
                print_result(True, f"{dep} instalado/verificado")
            except subprocess.CalledProcessError:
                print_result(False, f"Erro ao instalar {dep}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_result(False, f"Erro ao instalar aioredis: {e}")
        return False

def run_homologation():
    """Executa homologação novamente"""
    print_step("Re-executando homologação")
    
    try:
        result = subprocess.run([
            sys.executable, "execute_homologacao_now.py"
        ], capture_output=True, text=True)
        
        print("📊 RESULTADO DA HOMOLOGAÇÃO:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Avisos/Erros:")
            print(result.stderr)
        
        # Verificar se foi aprovado
        if "🟢 APROVADO PARA PRODUÇÃO" in result.stdout:
            print_result(True, "SISTEMA TOTALMENTE APROVADO!")
            return True
        elif "🟡 APROVADO COM RESSALVAS" in result.stdout:
            print_result(True, "Sistema aprovado com ressalvas")
            return True
        else:
            print_result(False, "Sistema ainda requer correções")
            return False
            
    except Exception as e:
        print_result(False, f"Erro ao executar homologação: {e}")
        return False

def main():
    """Execução principal"""
    print("="*60)
    print("🔧 CORREÇÃO E RE-EXECUÇÃO DA HOMOLOGAÇÃO")
    print("="*60)
    print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Passo 1: Instalar dependências
    deps_ok = install_dependencies()
    
    if not deps_ok:
        print_result(False, "Falha na instalação de dependências")
        return False
    
    # Passo 2: Re-executar homologação
    homolog_ok = run_homologation()
    
    # Resultado final
    print("\n" + "="*60)
    print("🎯 RESULTADO FINAL DAS CORREÇÕES")
    print("="*60)
    
    if homolog_ok:
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("🚀 Sistema pronto para produção")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Deploy em ambiente de produção")
        print("2. Configurar monitoramento")
        print("3. Executar testes com usuários reais")
        
    else:
        print("❌ Ainda existem problemas a resolver")
        print("🔍 Verifique os logs acima para detalhes")
    
    print(f"\n🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return homolog_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)