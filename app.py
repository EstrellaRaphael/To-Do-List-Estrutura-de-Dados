from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class Nodo:
    def __init__(self, dado=0, proximo_nodo=None):
        self.dado = dado
        self.proximo = proximo_nodo

    def __repr__(self):
        return "%s -> %s" % (self.dado, self.proximo)


class Fila:
    def __init__(self):
        self.primeiro = None
        self.ultimo = None

    def __repr__(self):
        return "[" + str(self.primeiro) + "]"

    def is_empty(self):
        return self.primeiro is None

    def enqueue(self, dado):
        novo_nodo = Nodo(dado)
        if self.is_empty():
            self.primeiro = novo_nodo
            self.ultimo = novo_nodo
        else:
            self.ultimo.proximo = novo_nodo
            self.ultimo = novo_nodo

    def dequeue(self):
        if self.is_empty():
            return None
        dado = self.primeiro.dado
        self.primeiro = self.primeiro.proximo
        if self.primeiro is None:
            self.ultimo = None
        return dado

    def get_all_tasks(self):
        tasks = []
        current = self.primeiro
        while current:
            tasks.append(current.dado)
            current = current.proximo
        return tasks


app = Flask(__name__)
app.secret_key = "supersecretkey"  # flash do flask
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# BD para guardar tarefas pendentes e concluídas
class TarefasPendentes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    criadoEm = db.Column(db.DateTime, default=datetime.utcnow)


class TarefasConcluidas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    criadoEm = db.Column(db.DateTime)
    concluidoEm = db.Column(db.DateTime, default=datetime.utcnow)


# fila para as tarefas pendentes
fila_tarefas = Fila()


# Carrega as tarefas pendentes do banco de dados para a fila.
def carregar_tarefas_pendentes():
    fila_tarefas.primeiro = None  # Limpa a fila antes de recarregar
    tarefas_pendentes = TarefasPendentes.query.order_by(TarefasPendentes.criadoEm).all()
    for tarefa in tarefas_pendentes:
        fila_tarefas.enqueue(
            {"id": tarefa.id, "titulo": tarefa.titulo, "criadoEm": tarefa.criadoEm}
        )


    # mostra todas as tarefas pendentes na fila
@app.route("/")
def index():
    listaTarefas = fila_tarefas.get_all_tasks()
    return render_template("index.html", listaTarefas=listaTarefas)


@app.route("/adicionar", methods=["POST"])
def adicionar():
    nomeTarefa = request.form.get("nomeTarefa")
    criadoEm = datetime.utcnow()
    nova_tarefa = TarefasPendentes(titulo=nomeTarefa, criadoEm=criadoEm)
    db.session.add(nova_tarefa)
    db.session.commit()

    carregar_tarefas_pendentes()  # Atualiza a fila com as tarefas mais recentes
    return redirect(url_for("index"))


@app.route("/concluir/<int:task_index>")
def concluir(task_index):
    listaTarefas = fila_tarefas.get_all_tasks()
    # Verifica se a tarefa é a primeira da fila seguindo o conceito fifo
    if task_index == 0:
        tarefa = fila_tarefas.dequeue()  # primeira tarefa da fila
        if tarefa:
            tarefa_concluida = TarefasConcluidas(
                titulo=tarefa["titulo"], criadoEm=tarefa["criadoEm"]
            )
            db.session.add(tarefa_concluida)
            tarefa_pendente = TarefasPendentes.query.filter_by(id=tarefa["id"]).first()
            if tarefa_pendente:
                db.session.delete(tarefa_pendente)

            db.session.commit()

        return redirect(url_for("index"))
    else:
        # Se a tarefa não for a primeira, exibe um aviso
        flash(
            "Você deve seguir a ordem FIFO (Primeiro a Entrar, Primeiro a Sair) para concluir as tarefas."
        )
        return redirect(url_for("index"))


@app.route("/deletar_concluida/<int:id>")
def deletar_concluida(id):
    tarefa_concluida = TarefasConcluidas.query.get(id)
    if tarefa_concluida:
        db.session.delete(tarefa_concluida)
        db.session.commit()
    return redirect(url_for("tarefasConcluidas"))


@app.route("/tarefasConcluidas")
def tarefasConcluidas():
    tarefasConcluidas = TarefasConcluidas.query.order_by(
        TarefasConcluidas.concluidoEm
    ).all()
    return render_template("concluidas.html", tarefasConcluidas=tarefasConcluidas)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        carregar_tarefas_pendentes()  # Carrega as tarefas pendentes na fila ao iniciar o app
    app.run(debug=True)
