"""
Módulo de Gestão da Conexão a Base de Dados SQLite.

Fornece a classe Database que encapsula toda a lógica de ligação,
execução de queries e gestão de transações.

Aplica os padrões:
    - Context Manager (with statement) para garantir fecho de ligações
    - Row Factory para retornar resultados como dicionários
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional

class Database:
    """
    Gestor de conexão à base de dados SQLite.

    Esta classe encapsula a lógica de ligação à BD e fornece métodos
    utilitários para executar queries de forma segura.

    Attributes:
        db_path (Path): Caminho para o ficheiro .db da base de dados.
        connection (sqlite3.Connection | None): Ligação ativa à BD.
    """
    def __init__(self, db_path: str = "database/loja_jogos.db") -> None:
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None

