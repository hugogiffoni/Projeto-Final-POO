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

# (titulo, criador, editora, genero, ano, idade_min, preco, stock)
JOGOS = [
    ("Catan",                  "Klaus Teuber",   "Devir",         "Estratégia",   1995, 10, 39.99, 15),
    ("Carcassonne",            "Klaus Teuber",   "Devir",         "Família",      2000,  8, 29.99, 20),
    ("Ticket to Ride",         "Reiner Knizia",  "Days of Wonder","Família",      2004,  8, 44.99, 12),
    ("Pandemic",               "Antoine Bauza",  "Z-Man Games",   "Cooperativo",  2008, 10, 39.99, 10),
    ("7 Wonders",              "Antoine Bauza",  "Asmodee",       "Estratégia",   2010, 10, 49.99,  8),
    ("Agricola",               "Uwe Rosenberg",  "Mebo Games",    "Eurogame",     2007, 12, 54.99,  6),
    ("Codenames",              "Vlaada Chvátil", "Devir",         "Party",        2015, 12, 19.99, 25),
    ("Dixit",                  "Bruno Cathala",  "Asmodee",       "Party",        2008,  8, 34.99, 18),
    ("Splendor",               "Bruno Cathala",  "Asmodee",       "Estratégia",   2014, 10, 32.99, 14),
    ("Terraforming Mars",      "Vital Lacerda",  "Mebo Games",    "Eurogame",     2016, 12, 64.99,  5),
    ("Azul",                   "Stefan Feld",    "Devir",         "Família",      2017,  8, 39.99, 16),
    ("Wingspan",               "Stefan Feld",    "Z-Man Games",   "Estratégia",   2019, 10, 59.99,  9),
    ("Exploding Kittens",      "Reiner Knizia",  "Asmodee",       "Cartas",       2015,  7, 19.99, 30),
    ("Gloomhaven",             "Vital Lacerda",  "Mebo Games",    "Aventura",     2017, 14, 99.99,  3),
    ("King of Tokyo",          "Bruno Cathala",  "Devir",         "Família",      2011,  8, 27.99, 22),
]

# (nome, morada, telefone, email)
CLIENTES = [
    ("Ana Silva",        "Rua das Flores 12, Lisboa",       "912345678", "ana.silva@email.pt"),
    ("Bruno Costa",      "Av. da Liberdade 45, Porto",      "923456789", "bruno.costa@email.pt"),
    ("Carla Mendes",     "Rua do Sol 8, Coimbra",           "934567890", "carla.mendes@email.pt"),
    ("Diogo Ferreira",   "Praceta Verde 3, Faro",           "945678901", "diogo.ferreira@email.pt"),
    ("Eva Martins",      "Rua Azul 27, Braga",              "956789012", "eva.martins@email.pt"),
    ("Filipe Santos",    "Av. Central 99, Aveiro",          "967890123", "filipe.santos@email.pt"),
    ("Gabriela Lopes",   "Rua Nova 15, Setúbal",            "978901234", "gabriela.lopes@email.pt"),
    ("Hugo Pereira",     "Travessa Antiga 6, Évora",        "989012345", "hugo.pereira@email.pt"),
]

# =====================================================================
# FUNÇÕES DE LIMPEZA
# =====================================================================

def limpar_tabelas(db: Database) -> None:
    """Apaga todos os dados das tabelas (mantém estrutura)."""
    print("Limpando tabelas existentes...")
    # Ordem inversa por causa das FKs
    tabelas = ["itens_venda", "vendas", "jogos", "clientes",
               "criadores", "editoras", "generos"]
    for tabela in tabelas:
        db.execute(f"DELETE FROM {tabela};")
        # Reset do AUTOINCREMENT
        db.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabela}';")
    print("Tabelas limpas com sucesso.\n")

# =====================================================================
# FUNÇÕES DE INSERÇÃO
# =====================================================================

def inserir_catalogos(db: Database) -> tuple[dict, dict, dict]:
    """
    Insere géneros, criadores e editoras.
    
    Returns:
        Três dicts {nome: id} para mapeamento rápido nos jogos.
    """
    print("Inserindo géneros, criadores e editoras...")

    generos_map = {}
    for nome in GENEROS:
        cursor = db.execute("INSERT INTO generos (nome) VALUES (?);", (nome,))
        generos_map[nome] = cursor.lastrowid

    criadores_map = {}
    for nome in CRIADORES:
        cursor = db.execute("INSERT INTO criadores (nome) VALUES (?);", (nome,))
        criadores_map[nome] = cursor.lastrowid

    editoras_map = {}
    for nome in EDITORAS:
        cursor = db.execute("INSERT INTO editoras (nome) VALUES (?);", (nome,))
        editoras_map[nome] = cursor.lastrowid

    print(f"  -> {len(generos_map)} géneros, "
          f"{len(criadores_map)} criadores, "
          f"{len(editoras_map)} editoras inseridos.\n")

    return generos_map, criadores_map, editoras_map
