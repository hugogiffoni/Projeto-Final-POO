"""
Ponto de entrada da GUI NiceGUI.

Executa com:
    python -m gui.main

(O Flask deve estar a correr em paralelo noutro terminal.)
"""
from nicegui import ui

from gui.paginas.home import criar_pagina_home
from gui.paginas.clientes import criar_pagina_clientes
from gui.paginas.jogos import criar_pagina_jogos
from gui.paginas.nova_venda import criar_pagina_nova_venda


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
            
# ---------------------------------------------------------------- rotas
@ui.page("/")
def pagina_home() -> None:
    cabecalho()
    criar_pagina_home()


@ui.page("/clientes")
def pagina_clientes() -> None:
    cabecalho()
    criar_pagina_clientes()


@ui.page("/jogos")
def pagina_jogos() -> None:
    cabecalho()
    criar_pagina_jogos()


@ui.page("/nova-venda")
def pagina_nova_venda() -> None:
    cabecalho()
    criar_pagina_nova_venda()


@ui.page("/historico")
def pagina_historico() -> None:
    cabecalho()
    ui.label("📊 Histórico — em construção").classes("text-2xl p-8")     

# ---------------------------------------------------------------- arranque
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Loja de Jogos — Call Center",
        port=8080,
        reload=False,
        favicon="🎲",
    )           