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

# ---------------------------------------------------------------- página
def criar_pagina_historico() -> None:
    """Constrói a página completa de histórico."""
    # Carregar lista de clientes para o filtro
    try:
        clientes = api_client.listar_clientes()
    except APIError as e:
        _notificar_erro(e)
        clientes = []

    opcoes_clientes = {c["id_cliente"]: c["nome"] for c in clientes}

    with ui.column().classes("w-full p-6 gap-4"):
        # Cabeçalho
        with ui.row().classes("w-full items-center"):
            ui.label("📊 Histórico de Vendas").classes("text-3xl font-bold")
            ui.space()
            ui.button(icon="refresh", on_click=_recarregar) \
                .props("flat round").tooltip("Recarregar")

        # Filtros
        with ui.card().classes("w-full"):
            ui.label("Filtros").classes("text-sm font-bold text-gray-600")
            with ui.row().classes("w-full items-center gap-2"):
                estado.campo_pesquisa = ui.input(
                    placeholder="Pesquisar por cliente ou jogo...",
                ).classes("flex-grow").props("clearable outlined dense")
                estado.campo_pesquisa.on("update:model-value",
                                         lambda _: _aplicar_filtros())

                estado.select_cliente = ui.select(
                    options=opcoes_clientes,
                    label="Filtrar por cliente",
                    with_input=True,
                    clearable=True,
                ).classes("min-w-[250px]").props("outlined dense")
                estado.select_cliente.on("update:model-value",
                                         lambda _: _aplicar_filtros())

                ui.button("Limpar", icon="clear", on_click=_limpar_filtros) \
                    .props("flat")

        # Total
        estado.label_total = ui.label("💰 Total faturado: 0,00 €") \
            .classes("text-xl font-bold text-primary")

        # Tabela
        colunas = [
            {"name": "id_venda", "label": "ID", "field": "id_venda",
             "align": "left", "sortable": True},
            {"name": "data_fmt", "label": "Data", "field": "data_fmt",
             "align": "left", "sortable": True},
            {"name": "nome_cliente", "label": "Cliente",
             "field": "nome_cliente", "align": "left", "sortable": True},
            {"name": "titulo_jogo", "label": "Jogo",
             "field": "titulo_jogo", "align": "left", "sortable": True},
            {"name": "quantidade", "label": "Qtd.", "field": "quantidade",
             "align": "center"},
            {"name": "preco_fmt", "label": "Preço Unit.",
             "field": "preco_fmt", "align": "right"},
            {"name": "desc_fmt", "label": "Desconto",
             "field": "desc_fmt", "align": "center"},
            {"name": "valor_fmt", "label": "Total",
             "field": "valor_fmt", "align": "right", "sortable": True},
        ]

        estado.tabela = ui.table(
            columns=colunas,
            rows=[],
            row_key="id_venda",
            pagination=15,
        ).classes("w-full")

    # Carga inicial
    _recarregar()    