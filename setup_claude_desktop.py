#!/usr/bin/env python3
"""
🖥️ SETUP CLAUDE DESKTOP - OMIE MCP PRODUCTION
Script para configurar Claude Desktop com nossos servidores FastMCP
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def print_step(step: str):
    """Imprime passo formatado"""
    print(f"\n🔧 {step}")
    print("-" * 50)

def print_result(success: bool, message: str):
    """Imprime resultado formatado"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def find_claude_config_path():
    """Encontra o caminho da configuração do Claude Desktop"""
    # Possíveis caminhos para Claude Desktop
    possible_paths = [
        # macOS
        os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/.config/claude-desktop/config.json"),
        # Windows
        os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),
        # Linux
        os.path.expanduser("~/.config/claude-desktop/claude_desktop_config.json")
    ]
    
    for path in possible_paths:
        if os.path.exists(path) or os.path.exists(os.path.dirname(path)):
            return path
    
    # Default para macOS se não encontrar
    return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")

def backup_existing_config(config_path: str):
    """Faz backup da configuração existente"""
    if os.path.exists(config_path):
        backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_path, backup_path)
        print_result(True, f"Backup criado: {backup_path}")
        return backup_path
    return None

def create_claude_config():
    """Cria configuração do Claude Desktop"""
    print_step("Configurando Claude Desktop para Omie MCP")
    
    # Encontrar caminho da configuração
    config_path = find_claude_config_path()
    print(f"📁 Caminho da configuração: {config_path}")
    
    # Criar diretório se não existir
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    print_result(True, f"Diretório criado/verificado: {config_dir}")
    
    # Fazer backup se já existir configuração
    backup_path = backup_existing_config(config_path)
    
    # Carregar configuração existente ou criar nova
    existing_config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print_result(True, "Configuração existente carregada")
        except Exception as e:
            print_result(False, f"Erro ao carregar configuração existente: {e}")
    
    # Nossa configuração Omie MCP
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Usar Python do ambiente virtual se disponível
    python_path = f"{project_path}/venv/bin/python3"
    if not os.path.exists(python_path):
        python_path = "python3"  # fallback para python global
    
    omie_config = {
        "omie-conjunto-1-enhanced": {
            "command": python_path,
            "args": [
                f"{project_path}/omie_fastmcp_conjunto_1_enhanced.py"
            ],
            "env": {
                "PYTHONPATH": project_path
            }
        },
        "omie-conjunto-2-complete": {
            "command": python_path,
            "args": [
                f"{project_path}/omie_fastmcp_conjunto_2_complete.py"
            ],
            "env": {
                "PYTHONPATH": project_path
            }
        }
    }
    
    # Mesclar configurações
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"].update(omie_config)
    
    # Salvar configuração
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)
        
        print_result(True, f"Configuração salva em: {config_path}")
        
        # Mostrar configuração final
        print("\n📋 CONFIGURAÇÃO CLAUDE DESKTOP:")
        print(json.dumps(omie_config, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        print_result(False, f"Erro ao salvar configuração: {e}")
        return False

def verify_setup():
    """Verifica se o setup está correto"""
    print_step("Verificando setup")
    
    # Verificar arquivos necessários
    required_files = [
        "omie_fastmcp_conjunto_1_enhanced.py",
        "omie_fastmcp_conjunto_2_complete.py",
        "credentials.json",
        "src/database/database_manager.py",
        "src/tools/tool_classifier_enhanced.py"
    ]
    
    all_files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print_result(True, f"Arquivo encontrado: {file}")
        else:
            print_result(False, f"Arquivo não encontrado: {file}")
            all_files_ok = False
    
    return all_files_ok

def create_test_script():
    """Cria script de teste para Claude Desktop"""
    test_script = '''#!/usr/bin/env python3
"""
🧪 TESTE CLAUDE DESKTOP - OMIE MCP
Script para testar as tools no Claude Desktop
"""

# Commands to test in Claude Desktop:
print("""
🧪 COMANDOS PARA TESTAR NO CLAUDE DESKTOP:

📋 CONJUNTO 1 (Enhanced):
1. "Consulte as categorias disponíveis no Omie"
2. "Liste os clientes cadastrados"  
3. "Verifique as contas a pagar vencidas"

🔧 CONJUNTO 2 (Complete):
4. "Crie um novo projeto chamado 'Teste Claude'"
5. "Liste todos os projetos cadastrados"
6. "Inclua uma conta corrente de teste"
7. "Liste todas as contas correntes"

📊 MONITORAMENTO:
8. "Verifique o status do database"
9. "Mostre as métricas de performance"
10. "Verifique alertas ativos"

🎯 RECURSOS AVANÇADOS:
11. "Execute o prompt de validação do conjunto 1"
12. "Mostre o roadmap de classificação das tools"
""")
'''
    
    with open("test_claude_desktop.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print_result(True, "Script de teste criado: test_claude_desktop.py")

def main():
    """Execução principal"""
    print("="*60)
    print("🖥️ SETUP CLAUDE DESKTOP - OMIE MCP PRODUCTION")
    print("="*60)
    print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = True
    
    # Etapa 1: Verificar setup
    if not verify_setup():
        print_result(False, "Setup incompleto - verifique os arquivos")
        success = False
    
    # Etapa 2: Configurar Claude Desktop
    if success:
        if not create_claude_config():
            print_result(False, "Falha na configuração do Claude Desktop")
            success = False
    
    # Etapa 3: Criar script de teste
    if success:
        create_test_script()
    
    # Resultado final
    print("\n" + "="*60)
    print("🎯 RESULTADO FINAL")
    print("="*60)
    
    if success:
        print("✅ CLAUDE DESKTOP CONFIGURADO COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reinicie o Claude Desktop")
        print("2. Verifique se os servidores MCP aparecem")
        print("3. Execute os comandos de teste")
        print("4. Use 'python test_claude_desktop.py' para ver comandos")
        
        print("\n🎯 SERVIDORES DISPONÍVEIS:")
        print("   - omie-conjunto-1-enhanced (3 tools)")
        print("   - omie-conjunto-2-complete (8 tools)")
        
    else:
        print("❌ Falha na configuração")
        print("🔍 Verifique os erros acima")
    
    print(f"\n🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        exit(1)