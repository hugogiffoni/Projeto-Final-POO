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

# ---------------------------------------------------------------- dados
def _recarregar() -> None:
    """Vai buscar vendas ao backend e aplica filtros."""
    if estado.tabela is None:
        return
    try:
        vendas = api_client.listar_vendas()
    except APIError as e:
        _notificar_erro(e)
        return

    estado.vendas = vendas
    _aplicar_filtros()


def _aplicar_filtros() -> None:
    """Filtra a cache local conforme pesquisa + cliente selecionado."""
    if estado.tabela is None:
        return

    vendas = list(estado.vendas)

    # Filtro por cliente
    if estado.select_cliente and estado.select_cliente.value:
        id_cli = estado.select_cliente.value
        vendas = [v for v in vendas if v.get("id_cliente") == id_cli]

    # Pesquisa livre
    termo = (estado.campo_pesquisa.value or "").lower().strip() \
        if estado.campo_pesquisa else ""
    if termo:
        vendas = [
            v for v in vendas
            if termo in (v.get("nome_cliente") or "").lower()
            or termo in (v.get("titulo_jogo") or "").lower()
        ]

    # Formatar campos para a tabela
    total_filtrado = 0.0
    for v in vendas:
        v["data_fmt"] = _formatar_data(v.get("data_hora"))
        v["preco_fmt"] = _formatar_eur(v.get("preco_unitario"))
        v["valor_fmt"] = _formatar_eur(v.get("valor_total"))
        v["desc_fmt"] = f"{float(v.get('desconto') or 0):.0f}%"
        total_filtrado += float(v.get("valor_total") or 0)

    estado.tabela.rows = vendas
    estado.tabela.update()

    if estado.label_total is not None:
        estado.label_total.text = (
            f"💰 Total faturado ({len(vendas)} venda(s)): "
            f"{_formatar_eur(total_filtrado)}"
        )


def _limpar_filtros() -> None:
    if estado.campo_pesquisa:
        estado.campo_pesquisa.set_value("")
    if estado.select_cliente:
        estado.select_cliente.set_value(None)
    _aplicar_filtros()