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

    # Properties com validação

    @property
    def id_jogo(self) -> Optional[int]:
        #ID do jogo (read-only, gerado pela BD)
        return self._id_jogo

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("O título do jogo não pode ser vazio.")
        self._titulo = valor.strip()

    @property
    def preco(self) -> float:
        return self._preco

    @preco.setter
    def preco(self, valor: float) -> None:
        if valor is None or float(valor) < 0:
            raise ValueError("O preço do jogo deve ser um número não negativo.")
        self._preco = float(valor)  

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if valor is None or int(valor) < 0:
            raise ValueError("O stock não pode ser um número negativo.")
        self._stock = int(valor)     

    @property
    def ano_lancamento(self) -> Optional[int]:
        return self._ano_lancamento

    @ano_lancamento.setter
    def ano_lancamento(self, valor: Optional[int]) -> None:
        if valor is not None:
            ano = int(valor)
            if ano < 1800 or ano > 2100:
                raise ValueError(f"O ano de lançamento invalido: {ano}.")   
            self._ano_lancamento = valor  
        else:
            self._ano_lancamento = None   

    @property
    def idade_minima(self) -> int:
        return self._idade_minima

    @idade_minima.setter
    def idade_minima(self, valor: int) -> None:
        idade = int(valor) if valor is not None else 0
        if idade < 0:
            raise ValueError("A idade mínima não pode ser negativa.")
        self._idade_minima = idade

    @property
    def criador(self) -> Optional[str]:
        return self._criador

    @property
    def editora(self) -> Optional[str]:
        return self._editora

    @property
    def genero(self) -> Optional[str]:
        return self._genero           