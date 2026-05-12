"""
Endpoints REST para Vendas.

Fluxo de uma venda:
    1. Validar cliente e itens recebidos.
    2. Verificar stock disponível de cada jogo.
    3. INICIAR TRANSAÇÃO:
        a) INSERT em 'vendas' (cabeçalho).
        b) INSERT em 'itens_venda' para cada linha.
        c) UPDATE em 'jogos' para descontar stock.
    4. COMMIT se tudo correu bem; ROLLBACK em qualquer erro.
"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from database.db import get_db
from models.item_venda import ItemVenda
from models.venda import Venda

vendas_bp = Blueprint("vendas", __name__, url_prefix="/api/vendas")


# ---------------------------------------------------------------- helpers
def _venda_row_to_dict(row, itens: list[dict]) -> dict:
    """Converte uma linha da BD (cabeçalho) + lista de itens num dict completo."""
    return {
        "id_venda": row["id_venda"],
        "id_cliente": row["id_cliente"],
        "nome_cliente": row["nome_cliente"],
        "data_hora": row["data_hora"],
        "desconto": row["desconto"],
        "valor_total": row["valor_total"],
        "total_itens": sum(i["quantidade"] for i in itens),
        "itens": itens,
    }


def _carregar_itens(db, id_venda: int) -> list[dict]:
    """Carrega todos os itens de uma venda, já com o título do jogo (JOIN)."""
    rows = db.execute(
        """
        SELECT iv.id_item, iv.id_venda, iv.id_jogo, iv.quantidade,
               iv.preco_unitario, j.titulo
          FROM itens_venda iv
          JOIN jogos j ON j.id_jogo = iv.id_jogo
         WHERE iv.id_venda = ?
         ORDER BY iv.id_item
        """,
        (id_venda,),
    ).fetchall()

    return [
        {
            "id_item": r["id_item"],
            "id_venda": r["id_venda"],
            "id_jogo": r["id_jogo"],
            "titulo": r["titulo"],
            "quantidade": r["quantidade"],
            "preco_unitario": r["preco_unitario"],
            "subtotal": round(r["quantidade"] * r["preco_unitario"], 2),
        }
        for r in rows
    ]


# ---------------------------------------------------------------- GET /api/vendas
@vendas_bp.route("", methods=["GET"])
def listar_vendas():
    """
    Lista vendas com filtros opcionais:
        ?id_cliente=1   -> só do cliente X
        ?data_inicio=2025-01-01
        ?data_fim=2025-12-31
    """
    id_cliente = request.args.get("id_cliente", type=int)
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    sql = """
        SELECT v.id_venda, v.id_cliente, v.data_hora, v.desconto, v.valor_total,
               c.nome AS nome_cliente
          FROM vendas v
          JOIN clientes c ON c.id_cliente = v.id_cliente
         WHERE 1=1
    """
    params: list = []

    if id_cliente is not None:
        sql += " AND v.id_cliente = ?"
        params.append(id_cliente)
    if data_inicio:
        sql += " AND v.data_hora >= ?"
        params.append(data_inicio)
    if data_fim:
        sql += " AND v.data_hora <= ?"
        params.append(data_fim + " 23:59:59")

    sql += " ORDER BY v.data_hora DESC"

    db = get_db()
    rows = db.execute(sql, params).fetchall()

    vendas = [_venda_row_to_dict(r, _carregar_itens(db, r["id_venda"])) for r in rows]

    return jsonify({"total": len(vendas), "vendas": vendas}), 200


# ---------------------------------------------------------------- GET /api/vendas/<id>
@vendas_bp.route("/<int:id_venda>", methods=["GET"])
def obter_venda(id_venda: int):
    """Devolve uma venda específica com todos os itens."""
    db = get_db()
    row = db.execute(
        """
        SELECT v.id_venda, v.id_cliente, v.data_hora, v.desconto, v.valor_total,
               c.nome AS nome_cliente
          FROM vendas v
          JOIN clientes c ON c.id_cliente = v.id_cliente
         WHERE v.id_venda = ?
        """,
        (id_venda,),
    ).fetchone()

    if row is None:
        return jsonify({"erro": "Venda não encontrada."}), 404

    itens = _carregar_itens(db, id_venda)
    return jsonify(_venda_row_to_dict(row, itens)), 200


# ---------------------------------------------------------------- POST /api/vendas
@vendas_bp.route("", methods=["POST"])
def criar_venda():
    """
    Regista uma nova venda.

    Body JSON esperado:
        {
            "id_cliente": 1,
            "desconto": 10,              // opcional, default 0
            "itens": [
                {"id_jogo": 5, "quantidade": 2},
                {"id_jogo": 7, "quantidade": 1}
            ]
        }

    Notas:
        - preco_unitario é obtido da BD (NUNCA confiar no que vem do cliente).
        - Stock é validado e descontado automaticamente.
        - Toda a operação é atómica (transação).
    """
    data = request.get_json(silent=True) or {}

    # Validação básica de entrada
    if "id_cliente" not in data:
        return jsonify({"erro": "Campo 'id_cliente' é obrigatório."}), 400
    if not data.get("itens"):
        return jsonify({"erro": "A venda tem de ter pelo menos um item."}), 400

    try:
        id_cliente = int(data["id_cliente"])
        desconto = float(data.get("desconto", 0) or 0)
    except (TypeError, ValueError):
        return jsonify({"erro": "id_cliente ou desconto inválidos."}), 400

    if not (0 <= desconto <= 100):
        return jsonify({"erro": "desconto tem de estar entre 0 e 100."}), 400

    db = get_db()

    # 1) Verificar se o cliente existe
    cliente = db.execute(
        "SELECT id_cliente, nome FROM clientes WHERE id_cliente = ?",
        (id_cliente,),
    ).fetchone()
    if cliente is None:
        return jsonify({"erro": f"Cliente {id_cliente} não existe."}), 404

    # 2) Construir os ItemVenda a partir dos dados da BD (preço + stock)
    venda = Venda(id_cliente=id_cliente, desconto=desconto,
                  nome_cliente=cliente["nome"])

    for raw in data["itens"]:
        if "id_jogo" not in raw or "quantidade" not in raw:
            return jsonify({"erro": "Cada item precisa de 'id_jogo' e 'quantidade'."}), 400

        try:
            id_jogo = int(raw["id_jogo"])
            quantidade = int(raw["quantidade"])
        except (TypeError, ValueError):
            return jsonify({"erro": "id_jogo/quantidade inválidos."}), 400

        jogo = db.execute(
            "SELECT id_jogo, titulo, preco, stock FROM jogos WHERE id_jogo = ?",
            (id_jogo,),
        ).fetchone()

        if jogo is None:
            return jsonify({"erro": f"Jogo {id_jogo} não existe."}), 404

        if jogo["stock"] < quantidade:
            return jsonify({
                "erro": f"Stock insuficiente para '{jogo['titulo']}' "
                        f"(pedido: {quantidade}, disponível: {jogo['stock']})."
            }), 409

        try:
            item = ItemVenda(
                id_jogo=jogo["id_jogo"],
                quantidade=quantidade,
                preco_unitario=jogo["preco"],
            )
            venda.adicionar_item(item)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    # 3) Validação final da venda
    try:
        venda.validar()
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    # 4) ⚡ TRANSAÇÃO ATÓMICA ⚡
    try:
        data_hora_str = venda.data_hora.strftime("%Y-%m-%d %H:%M:%S")
        valor_total = venda.valor_total()

        # 4a) Inserir cabeçalho
        cursor = db.execute(
            """
            INSERT INTO vendas (id_cliente, data_hora, desconto, valor_total)
            VALUES (?, ?, ?, ?)
            """,
            (id_cliente, data_hora_str, desconto, valor_total),
        )
        id_venda = cursor.lastrowid

        # 4b) Inserir itens + descontar stock
        for item in venda.itens:
            db.execute(
                """
                INSERT INTO itens_venda (id_venda, id_jogo, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (id_venda, item.id_jogo, item.quantidade, item.preco_unitario),
            )
            db.execute(
                "UPDATE jogos SET stock = stock - ? WHERE id_jogo = ?",
                (item.quantidade, item.id_jogo),
            )

        db.commit()  # ✅ Tudo OK!

    except Exception as e:
        db.rollback()  # ❌ Algo falhou — desfaz tudo
        return jsonify({"erro": f"Erro ao registar venda: {e}"}), 500

    # 5) Devolver a venda completa recém-criada
    itens_persistidos = _carregar_itens(db, id_venda)
    resposta = {
        "id_venda": id_venda,
        "id_cliente": id_cliente,
        "nome_cliente": cliente["nome"],
        "data_hora": data_hora_str,
        "desconto": desconto,
        "valor_total": valor_total,
        "total_itens": sum(i["quantidade"] for i in itens_persistidos),
        "itens": itens_persistidos,
    }
    return jsonify(resposta), 201


# ---------------------------------------------------------------- DELETE /api/vendas/<id>
@vendas_bp.route("/<int:id_venda>", methods=["DELETE"])
def anular_venda(id_venda: int):
    """
    Anula uma venda e DEVOLVE o stock dos jogos.

    Útil para correção de erros do call center.
    Operação também atómica.
    """
    db = get_db()

    # Verificar se existe
    venda = db.execute(
        "SELECT id_venda FROM vendas WHERE id_venda = ?", (id_venda,)
    ).fetchone()
    if venda is None:
        return jsonify({"erro": "Venda não encontrada."}), 404

    # Buscar itens para devolver stock
    itens = db.execute(
        "SELECT id_jogo, quantidade FROM itens_venda WHERE id_venda = ?",
        (id_venda,),
    ).fetchall()

    try:
        # Devolver stock
        for it in itens:
            db.execute(
                "UPDATE jogos SET stock = stock + ? WHERE id_jogo = ?",
                (it["quantidade"], it["id_jogo"]),
            )
        # Apagar itens e venda (ON DELETE CASCADE também faria, mas explicitar é mais seguro)
        db.execute("DELETE FROM itens_venda WHERE id_venda = ?", (id_venda,))
        db.execute("DELETE FROM vendas WHERE id_venda = ?", (id_venda,))
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"erro": f"Erro ao anular venda: {e}"}), 500

    return jsonify({"mensagem": f"Venda {id_venda} anulada e stock reposto."}), 200


# ---------------------------------------------------------------- GET histórico cliente
@vendas_bp.route("/cliente/<int:id_cliente>", methods=["GET"])
def historico_cliente(id_cliente: int):
    """
    Histórico de vendas de um cliente específico.
    Requisito explícito do briefing: "Visualização do histórico de vendas de um cliente."
    """
    db = get_db()

    cliente = db.execute(
        "SELECT id_cliente, nome FROM clientes WHERE id_cliente = ?",
        (id_cliente,),
    ).fetchone()
    if cliente is None:
        return jsonify({"erro": "Cliente não encontrado."}), 404

    rows = db.execute(
        """
        SELECT v.id_venda, v.id_cliente, v.data_hora, v.desconto, v.valor_total,
               c.nome AS nome_cliente
          FROM vendas v
          JOIN clientes c ON c.id_cliente = v.id_cliente
         WHERE v.id_cliente = ?
         ORDER BY v.data_hora DESC
        """,
        (id_cliente,),
    ).fetchall()

    vendas = [_venda_row_to_dict(r, _carregar_itens(db, r["id_venda"])) for r in rows]

    total_gasto = round(sum(v["valor_total"] for v in vendas), 2)

    return jsonify({
        "cliente": {"id_cliente": cliente["id_cliente"], "nome": cliente["nome"]},
        "total_vendas": len(vendas),
        "total_gasto": total_gasto,
        "vendas": vendas,
    }), 200
