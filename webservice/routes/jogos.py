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