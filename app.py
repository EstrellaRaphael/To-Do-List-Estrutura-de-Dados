from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///db.sqlite"  # caminho para o banco de dados
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tarefas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    completa = db.Column(db.Boolean)
    criadoEm = db.Column(db.DateTime, default=datetime.utcnow)  # data de criação


class TarefasConcluidas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    concluidoEm = db.Column(
        db.DateTime, default=datetime.utcnow
    )  # guarda a data de conclusão


@app.route("/")
def index():
    # Mostrar todas as tarefas
    listaTarefas = Tarefas.query.order_by(Tarefas.criadoEm).all()
    return render_template("index.html", listaTarefas=listaTarefas)


@app.route("/adicionar", methods=["POST"])
def adicionar():
    # adicionar nova tarefa
    nomeTarefa = request.form.get("nomeTarefa")
    novaTarefa = Tarefas(titulo=nomeTarefa, completa=False)
    db.session.add(novaTarefa)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/concluir/<int:nomeTarefa_id>")
def concluir(nomeTarefa_id):
    # atualiza status da tarefa
    nomeTarefa = Tarefas.query.filter_by(id=nomeTarefa_id).first()
    nomeTarefa.completa = not nomeTarefa.completa
    tarefasConcluidas = TarefasConcluidas(titulo=nomeTarefa_id)
    db.session.add(tarefasConcluidas)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/deletar/<int:nomeTarefa_id>")
def deletar(nomeTarefa_id):
    # deleta uma tarefa
    nomeTarefa = Tarefas.query.filter_by(id=nomeTarefa_id).first()
    db.session.delete(nomeTarefa)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/concluirMaisAntiga")
def concluirMaisAntiga():
    # procupa pela tarefa incompleta mais antiga
    maisAntiga = (
        Tarefas.query.filter_by(completa=False).order_by(Tarefas.criadoEm).first()
    )
    if maisAntiga:
        tarefasConcluidas = TarefasConcluidas(titulo=maisAntiga.titulo)
        db.session.add(tarefasConcluidas)
        maisAntiga.completa = True
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/tarefasConcluidas")
def tarefasConcluidas():
    tarefasConcluidas = TarefasConcluidas.query.order_by(TarefasConcluidas.concluidoEm).all()
    return render_template("concluidas.html", tarefasConcluidas=tarefasConcluidas)



if __name__ == "__main__":
    with app.app_context():  # contexto de aplicação
        db.create_all()  # cria o db
    app.run(debug=True)
