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

# ---------------------------------------------------------------- estado
class _Estado:
    """Container para referências partilhadas na página."""
    tabela: ui.table | None = None
    campo_pesquisa: ui.input | None = None


estado = _Estado()