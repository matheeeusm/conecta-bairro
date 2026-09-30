import pytest

from app import app, db, Cliente, Produto, Pedido, ItemPedido


@pytest.fixture
def cliente_teste():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        with app.test_client() as cliente:
            yield cliente

        db.session.remove()
        db.drop_all()


def test_pagina_inicial(cliente_teste):
    resposta = cliente_teste.get("/")

    assert resposta.status_code == 200
    assert b"Conecta Bairro" in resposta.data


def test_pagina_clientes(cliente_teste):
    resposta = cliente_teste.get("/clientes")

    assert resposta.status_code == 200


def test_cadastro_cliente(cliente_teste):
    resposta = cliente_teste.post(
        "/clientes",
        data={
            "nome": "Cliente Teste",
            "telefone": "11999999999"
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    cliente = Cliente.query.filter_by(
        nome="Cliente Teste"
    ).first()

    assert cliente is not None
    assert cliente.telefone == "11999999999"


def test_cliente_sem_nome(cliente_teste):
    resposta = cliente_teste.post(
        "/clientes",
        data={
            "nome": "",
            "telefone": "11999999999"
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200
    assert "Informe o nome do cliente." in resposta.get_data(as_text=True)


def test_cadastro_produto(cliente_teste):
    resposta = cliente_teste.post(
        "/produtos",
        data={
            "nome": "Arroz 5kg",
            "preco": "25,50"
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    produto = Produto.query.filter_by(
        nome="Arroz 5kg"
    ).first()

    assert produto is not None
    assert produto.preco == 25.50


def test_produto_preco_invalido(cliente_teste):
    resposta = cliente_teste.post(
        "/produtos",
        data={
            "nome": "Produto Teste",
            "preco": "abc"
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200
    assert "Informe um preço válido." in resposta.get_data(as_text=True)


def test_integracao_cliente_produto_pedido(cliente_teste):
    cliente = Cliente(
        nome="Maria Silva",
        telefone="11988887777"
    )

    produto = Produto(
        nome="Feijão 1kg",
        preco=8.50,
        disponivel=True
    )

    db.session.add(cliente)
    db.session.add(produto)
    db.session.commit()

    pedido = Pedido(
        cliente_id=cliente.id,
        status="Recebido"
    )

    db.session.add(pedido)
    db.session.commit()

    item = ItemPedido(
        pedido_id=pedido.id,
        produto_id=produto.id,
        quantidade=2,
        preco_unitario=produto.preco
    )

    db.session.add(item)
    db.session.commit()

    pedido_salvo = Pedido.query.first()

    assert pedido_salvo is not None
    assert pedido_salvo.cliente.nome == "Maria Silva"
    assert pedido_salvo.itens[0].produto.nome == "Feijão 1kg"
    assert pedido_salvo.itens[0].quantidade == 2
    assert pedido_salvo.itens[0].preco_unitario == 8.50