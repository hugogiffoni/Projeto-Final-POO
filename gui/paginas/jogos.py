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

# ---------------------------------------------------------------- helpers
def _notificar_erro(e: APIError) -> None:
    ui.notify(f"❌ {e}", type="negative", position="top")


def _notificar_sucesso(msg: str) -> None:
    ui.notify(f"✅ {msg}", type="positive", position="top")


def _formatar_preco(valor: float | None) -> str:
    """Formata um preço em euros (formato pt-PT)."""
    if valor is None:
        return "—"
    return f"{valor:.2f} €".replace(".", ",")


def _recarregar_tabela() -> None:
    """Vai buscar a lista de jogos ao backend e atualiza a tabela."""
    if estado.tabela is None:
        return
    try:
        jogos = api_client.listar_jogos()
    except APIError as e:
        _notificar_erro(e)
        return

    # Filtro client-side (pesquisa em vários campos)
    termo = (estado.campo_pesquisa.value or "").lower().strip() \
        if estado.campo_pesquisa else ""
    if termo:
        jogos = [
            j for j in jogos
            if termo in (j.get("titulo") or "").lower()
            or termo in (j.get("criador") or "").lower()
            or termo in (j.get("editora") or "").lower()
            or termo in (j.get("genero") or "").lower()
        ]

    # Adicionar campo formatado para a tabela
    for j in jogos:
        j["preco_fmt"] = _formatar_preco(j.get("preco"))

    estado.tabela.rows = jogos
    estado.tabela.update()