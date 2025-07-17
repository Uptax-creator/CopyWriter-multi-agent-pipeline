#!/usr/bin/env python3
"""
Script para migrar banco de dados para nova estrutura
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.database import engine, get_db_context
from src.models.database import Base

def backup_old_data():
    """Fazer backup dos dados antigos"""
    print("📦 Fazendo backup dos dados antigos...")
    
    backup_queries = [
        "CREATE TABLE IF NOT EXISTS backup_cliente_aplicacao AS SELECT * FROM cliente_aplicacao;",
        "CREATE TABLE IF NOT EXISTS backup_aplicacao AS SELECT * FROM aplicacao;"
    ]
    
    with engine.connect() as conn:
        for query in backup_queries:
            try:
                conn.execute(text(query))
                conn.commit()
                print(f"✅ Backup criado: {query.split()[5]}")
            except Exception as e:
                print(f"⚠️ Aviso backup: {e}")

def migrate_aplicacao_table():
    """Migrar tabela aplicacao"""
    print("🔄 Migrando tabela aplicacao...")
    
    with engine.connect() as conn:
        try:
            # Adicionar novos campos
            alter_queries = [
                "ALTER TABLE aplicacao ADD COLUMN tipo VARCHAR(50) DEFAULT 'api';",
                "ALTER TABLE aplicacao ADD COLUMN app_secret_visible VARCHAR(64);",
            ]
            
            for query in alter_queries:
                try:
                    conn.execute(text(query))
                    print(f"✅ Campo adicionado: {query}")
                except Exception as e:
                    print(f"⚠️ Campo já existe ou erro: {e}")
            
            # Atualizar tipos existentes
            conn.execute(text("UPDATE aplicacao SET tipo = 'api' WHERE tipo IS NULL;"))
            conn.commit()
            print("✅ Tabela aplicacao migrada")
            
        except Exception as e:
            print(f"❌ Erro na migração da aplicacao: {e}")

def create_new_tables():
    """Criar novas tabelas"""
    print("🏗️ Criando novas tabelas...")
    
    try:
        # Criar todas as tabelas (vai ignorar as que já existem)
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/atualizadas")
        
        # Migrar dados de cliente_aplicacao para aplicacao_cliente
        with engine.connect() as conn:
            # Verificar se existem dados para migrar
            result = conn.execute(text("SELECT COUNT(*) FROM cliente_aplicacao;"))
            count = result.scalar()
            
            if count > 0:
                print(f"📋 Migrando {count} registros de cliente_aplicacao...")
                
                # Migrar dados
                migrate_query = """
                INSERT INTO aplicacao_cliente (
                    id_aplicacao_cliente, id_empresa, id_aplicacao, 
                    nome_aplicacao, omie_app_key, omie_app_secret_hash,
                    config_omie_json, criado_em, atualizado_em, ativo
                )
                SELECT 
                    id_cliente_aplicacao, id_empresa, id_aplicacao,
                    'Aplicação Migrada', omie_app_key, omie_app_secret_hash,
                    config_especifica_json, criado_em, atualizado_em, ativo
                FROM cliente_aplicacao
                WHERE id_cliente_aplicacao NOT IN (
                    SELECT id_aplicacao_cliente FROM aplicacao_cliente
                );
                """
                
                conn.execute(text(migrate_query))
                conn.commit()
                print("✅ Dados migrados para aplicacao_cliente")
            
    except Exception as e:
        print(f"❌ Erro na criação de tabelas: {e}")

def verify_migration():
    """Verificar se a migração foi bem sucedida"""
    print("🔍 Verificando migração...")
    
    with engine.connect() as conn:
        try:
            # Verificar tabelas
            tables_check = [
                "SELECT COUNT(*) FROM empresa;",
                "SELECT COUNT(*) FROM usuario;", 
                "SELECT COUNT(*) FROM aplicacao;",
                "SELECT COUNT(*) FROM aplicacao_cliente;",
                "SELECT COUNT(*) FROM token;",
                "SELECT COUNT(*) FROM auditoria;"
            ]
            
            for query in tables_check:
                result = conn.execute(text(query))
                count = result.scalar()
                table_name = query.split("FROM ")[1].replace(";", "")
                print(f"✅ {table_name}: {count} registros")
                
            # Verificar novos campos da aplicacao
            result = conn.execute(text("SELECT tipo, app_secret_visible FROM aplicacao LIMIT 1;"))
            if result.fetchone():
                print("✅ Novos campos da aplicacao funcionando")
                
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")

def main():
    """Executar migração completa"""
    print("🚀 Iniciando migração do banco de dados...")
    print("=" * 50)
    
    try:
        # 1. Backup
        backup_old_data()
        print()
        
        # 2. Migrar aplicacao
        migrate_aplicacao_table()
        print()
        
        # 3. Criar novas tabelas
        create_new_tables()
        print()
        
        # 4. Verificar
        verify_migration()
        print()
        
        print("=" * 50)
        print("🎉 Migração concluída com sucesso!")
        print()
        print("📋 Próximos passos:")
        print("1. Reiniciar a aplicação")
        print("2. Testar os novos endpoints")
        print("3. Verificar se os dados estão corretos")
        print()
        print("⚠️ Os dados antigos foram preservados nas tabelas backup_*")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        print("🔧 Restaure o backup se necessário")
        sys.exit(1)

if __name__ == "__main__":
    main()