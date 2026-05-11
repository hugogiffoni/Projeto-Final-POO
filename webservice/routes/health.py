"""
Endpoint de Health Check.

Permite verificar se o web service está a funcionar e se a base
de dados está acessível. Útil para testes e monitorização.
"""

from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify

from database.connection import Database
from webservice.config import Config

# Blueprint = "mini-aplicação" Flask que agrupa rotas relacionadas
health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Verifica o estado do serviço.

    Returns:
        JSON com estado do serviço, timestamp e info da BD.
    """
    db_path: Path = Config.DATABASE_PATH
    db_exists = db_path.exists()

    # Tentat contar registros numa tabela (verrifica se a BD responde)
    db_ok = False
    total_jogos = None
    erro_bd = None

    if db_exists:
        try:
            with Database(str(db_path)) as db:
                resultado = db.execute("SELECT COUNT(*) AS total FROM jogos")
                total_jogos = resultado["total"]
                db_ok = True
        except Exception as e:
            erro_bd = str(e)

    return jsonify({
        "status": "ok" if db_ok else "error",
        "servico": "Loja de Jogos de Tabuleiro - API",
        "versao": "1.0.0",     
        "timestamp": datetime.now().isoformat(),
        "database": {
            "caminho": str(db_path),
            "existe": db_exists,
            "acessivel": db_ok,
            "total_jogos": total_jogos,
            "erro": erro_bd
            },
        }), (200 if db_ok else 500)