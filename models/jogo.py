"""
Módulo que define a classe Jogo.

Representa um jogo de tabuleiro do catálogo da loja.
Os campos criador, editora e género serão FKs na BD (após normalização),
mas nesta classe são tratados como nomes (strings) para facilitar o uso
na GUI e nas respostas JSON do web service.
"""
from typing import Any, Optional

class Jogo:
    """
    Representa um jogo de tabuleiro do catálogo.

    Corresponde à tabela 'jogos' da base de dados (eventualmente com
    JOINs às tabelas 'criadores', 'editoras' e 'generos').

    Attributes:
        id_jogo (int | None): ID único do jogo.
        titulo (str): Título do jogo.
        preco (float): Preço unitário (>= 0).
        stock (int): Quantidade em stock (>= 0).
        criador (str | None): Nome do designer/criador.
        editora (str | None): Nome da editora.
        genero (str | None): Nome do género.
        ano_lancamento (int | None): Ano de lançamento.
        idade_minima (int): Idade mínima recomendada.
    """
    def __init__(
            self,
            titulo: str,
            preco: float,
            stock: int = 0,
            criador: Optional[str] = None,
            editora: Optional[str] = None,
            genero: Optional[str] = None,
            ano_lancamento: Optional[int] = None,
            idade_minima: int = 0,
            id_jogo: Optional[int] = None,
    ) -> None:
        self.id_jogo = id_jogo
        self.titulo = titulo          # usa setter (validação)
        self.preco = preco            # usa setter (validação)
        self.stock = stock            # usa setter (validação)
        self.criador = criador
        self.editora = editora
        self.genero = genero
        self.ano_lancamento = ano_lancamento
        self.idade_minima = idade_minima  # usa setter (validação)