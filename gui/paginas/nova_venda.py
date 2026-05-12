"""
Página de registo de uma Nova Venda (carrinho de compras).

Fluxo:
    1. Selecionar cliente (existente ou criar novo)
    2. Adicionar jogos ao carrinho (quantidade + desconto por linha)
    3. Ver total calculado em tempo real
    4. Confirmar -> POST /api/vendas para cada linha
"""
from nicegui import ui

from gui import api_client
from gui.api_client import APIError


# ---------------------------------------------------------------- estado
class _Estado:
    """Estado da página de nova venda."""
    cliente: dict | None = None
    carrinho: list[dict] = []  # [{jogo: dict, quantidade: int, desconto: float}]

    # Referências de UI para refresh
    label_cliente: ui.label | None = None
    tabela_carrinho: ui.table | None = None
    label_total: ui.label | None = None
    select_jogo: ui.select | None = None
    todos_os_jogos: list[dict] = []


estado = _Estado()


# ---------------------------------------------------------------- helpers
def _notificar_erro(e: APIError | str) -> None:
    msg = str(e)
    ui.notify(f"❌ {msg}", type="negative", position="top")


def _notificar_sucesso(msg: str) -> None:
    ui.notify(f"✅ {msg}", type="positive", position="top")


def _formatar_eur(valor: float) -> str:
    return f"{valor:.2f} €".replace(".", ",")


def _calcular_subtotal(linha: dict) -> float:
    """Subtotal de uma linha = preço * quantidade * (1 - desconto%)."""
    preco = float(linha["jogo"].get("preco") or 0)
    qtd = int(linha["quantidade"])
    desc = float(linha["desconto"]) / 100.0
    return round(preco * qtd * (1 - desc), 2)


def _calcular_total() -> float:
    return round(sum(_calcular_subtotal(l) for l in estado.carrinho), 2)


# ---------------------------------------------------------------- cliente
def _dialog_selecionar_cliente() -> None:
    """Dialog para pesquisar e selecionar um cliente."""
    try:
        clientes = api_client.listar_clientes()
    except APIError as e:
        _notificar_erro(e)
        return

    with ui.dialog() as dialog, ui.card().classes("min-w-[600px]"):
        ui.label("👤 Selecionar Cliente").classes("text-xl font-bold")

        campo_pesq = ui.input(placeholder="Pesquisar...") \
            .classes("w-full").props("clearable outlined dense")

        colunas = [
            {"name": "nome", "label": "Nome", "field": "nome", "align": "left"},
            {"name": "email", "label": "Email", "field": "email", "align": "left"},
            {"name": "telefone", "label": "Telefone", "field": "telefone",
             "align": "left"},
        ]

        tabela = ui.table(
            columns=colunas,
            rows=clientes,
            row_key="id_cliente",
            pagination=5,
            selection="single",
        ).classes("w-full")

        def filtrar() -> None:
            termo = (campo_pesq.value or "").lower().strip()
            if not termo:
                tabela.rows = clientes
            else:
                tabela.rows = [
                    c for c in clientes
                    if termo in (c.get("nome") or "").lower()
                    or termo in (c.get("email") or "").lower()
                    or termo in (c.get("telefone") or "").lower()
                ]
            tabela.update()

        campo_pesq.on("update:model-value", lambda _: filtrar())

        def confirmar() -> None:
            if not tabela.selected:
                ui.notify("Seleciona um cliente.", type="warning")
                return
            estado.cliente = tabela.selected[0]
            _atualizar_label_cliente()
            dialog.close()
            _notificar_sucesso(f"Cliente: {estado.cliente['nome']}")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Selecionar", on_click=confirmar, icon="check") \
                .props("color=primary")

    dialog.open()


def _dialog_novo_cliente() -> None:
    """Cria rapidamente um cliente e seleciona-o automaticamente."""
    with ui.dialog() as dialog, ui.card().classes("min-w-96"):
        ui.label("➕ Novo Cliente").classes("text-xl font-bold")

        in_nome = ui.input("Nome *").classes("w-full")
        in_email = ui.input("Email").classes("w-full")
        in_telefone = ui.input("Telefone").classes("w-full")
        in_morada = ui.input("Morada").classes("w-full")

        def guardar() -> None:
            if not (in_nome.value or "").strip():
                ui.notify("O nome é obrigatório.", type="warning")
                return
            payload = {
                "nome": in_nome.value.strip(),
                "email": (in_email.value or "").strip() or None,
                "telefone": (in_telefone.value or "").strip() or None,
                "morada": (in_morada.value or "").strip() or None,
            }
            try:
                novo = api_client.criar_cliente(payload)
            except APIError as e:
                _notificar_erro(e)
                return

            estado.cliente = novo
            _atualizar_label_cliente()
            dialog.close()
            _notificar_sucesso(f"Cliente '{novo['nome']}' criado e selecionado.")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancelar", on_click=dialog.close).props("flat")
            ui.button("Criar", on_click=guardar, icon="save") \
                .props("color=primary")

    dialog.open()


def _atualizar_label_cliente() -> None:
    if estado.label_cliente is None:
        return
    if estado.cliente is None:
        estado.label_cliente.text = "Nenhum cliente selecionado"
        estado.label_cliente.classes(replace="text-lg text-gray-500 italic")
    else:
        c = estado.cliente
        partes = [c["nome"]]
        if c.get("telefone"):
            partes.append(f"📞 {c['telefone']}")
        if c.get("email"):
            partes.append(f"✉️ {c['email']}")
        estado.label_cliente.text = "  •  ".join(partes)
        estado.label_cliente.classes(replace="text-lg font-semibold text-primary")

# ---------------------------------------------------------------- carrinho
def _adicionar_jogo() -> None:
    """Adiciona o jogo selecionado no dropdown ao carrinho."""
    if estado.select_jogo is None or estado.select_jogo.value is None:
        ui.notify("Seleciona um jogo primeiro.", type="warning")
        return

    id_jogo = estado.select_jogo.value
    jogo = next((j for j in estado.todos_os_jogos if j["id_jogo"] == id_jogo), None)
    if jogo is None:
        ui.notify("Jogo inválido.", type="negative")
        return

    # Se já está no carrinho, incrementa quantidade em vez de duplicar
    for linha in estado.carrinho:
        if linha["jogo"]["id_jogo"] == id_jogo:
            linha["quantidade"] += 1
            _refrescar_carrinho()
            return

    estado.carrinho.append({
        "jogo": jogo,
        "quantidade": 1,
        "desconto": 0.0,
    })
    estado.select_jogo.set_value(None)
    _refrescar_carrinho()


def _remover_linha(id_jogo: int) -> None:
    estado.carrinho = [
        l for l in estado.carrinho if l["jogo"]["id_jogo"] != id_jogo
    ]
    _refrescar_carrinho()


def _refrescar_carrinho() -> None:
    """Reconstrói as rows da tabela do carrinho e atualiza o total."""
    if estado.tabela_carrinho is None:
        return

    rows = []
    for linha in estado.carrinho:
        rows.append({
            "id_jogo": linha["jogo"]["id_jogo"],
            "titulo": linha["jogo"]["titulo"],
            "preco_fmt": _formatar_eur(float(linha["jogo"].get("preco") or 0)),
            "quantidade": linha["quantidade"],
            "desconto": linha["desconto"],
            "subtotal_fmt": _formatar_eur(_calcular_subtotal(linha)),
        })

    estado.tabela_carrinho.rows = rows
    estado.tabela_carrinho.update()

    if estado.label_total is not None:
        estado.label_total.text = f"Total: {_formatar_eur(_calcular_total())}"


def _atualizar_quantidade(id_jogo: int, nova_qtd) -> None:
    try:
        qtd = int(nova_qtd)
    except (TypeError, ValueError):
        return
    if qtd < 1:
        qtd = 1
    for linha in estado.carrinho:
        if linha["jogo"]["id_jogo"] == id_jogo:
            linha["quantidade"] = qtd
            break
    _refrescar_carrinho()


def _atualizar_desconto(id_jogo: int, novo_desc) -> None:
    try:
        desc = float(novo_desc)
    except (TypeError, ValueError):
        return
    desc = max(0.0, min(100.0, desc))
    for linha in estado.carrinho:
        if linha["jogo"]["id_jogo"] == id_jogo:
            linha["desconto"] = desc
            break
    _refrescar_carrinho()        

# ---------------------------------------------------------------- confirmar
def _confirmar_venda() -> None:
    """Envia cada linha do carrinho como uma venda separada para o backend."""
    if estado.cliente is None:
        ui.notify("Seleciona um cliente.", type="warning")
        return
    if not estado.carrinho:
        ui.notify("O carrinho está vazio.", type="warning")
        return

    erros: list[str] = []
    sucesso = 0
    for linha in estado.carrinho:
        payload = {
            "id_cliente": estado.cliente["id_cliente"],
            "id_jogo": linha["jogo"]["id_jogo"],
            "quantidade": linha["quantidade"],
            "desconto": linha["desconto"],
        }
        try:
            api_client.criar_venda(payload)
            sucesso += 1
        except APIError as e:
            erros.append(f"{linha['jogo']['titulo']}: {e}")

    if erros:
        _notificar_erro("Algumas linhas falharam:\n" + "\n".join(erros))
    if sucesso:
        _notificar_sucesso(
            f"Venda registada! {sucesso} linha(s) gravada(s). "
            f"Total: {_formatar_eur(_calcular_total())}"
        )
        # Limpar para nova venda
        estado.cliente = None
        estado.carrinho = []
        _atualizar_label_cliente()
        _refrescar_carrinho()    

# ---------------------------------------------------------------- página
def criar_pagina_nova_venda() -> None:
    """Constrói a página completa de nova venda."""
    # Carrega catálogo de jogos para o dropdown
    try:
        estado.todos_os_jogos = api_client.listar_jogos()
    except APIError as e:
        _notificar_erro(e)
        estado.todos_os_jogos = []

    opcoes_jogos = {
        j["id_jogo"]: f"{j['titulo']} — {_formatar_eur(float(j.get('preco') or 0))}"
        for j in estado.todos_os_jogos
    }

    with ui.column().classes("w-full p-6 gap-4"):
        ui.label("🛒 Nova Venda").classes("text-3xl font-bold")

        # ---------- Cartão do Cliente ----------
        with ui.card().classes("w-full"):
            ui.label("1️⃣ Cliente").classes("text-lg font-bold")
            with ui.row().classes("w-full items-center gap-2"):
                estado.label_cliente = ui.label("Nenhum cliente selecionado") \
                    .classes("text-lg text-gray-500 italic flex-grow")
                ui.button("Selecionar", icon="search",
                          on_click=_dialog_selecionar_cliente) \
                    .props("color=primary outline")
                ui.button("Novo Cliente", icon="person_add",
                          on_click=_dialog_novo_cliente) \
                    .props("color=primary")

        # ---------- Cartão de Adicionar Jogos ----------
        with ui.card().classes("w-full"):
            ui.label("2️⃣ Adicionar Jogos").classes("text-lg font-bold")
            with ui.row().classes("w-full items-end gap-2"):
                estado.select_jogo = ui.select(
                    options=opcoes_jogos,
                    label="Jogo",
                    with_input=True,
                    clearable=True,
                ).classes("flex-grow").props("outlined dense")
                ui.button("Adicionar", icon="add_shopping_cart",
                          on_click=_adicionar_jogo) \
                    .props("color=primary")

        # ---------- Cartão do Carrinho ----------
        with ui.card().classes("w-full"):
            ui.label("3️⃣ Carrinho").classes("text-lg font-bold")

            colunas = [
                {"name": "titulo", "label": "Jogo", "field": "titulo",
                 "align": "left"},
                {"name": "preco_fmt", "label": "Preço Unit.",
                 "field": "preco_fmt", "align": "right"},
                {"name": "quantidade", "label": "Qtd.", "field": "quantidade",
                 "align": "center"},
                {"name": "desconto", "label": "Desc. (%)", "field": "desconto",
                 "align": "center"},
                {"name": "subtotal_fmt", "label": "Subtotal",
                 "field": "subtotal_fmt", "align": "right"},
                {"name": "acoes", "label": "", "field": "acoes",
                 "align": "center"},
            ]

            estado.tabela_carrinho = ui.table(
                columns=colunas,
                rows=[],
                row_key="id_jogo",
            ).classes("w-full")

            # Quantidade editável
            estado.tabela_carrinho.add_slot("body-cell-quantidade", r"""
                <q-td :props="props">
                    <q-input dense type="number" :model-value="props.row.quantidade"
                             @update:model-value="(v) => $parent.$emit('qtd', {id: props.row.id_jogo, v: v})"
                             style="width: 80px" :min="1" />
                </q-td>
            """)

            # Desconto editável
            estado.tabela_carrinho.add_slot("body-cell-desconto", r"""
                <q-td :props="props">
                    <q-input dense type="number" :model-value="props.row.desconto"
                             @update:model-value="(v) => $parent.$emit('desc', {id: props.row.id_jogo, v: v})"
                             style="width: 80px" :min="0" :max="100" />
                </q-td>
            """)

            # Botão remover
            estado.tabela_carrinho.add_slot("body-cell-acoes", r"""
                <q-td :props="props">
                    <q-btn flat dense round icon="delete" color="negative"
                           @click="() => $parent.$emit('remover', props.row.id_jogo)" />
                </q-td>
            """)

            estado.tabela_carrinho.on(
                "qtd", lambda e: _atualizar_quantidade(e.args["id"], e.args["v"]))
            estado.tabela_carrinho.on(
                "desc", lambda e: _atualizar_desconto(e.args["id"], e.args["v"]))
            estado.tabela_carrinho.on(
                "remover", lambda e: _remover_linha(e.args))

            # Total + botão confirmar
            with ui.row().classes("w-full items-center justify-end mt-4 gap-4"):
                estado.label_total = ui.label("Total: 0,00 €") \
                    .classes("text-2xl font-bold text-primary")
                ui.button("Confirmar Venda", icon="check_circle",
                          on_click=_confirmar_venda) \
                    .props("color=positive size=lg")

    # Estado inicial
    _atualizar_label_cliente()
    _refrescar_carrinho()        