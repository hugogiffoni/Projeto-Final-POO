"""
Página de gestão de Jogos.

Funcionalidades:
    - Listar jogos em tabela (com pesquisa)
    - Criar novo jogo (dialog)
    - Editar jogo existente (dialog)
    - Apagar jogo (com confirmação)
"""
from nicegui import ui

from gui import api_client
from gui.api_client import APIError