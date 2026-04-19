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

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
       """
        Executa uma query SQL (INSERT, UPDATE, DELETE) com commit automático.

        Args:
            query: A instrução SQL a executar.
            params: Parâmetros para substituir os '?' na query (evita SQL injection).

        Returns:
            sqlite3.Cursor: Cursor com o resultado da execução.

        Raises:
            sqlite3.Error: Se a execução falhar (faz rollback automático).
        """
       if self.connection is None:
           raise RuntimeError("Conexão à base de dados não estabelecida. Chame connect() primeiro.")
       
       try:
           cursor = self.connection.execute(query, params)
           self.connection.commit() # Commit automático para garantir persistência
           return cursor
       except sqlite3.Error as e:
           self.connection.rollback() # Rollback automático em caso de erro
           raise e
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict[str, Any]]:
        """
        Executa uma query SELECT e retorna UMA linha como dicionário.

        Args:
            query: A instrução SELECT.
            params: Parâmetros para a query.

        Returns:
            dict com os dados da linha, ou None se não houver resultados.
        """
        if self.connection is None:
            raise RuntimeError("Base de dados não esta conectada.")
        
        cursor = self.connection.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """
        Executa uma query SELECT e retorna TODAS as linhas como lista de dicionários.

        Args:
            query: A instrução SELECT.
            params: Parâmetros para a query.

        Returns:
            Lista de dicionários (vazia se não houver resultados).
        """
        if self.connection is None:
            raise RuntimeError("Base de dados não esta conectada.")
        
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def execute_script(self, sql_script: str) -> None:
        """
        Executa um script SQL completo (várias instruções separadas por ';').

        Usado principalmente para criar o schema a partir do ficheiro schema.sql.

        Args:
            sql_script: String contendo um ou mais comandos SQL.
        """ 
        if self.connection is None:
            raise RuntimeError("Base de dados não esta conectada.")
        
        self.connection.executescript(sql_script)
        self.connection.commit() # Commit automático para garantir persistência

    # -----------------------------------------------------------------
    # Suporte a Context Manager (permite usar 'with Database() as db:')
    # -----------------------------------------------------------------

    def __enter__(self) -> "Database":
        """Permite usar a classe com o statement 'with' (abre a ligação)."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Fecha a ligação automaticamente ao sair do bloco 'with'."""
        self.close()    