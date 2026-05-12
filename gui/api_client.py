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