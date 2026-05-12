"""
Rotas dos catálogos auxiliares: géneros, criadores e editoras.

Estes endpoints são read-only (apenas GET) e servem para alimentar
os dropdowns da GUI. A criação automática de novos valores acontece
nas rotas de jogos via lógica 'get_or_create'.
"""
from flask import Blueprint, jsonify

from database.connection import Database
from database.init_db import DB_FILE

catalogos_bp = Blueprint("catalogos", __name__, url_prefix="/api")

def _listar(tabela: str, id_col: str) -> list[dict]:
    """Helper genérico para listar registos de uma tabela de catálogo."""
    with Database(str(DB_FILE)) as db:
        rows = db.fetch_all(
            f"SELECT {id_col}, nome FROM {tabela} ORDER BY nome COLLATE NOCASE;"
        )
    return [dict(r) for r in rows]