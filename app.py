from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///conecta_bairro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# MODELOS DO BANCO DE DADOS
# =========================

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    disponivel = db.Column(db.Boolean, default=True)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("cliente.id"),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Recebido"
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.now
    )

    cliente = db.relationship(
        "Cliente",
        backref="pedidos"
    )


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedido.id"),
        nullable=False
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produto.id"),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    preco_unitario = db.Column(
        db.Float,
        nullable=False
    )

    pedido = db.relationship(
        "Pedido",
        backref="itens"
    )

    produto = db.relationship("Produto")


# =========================
# PÁGINA INICIAL
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# CLIENTES
# =========================

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()

        if not nome:
            erro = "Informe o nome do cliente."

        else:
            novo_cliente = Cliente(
                nome=nome,
                telefone=telefone
            )

            db.session.add(novo_cliente)
            db.session.commit()

            return redirect(url_for("clientes"))

    lista_clientes = Cliente.query.order_by(
        Cliente.id.desc()
    ).all()

    return render_template(
        "clientes.html",
        clientes=lista_clientes,
        erro=erro
    )


# =========================
# PRODUTOS
# =========================

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_texto = request.form.get("preco", "").strip()

        if not nome:
            erro = "Informe o nome do produto."

        elif not preco_texto:
            erro = "Informe o preço do produto."

        else:
            try:
                preco = float(
                    preco_texto.replace(",", ".")
                )

                if preco <= 0:
                    erro = "O preço deve ser maior que zero."

                else:
                    novo_produto = Produto(
                        nome=nome,
                        preco=preco,
                        disponivel=True
                    )

                    db.session.add(novo_produto)
                    db.session.commit()

                    return redirect(
                        url_for("produtos")
                    )

            except ValueError:
                erro = "Informe um preço válido."

    lista_produtos = Produto.query.order_by(
        Produto.id.desc()
    ).all()

    return render_template(
        "produtos.html",
        produtos=lista_produtos,
        erro=erro
    )

# =========================
# PEDIDOS
# =========================

@app.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    erro = None

    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.filter_by(disponivel=True).order_by(Produto.nome).all()

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        produto_id = request.form.get("produto_id")
        quantidade_texto = request.form.get("quantidade", "").strip()

        if not cliente_id:
            erro = "Selecione um cliente."

        elif not produto_id:
            erro = "Selecione um produto."

        elif not quantidade_texto:
            erro = "Informe a quantidade."

        else:
            try:
                quantidade = int(quantidade_texto)

                if quantidade <= 0:
                    erro = "A quantidade deve ser maior que zero."

                else:
                    produto = db.session.get(Produto, int(produto_id))
                    cliente = db.session.get(Cliente, int(cliente_id))

                    if not produto or not produto.disponivel:
                        erro = "Produto inválido ou indisponível."

                    elif not cliente:
                        erro = "Cliente inválido."

                    else:
                        novo_pedido = Pedido(
                            cliente_id=cliente.id,
                            status="Recebido"
                        )

                        db.session.add(novo_pedido)
                        db.session.flush()

                        item = ItemPedido(
                            pedido_id=novo_pedido.id,
                            produto_id=produto.id,
                            quantidade=quantidade,
                            preco_unitario=produto.preco
                        )

                        db.session.add(item)
                        db.session.commit()

                        return redirect(url_for("pedidos"))

            except (ValueError, TypeError):
                erro = "Dados do pedido inválidos."

    lista_pedidos = Pedido.query.order_by(
        Pedido.id.desc()
    ).all()

    return render_template(
        "pedidos.html",
        clientes=clientes,
        produtos=produtos,
        pedidos=lista_pedidos,
        erro=erro
    )

# =========================
# CRIAÇÃO DO BANCO
# =========================

with app.app_context():
    db.create_all()


# =========================
# EXECUÇÃO DA APLICAÇÃO
# =========================

if __name__ == "__main__":
    app.run(debug=True)