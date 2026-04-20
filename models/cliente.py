"""
Módulo que define a classe Cliente.

Representa um cliente da loja de jogos de tabuleiro, com validações
de email e encapsulamento dos atributos.
"""
import re
from typing import Any, Optional

class Cliente:
    """
    Representa um cliente da loja.

    Corresponde à tabela 'clientes' da base de dados.

    Attributes:
        id_cliente (int | None): ID único (None antes de ser guardado na BD).
        nome (str): Nome completo do cliente.
        email (str | None): Email único (validado).
        morada (str | None): Morada do cliente.
        telefone (str | None): Número de telefone.
        data_registo (str | None): Data/hora de registo (preenchida pela BD).
    """

    # Regex simples para validação de email
    _EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(
            self,
        nome: str,
        email: Optional[str] = None,
        morada: Optional[str] = None,
        telefone: Optional[str] = None,
        id_cliente: Optional[int] = None,
        data_registo: Optional[str] = None,
    ) -> None:
        self.id_cliente = id_cliente
        self.nome = nome    # usa setter (validação)
        self.email = email  # usa setter (validação)
        self.morada = morada
        self.telefone = telefone
        self.data_registo = data_registo

    # Properties (Encapsulamento + Validação)       
    
     
