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
        self.titulo = titulo
        self.preco = preco
        self.stock = stock
        self.criador = criador
        self.editora = editora
        self.genero = genero
        self.ano_lancamento = ano_lancamento
        self.idade_minima = idade_minima

    # ---------- Properties com validação ----------

    @property
    def id_jogo(self) -> Optional[int]:
        """ID do jogo (gerado pela BD)."""
        return self._id_jogo

    @id_jogo.setter
    def id_jogo(self, valor: Optional[int]) -> None:
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("id_jogo deve ser um inteiro positivo ou None.")
        self._id_jogo = valor

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
        self._preco = round(float(valor), 2)

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
        if valor is None:
            self._ano_lancamento = None
            return
        ano = int(valor)
        if ano < 1800 or ano > 2100:
            raise ValueError(f"Ano de lançamento inválido: {ano}.")
        self._ano_lancamento = ano  # 🐛 BUG corrigido (era 'valor')

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

    @criador.setter
    def criador(self, valor: Optional[str]) -> None:
        self._criador = valor.strip() if valor else None

    @property
    def editora(self) -> Optional[str]:
        return self._editora

    @editora.setter
    def editora(self, valor: Optional[str]) -> None:
        self._editora = valor.strip() if valor else None

    @property
    def genero(self) -> Optional[str]:
        return self._genero

    @genero.setter
    def genero(self, valor: Optional[str]) -> None:
        self._genero = valor.strip() if valor else None

    # ---------- Métodos de negócio ----------

    def tem_stock(self, quantidade: int = 1) -> bool:
        """Verifica se há stock suficiente para a quantidade pedida."""
        return self.stock >= quantidade

    def calcular_subtotal(self, quantidade: int) -> float:
        """Calcula o subtotal para uma dada quantidade (sem desconto)."""
        if quantidade < 1:
            raise ValueError("A quantidade deve ser pelo menos 1.")
        return round(self.preco * quantidade, 2)

    # ---------- Serialização ----------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Jogo":
        """Cria um Jogo a partir de um dict (linha da BD ou JSON)."""
        return cls(
            id_jogo=data.get("id_jogo"),
            titulo=data["titulo"],
            preco=data["preco"],
            stock=data.get("stock", 0),
            criador=data.get("criador"),
            editora=data.get("editora"),
            genero=data.get("genero"),
            ano_lancamento=data.get("ano_lancamento"),
            idade_minima=data.get("idade_minima", 0),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte o objeto Jogo para um dict (útil para JSON)."""
        return {
            "id_jogo": self.id_jogo,
            "titulo": self.titulo,
            "preco": self.preco,
            "stock": self.stock,
            "criador": self.criador,
            "editora": self.editora,
            "genero": self.genero,
            "ano_lancamento": self.ano_lancamento,
            "idade_minima": self.idade_minima,
        }

    # ---------- Dunder methods ----------

    def __str__(self) -> str:
        ano = self._ano_lancamento or "-"
        return f"{self._titulo} ({ano}) - €{self._preco:.2f}"

    def __repr__(self) -> str:
        return (
            f"Jogo(id_jogo={self._id_jogo!r}, titulo={self._titulo!r}, "
            f"preco={self._preco!r}, stock={self._stock!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Jogo):
            return NotImplemented
        if self.id_jogo is not None and other.id_jogo is not None:
            return self.id_jogo == other.id_jogo
        return self.titulo == other.titulo

    def __hash__(self) -> int:
        return hash((self.id_jogo, self.titulo))
