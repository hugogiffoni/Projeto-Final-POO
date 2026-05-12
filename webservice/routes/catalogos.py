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