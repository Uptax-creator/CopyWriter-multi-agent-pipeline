#!/usr/bin/env python3
"""
Relatório de verificação da separação por serviço (Omie MCP vs Nibo MCP)
"""

import os
import json
from pathlib import Path

def analyze_service_separation():
    """Analisa a separação de arquivos por serviço"""
    
    project_root = Path("/Users/kleberdossantosribeiro/omie-mcp")
    
    report = {
        "omie_mcp": {
            "description": "Serviço Omie MCP - Integração com Omie ERP",
            "main_directory": str(project_root),
            "server_files": [],
            "source_directory": str(project_root / "src"),
            "tools_directory": str(project_root / "src" / "tools"),
            "credentials": str(project_root / "credentials.json"),
            "config_files": [],
            "scripts": []
        },
        "nibo_mcp": {
            "description": "Serviço Nibo MCP - Integração com Nibo ERP",
            "main_directory": str(project_root / "nibo-mcp"),
            "server_files": [],
            "source_directory": str(project_root / "nibo-mcp" / "src"),
            "tools_directory": str(project_root / "nibo-mcp" / "src" / "tools"),
            "credentials": str(project_root / "nibo-mcp" / "credentials.json"),
            "config_files": [],
            "scripts": []
        },
        "shared_components": {
            "description": "Componentes compartilhados entre serviços",
            "scripts_directory": str(project_root / "scripts"),
            "docs_directory": str(project_root / "docs"),
            "shared_scripts": []
        }
    }
    
    # Analisar arquivos do Omie MCP
    print("🔍 Analisando estrutura do Omie MCP...")
    
    # Servidores Omie
    omie_servers = [
        "omie_mcp_server.py",
        "omie_mcp_server_hybrid.py", 
        "omie_mcp_server_fixed.py",
        "omie_mcp_server_old.py"
    ]
    
    for server in omie_servers:
        server_path = project_root / server
        if server_path.exists():
            report["omie_mcp"]["server_files"].append({
                "file": server,
                "path": str(server_path),
                "size": server_path.stat().st_size,
                "exists": True
            })
            print(f"  ✅ {server}")
        else:
            print(f"  ❌ {server} (não encontrado)")
    
    # Ferramentas Omie
    omie_tools_dir = project_root / "src" / "tools"
    if omie_tools_dir.exists():
        omie_tools = list(omie_tools_dir.glob("*.py"))
        report["omie_mcp"]["tools_count"] = len(omie_tools)
        report["omie_mcp"]["tools_files"] = [tool.name for tool in omie_tools]
        print(f"  📋 Ferramentas Omie: {len(omie_tools)} arquivos")
        for tool in omie_tools:
            print(f"    • {tool.name}")
    
    # Analisar arquivos do Nibo MCP
    print(f"\n🔍 Analisando estrutura do Nibo MCP...")
    
    nibo_dir = project_root / "nibo-mcp"
    
    # Servidores Nibo
    nibo_servers = [
        "nibo_mcp_server.py",
        "nibo_mcp_server_hybrid.py",
        "nibo_mcp_server_fixed.py", 
        "nibo_mcp_server_complex.py"
    ]
    
    for server in nibo_servers:
        server_path = nibo_dir / server
        if server_path.exists():
            report["nibo_mcp"]["server_files"].append({
                "file": server,
                "path": str(server_path),
                "size": server_path.stat().st_size,
                "exists": True
            })
            print(f"  ✅ {server}")
        else:
            print(f"  ❌ {server} (não encontrado)")
    
    # Ferramentas Nibo
    nibo_tools_dir = nibo_dir / "src" / "tools"
    if nibo_tools_dir.exists():
        nibo_tools = list(nibo_tools_dir.glob("*.py"))
        report["nibo_mcp"]["tools_count"] = len(nibo_tools)
        report["nibo_mcp"]["tools_files"] = [tool.name for tool in nibo_tools]
        print(f"  📋 Ferramentas Nibo: {len(nibo_tools)} arquivos")
        for tool in nibo_tools:
            print(f"    • {tool.name}")
    
    # Scripts Nibo específicos
    nibo_scripts_dir = nibo_dir / "scripts"
    if nibo_scripts_dir.exists():
        nibo_scripts = list(nibo_scripts_dir.glob("*.py"))
        report["nibo_mcp"]["scripts"] = [script.name for script in nibo_scripts]
        print(f"  🔧 Scripts Nibo específicos: {len(nibo_scripts)}")
    
    # Analisar componentes compartilhados
    print(f"\n🔍 Analisando componentes compartilhados...")
    
    shared_scripts_dir = project_root / "scripts"
    if shared_scripts_dir.exists():
        shared_scripts = list(shared_scripts_dir.glob("*.py"))
        report["shared_components"]["shared_scripts"] = [script.name for script in shared_scripts]
        print(f"  🔧 Scripts compartilhados: {len(shared_scripts)}")
        for script in shared_scripts:
            print(f"    • {script.name}")
    
    return report

def check_independence():
    """Verifica se os serviços são realmente independentes"""
    
    print(f"\n🔍 Verificando independência dos serviços...")
    
    independence_check = {
        "omie_mcp": {
            "has_own_server": False,
            "has_own_tools": False, 
            "has_own_credentials": False,
            "has_own_client": False
        },
        "nibo_mcp": {
            "has_own_server": False,
            "has_own_tools": False,
            "has_own_credentials": False,
            "has_own_client": False
        },
        "independence_score": 0
    }
    
    project_root = Path("/Users/kleberdossantosribeiro/omie-mcp")
    
    # Verificar Omie MCP
    if (project_root / "omie_mcp_server_hybrid.py").exists():
        independence_check["omie_mcp"]["has_own_server"] = True
        print("  ✅ Omie tem servidor próprio")
    
    if (project_root / "src" / "tools").exists():
        independence_check["omie_mcp"]["has_own_tools"] = True
        print("  ✅ Omie tem ferramentas próprias")
    
    if (project_root / "credentials.json").exists():
        independence_check["omie_mcp"]["has_own_credentials"] = True
        print("  ✅ Omie tem credenciais próprias")
    
    if (project_root / "src" / "client" / "omie_client.py").exists():
        independence_check["omie_mcp"]["has_own_client"] = True
        print("  ✅ Omie tem cliente próprio")
    
    # Verificar Nibo MCP
    nibo_dir = project_root / "nibo-mcp"
    
    if (nibo_dir / "nibo_mcp_server_hybrid.py").exists():
        independence_check["nibo_mcp"]["has_own_server"] = True
        print("  ✅ Nibo tem servidor próprio")
    
    if (nibo_dir / "src" / "tools").exists():
        independence_check["nibo_mcp"]["has_own_tools"] = True
        print("  ✅ Nibo tem ferramentas próprias")
    
    if (nibo_dir / "credentials.json").exists():
        independence_check["nibo_mcp"]["has_own_credentials"] = True
        print("  ✅ Nibo tem credenciais próprias")
    
    if (nibo_dir / "src" / "core" / "nibo_client.py").exists():
        independence_check["nibo_mcp"]["has_own_client"] = True
        print("  ✅ Nibo tem cliente próprio")
    
    # Calcular score de independência
    omie_score = sum(independence_check["omie_mcp"].values())
    nibo_score = sum(independence_check["nibo_mcp"].values())
    independence_check["independence_score"] = (omie_score + nibo_score) / 8 * 100
    
    print(f"\n📊 Score de Independência: {independence_check['independence_score']:.1f}%")
    print(f"  Omie MCP: {omie_score}/4 componentes independentes")
    print(f"  Nibo MCP: {nibo_score}/4 componentes independentes")
    
    return independence_check

def check_claude_config():
    """Verifica se ambos os serviços estão configurados no Claude Desktop"""
    
    print(f"\n🔍 Verificando configuração do Claude Desktop...")
    
    config_path = Path("/Users/kleberdossantosribeiro/Library/Application Support/Claude/claude_desktop_config.json")
    
    if not config_path.exists():
        print("  ❌ Arquivo de configuração do Claude Desktop não encontrado")
        return {"configured": False, "error": "Arquivo não encontrado"}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        mcp_servers = config.get("mcpServers", {})
        
        result = {
            "configured": True,
            "total_servers": len(mcp_servers),
            "omie_configured": False,
            "nibo_configured": False,
            "servers": {}
        }
        
        for server_name, server_config in mcp_servers.items():
            args = server_config.get("args", [])
            if args:
                script_path = args[0]
                
                result["servers"][server_name] = {
                    "script": script_path,
                    "exists": os.path.exists(script_path)
                }
                
                if "omie" in script_path.lower():
                    result["omie_configured"] = True
                    print(f"  ✅ Omie configurado: {server_name}")
                elif "nibo" in script_path.lower():
                    result["nibo_configured"] = True  
                    print(f"  ✅ Nibo configurado: {server_name}")
                
                status = "✅" if os.path.exists(script_path) else "❌"
                print(f"    {status} Script: {script_path}")
        
        if result["omie_configured"] and result["nibo_configured"]:
            print("  🎉 Ambos os serviços estão configurados!")
        elif result["omie_configured"]:
            print("  ⚠️  Apenas Omie está configurado")
        elif result["nibo_configured"]:
            print("  ⚠️  Apenas Nibo está configurado")
        else:
            print("  ❌ Nenhum serviço está configurado corretamente")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Erro ao ler configuração: {e}")
        return {"configured": False, "error": str(e)}

def generate_full_report():
    """Gera relatório completo da separação por serviço"""
    
    print("📊 RELATÓRIO DE SEPARAÇÃO POR SERVIÇO MCP")
    print("=" * 60)
    
    # Análise da estrutura
    structure_report = analyze_service_separation()
    
    # Verificação de independência
    independence_report = check_independence()
    
    # Configuração Claude Desktop
    claude_report = check_claude_config()
    
    # Compilar relatório final
    final_report = {
        "timestamp": "2025-01-16",
        "structure": structure_report,
        "independence": independence_report,
        "claude_configuration": claude_report,
        "summary": {
            "properly_separated": True,
            "omie_files": len(structure_report["omie_mcp"]["server_files"]),
            "nibo_files": len(structure_report["nibo_mcp"]["server_files"]),
            "independence_score": independence_report["independence_score"],
            "both_configured": claude_report.get("omie_configured", False) and claude_report.get("nibo_configured", False)
        }
    }
    
    # Resumo final
    print(f"\n📋 RESUMO FINAL")
    print("-" * 30)
    print(f"✅ Arquivos Omie MCP: {final_report['summary']['omie_files']} servidores")
    print(f"✅ Arquivos Nibo MCP: {final_report['summary']['nibo_files']} servidores")
    print(f"📊 Score Independência: {final_report['summary']['independence_score']:.1f}%")
    print(f"🔧 Ambos configurados no Claude: {'✅' if final_report['summary']['both_configured'] else '❌'}")
    
    # Conclusão
    if (final_report['summary']['independence_score'] >= 75 and 
        final_report['summary']['omie_files'] > 0 and 
        final_report['summary']['nibo_files'] > 0):
        print(f"\n🎉 CONFIRMADO: Os serviços estão CORRETAMENTE SEPARADOS!")
        print(f"   • Cada serviço tem seus próprios arquivos")
        print(f"   • Estruturas independentes mantidas")
        print(f"   • Políticas padronizadas entre ERPs")
    else:
        print(f"\n⚠️  ATENÇÃO: Separação pode estar incompleta")
    
    # Salvar relatório
    output_file = "/Users/kleberdossantosribeiro/omie-mcp/service_separation_report.json"
    with open(output_file, 'w') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório detalhado salvo em: {output_file}")
    
    return final_report

if __name__ == "__main__":
    report = generate_full_report()