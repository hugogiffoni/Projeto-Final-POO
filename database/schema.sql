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
