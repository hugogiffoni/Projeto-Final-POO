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

# ---------------------------------------------------------------- helpers
def _notificar_erro(e: APIError) -> None:
    ui.notify(f"❌ {e}", type="negative", position="top")


def _notificar_sucesso(msg: str) -> None:
    ui.notify(f"✅ {msg}", type="positive", position="top")


def _recarregar_tabela() -> None:
    """Vai buscar a lista de clientes ao backend e atualiza a tabela."""
    if estado.tabela is None:
        return
    termo = estado.campo_pesquisa.value if estado.campo_pesquisa else None
    try:
        clientes = api_client.listar_clientes(termo or None)
    except APIError as e:
        _notificar_erro(e)
        return
    estado.tabela.rows = clientes
    estado.tabela.update()