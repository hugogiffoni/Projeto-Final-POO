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

# ---------------------------------------------------------------- dialogs
def _dialog_cliente(cliente: dict | None = None) -> None:
    """
    Dialog para criar (cliente=None) ou editar (cliente=dict) um cliente.
    """
    a_editar = cliente is not None
    titulo = "✏️ Editar Cliente" if a_editar else "➕ Novo Cliente"

    with ui.dialog() as dialog, ui.card().classes("min-w-96"):
        ui.label(titulo).classes("text-xl font-bold")

        in_nome = ui.input("Nome *", value=cliente["nome"] if a_editar else "") \
            .classes("w-full")
        in_email = ui.input("Email",
                            value=cliente.get("email", "") if a_editar else "") \
            .classes("w-full")
        in_telefone = ui.input("Telefone",
                               value=cliente.get("telefone", "") if a_editar else "") \
            .classes("w-full")
        in_morada = ui.input("Morada",
                             value=cliente.get("morada", "") if a_editar else "") \
            .classes("w-full")

        def guardar() -> None:
            payload = {
                "nome": in_nome.value.strip(),
                "email": in_email.value.strip() or None,
                "telefone": in_telefone.value.strip() or None,
                "morada": in_morada.value.strip() or None,
            }
            if not payload["nome"]:
                ui.notify("O nome é obrigatório.", type="warning")
                return
            try:
                if a_editar:
                    api_client.atualizar_cliente(cliente["id_cliente"], payload)
                    _notificar_sucesso("Cliente atualizado.")
                else:
                    api_client.criar_cliente(payload)
                    _notificar_sucesso("Cliente criado.")
            except APIError as e:
                _notificar_erro(e)
                return
            dialog.close()
            _recarregar_tabela()

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Guardar", on_click=guardar, icon="save").props("color=primary")

    dialog.open()


def _confirmar_apagar(cliente: dict) -> None:
    """Dialog de confirmação antes de apagar."""
    with ui.dialog() as dialog, ui.card():
        ui.label(f"Apagar o cliente '{cliente['nome']}'?").classes("text-lg")
        ui.label("Esta ação não pode ser desfeita.").classes("text-sm text-gray-600")

        def confirmar() -> None:
            try:
                api_client.apagar_cliente(cliente["id_cliente"])
                _notificar_sucesso("Cliente apagado.")
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
def criar_pagina_clientes() -> None:
    """Constrói a página completa de clientes."""
    with ui.column().classes("w-full p-6 gap-4"):
        # Cabeçalho da página
        with ui.row().classes("w-full items-center"):
            ui.label("👥 Gestão de Clientes").classes("text-3xl font-bold")
            ui.space()
            ui.button("Novo Cliente", icon="person_add",
                      on_click=lambda: _dialog_cliente()) \
                .props("color=primary")

        # Barra de pesquisa
        with ui.row().classes("w-full items-center gap-2"):
            estado.campo_pesquisa = ui.input(
                placeholder="Pesquisar por nome, email ou telefone...",
            ).classes("flex-grow").props("clearable outlined dense")
            estado.campo_pesquisa.on("update:model-value",
                                     lambda _: _recarregar_tabela())
            ui.button(icon="refresh", on_click=_recarregar_tabela) \
                .props("flat round").tooltip("Recarregar")

        # Tabela
        colunas = [
            {"name": "id_cliente", "label": "ID", "field": "id_cliente",
             "align": "left", "sortable": True},
            {"name": "nome", "label": "Nome", "field": "nome",
             "align": "left", "sortable": True},
            {"name": "email", "label": "Email", "field": "email", "align": "left"},
            {"name": "telefone", "label": "Telefone", "field": "telefone",
             "align": "left"},
            {"name": "morada", "label": "Morada", "field": "morada", "align": "left"},
            {"name": "acoes", "label": "Ações", "field": "acoes", "align": "center"},
        ]

        estado.tabela = ui.table(
            columns=colunas,
            rows=[],
            row_key="id_cliente",
            pagination=10,
        ).classes("w-full")

        # Slot personalizado para a coluna "acoes" (botões editar/apagar)
        estado.tabela.add_slot("body-cell-acoes", r"""
            <q-td :props="props">
                <q-btn flat dense round icon="edit" color="primary"
                       @click="() => $parent.$emit('editar', props.row)" />
                <q-btn flat dense round icon="delete" color="negative"
                       @click="() => $parent.$emit('apagar', props.row)" />
            </q-td>
        """)

        estado.tabela.on("editar", lambda e: _dialog_cliente(e.args))
        estado.tabela.on("apagar", lambda e: _confirmar_apagar(e.args))

    # Carregar dados iniciais
    _recarregar_tabela()    
