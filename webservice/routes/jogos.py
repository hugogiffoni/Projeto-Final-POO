"""
Módulo de Rotas: Jogos.

Define os endpoints REST para o CRUD de jogos:
    GET    /api/jogos        -> Lista todos os jogos
    GET    /api/jogos/<id>   -> Obtém um jogo específico
    POST   /api/jogos        -> Cria um novo jogo
    PUT    /api/jogos/<id>   -> Atualiza um jogo existente
    DELETE /api/jogos/<id>   -> Remove um jogo

Todas as comunicações usam JSON.
"""
from flask import Blueprint, request, jsonify
from database.connection import Database
from config import Config

# Blueprint = "mini-app" Flask que agrupa rotas relacionadas.
# url_prefix faz com que TODAS as rotas comecem por /api/jogos
jogos_bp = Blueprint("jogos", __name__, url_prefix=f"{Config.API_PREFIX}/jogos")


# Campos obrigatórios ao criar um jogo (validação no POST)
CAMPOS_OBRIGATORIOS = ["titulo", "criador", "editora", "ano_lancamento",
                       "genero", "idade_minima", "preco"]

# ============================================================
# GET /api/jogos  -> Lista todos os jogos
# ============================================================
@jogos_bp.route("", methods=["GET"])
def listar_jogos():
    """Retorna a lista completa de jogos da base de dados."""
    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            jogos = db.fetch_all("SELECT * FROM jogos ORDER BY titulo")

        return jsonify({
            "sucesso": True,
            "total": len(jogos),
            "jogos": jogos
        }), 200

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500

# ============================================================
# GET /api/jogos/<id>  -> Obtém UM jogo específico
# ============================================================
@jogos_bp.route("/<int:id_jogo>", methods=["GET"])
def obter_jogo(id_jogo: int):
    """Retorna os dados de um único jogo pelo seu ID."""
    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            jogo = db.fetch_one(
                "SELECT * FROM jogos WHERE id_jogo = ?",
                (id_jogo,)
            )

        if jogo is None:
            return jsonify({
                "sucesso": False,
                "erro": f"Jogo com id {id_jogo} não encontrado."
            }), 404
        
        return jsonify({"sucesso": True, "jogo": jogo}), 200
    
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500

# ============================================================
# POST /api/jogos  -> Cria um novo jogo
# ============================================================

@jogos_bp.route("", methods=["POST"])
def criar_jogo():
    """Cria um novo jogo. Espera JSON com todos os campos obrigatórios."""
    dados = request.get_json(silent=True)

    # Validação 1: corpo JSON existe?
    if not dados:
        return jsonify({
            "sucesso": False,
            "erro": "Corpo JSON em falta ou inválido."
        }), 400
    
    # Validação 2: todos os campos obrigatórios estão presentes?
    em_falta = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in dados]
    if em_falta:
        return jsonify({
            "sucesso": False,
            "erro": f"Campos obrigatórios em falta: {em_falta}"
        }), 400
    
    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            cursor = db.execute(
                """
                INSERT INTO jogos
                    (titulo, criador, editora, ano_lancamento,
                     genero, idade_minima, preco)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados["titulo"],
                    dados["criador"],
                    dados["editora"],
                    dados["ano_lancamento"],
                    dados["genero"],
                    dados["idade_minima"],
                    dados["preco"],
                )
            )
            novo_id = cursor.lastrowid

            # Buscar o jogo recém-criado para devolver ao cliente
            jogo_criado = db.fetch_one(
                "SELECT * FROM jogos WHERE id_jogo = ?",
                (novo_id,)
            )

        return jsonify({
            "sucesso": True,
            "mensagem": "Jogo criado com sucesso.",
            "jogo": jogo_criado
        }), 201   # 201 Created

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500
