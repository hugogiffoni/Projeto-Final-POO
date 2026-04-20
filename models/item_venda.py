"""
Módulo que define a classe ItemVenda.

Representa uma linha de uma venda: um jogo específico comprado numa
determinada quantidade, com o preço unitário "congelado" no momento
da venda (para não ser afetado por alterações futuras de preço).
"""

from typing import Any, Optional

from models.jogo import Jogo

class ItemVenda:
    """
    Representa uma linha de uma venda (1 jogo + quantidade).

    Corresponde à tabela 'itens_venda' da base de dados.

    Attributes:
        id_item (int | None): ID único do item (atribuído pela BD).
        id_venda (int | None): ID da venda a que pertence.
        id_jogo (int): ID do jogo comprado.
        quantidade (int): Quantidade comprada (>= 1).
        preco_unitario (float): Preço do jogo no momento da venda.
        jogo (Jogo | None): Objeto Jogo completo (opcional, para exibição).
    """
    
    def __init__(
            self,
            id_jogo: int,
            quantidade: int,
            preco_unitario: float,
            id_item: Optional[int] = None,
            id_venda: Optional[int] = None,
            jogo: Optional[Jogo] = None,
    ) -> None:
        self.id_item = id_item
        self.id_venda = id_venda
        self.id_jogo = id_jogo
        self.quantidade = quantidade  # usa setter (validação)
        self.preco_unitario = preco_unitario  # usa setter (validação)
        self.jogo = jogo  # pode ser None ou um objeto Jogo completo

    # Factory method: criar ItemVenda a partir de um Jogo

    def a_partir_de_jogo(cls, jogo: Jogo, quantidade: int) -> "ItemVenda":
        """
        Cria um ItemVenda a partir de um objeto Jogo.

        O preço unitário é "congelado" no preço atual do jogo.
        Útil na GUI quando o utilizador adiciona um jogo ao carrinho.

        Args:
            jogo: Objeto Jogo a adicionar.
            quantidade: Quantidade desejada.

        Returns:
            Nova instância de ItemVenda.

        Raises:
            ValueError: Se o jogo não tiver ID ou stock insuficiente.
        """
        if jogo.id_jogo is None:
            raise ValueError("O jogo precisa de estar guardado na BD (ter id_jogo)")
        if not jogo.tem_stock(quantidade):
            raise ValueError(
                f"Stock insuficiente para '{jogo.titulo}' "  
                f"(pedido: {quantidade}, disponível: {jogo.stock})" 
            )  
        return cls(
            id_jogo=jogo.id_jogo,
            quantidade=quantidade,
            preco_unitario=jogo.preco,
            jogo=jogo,
        )
    
    
    # Properties com validação

    @property
    def id_item(self) -> Optional[int]:
        #ID do item (read-only, gerado pela BD)
        return self._id_item
    
    @property
    def id_venda(self) -> Optional[int]:
        return self._id_venda
    
    @id_venda.setter
    def id_venda(self, valor: Optional[int]) -> None:
        """setter puplico - usado pela Venda ao guardar no BD"""
        self._id_venda = valor

    @property
    def id_jogo(self) -> int:
        return self._id_jogo

    @property
    def quantidade(self) -> int:
        return self._quantidade

    @quantidade.setter
    def quantidade(self, valor: int) -> None:
        qtd = int(valor) if valor is not None else 0
        if qtd < 1:
            raise ValueError("A quantidade deve ser pelo menos 1.") 
        self._quantidade = qtd

    @property
    def preco_unitario(self) -> float:
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, valor: float) -> None:
        if valor is None or float(valor) < 0:
            raise ValueError("O preço unitário não pode ser negativo.")
        self._preco_unitario = float(valor)       

    @property
    def jogo(self) -> Optional[Jogo]:
        """Objeto Jogo associado (opcional, pode ser None se nao foi carregado)."""
        return self._jogo    
    

    # Métodos de negócio

    def subtotal(self) -> float:
        """
        Calcula o subtotal desta linha (preço × quantidade).

        Returns:
            Subtotal arredondado a 2 casas decimais.
        """
        return round(self.preco_unitario * self.quantidade, 2)
    