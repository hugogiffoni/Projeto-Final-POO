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

# ---------------------------------------------------------------- página
def criar_pagina_jogos() -> None:
    """Constrói a página completa de jogos."""
    with ui.column().classes("w-full p-6 gap-4"):
        # Cabeçalho
        with ui.row().classes("w-full items-center"):
            ui.label("🎮 Catálogo de Jogos").classes("text-3xl font-bold")
            ui.space()
            ui.button("Novo Jogo", icon="add",
                      on_click=lambda: _dialog_jogo()) \
                .props("color=primary")

        # Pesquisa
        with ui.row().classes("w-full items-center gap-2"):
            estado.campo_pesquisa = ui.input(
                placeholder="Pesquisar por título, criador, editora ou género...",
            ).classes("flex-grow").props("clearable outlined dense")
            estado.campo_pesquisa.on("update:model-value",
                                     lambda _: _recarregar_tabela())
            ui.button(icon="refresh", on_click=_recarregar_tabela) \
                .props("flat round").tooltip("Recarregar")

        # Tabela
        colunas = [
            {"name": "id_jogo", "label": "ID", "field": "id_jogo",
             "align": "left", "sortable": True},
            {"name": "titulo", "label": "Título", "field": "titulo",
             "align": "left", "sortable": True},
            {"name": "criador", "label": "Criador", "field": "criador",
             "align": "left"},
            {"name": "editora", "label": "Editora", "field": "editora",
             "align": "left"},
            {"name": "ano_lancamento", "label": "Ano", "field": "ano_lancamento",
             "align": "center", "sortable": True},
            {"name": "genero", "label": "Género", "field": "genero",
             "align": "left"},
            {"name": "idade_minima", "label": "Idade Mín.",
             "field": "idade_minima", "align": "center"},
            {"name": "preco_fmt", "label": "Preço", "field": "preco_fmt",
             "align": "right", "sortable": True},
            {"name": "acoes", "label": "Ações", "field": "acoes",
             "align": "center"},
        ]

        estado.tabela = ui.table(
            columns=colunas,
            rows=[],
            row_key="id_jogo",
            pagination=10,
        ).classes("w-full")

        # Slot para botões de ação
        estado.tabela.add_slot("body-cell-acoes", r"""
            <q-td :props="props">
                <q-btn flat dense round icon="edit" color="primary"
                       @click="() => $parent.$emit('editar', props.row)" />
                <q-btn flat dense round icon="delete" color="negative"
                       @click="() => $parent.$emit('apagar', props.row)" />
            </q-td>
        """)

        estado.tabela.on("editar", lambda e: _dialog_jogo(e.args))
        estado.tabela.on("apagar", lambda e: _confirmar_apagar(e.args))

    # Carregar dados iniciais
    _recarregar_tabela()