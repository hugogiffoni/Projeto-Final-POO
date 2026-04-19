-- =====================================================================
-- Schema da Base de Dados - Sistema de Gestão de Vendas
-- Loja de Jogos de Tabuleiro
-- Normalizado até à 3ª Forma Normal (3NF)
-- =====================================================================

-- Ativar suporte a chaves estrangeiras (SQLite exige isto explicitamente)
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Tabela: clientes
-- Armazena os dados dos clientes da loja
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    morada      TEXT,
    telefone    TEXT,
    email       TEXT    UNIQUE,
    data_registo DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Tabela: generos
-- Catálogo de géneros de jogos (Estratégia, Família, Party, etc.)
-- Evita repetição de strings na tabela 'jogos' (3NF)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS generos (
    id_genero  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT    NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- Tabela: editoras
-- Catálogo de editoras de jogos (Devir, Asmodee, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS editoras (
    id_editora  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- Tabela: criadores
-- Catálogo de autores/designer de jogos
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS criadores (
    id_criador INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT    NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- Tabela: jogos
-- Catálogo de jogos de tabuleiro disponíveis para venda
-- Usa FKs para género, editora e criador (normalização)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jogos (
    id_jogo         INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT    NOT NULL,
    id_criador      INTEGER,
    id_editora      INTEGER,
    id_genero       INTEGER,
    ano_lancamento  INTEGER,
    idade_minima    INTEGER DEFAULT 0,
    preco           REAL    NOT NULL CHECK (preco >= 0),
    stock           INTEGER DEFAULT 0 CHECK (stock >= 0),

    FOREIGN KEY (id_criador) REFERENCES criadores(id_criador) ON DELETE SET NULL,
    FOREIGN KEY (id_editora) REFERENCES editoras(id_editora) ON DELETE SET NULL,
    FOREIGN KEY (id_genero)  REFERENCES generos(id_genero)   ON DELETE SET NULL
);