"""
Ponto de entrada da GUI NiceGUI.

Executa com:
    python -m gui.main

(O Flask deve estar a correr em paralelo noutro terminal.)
"""
from nicegui import ui

from gui.paginas.home import criar_pagina_home

# ---------------------------------------------------------------- layout
def cabecalho() -> None:
    """Barra de navegação superior (aparece em todas as páginas)."""
    with ui.header().classes("bg-primary text-white items-center"):
        ui.button(icon="home", on_click=lambda: ui.navigate.to("/")) \
            .props("flat color=white")
        ui.label("Loja de Jogos — Call Center").classes("text-xl font-bold")
        ui.space()
        with ui.row().classes("gap-2"):
            ui.button("Nova Venda", icon="shopping_cart",
                      on_click=lambda: ui.navigate.to("/nova-venda")) \
                .props("flat color=white")
            ui.button("Clientes", icon="people",
                      on_click=lambda: ui.navigate.to("/clientes")) \
                .props("flat color=white")
            ui.button("Jogos", icon="casino",
                      on_click=lambda: ui.navigate.to("/jogos")) \
                .props("flat color=white")
            ui.button("Histórico", icon="history",
                      on_click=lambda: ui.navigate.to("/historico")) \
                .props("flat color=white")