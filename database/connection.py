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
    def connect(self) -> sqlite3.connection:
        """
        Abre uma ligação à base de dados.

        Configura a ligação para:
            - Ativar suporte a chaves estrangeiras (PRAGMA foreign_keys).
            - Retornar resultados como sqlite3.Row (acesso tipo dicionário).

        Returns:
            sqlite3.Connection: A ligação ativa.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  # Garante que a pasta existe antes de criar o BD

        self.connection = sqlite3.connect(self.db_path) # Abre a ligação(cria o ficheiro se não existir
        
        self.connection.execute("PRAGMA foreign_keys = ON") # Ativa suporte a chaves estrangeiras (SQLite exige isso em cada ligação)

        self.connection.row_factory = sqlite3.Row # Configura para retornar linhas como Row (permite acesso pelo nome) row["nome"]

        return self.connection
    
    def close(self) -> None:
        """
        Fecha a ligacao a base de dados, se estiver aberta.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            
