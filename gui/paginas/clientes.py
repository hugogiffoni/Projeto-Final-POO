"""
Página de gestão de Clientes.

Funcionalidades:
    - Listar clientes em tabela (com pesquisa)
    - Criar novo cliente (dialog)
    - Editar cliente existente (dialog)
    - Apagar cliente (com confirmação)
"""

from nicegui import ui

from gui import api_client
from gui.api_client import APIError


# ---------------------------------------------------------------- estado
class _Estado:
    """Container simples para guardar referências partilhadas na página."""
    tabela: ui.table | None = None
    campo_pesquisa: ui.input | None = None


estado = _Estado()