"""
Configuração do banco de dados SQLite
"""

import os
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import shutil
from datetime import datetime

# Diretório do banco de dados
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "omie_tenant.db"
BACKUP_DIR = DB_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# URL do banco
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Configuração do SQLite
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20,
    },
    echo=False  # True para debug SQL
)

# Habilitar WAL mode para melhor performance
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurar pragmas do SQLite para otimização"""
    cursor = dbapi_connection.cursor()
    
    # WAL mode (Write-Ahead Logging) - melhor para concorrência
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Sincronização normal (balance entre performance e segurança)
    cursor.execute("PRAGMA synchronous=NORMAL")
    
    # Cache size (10MB)
    cursor.execute("PRAGMA cache_size=10000")
    
    # Foreign keys habilitadas
    cursor.execute("PRAGMA foreign_keys=ON")
    
    # Timeout para transações
    cursor.execute("PRAGMA busy_timeout=30000")
    
    cursor.close()

# Sessão do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager para transações manuais"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def backup_database() -> str:
    """Fazer backup do banco de dados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"backup_{timestamp}.db"
    
    try:
        # Fazer checkpoint do WAL antes do backup
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
        
        # Copiar arquivo
        shutil.copy2(DB_PATH, backup_file)
        
        # Comprimir backup se for grande
        if backup_file.stat().st_size > 50 * 1024 * 1024:  # 50MB
            import gzip
            compressed_file = backup_file.with_suffix('.db.gz')
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_file.unlink()  # Remover não comprimido
            backup_file = compressed_file
        
        return str(backup_file)
        
    except Exception as e:
        raise Exception(f"Erro ao fazer backup: {str(e)}")

def restore_database(backup_file: str) -> bool:
    """Restaurar banco de dados do backup"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
    
    try:
        # Fazer backup atual antes de restaurar
        current_backup = backup_database()
        print(f"Backup atual salvo em: {current_backup}")
        
        # Fechar todas as conexões
        engine.dispose()
        
        # Restaurar do backup
        if backup_path.suffix == '.gz':
            import gzip
            with gzip.open(backup_path, 'rb') as f_in:
                with open(DB_PATH, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup_path, DB_PATH)
        
        print(f"Banco restaurado do backup: {backup_file}")
        return True
        
    except Exception as e:
        print(f"Erro ao restaurar backup: {str(e)}")
        return False

def cleanup_old_backups(keep_days: int = 30):
    """Limpar backups antigos"""
    cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
    
    for backup_file in BACKUP_DIR.glob("backup_*.db*"):
        if backup_file.stat().st_mtime < cutoff_time:
            backup_file.unlink()
            print(f"Backup antigo removido: {backup_file}")

def get_db_stats() -> dict:
    """Obter estatísticas do banco de dados"""
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            
            # Tamanho do arquivo
            db_size = DB_PATH.stat().st_size
            
            # Número de tabelas
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Número total de registros (aproximado)
            cursor.execute("""
                SELECT SUM(cnt) FROM (
                    SELECT COUNT(*) as cnt FROM empresa
                    UNION ALL SELECT COUNT(*) FROM usuario
                    UNION ALL SELECT COUNT(*) FROM aplicacao
                    UNION ALL SELECT COUNT(*) FROM cliente_aplicacao
                    UNION ALL SELECT COUNT(*) FROM auditoria
                )
            """)
            total_records = cursor.fetchone()[0] or 0
            
            # Informações do WAL
            cursor.execute("PRAGMA wal_checkpoint")
            
            return {
                "db_size_mb": round(db_size / (1024 * 1024), 2),
                "db_path": str(DB_PATH),
                "table_count": table_count,
                "total_records": total_records,
                "last_backup": get_last_backup_info()
            }
            
    except Exception as e:
        return {"error": str(e)}

def get_last_backup_info() -> dict:
    """Obter informações do último backup"""
    try:
        backup_files = list(BACKUP_DIR.glob("backup_*.db*"))
        if not backup_files:
            return {"status": "no_backups"}
        
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
        backup_size = latest_backup.stat().st_size
        
        return {
            "status": "ok",
            "file": latest_backup.name,
            "created_at": backup_time.strftime("%Y-%m-%d %H:%M:%S"),
            "size_mb": round(backup_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def init_database():
    """Inicializar banco de dados e criar tabelas"""
    from .models.database import Base
    
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        # Fazer backup inicial se não existir
        if not list(BACKUP_DIR.glob("backup_*.db*")):
            backup_file = backup_database()
            print(f"Backup inicial criado: {backup_file}")
        
        print("Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao inicializar banco: {str(e)}")
        return False

# Auto-backup diário (configuração para produção)
def setup_auto_backup():
    """Configurar backup automático"""
    import schedule
    import threading
    import time
    
    def backup_job():
        try:
            backup_file = backup_database()
            cleanup_old_backups()
            print(f"Backup automático criado: {backup_file}")
        except Exception as e:
            print(f"Erro no backup automático: {str(e)}")
    
    # Agendar backup diário às 02:00
    schedule.every().day.at("02:00").do(backup_job)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    # Executar scheduler em thread separada
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("Backup automático configurado (diário às 02:00)")

if __name__ == "__main__":
    # Teste das funções
    init_database()
    stats = get_db_stats()
    print("Estatísticas do banco:", stats)