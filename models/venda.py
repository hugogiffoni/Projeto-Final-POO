"""
Módulo que define a classe Venda.

Representa uma encomenda completa: cabeçalho (cliente, data, desconto)
+ vários ItemVenda (linhas do carrinho).
"""

from datetime import datetime
from typing import Any, Optional

from models.item_venda import ItemVenda


class Venda:
    """
    Representa uma venda (encomenda) completa.

    Corresponde à tabela 'vendas' da BD e agrega vários ItemVenda
    (tabela 'itens_venda').

    Atributos:
        id_venda (int | None): ID único da venda.
        id_cliente (int): ID do cliente que fez a compra.
        data_hora (datetime): Data e hora da venda.
        desconto (float): Desconto em % (0 a 100) aplicado ao total.
        itens (list[ItemVenda]): Lista de linhas do carrinho.
        nome_cliente (str | None): Nome do cliente (opcional, p/ exibição).
    """

    def __init__(
        self,
        id_cliente: int,
        desconto: float = 0.0,
        itens: Optional[list[ItemVenda]] = None,
        data_hora: Optional[datetime] = None,
        id_venda: Optional[int] = None,
        nome_cliente: Optional[str] = None,
    ) -> None:
        self._id_venda = id_venda
        self._id_cliente = id_cliente
        self.desconto = desconto                        # usa setter
        self._data_hora = data_hora or datetime.now()
        self._itens: list[ItemVenda] = itens or []
        self._nome_cliente = nome_cliente

    # Properties

    @property
    def id_venda(self) -> Optional[int]:
        return self._id_venda

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @property
    def data_hora(self) -> datetime:
        return self._data_hora

    @property
    def desconto(self) -> float:
        return self._desconto

    @desconto.setter
    def desconto(self, valor: float) -> None:
        d = float(valor) if valor is not None else 0.0
        if d < 0 or d > 100:
            raise ValueError("O desconto deve estar entre 0 e 100 (%).")
        self._desconto = d

    @property
    def itens(self) -> list[ItemVenda]:
        """Devolve uma cópia da lista (proteção contra modificação externa)."""
        return list(self._itens)

    @property
    def nome_cliente(self) -> Optional[str]:
        return self._nome_cliente

    # Gestão do carrinho

    def adicionar_item(self, item: ItemVenda) -> None:
        """
        Adiciona um item ao carrinho.

        Se já existir um item com o mesmo id_jogo, soma a quantidade
        em vez de duplicar a linha.
        """
        for existente in self._itens:
            if existente.id_jogo == item.id_jogo:
                existente.quantidade += item.quantidade
                return
        self._itens.append(item)

    def remover_item(self, id_jogo: int) -> bool:
        """
        Remove um item do carrinho pelo id_jogo.

        Returns:
            True se removeu, False se não encontrou.
        """
        for i, item in enumerate(self._itens):
            if item.id_jogo == id_jogo:
                del self._itens[i]
                return True
        return False

    def limpar(self) -> None:
        """Esvazia o carrinho."""
        self._itens.clear()

    def total_itens(self) -> int:
        """Devolve o número total de unidades no carrinho."""
        return sum(item.quantidade for item in self._itens)

    # Cálculos financeiros

    def subtotal(self) -> float:
        """Soma dos subtotais de todas as linhas (sem desconto)."""
        return round(sum(item.subtotal() for item in self._itens), 2)

    def valor_desconto(self) -> float:
        """Valor monetário do desconto aplicado."""
        return round(self.subtotal() * (self._desconto / 100), 2)

    def valor_total(self) -> float:
        """
        Valor final da venda (subtotal - desconto).

        Fórmula:
            valor_total = subtotal × (1 - desconto/100)
        """
        return round(self.subtotal() - self.valor_desconto(), 2)

    # Validação antes de gravar

    def validar(self) -> None:
        """
        Garante que a venda está pronta para ser gravada.

        Raises:
            ValueError: Se o carrinho estiver vazio ou inválido.
        """
        if not self._itens:
            raise ValueError("Não é possível gravar uma venda sem itens.")
        if self._id_cliente is None:
            raise ValueError("A venda precisa de estar associada a um cliente.")

    # Factory + Serialização

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Venda":
        """Cria uma Venda a partir de um dict (linha da BD ou JSON)."""
        # Converter data_hora (vem como string em JSON)
        dh = data.get("data_hora")
        if isinstance(dh, str):
            try:
                dh = datetime.fromisoformat(dh)
            except ValueError:
                dh = None

        # Converter lista de itens
        itens_data = data.get("itens", [])
        itens = [ItemVenda.from_dict(i) for i in itens_data]

        return cls(
            id_venda=data.get("id_venda"),
            id_cliente=data["id_cliente"],
            desconto=data.get("desconto", 0.0),
            data_hora=dh,
            itens=itens,
            nome_cliente=data.get("nome_cliente"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte a Venda num dicionário (útil para JSON)."""
        return {
            "id_venda": self._id_venda,
            "id_cliente": self._id_cliente,
            "nome_cliente": self._nome_cliente,
            "data_hora": self._data_hora.isoformat(),
            "desconto": self._desconto,
            "subtotal": self.subtotal(),
            "valor_desconto": self.valor_desconto(),
            "valor_total": self.valor_total(),
            "total_itens": self.total_itens(),
            "itens": [item.to_dict() for item in self._itens],
        }

    # Dunder methods
    

    def __str__(self) -> str:
        cliente = self._nome_cliente or f"Cliente #{self._id_cliente}"
        return (
            f"Venda #{self._id_venda or '—'} | {cliente} | "
            f"{len(self._itens)} linha(s) | Total: €{self.valor_total():.2f}"
        )

    def __repr__(self) -> str:
        return (
            f"Venda(id_venda={self._id_venda!r}, "
            f"id_cliente={self._id_cliente}, "
            f"itens={len(self._itens)}, "
            f"total={self.valor_total()})"
        )

    def __len__(self) -> int:
        """Permite usar len(venda) para saber quantas linhas tem."""
        return len(self._itens)
