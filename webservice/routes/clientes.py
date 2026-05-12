"""
Endpoints REST para gestão de Clientes.

Rotas:
    GET    /api/clientes          → Listar todos
    GET    /api/clientes/<id>     → Obter um
    POST   /api/clientes          → Criar
    PUT    /api/clientes/<id>     → Atualizar
    DELETE /api/clientes/<id>     → Apagar
"""

from flask import Blueprint, jsonify, request
from database.connection import Database
from webservice.config import Config
from models.cliente import Cliente

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


def _get_db() -> Database:
    """Cria uma conexão à BD (uma por request)."""
    db = Database(str(Config.DATABASE_PATH))
    db.connect()
    return db

