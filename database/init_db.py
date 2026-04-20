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