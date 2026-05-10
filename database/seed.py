"""
Script de Povoamento da Base de Dados (Seed).

Insere dados de teste realistas na BD para permitir o desenvolvimento
e teste da GUI e do web service sem ter de inserir dados manualmente.

Uso:
    python -m database.seed              # Adiciona dados (mantém existentes)
    python -m database.seed --reset      # Apaga tudo e reinsere

Ordem de inserção (respeita FKs):
    1. generos, criadores, editoras  (catálogos base)
    2. jogos                         (depende dos catálogos)
    3. clientes                      (independente)
    4. vendas + itens_venda          (depende de clientes e jogos)
"""
import sys
from datetime import datetime, timedelta

from database.connection import Database
from database.init_db import DB_FILE

# =====================================================================
# DADOS DE TESTE
# =====================================================================

GENEROS = [
    "Estratégia",
    "Família",
    "Party",
    "Cooperativo",
    "Eurogame",
    "Cartas",
    "Aventura",
]

CRIADORES = [
    "Klaus Teuber",
    "Reiner Knizia",
    "Uwe Rosenberg",
    "Vlaada Chvátil",
    "Antoine Bauza",
    "Bruno Cathala",
    "Vital Lacerda",
    "Stefan Feld",
]

EDITORAS = [
    "Devir",
    "Asmodee",
    "Mebo Games",
    "Z-Man Games",
    "Days of Wonder",
]