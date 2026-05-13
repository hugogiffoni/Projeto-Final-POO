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
