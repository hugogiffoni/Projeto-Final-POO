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

    @property
    def id_cliente(self) -> Optional[int]:
        #ID do cliente (read-only, gerado pela BD)
        return self._id_cliente   

    @property
    def nome(self) -> str:
        return self._nome
    
    @nome.setter
    def nome(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("O nome do cliente não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, valor: Optional[str]) -> None:
        if valor is not None and valor.strip():
            if not self._EMAIL_REGEX.match(valor.strip()):
                raise ValueError(f"Email inválido: '{valor!r}'")
            self._email = valor.strip().lower()
        else:
            self._email = None  # Permite email ser None ou string vazia (tratada como None)
    
    @property
    def morada(self) -> Optional[str]:
        return self._morada
    
    @morada.setter
    def morada(self, valor: Optional[str]) -> None:
        self._morada = valor.strip() if valor else None

    @property
    def telefone(self) -> Optional[str]:
        return self._telefone
    
    @telefone.setter
    def telefone(self, valor: Optional[str]) -> None:
        self._telefone = valor.strip() if valor else None

    @property
    def data_registo(self) -> Optional[str]:
        #Data de registo do cliente (read-only, gerada pela BD)
        return self._data_registo

    # Factory Methods (formas alternativas de criar Cliente)

    @classmethod  
    def from_dict(cls, data: dict[str, Any]) -> "Cliente":
        """
        Cria um Cliente a partir de um dicionário.

        Útil para converter linhas da BD ou payloads JSON em objetos.

        Args:
            data: Dicionário com as chaves das colunas da tabela.

        Returns:
            Nova instância de Cliente.
        """
        return cls(
            id_cliente=data.get("id_cliente"),
            nome=data["nome"],  # nome é obrigatório
            email=data.get("email"),
            morada=data.get("morada"),
            telefone=data.get("telefone"),
            data_registo=data.get("data_registo"),
        )
    
    # Serializaçâo 

    def to_dict(self) -> dict[str, Any]:
        """
        Converte o objeto num dicionário (útil para JSON no Flask).

        Returns:
            Dicionário com todos os atributos do cliente.
        """
        return {
            "id_cliente": self.id_cliente,
            "nome": self.nome,
            "email": self.email,
            "morada": self.morada,
            "telefone": self.telefone,
            "data_registo": self.data_registo,
        }
    
    # Duner Methods

    def __str__(self) -> str:
        return f"{self._nome} <{self._email or 'sem email'}>"
    
    def __repr__(self) -> str:
        return (
            f"Cliente(id_cliente={self.id_cliente!r}, nome={self.nome!r}, "
            f"email={self.email!r}, morada={self.morada!r}, "
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cliente):
            return NotImplemented
        
        # Dois clientes sao iguais se tiverem o mesmo ID(quando existem)
        if self.id_cliente is not None and other.id_cliente is not None:
            return self.id_cliente == other.id_cliente
        return self._email == other.email and self.nome == other.nome