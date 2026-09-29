from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///conecta_bairro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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
    status = db.Column(db.String(30), default="Recebido")
    criado_em = db.Column(db.DateTime, default=datetime.now)

    cliente = db.relationship("Cliente", backref="pedidos")


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
    quantidade = db.Column(db.Integer, nullable=False)

    pedido = db.relationship("Pedido", backref="itens")
    produto = db.relationship("Produto")


@app.route("/")
def index():
    return render_template("index.html")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)