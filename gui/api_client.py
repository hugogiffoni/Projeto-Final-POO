"""
Cliente HTTP para comunicar com o web service Flask.

Centraliza todas as chamadas à API. As páginas NiceGUI usam
estas funções em vez de fazer httpx diretamente.

Levanta APIError em caso de erro HTTP, com a mensagem do servidor.
"""

from typing import Any

import httpx

BASE_URL = "http://127.0.0.1:5000/api"
TIMEOUT = 5.0  # segundos


class APIError(Exception):
    """Erro genérico vindo da API (4xx, 5xx ou falha de ligação)."""

    def __init__(self, mensagem: str, status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.status_code = status_code

# ---------------------------------------------------------------- helper
def _request(method: str, path: str, **kwargs) -> Any:
    """Faz um pedido HTTP e devolve o JSON ou levanta APIError."""
    url = f"{BASE_URL}{path}"
    try:
        r = httpx.request(method, url, timeout=TIMEOUT, **kwargs)
    except httpx.ConnectError as e:
        raise APIError(f"Não foi possível ligar ao servidor ({url}). "
                       f"O Flask está a correr?") from e
    except httpx.TimeoutException as e:
        raise APIError("Tempo de espera esgotado.") from e

    if r.status_code >= 400:
        try:
            erro = r.json().get("erro", r.text)
        except Exception:
            erro = r.text or f"HTTP {r.status_code}"
        raise APIError(erro, status_code=r.status_code)

    if r.status_code == 204 or not r.content:
        return None
    return r.json()      

# ================================================================ CLIENTES
def listar_clientes(termo: str | None = None) -> list[dict]:
    params = {"q": termo} if termo else None
    data = _request("GET", "/clientes", params=params)
    return data.get("clientes", data) if isinstance(data, dict) else data


def obter_cliente(id_cliente: int) -> dict:
    return _request("GET", f"/clientes/{id_cliente}")


def criar_cliente(payload: dict) -> dict:
    return _request("POST", "/clientes", json=payload)


def atualizar_cliente(id_cliente: int, payload: dict) -> dict:
    return _request("PUT", f"/clientes/{id_cliente}", json=payload)


def apagar_cliente(id_cliente: int) -> None:
    _request("DELETE", f"/clientes/{id_cliente}")  

# ================================================================ JOGOS
def listar_jogos(termo: str | None = None) -> list[dict]:
    params = {"q": termo} if termo else None
    data = _request("GET", "/jogos", params=params)
    return data.get("jogos", data) if isinstance(data, dict) else data


def obter_jogo(id_jogo: int) -> dict:
    return _request("GET", f"/jogos/{id_jogo}")


def criar_jogo(payload: dict) -> dict:
    return _request("POST", "/jogos", json=payload)


def atualizar_jogo(id_jogo: int, payload: dict) -> dict:
    return _request("PUT", f"/jogos/{id_jogo}", json=payload)


def apagar_jogo(id_jogo: int) -> None:
    _request("DELETE", f"/jogos/{id_jogo}")


# ================================================================ VENDAS
def listar_vendas() -> list[dict]:
    data = _request("GET", "/vendas")
    return data.get("vendas", data) if isinstance(data, dict) else data


def obter_venda(id_venda: int) -> dict:
    return _request("GET", f"/vendas/{id_venda}")


def criar_venda(payload: dict) -> dict:
    return _request("POST", "/vendas", json=payload)


def anular_venda(id_venda: int) -> dict:
    return _request("DELETE", f"/vendas/{id_venda}")


def historico_cliente(id_cliente: int) -> dict:
    return _request("GET", f"/vendas/cliente/{id_cliente}")