"""
Módulo de Rotas: Catálogos auxiliares.

Endpoints read-only para alimentar dropdowns na GUI:
    GET /api/generos
    GET /api/criadores
    GET /api/editoras

A criação automática de novos valores acontece nas rotas de jogos
via lógica 'get_or_create'.
"""
from flask import Blueprint, jsonify

from database.connection import Database
from webservice.config import Config

catalogos_bp = Blueprint(
    "catalogos", __name__, url_prefix=Config.API_PREFIX
)


def _listar(tabela: str, id_col: str) -> list[dict]:
    """Helper genérico: lista registos de uma tabela de catálogo."""
    with Database(str(Config.DATABASE_PATH)) as db:
        rows = db.fetch_all(
            f"SELECT {id_col}, nome FROM {tabela} "
            f"ORDER BY nome COLLATE NOCASE;"
        )
    return [dict(r) for r in rows]


@catalogos_bp.route("/generos", methods=["GET"])
def listar_generos():
    """Lista todos os géneros disponíveis."""
    try:
        generos = _listar("generos", "id_genero")
        return jsonify({
            "sucesso": True, "total": len(generos), "generos": generos
        }), 200
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@catalogos_bp.route("/criadores", methods=["GET"])
def listar_criadores():
    """Lista todos os criadores/designers disponíveis."""
    try:
        criadores = _listar("criadores", "id_criador")
        return jsonify({
            "sucesso": True, "total": len(criadores), "criadores": criadores
        }), 200
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@catalogos_bp.route("/editoras", methods=["GET"])
def listar_editoras():
    """Lista todas as editoras disponíveis."""
    try:
        editoras = _listar("editoras", "id_editora")
        return jsonify({
            "sucesso": True, "total": len(editoras), "editoras": editoras
        }), 200
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500
