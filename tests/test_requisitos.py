"""
Suite de testes para verificar todos os requisitos do projeto.
Testa: Base de dados, Web Service (Flask), modelos e comunicação GUI→API.

Execução:
    python -m pytest tests/test_requisitos.py -v
"""

import json
import sys
import os
import tempfile
import sqlite3
import pytest

# Garante que a raiz do projeto está no PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    """Cria uma BD temporária com o schema real para os testes."""
    path = tmp_path_factory.mktemp("db") / "test.db"
    schema_file = os.path.join(ROOT, "database", "schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = sqlite3.connect(str(path))
    conn.executescript(schema)
    conn.close()
    return str(path)


@pytest.fixture(scope="session")
def flask_app(db_path):
    """Cria a app Flask apontando para BD de teste."""
    from webservice.config import Config
    from webservice.app import create_app
    from pathlib import Path

    class TestConfig(Config):
        TESTING = True
        DATABASE_PATH = Path(db_path)

    app = create_app(TestConfig)
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(flask_app):
    """Cliente HTTP de teste do Flask."""
    with flask_app.test_client() as c:
        yield c


# =====================================================================
# 1. BASE DE DADOS — SCHEMA E TABELAS
# =====================================================================

class TestBaseDados:
    """Verifica que o schema SQLite cumpre os requisitos."""

    def test_tabela_clientes_existe(self, db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        assert cur.fetchone() is not None, "Tabela 'clientes' não existe"
        conn.close()

    def test_tabela_jogos_existe(self, db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jogos'")
        assert cur.fetchone() is not None, "Tabela 'jogos' não existe"
        conn.close()

    def test_tabela_vendas_existe(self, db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vendas'")
        assert cur.fetchone() is not None, "Tabela 'vendas' não existe"
        conn.close()

    def test_clientes_colunas_obrigatorias(self, db_path):
        conn = sqlite3.connect(db_path)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(clientes)")}
        conn.close()
        for col in ["id_cliente", "nome", "morada", "telefone", "email"]:
            assert col in cols, f"Coluna '{col}' em falta na tabela clientes"

    def test_jogos_colunas_obrigatorias(self, db_path):
        conn = sqlite3.connect(db_path)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(jogos)")}
        conn.close()
        # schema normalizado: criador/editora/genero são FKs para tabelas separadas
        for col in ["id_jogo", "titulo", "ano_lancamento", "idade_minima", "preco"]:
            assert col in cols, f"Coluna '{col}' em falta na tabela jogos"

    def test_vendas_colunas_obrigatorias(self, db_path):
        conn = sqlite3.connect(db_path)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(vendas)")}
        conn.close()
        for col in ["id_venda", "id_cliente", "data_hora", "desconto", "valor_total"]:
            assert col in cols, f"Coluna '{col}' em falta na tabela vendas"

    def test_chave_estrangeira_vendas_cliente(self, db_path):
        conn = sqlite3.connect(db_path)
        fks = conn.execute("PRAGMA foreign_key_list(vendas)").fetchall()
        conn.close()
        tabelas_ref = {r[2] for r in fks}
        assert "clientes" in tabelas_ref, "FK vendas→clientes em falta"

    def test_normalizacao_tabelas_extra(self, db_path):
        """Schema normalizado deve ter tabelas além das 3 base (generos, editoras, criadores)."""
        conn = sqlite3.connect(db_path)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        conn.close()
        extras = tables - {"clientes", "jogos", "vendas", "sqlite_sequence"}
        assert len(extras) >= 1, "Esperado pelo menos uma tabela extra para normalização (ex: generos, editoras)"

    def test_itens_venda_existe(self, db_path):
        """Schema normalizado deve separar itens de venda numa tabela própria."""
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='itens_venda'")
        result = cur.fetchone()
        conn.close()
        assert result is not None, "Tabela 'itens_venda' não existe (necessária para normalização)"


# =====================================================================
# 2. MODELOS PYTHON
# =====================================================================

class TestModeloCliente:
    def test_criar_cliente_valido(self):
        from models.cliente import Cliente
        c = Cliente(nome="Ana Silva", email="ana@email.com", telefone="912345678")
        assert c.nome == "Ana Silva"
        assert c.email == "ana@email.com"

    def test_nome_vazio_levanta_erro(self):
        from models.cliente import Cliente
        with pytest.raises(ValueError):
            Cliente(nome="")

    def test_email_invalido_levanta_erro(self):
        from models.cliente import Cliente
        with pytest.raises(ValueError):
            Cliente(nome="Teste", email="nao_e_email")

    def test_to_dict(self):
        from models.cliente import Cliente
        c = Cliente(nome="Joao", email="joao@x.pt")
        d = c.to_dict()
        assert d["nome"] == "Joao"
        assert d["email"] == "joao@x.pt"

    def test_from_dict(self):
        from models.cliente import Cliente
        d = {"nome": "Maria", "email": "maria@x.pt", "morada": "Rua A", "telefone": "910000000"}
        c = Cliente.from_dict(d)
        assert c.nome == "Maria"

    def test_str_representacao(self):
        from models.cliente import Cliente
        c = Cliente(nome="Pedro", email="pedro@x.pt")
        assert "Pedro" in str(c)


class TestModeloVenda:
    def test_criar_venda(self):
        from models.venda import Venda
        v = Venda(id_cliente=1, desconto=10.0)
        assert v.id_cliente == 1
        assert v.desconto == 10.0

    def test_desconto_invalido(self):
        from models.venda import Venda
        with pytest.raises(ValueError):
            Venda(id_cliente=1, desconto=150)

    def test_adicionar_item(self):
        from models.venda import Venda
        from models.item_venda import ItemVenda
        v = Venda(id_cliente=1)
        item = ItemVenda(id_jogo=1, quantidade=2, preco_unitario=25.0)
        v.adicionar_item(item)
        assert len(v.itens) == 1

    def test_valor_total_com_desconto(self):
        from models.venda import Venda
        from models.item_venda import ItemVenda
        v = Venda(id_cliente=1, desconto=10.0)
        v.adicionar_item(ItemVenda(id_jogo=1, quantidade=1, preco_unitario=100.0))
        assert v.valor_total() == 90.0

    def test_validar_sem_itens(self):
        from models.venda import Venda
        v = Venda(id_cliente=1)
        with pytest.raises(ValueError):
            v.validar()

    def test_remover_item(self):
        from models.venda import Venda
        from models.item_venda import ItemVenda
        v = Venda(id_cliente=1)
        v.adicionar_item(ItemVenda(id_jogo=5, quantidade=1, preco_unitario=20.0))
        removido = v.remover_item(5)
        assert removido is True
        assert len(v.itens) == 0


class TestModeloItemVenda:
    def test_criar_item(self):
        from models.item_venda import ItemVenda
        item = ItemVenda(id_jogo=3, quantidade=2, preco_unitario=30.0)
        assert item.subtotal() == 60.0

    def test_quantidade_invalida(self):
        from models.item_venda import ItemVenda
        with pytest.raises(ValueError):
            ItemVenda(id_jogo=1, quantidade=0, preco_unitario=10.0)

    def test_preco_negativo(self):
        from models.item_venda import ItemVenda
        with pytest.raises(ValueError):
            ItemVenda(id_jogo=1, quantidade=1, preco_unitario=-5.0)


# =====================================================================
# 3. WEB SERVICE FLASK — ENDPOINTS
# =====================================================================

class TestHealthEndpoint:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data is not None

    def test_root_endpoint(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.get_json()
        assert "servico" in data or "endpoints_disponiveis" in data or "versao" in data


class TestClientesEndpoints:
    def test_listar_clientes_vazio(self, client):
        r = client.get("/api/clientes")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)

    def test_criar_cliente(self, client):
        import time
        ts = int(time.time() * 1000)
        payload = {"nome": "Test User", "email": f"testuser{ts}@example.com", "telefone": "912000001"}
        r = client.post("/api/clientes", json=payload)
        assert r.status_code == 201
        data = r.get_json()
        assert data["nome"] == "Test User"
        assert "id_cliente" in data
        return data["id_cliente"]

    def test_criar_cliente_sem_nome(self, client):
        r = client.post("/api/clientes", json={"email": "x@x.com"})
        assert r.status_code in (400, 422)

    def test_criar_cliente_email_duplicado(self, client):
        email = "duplicado_test@example.com"
        client.post("/api/clientes", json={"nome": "A", "email": email})
        r = client.post("/api/clientes", json={"nome": "B", "email": email})
        assert r.status_code == 409

    def test_obter_cliente_nao_existe(self, client):
        r = client.get("/api/clientes/999999")
        assert r.status_code == 404

    def test_atualizar_cliente(self, client):
        import time
        ts = int(time.time() * 1000)
        r = client.post("/api/clientes", json={"nome": "Para Atualizar", "email": f"update{ts}@x.com"})
        assert r.status_code == 201
        id_c = r.get_json()["id_cliente"]
        r2 = client.put(f"/api/clientes/{id_c}", json={"nome": "Atualizado"})
        assert r2.status_code == 200
        assert r2.get_json()["nome"] == "Atualizado"

    def test_apagar_cliente_sem_vendas(self, client):
        import time
        ts = int(time.time() * 1000)
        r = client.post("/api/clientes", json={"nome": "Para Apagar", "email": f"delete{ts}@x.com"})
        assert r.status_code == 201
        id_c = r.get_json()["id_cliente"]
        r2 = client.delete(f"/api/clientes/{id_c}")
        assert r2.status_code == 200

    def test_pesquisa_clientes(self, client):
        client.post("/api/clientes", json={"nome": "Pesquisa Unico", "email": "pesquisa_unico@x.com"})
        r = client.get("/api/clientes?q=Pesquisa Unico")
        assert r.status_code == 200


class TestJogosEndpoints:
    def _criar_jogo(self, client, titulo="Catan", preco=39.99):
        payload = {
            "titulo": titulo,
            "criador": "Klaus Teuber",
            "editora": "Devir",
            "genero": "Estratégia",
            "ano_lancamento": 1995,
            "idade_minima": 10,
            "preco": preco,
            "stock": 10,
        }
        return client.post("/api/jogos", json=payload)

    def _jogo_data(self, response):
        """Extrai dados do jogo, independentemente do formato da resposta."""
        d = response.get_json()
        # Suporte a resposta aninhada {"jogo": {...}} ou plana
        return d.get("jogo", d) if isinstance(d, dict) else d

    def test_listar_jogos(self, client):
        r = client.get("/api/jogos")
        assert r.status_code == 200

    def test_criar_jogo(self, client):
        r = self._criar_jogo(client, "Ticket to Ride", 49.99)
        assert r.status_code == 201
        data = self._jogo_data(r)
        assert data["titulo"] == "Ticket to Ride"
        assert "id_jogo" in data

    def test_criar_jogo_sem_titulo(self, client):
        r = client.post("/api/jogos", json={"preco": 10.0})
        assert r.status_code in (400, 422)

    def test_obter_jogo_nao_existe(self, client):
        r = client.get("/api/jogos/999999")
        assert r.status_code == 404

    def test_atualizar_jogo(self, client):
        r = self._criar_jogo(client, "Para Atualizar Jogo", 20.0)
        id_j = self._jogo_data(r)["id_jogo"]
        r2 = client.put(f"/api/jogos/{id_j}", json={"preco": 25.0})
        assert r2.status_code == 200
        assert self._jogo_data(r2)["preco"] == 25.0

    def test_apagar_jogo(self, client):
        r = self._criar_jogo(client, "Para Apagar Jogo", 10.0)
        id_j = self._jogo_data(r)["id_jogo"]
        r2 = client.delete(f"/api/jogos/{id_j}")
        assert r2.status_code == 200


class TestVendasEndpoints:
    def _criar_jogo_helper(self, client):
        """Cria um jogo e devolve o seu id, suportando resposta aninhada."""
        import time
        ts = str(int(time.time() * 1000))
        rj = client.post("/api/jogos", json={
            "titulo": f"Jogo Venda {ts}", "criador": "A", "editora": "B",
            "genero": "Estratégia", "ano_lancamento": 2020,
            "idade_minima": 8, "preco": 30.0, "stock": 20
        })
        assert rj.status_code == 201
        d = rj.get_json()
        return d.get("jogo", d)["id_jogo"] if isinstance(d, dict) else d["id_jogo"]

    def _setup_cliente_e_jogo(self, client):
        import time
        ts = str(int(time.time() * 1000))
        rc = client.post("/api/clientes", json={"nome": f"Cliente Venda {ts}", "email": f"cv{ts}@x.com"})
        assert rc.status_code == 201
        id_c = rc.get_json()["id_cliente"]
        id_j = self._criar_jogo_helper(client)
        return id_c, id_j

    def _get_stock(self, client, id_j):
        r = client.get(f"/api/jogos/{id_j}")
        d = r.get_json()
        return d.get("jogo", d)["stock"] if isinstance(d, dict) else d["stock"]

    def test_criar_venda(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        payload = {"id_cliente": id_c, "desconto": 0, "itens": [{"id_jogo": id_j, "quantidade": 2}]}
        r = client.post("/api/vendas", json=payload)
        assert r.status_code == 201
        data = r.get_json()
        assert data["id_cliente"] == id_c
        assert data["valor_total"] == 60.0

    def test_criar_venda_com_desconto(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        payload = {"id_cliente": id_c, "desconto": 10, "itens": [{"id_jogo": id_j, "quantidade": 1}]}
        r = client.post("/api/vendas", json=payload)
        assert r.status_code == 201
        assert r.get_json()["valor_total"] == 27.0

    def test_criar_venda_sem_cliente(self, client):
        r = client.post("/api/vendas", json={"id_cliente": 999999, "itens": [{"id_jogo": 1, "quantidade": 1}]})
        assert r.status_code == 404

    def test_criar_venda_sem_itens(self, client):
        id_c, _ = self._setup_cliente_e_jogo(client)
        r = client.post("/api/vendas", json={"id_cliente": id_c, "itens": []})
        assert r.status_code == 400

    def test_stock_decrementado_apos_venda(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        stock_antes = self._get_stock(client, id_j)
        client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 3}]})
        stock_depois = self._get_stock(client, id_j)
        assert stock_depois == stock_antes - 3

    def test_stock_insuficiente(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        r = client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 9999}]})
        assert r.status_code == 409

    def test_listar_vendas(self, client):
        r = client.get("/api/vendas")
        assert r.status_code == 200
        data = r.get_json()
        assert "vendas" in data or isinstance(data, list)

    def test_obter_venda(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        rv = client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 1}]})
        id_v = rv.get_json()["id_venda"]
        r = client.get(f"/api/vendas/{id_v}")
        assert r.status_code == 200
        assert r.get_json()["id_venda"] == id_v

    def test_anular_venda_repoe_stock(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        stock_antes = self._get_stock(client, id_j)
        rv = client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 2}]})
        id_v = rv.get_json()["id_venda"]
        client.delete(f"/api/vendas/{id_v}")
        assert self._get_stock(client, id_j) == stock_antes

    def test_historico_cliente(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 1}]})
        r = client.get(f"/api/vendas/cliente/{id_c}")
        assert r.status_code == 200
        data = r.get_json()
        assert "vendas" in data
        assert data["total_vendas"] >= 1

    def test_apagar_cliente_com_vendas_bloqueado(self, client):
        id_c, id_j = self._setup_cliente_e_jogo(client)
        client.post("/api/vendas", json={"id_cliente": id_c, "itens": [{"id_jogo": id_j, "quantidade": 1}]})
        r = client.delete(f"/api/clientes/{id_c}")
        assert r.status_code == 409


# =====================================================================
# 4. RESPOSTAS JSON CORRETAS
# =====================================================================

class TestRespostasJSON:
    def test_erro_404_e_json(self, client):
        r = client.get("/api/clientes/999999")
        assert r.content_type and "json" in r.content_type

    def test_erro_metodo_nao_permitido(self, client):
        r = client.patch("/api/clientes")
        assert r.status_code == 405

    def test_criacao_retorna_201(self, client):
        import time
        ts = int(time.time() * 1000)
        r = client.post("/api/clientes", json={"nome": f"JSON Test {ts}", "email": f"json{ts}@x.com"})
        assert r.status_code == 201

    def test_gui_usa_httpx_nao_direto_bd(self):
        """Verifica que o api_client usa httpx e não sqlite3 diretamente."""
        import inspect
        import gui.api_client as api_mod
        src = inspect.getsource(api_mod)
        assert "httpx" in src, "GUI api_client deve usar httpx"
        assert "sqlite3" not in src, "GUI não deve importar sqlite3 (comunicação via API)"

    def test_api_client_tem_funcoes_crud_clientes(self):
        from gui import api_client
        assert callable(api_client.listar_clientes)
        assert callable(api_client.criar_cliente)
        assert callable(api_client.atualizar_cliente)
        assert callable(api_client.apagar_cliente)

    def test_api_client_tem_funcoes_vendas(self):
        from gui import api_client
        assert callable(api_client.criar_venda)
        assert callable(api_client.listar_vendas)
        assert callable(api_client.historico_cliente)


# =====================================================================
# 5. CONEXÃO À BD
# =====================================================================

class TestConexaoBD:
    def test_context_manager(self, db_path):
        from database.connection import Database
        with Database(db_path) as db:
            result = db.fetch_all("SELECT * FROM clientes")
        assert isinstance(result, list)

    def test_fetch_one_inexistente(self, db_path):
        from database.connection import Database
        with Database(db_path) as db:
            result = db.fetch_one("SELECT * FROM clientes WHERE id_cliente = ?", (999999,))
        assert result is None

    def test_insert_e_fetch(self, db_path):
        from database.connection import Database
        with Database(db_path) as db:
            new_id = db.insert(
                "INSERT INTO clientes (nome, email) VALUES (?, ?)",
                ("DB Test", "dbtest_conn@x.com")
            )
            assert new_id is not None
            row = db.fetch_one("SELECT * FROM clientes WHERE id_cliente = ?", (new_id,))
            assert row["nome"] == "DB Test"

    def test_rollback_em_erro(self, db_path):
        from database.connection import Database
        with Database(db_path) as db:
            with pytest.raises(Exception):
                db.execute("INSERT INTO tabela_inexistente (col) VALUES (?)", ("x",))
