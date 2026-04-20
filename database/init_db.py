"""
Script de Inicialização da Base de Dados.

Lê o ficheiro schema.sql e cria todas as tabelas na base de dados SQLite.

Uso:
    python -m database.init_db

Este script pode ser executado múltiplas vezes sem problema:
    - Se a BD não existir, cria-a.
    - Se as tabelas já existirem, não faz nada (devido ao IF NOT EXISTS).
    - Se usares o parâmetro --reset, apaga a BD antes de criar (CUIDADO!).
"""

import sys
from pathlib import Path

from database.connection import Database


# Caminho base: pasta 'database' (onde este ficheiro está)
BASE_DIR = Path(__file__).resolve().parent

# Caminhos para os ficheiros
SCHEMA_FILE = BASE_DIR / "schema.sql"
DB_FILE = BASE_DIR / "loja_jogos.db"

def read_schema() -> str:
    """
    Lê o conteúdo do ficheiro schema.sql.

    Returns:
        str: Todo o conteúdo SQL como texto.

    Raises:
        FileNotFoundError: Se schema.sql não existir.
    """
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Ficheiro de esquema não encontrado: {SCHEMA_FILE}")
    
    return SCHEMA_FILE.read_text(encoding="utf-8")

def init_database(reset: bool = False) -> None:
    """
    Inicializa a base de dados executando o schema.sql.

    Args:
        reset: Se True, apaga a BD existente antes de criar. Default: False.
    """
    # Se reset=True, apaga o ficheiro .db existente
    if reset and DB_FILE.exists():
        print(f"Apagando a base de dados existente: {DB_FILE.name}")
        DB_FILE.unlink()  # Apaga o ficheiro

    # Lê o esquema SQL
    print(f"Lendo esquema SQL de: {SCHEMA_FILE.name}")
    schema_sql = read_schema()

    # Usa a classe Database com context manager
    print(f"Criando/Atualizando a base de dados: {DB_FILE.name}")
    with Database(str(DB_FILE)) as db:
        cursor = db.execute_script(schema_sql)  # Executa o esquema SQL

    print("Base de dados inicializada com sucesso.")
    print(f"Localização da BD: {DB_FILE}")

def list_tables() -> None:
    """
    Lista todas as tabelas criadas na base de dados.

    Útil para verificar que a inicialização correu bem.
    """
    with Database(str(DB_FILE)) as db:
        tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

    if not tables:
        print("Nenhuma tabela encontrada na base de dados.")
        return

    print("\nTabelas encontradas na base de dados:")
    for table in tables:
        print(f" - {table['name']}")

if __name__ == "__main__":
    # Verifica se o utilizador passou --reset foi passado
    reset_flag = "--reset" in sys.argv

    try:
        init_database(reset=reset_flag)
        list_tables()   
    except Exception as e:
        print(f"Erro ao inicializar a base de dados: {e}")
        sys.exit(1)         