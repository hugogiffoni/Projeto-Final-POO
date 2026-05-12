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

# ---------------------------------------------------------------------
# GET /api/clientes/<id>  → obter um
# ---------------------------------------------------------------------
@clientes_bp.route("/<int:id_cliente>", methods=["GET"])
def obter_cliente(id_cliente: int):
    """Devolve um cliente específico pelo ID."""
    db = _get_db()
    try:
        row = db.fetch_one(
            "SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,)
        )
        if not row:
            return jsonify({"erro": f"Cliente {id_cliente} não encontrado."}), 404

        return jsonify(Cliente.from_dict(row).to_dict()), 200
    finally:
        db.close()  

# ---------------------------------------------------------------------
# POST /api/clientes  → criar novo
# ---------------------------------------------------------------------
@clientes_bp.route("", methods=["POST"])
def criar_cliente():
    """Cria um novo cliente."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"erro": "Corpo JSON ausente ou inválido."}), 400

    db = _get_db()
    try:
        # Cria instância (dispara validações dos setters)
        try:
            cliente = Cliente.from_dict(data)
        except (ValueError, KeyError) as e:
            return jsonify({"erro": str(e)}), 400

        # Verifica email duplicado (se fornecido)
        if cliente.email:
            existe = db.fetch_one(
                "SELECT id_cliente FROM clientes WHERE email = ?", (cliente.email,)
            )
            if existe:
                return jsonify(
                    {"erro": f"Já existe um cliente com o email '{cliente.email}'."}
                ), 409

        # Insere na BD
        novo_id = db.execute(
            """
            INSERT INTO clientes (nome, morada, telefone, email)
            VALUES (?, ?, ?, ?)
            """,
            (cliente.nome, cliente.morada, cliente.telefone, cliente.email),
        )

        # Devolve o registo completo (já com id e data_registo)
        row = db.fetch_one(
            "SELECT * FROM clientes WHERE id_cliente = ?", (novo_id,)
        )
        return jsonify(Cliente.from_dict(row).to_dict()), 201
    finally:
        db.close()
