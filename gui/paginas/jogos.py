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

# ---------------------------------------------------------------- dialogs
def _dialog_jogo(jogo: dict | None = None) -> None:
    """Dialog para criar (jogo=None) ou editar um jogo."""
    a_editar = jogo is not None
    titulo = "✏️ Editar Jogo" if a_editar else "➕ Novo Jogo"

    with ui.dialog() as dialog, ui.card().classes("min-w-[500px]"):
        ui.label(titulo).classes("text-xl font-bold")

        in_titulo = ui.input(
            "Título *",
            value=jogo["titulo"] if a_editar else "",
        ).classes("w-full")

        with ui.row().classes("w-full gap-2"):
            in_criador = ui.input(
                "Criador",
                value=jogo.get("criador", "") if a_editar else "",
            ).classes("flex-grow")
            in_editora = ui.input(
                "Editora",
                value=jogo.get("editora", "") if a_editar else "",
            ).classes("flex-grow")

        with ui.row().classes("w-full gap-2"):
            in_ano = ui.number(
                "Ano de lançamento",
                value=jogo.get("ano_lancamento") if a_editar else None,
                format="%d",
                min=1900,
                max=2100,
            ).classes("flex-grow")
            in_idade = ui.number(
                "Idade mínima",
                value=jogo.get("idade_minima") if a_editar else None,
                format="%d",
                min=0,
                max=99,
            ).classes("flex-grow")

        in_genero = ui.input(
            "Género",
            value=jogo.get("genero", "") if a_editar else "",
        ).classes("w-full")

        in_preco = ui.number(
            "Preço (€) *",
            value=jogo.get("preco") if a_editar else None,
            format="%.2f",
            min=0,
            step=0.01,
        ).classes("w-full")

        def guardar() -> None:
            # Validações
            if not (in_titulo.value or "").strip():
                ui.notify("O título é obrigatório.", type="warning")
                return
            if in_preco.value is None or in_preco.value < 0:
                ui.notify("O preço é obrigatório e não pode ser negativo.",
                          type="warning")
                return

            payload = {
                "titulo": in_titulo.value.strip(),
                "criador": (in_criador.value or "").strip() or None,
                "editora": (in_editora.value or "").strip() or None,
                "ano_lancamento": int(in_ano.value) if in_ano.value else None,
                "genero": (in_genero.value or "").strip() or None,
                "idade_minima": int(in_idade.value) if in_idade.value else None,
                "preco": float(in_preco.value),
            }

            try:
                if a_editar:
                    api_client.atualizar_jogo(jogo["id_jogo"], payload)
                    _notificar_sucesso("Jogo atualizado.")
                else:
                    api_client.criar_jogo(payload)
                    _notificar_sucesso("Jogo criado.")
            except APIError as e:
                _notificar_erro(e)
                return

            dialog.close()
            _recarregar_tabela()

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Guardar", on_click=guardar, icon="save") \
                .props("color=primary")

    dialog.open()


def _confirmar_apagar(jogo: dict) -> None:
    """Dialog de confirmação antes de apagar."""
    with ui.dialog() as dialog, ui.card():
        ui.label(f"Apagar o jogo '{jogo['titulo']}'?").classes("text-lg")
        ui.label("Esta ação não pode ser desfeita.") \
            .classes("text-sm text-gray-600")

        def confirmar() -> None:
            try:
                api_client.apagar_jogo(jogo["id_jogo"])
                _notificar_sucesso("Jogo apagado.")
            except APIError as e:
                _notificar_erro(e)
                dialog.close()
                return
            dialog.close()
            _recarregar_tabela()

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Apagar", on_click=confirmar, icon="delete") \
                .props("color=negative")

    dialog.open()    