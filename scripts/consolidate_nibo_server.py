#!/usr/bin/env python3
"""
Script para consolidar servidor Nibo MCP em um único arquivo híbrido
"""

import os
import shutil
import sys
from datetime import datetime

def consolidate_nibo_server():
    """Consolida servidor Nibo em um único arquivo"""
    
    print("🔄 Consolidando servidor Nibo MCP...")
    
    # Caminhos dos arquivos
    hybrid_file = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py"
    original_file = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server.py"
    fixed_file = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_fixed.py"
    complex_file = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_complex.py"
    backup_dir = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/backup"
    
    # Criar diretório de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/{timestamp}"
    os.makedirs(backup_path, exist_ok=True)
    
    # Fazer backup dos arquivos existentes
    print("📦 Fazendo backup dos arquivos existentes...")
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, f"{backup_path}/nibo_mcp_server_original.py")
        print(f"  ✅ Backup: {original_file} -> {backup_path}/nibo_mcp_server_original.py")
    
    if os.path.exists(fixed_file):
        shutil.copy2(fixed_file, f"{backup_path}/nibo_mcp_server_fixed.py")
        print(f"  ✅ Backup: {fixed_file} -> {backup_path}/nibo_mcp_server_fixed.py")
    
    if os.path.exists(complex_file):
        shutil.copy2(complex_file, f"{backup_path}/nibo_mcp_server_complex.py")
        print(f"  ✅ Backup: {complex_file} -> {backup_path}/nibo_mcp_server_complex.py")
    
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
    
    temp_files = [fixed_file, complex_file]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"  ✅ Removido: {temp_file}")
    
    # Atualizar permissões
    os.chmod(original_file, 0o755)
    print(f"  ✅ Permissões atualizadas: {original_file}")
    
    # Criar link simbólico para compatibilidade
    hybrid_link = "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py"
    if os.path.exists(hybrid_link) and os.path.islink(hybrid_link):
        os.remove(hybrid_link)
    if os.path.exists(hybrid_link) and not os.path.islink(hybrid_link):
        os.remove(hybrid_link)
    os.symlink(original_file, hybrid_link)
    print(f"  ✅ Link simbólico criado: {hybrid_link} -> {original_file}")
    
    print("\n🎉 Consolidação do Nibo concluída!")
    print("\n📋 Resumo das mudanças:")
    print(f"  • Backup salvo em: {backup_path}")
    print(f"  • Arquivo principal: {original_file}")
    print(f"  • Suporte a dois modos: --mode stdio | --mode http")
    print(f"  • Porta padrão HTTP: 3002")
    
    print("\n🚀 Como usar:")
    print("  # Para Claude Desktop:")
    print("  python nibo_mcp_server.py --mode stdio")
    print("")
    print("  # Para integrações web:")
    print("  python nibo_mcp_server.py --mode http --port 3002")
    
    print("\n🔧 Ferramentas exclusivas do Nibo:")
    print("  • consultar_socios")
    print("  • incluir_socio")
    print("  • incluir_multiplos_clientes")
    print("  • consultar_centros_custo")
    
    return True

def test_consolidated_nibo_server():
    """Testa servidor Nibo consolidado"""
    
    print("\n🧪 Testando servidor Nibo consolidado...")
    
    # Testar importação
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            "/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server.py", 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ Servidor Nibo consolidado funciona corretamente")
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
    
    print("🔧 Script de Consolidação do Servidor Nibo MCP")
    print("=" * 55)
    
    # Verificar se usuário quer continuar
    response = input("\nDeseja consolidar o servidor Nibo em um único arquivo? (y/n): ")
    if response.lower() != 'y':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Consolidar servidor
    if consolidate_nibo_server():
        # Testar servidor consolidado
        if test_consolidated_nibo_server():
            print("\n🎉 Consolidação do Nibo realizada com sucesso!")
            print("\n📝 Próximos passos:")
            print("1. Teste o servidor: python nibo-mcp/scripts/test_nibo_hybrid_server.py")
            print("2. Configure no Claude Desktop")
            print("3. Teste integrações web")
            print("4. Explore ferramentas exclusivas do Nibo")
        else:
            print("\n⚠️  Consolidação realizada, mas testes falharam")
    else:
        print("\n❌ Falha na consolidação")

if __name__ == "__main__":
    main()