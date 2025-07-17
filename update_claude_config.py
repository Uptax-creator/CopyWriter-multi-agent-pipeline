#!/usr/bin/env python3

import json
import os

def update_claude_config():
    """Atualiza configuração do Claude Desktop para usar servidores híbridos"""
    
    # Configuração para usar servidores HTTP híbridos
    config = {
        'mcpServers': {
            'omie-erp': {
                'command': 'python3',
                'args': [
                    '/Users/kleberdossantosribeiro/omie-mcp/omie_mcp_server_hybrid.py',
                    '--mode', 'stdio'
                ]
            },
            'nibo-erp': {
                'command': 'python3', 
                'args': [
                    '/Users/kleberdossantosribeiro/omie-mcp/nibo-mcp/nibo_mcp_server_hybrid.py',
                    '--mode', 'stdio'
                ]
            }
        }
    }
    
    # Salvar configuração
    config_path = os.path.expanduser('~/Library/Application Support/Claude/claude_desktop_config.json')
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ Configuração Claude Desktop atualizada para servidores híbridos')
    print('✅ Modo: STDIO (com suporte HTTP interno)')
    print('✅ Reinicie o Claude Desktop para aplicar as mudanças')
    
    # Mostrar configuração atual
    print('\n📋 Configuração aplicada:')
    print(json.dumps(config, indent=2))

if __name__ == '__main__':
    update_claude_config()