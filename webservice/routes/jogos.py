"""
Módulo de Rotas: Jogos.

Define os endpoints REST para o CRUD de jogos:
    GET    /api/jogos        -> Lista todos os jogos (com filtros opcionais)
    GET    /api/jogos/<id>   -> Obtém um jogo específico
    POST   /api/jogos        -> Cria um novo jogo
    PUT    /api/jogos/<id>   -> Atualiza um jogo existente
    DELETE /api/jogos/<id>   -> Remove um jogo

A tabela 'jogos' está normalizada (FKs para criadores/editoras/generos),
mas a API expõe os nomes diretamente. A conversão nome <-> ID é feita
via 'get_or_create' (cria automaticamente se o nome não existir).

Todas as comunicações usam JSON.
"""
from flask import Blueprint, request, jsonify

from database.connection import Database
from webservice.config import Config
from models.jogo import Jogo

jogos_bp = Blueprint("jogos", __name__, url_prefix=f"{Config.API_PREFIX}/jogos")


# Campos obrigatórios ao criar um jogo
CAMPOS_OBRIGATORIOS = ["titulo", "preco"]

# Query base com JOINs (devolve os nomes dos catálogos)
SELECT_JOGO_SQL = """
    SELECT
        j.id_jogo,
        j.titulo,
        j.preco,
        j.stock,
        j.ano_lancamento,
        j.idade_minima,
        c.nome AS criador,
        e.nome AS editora,
        g.nome AS genero
    FROM jogos j
    LEFT JOIN criadores c ON j.id_criador = c.id_criador
    LEFT JOIN editoras  e ON j.id_editora = e.id_editora
    LEFT JOIN generos   g ON j.id_genero  = g.id_genero
"""


# ============================================================
# HELPERS
# ============================================================

def _get_or_create(db: Database, tabela: str, id_col: str,
                   nome: str | None) -> int | None:
    """
    Devolve o ID de um catálogo pelo nome. Cria se não existir.

    Args:
        db: conexão à BD.
        tabela: 'criadores', 'editoras' ou 'generos'.
        id_col: nome da coluna PK.
        nome: nome a procurar/inserir. Se None/vazio, devolve None.

    Returns:
        ID existente, recém-criado, ou None.
    """
    if not nome or not str(nome).strip():
        return None

    nome = str(nome).strip()
    row = db.fetch_one(
        f"SELECT {id_col} FROM {tabela} WHERE nome = ? COLLATE NOCASE;",
        (nome,),
    )
    if row:
        return row[id_col]

    cursor = db.execute(f"INSERT INTO {tabela} (nome) VALUES (?);", (nome,))
    return cursor.lastrowid


def _buscar_jogo(db: Database, id_jogo: int) -> dict | None:
    """Devolve um jogo (com nomes via JOINs) ou None."""
    row = db.fetch_one(SELECT_JOGO_SQL + " WHERE j.id_jogo = ?;", (id_jogo,))
    return dict(row) if row else None


# ============================================================
# GET /api/jogos  -> Lista todos os jogos (com filtros)
# ============================================================
@jogos_bp.route("", methods=["GET"])
def listar_jogos():
    """
    Retorna a lista de jogos com nomes de criador/editora/género.

    Query params (todos opcionais):
        q          : pesquisa por título (LIKE)
        genero     : filtra por nome de género
        preco_max  : preço máximo
        idade_max  : idade mínima do jogo <= este valor
        em_stock   : 'true' para mostrar apenas com stock > 0
    """
    try:
        q = request.args.get("q", "").strip()
        genero = request.args.get("genero", "").strip()
        preco_max = request.args.get("preco_max", type=float)
        idade_max = request.args.get("idade_max", type=int)
        em_stock = request.args.get("em_stock", "").lower() == "true"

        sql = SELECT_JOGO_SQL
        where = []
        params: list = []

        if q:
            where.append("j.titulo LIKE ? COLLATE NOCASE")
            params.append(f"%{q}%")
        if genero:
            where.append("g.nome = ? COLLATE NOCASE")
            params.append(genero)
        if preco_max is not None:
            where.append("j.preco <= ?")
            params.append(preco_max)
        if idade_max is not None:
            where.append("j.idade_minima <= ?")
            params.append(idade_max)
        if em_stock:
            where.append("j.stock > 0")

        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY j.titulo COLLATE NOCASE;"

        with Database(str(Config.DATABASE_PATH)) as db:
            rows = db.fetch_all(sql, tuple(params))
            jogos = [dict(r) for r in rows]

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
    """Retorna os dados de um único jogo pelo seu ID (com JOINs)."""
    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            jogo = _buscar_jogo(db, id_jogo)

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
    """
    Cria um novo jogo.

    Campos obrigatórios: titulo, preco.
    Campos opcionais: stock, ano_lancamento, idade_minima,
                      criador, editora, genero (criados se não existirem).
    """
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "sucesso": False,
            "erro": "Corpo JSON em falta ou inválido."
        }), 400

    em_falta = [c for c in CAMPOS_OBRIGATORIOS if c not in dados]
    if em_falta:
        return jsonify({
            "sucesso": False,
            "erro": f"Campos obrigatórios em falta: {em_falta}"
        }), 400

    # Valida via modelo (levanta ValueError em campos inválidos)
    try:
        jogo = Jogo.from_dict(dados)
    except (ValueError, TypeError, KeyError) as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Dados inválidos: {e}"
        }), 400

    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            id_criador = _get_or_create(db, "criadores", "id_criador", jogo.criador)
            id_editora = _get_or_create(db, "editoras",  "id_editora", jogo.editora)
            id_genero  = _get_or_create(db, "generos",   "id_genero",  jogo.genero)

            cursor = db.execute(
                """
                INSERT INTO jogos
                    (titulo, id_criador, id_editora, id_genero,
                     ano_lancamento, idade_minima, preco, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    jogo.titulo, id_criador, id_editora, id_genero,
                    jogo.ano_lancamento, jogo.idade_minima,
                    jogo.preco, jogo.stock,
                ),
            )
            jogo_criado = _buscar_jogo(db, cursor.lastrowid)

        return jsonify({
            "sucesso": True,
            "mensagem": "Jogo criado com sucesso.",
            "jogo": jogo_criado
        }), 201

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


# ============================================================
# PUT /api/jogos/<id>  -> Atualiza um jogo existente
# ============================================================
@jogos_bp.route("/<int:id_jogo>", methods=["PUT"])
def atualizar_jogo(id_jogo: int):
    """Atualiza os campos enviados no JSON. Atualização parcial permitida."""
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "sucesso": False,
            "erro": "Corpo JSON em falta ou inválido."
        }), 400

    campos_permitidos = {
        "titulo", "preco", "stock", "ano_lancamento", "idade_minima",
        "criador", "editora", "genero",
    }
    enviados = {k: v for k, v in dados.items() if k in campos_permitidos}

    if not enviados:
        return jsonify({
            "sucesso": False,
            "erro": "Nenhum campo válido para atualizar."
        }), 400

    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            atual = _buscar_jogo(db, id_jogo)
            if atual is None:
                return jsonify({
                    "sucesso": False,
                    "erro": f"Jogo com id {id_jogo} não encontrado."
                }), 404

            # Funde dados atuais com os novos e valida via modelo
            merged = {**atual, **enviados}
            try:
                jogo = Jogo.from_dict(merged)
            except (ValueError, TypeError, KeyError) as e:
                return jsonify({
                    "sucesso": False,
                    "erro": f"Dados inválidos: {e}"
                }), 400

            id_criador = _get_or_create(db, "criadores", "id_criador", jogo.criador)
            id_editora = _get_or_create(db, "editoras",  "id_editora", jogo.editora)
            id_genero  = _get_or_create(db, "generos",   "id_genero",  jogo.genero)

            db.execute(
                """
                UPDATE jogos
                SET titulo = ?, id_criador = ?, id_editora = ?, id_genero = ?,
                    ano_lancamento = ?, idade_minima = ?, preco = ?, stock = ?
                WHERE id_jogo = ?
                """,
                (
                    jogo.titulo, id_criador, id_editora, id_genero,
                    jogo.ano_lancamento, jogo.idade_minima,
                    jogo.preco, jogo.stock, id_jogo,
                ),
            )
            jogo_atualizado = _buscar_jogo(db, id_jogo)

        return jsonify({
            "sucesso": True,
            "mensagem": "Jogo atualizado com sucesso.",
            "jogo": jogo_atualizado
        }), 200

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


# ============================================================
# DELETE /api/jogos/<id>  -> Remove um jogo
# ============================================================
@jogos_bp.route("/<int:id_jogo>", methods=["DELETE"])
def remover_jogo(id_jogo: int):
    """
    Remove um jogo pelo seu ID.
    Bloqueia se o jogo tiver itens de venda associados (409).
    """
    try:
        with Database(str(Config.DATABASE_PATH)) as db:
            if _buscar_jogo(db, id_jogo) is None:
                return jsonify({
                    "sucesso": False,
                    "erro": f"Jogo com id {id_jogo} não encontrado."
                }), 404

            usado = db.fetch_one(
                "SELECT COUNT(*) AS total FROM itens_venda WHERE id_jogo = ?;",
                (id_jogo,),
            )
            if usado and usado["total"] > 0:
                return jsonify({
                    "sucesso": False,
                    "erro": (f"Não é possível apagar: existem "
                             f"{usado['total']} item(s) de venda associados.")
                }), 409

            db.execute("DELETE FROM jogos WHERE id_jogo = ?", (id_jogo,))

        return jsonify({
            "sucesso": True,
            "mensagem": f"Jogo {id_jogo} removido com sucesso."
        }), 200

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500
