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

# ---------------------------------------------------------------------
# GET /api/clientes  → listar todos
# ---------------------------------------------------------------------
@clientes_bp.route("", methods=["GET"])
def listar_clientes():
    """Lista todos os clientes (com pesquisa opcional por nome ou email)."""
    db = _get_db()
    try:
        # Pesquisa opcional via ?q=texto
        termo = request.args.get("q", "").strip()

        if termo:
            sql = """
                SELECT * FROM clientes
                WHERE nome LIKE ? OR email LIKE ?
                ORDER BY nome
            """
            param = f"%{termo}%"
            rows = db.fetch_all(sql, (param, param))
        else:
            rows = db.fetch_all("SELECT * FROM clientes ORDER BY nome")

        clientes = [Cliente.from_dict(row).to_dict() for row in rows]
        return jsonify(clientes), 200
    finally:
        db.close()