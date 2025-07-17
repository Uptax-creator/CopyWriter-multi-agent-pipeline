#!/usr/bin/env python3
"""
Script para consolidar servidores MCP em um único arquivo
"""

import os
import shutil
import sys
from datetime import datetime

def consolidate_servers():
    """Consolida servidores em um único arquivo"""
    
    print("🔄 Consolidando servidores MCP...")
    
    # Caminhos dos arquivos
    hybrid_file = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    original_file = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server.py"
    fixed_file = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_fixed.py"
    backup_dir = "/Users/kleberdossantosribeiro/omie-mcp/backup"
    
    # Criar diretório de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/{timestamp}"
    os.makedirs(backup_path, exist_ok=True)
    
    # Fazer backup dos arquivos existentes
    print("📦 Fazendo backup dos arquivos existentes...")
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, f"{backup_path}/omie_mcp_server_original.py")
        print(f"  ✅ Backup: {original_file} -> {backup_path}/omie_mcp_server_original.py")
    
    if os.path.exists(fixed_file):
        shutil.copy2(fixed_file, f"{backup_path}/omie_mcp_server_fixed.py")
        print(f"  ✅ Backup: {fixed_file} -> {backup_path}/omie_mcp_server_fixed.py")
    
    # Verificar se arquivo híbrido existe
    if not os.path.exists(hybrid_file):
        print(f"❌ Arquivo híbrido não encontrado: {hybrid_file}")
        return False
    
    # Substituir arquivo original pelo híbrido
    print("🔄 Substituindo arquivo original pelo híbrido...")
    shutil.copy2(hybrid_file, original_file)
    print(f"  ✅ Copiado: {hybrid_file} -> {original_file}")
    
    # Remover arquivos temporários
    print("🧹 Removendo arquivos temporários...")
    
    if os.path.exists(fixed_file):
        os.remove(fixed_file)
        print(f"  ✅ Removido: {fixed_file}")
    
    # Atualizar permissões
    os.chmod(original_file, 0o755)
    print(f"  ✅ Permissões atualizadas: {original_file}")
    
    # Criar link simbólico para compatibilidade
    hybrid_link = "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py"
    if os.path.exists(hybrid_link):
        os.remove(hybrid_link)
    os.symlink(original_file, hybrid_link)
    print(f"  ✅ Link simbólico criado: {hybrid_link} -> {original_file}")
    
    print("\n🎉 Consolidação concluída!")
    print("\n📋 Resumo das mudanças:")
    print(f"  • Backup salvo em: {backup_path}")
    print(f"  • Arquivo principal: {original_file}")
    print(f"  • Suporte a dois modos: --mode stdio | --mode http")
    
    print("\n🚀 Como usar:")
    print("  # Para Claude Desktop:")
    print("  python omie_mcp_server.py --mode stdio")
    print("")
    print("  # Para integrações web:")
    print("  python omie_mcp_server.py --mode http --port 3000")
    
    return True

def test_consolidated_server():
    """Testa servidor consolidado"""
    
    print("\n🧪 Testando servidor consolidado...")
    
    # Testar importação
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            "/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server.py", 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ Servidor consolidado funciona corretamente")
            print(f"  📋 Ajuda disponível:\n{result.stdout}")
            return True
        else:
            print(f"  ❌ Erro no servidor: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao testar servidor: {e}")
        return False

def main():
    """Função principal"""
    
    print("🔧 Script de Consolidação de Servidores MCP")
    print("=" * 50)
    
    # Verificar se usuário quer continuar
    response = input("\nDeseja consolidar os servidores em um único arquivo? (y/n): ")
    if response.lower() != 'y':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Consolidar servidores
    if consolidate_servers():
        # Testar servidor consolidado
        if test_consolidated_server():
            print("\n🎉 Consolidação realizada com sucesso!")
            print("\n📝 Próximos passos:")
            print("1. Teste o servidor: python scripts/test_hybrid_server.py")
            print("2. Configure no Claude Desktop")
            print("3. Teste integrações web")
        else:
            print("\n⚠️  Consolidação realizada, mas testes falharam")
    else:
        print("\n❌ Falha na consolidação")

if __name__ == "__main__":
    main()