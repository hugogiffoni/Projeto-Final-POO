"""
Página de Histórico de Vendas.

Funcionalidades:
    - Listar todas as vendas (com join de cliente e jogo já no backend)
    - Filtrar por cliente
    - Pesquisa livre (cliente / jogo)
    - Mostrar total faturado das vendas visíveis
"""
from datetime import datetime

from nicegui import ui

from gui import api_client
from gui.api_client import APIError

# ---------------------------------------------------------------- estado
class _Estado:
    tabela: ui.table | None = None
    campo_pesquisa: ui.input | None = None
    select_cliente: ui.select | None = None
    label_total: ui.label | None = None
    vendas: list[dict] = []  # cache da última resposta


estado = _Estado()


# ---------------------------------------------------------------- helpers
def _notificar_erro(e: APIError | str) -> None:
    ui.notify(f"❌ {e}", type="negative", position="top")


def _formatar_eur(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"{float(valor):.2f} €".replace(".", ",")


def _formatar_data(s: str | None) -> str:
    """Aceita ISO ('2026-05-12T22:30:00') ou 'YYYY-MM-DD HH:MM:SS'."""
    if not s:
        return "—"
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(s, fmt).strftime("%d/%m/%Y %H:%M")
        except ValueError:
            continue
    return s  # fallback: mostra como veio