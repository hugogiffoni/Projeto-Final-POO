"""Página inicial — menu principal."""
from nicegui import ui


def criar_pagina_home() -> None:
    """Página inicial com cartões de navegação."""
    with ui.column().classes("w-full items-center p-8 gap-6"):
        ui.label("🎲 Loja de Jogos de Tabuleiro").classes(
            "text-4xl font-bold text-primary"
        )
        ui.label("Sistema de Gestão de Vendas — Call Center").classes(
            "text-lg text-gray-600"
        )

        with ui.row().classes("gap-6 mt-8 flex-wrap justify-center"):
            _cartao("🛒", "Nova Venda", "Registar uma encomenda", "/nova-venda",
                    "bg-green-500")
            _cartao("👥", "Clientes", "Gerir clientes", "/clientes",
                    "bg-blue-500")
            _cartao("🎮", "Jogos", "Catálogo de jogos", "/jogos",
                    "bg-purple-500")
            _cartao("📊", "Histórico", "Vendas por cliente", "/historico",
                    "bg-orange-500")


def _cartao(emoji: str, titulo: str, descricao: str, rota: str,
            cor: str) -> None:
    """Cartão clicável que navega para uma rota."""
    with ui.card().classes(
        f"cursor-pointer hover:shadow-2xl transition-all "
        f"w-64 h-48 {cor} text-white"
    ).on("click", lambda: ui.navigate.to(rota)):
        with ui.column().classes("items-center justify-center h-full gap-2"):
            ui.label(emoji).classes("text-6xl")
            ui.label(titulo).classes("text-2xl font-bold")
            ui.label(descricao).classes("text-sm opacity-90")
