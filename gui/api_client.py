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