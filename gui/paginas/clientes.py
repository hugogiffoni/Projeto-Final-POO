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
