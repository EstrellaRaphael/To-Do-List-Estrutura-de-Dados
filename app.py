from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Estrutura de Nodo para a Fila
class Nodo:
    def __init__(self, dado=0, proximo_nodo=None):
        self.dado = dado
        self.proximo = proximo_nodo

    def __repr__(self):
        return f"{self.dado} -> {self.proximo}"


# Estrutura de Fila com comportamento FIFO
class Fila:
    def __init__(self):
        self.primeiro = None
        self.ultimo = None

    def __repr__(self):
        return f"[{self.primeiro}]"

    # Verifica se a fila está vazia
    def is_empty(self):
        return self.primeiro is None

    # Adiciona um novo elemento ao final da fila
    def enqueue(self, dado):
        novo_nodo = Nodo(dado)
        if self.is_empty():
            self.primeiro = novo_nodo
            self.ultimo = novo_nodo
        else:
            self.ultimo.proximo = novo_nodo
            self.ultimo = novo_nodo

    # Remove o primeiro elemento da fila
    def dequeue(self):
        if self.is_empty():
            return None
        dado = self.primeiro.dado
        self.primeiro = self.primeiro.proximo
        if self.primeiro is None:
            self.ultimo = None
        return dado

    #    # Retorna todas as tarefas na fila como uma lista
    def get_all_tasks(self):
        tasks = []
        current = self.primeiro
        while current:
            tasks.append(current.dado)
            current = current.proximo
        return tasks


# Configuração inicial da aplicação Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Chave secreta para mensagens de flash
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"  # Banco de dados SQLite
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Desativa avisos de modificação
db = SQLAlchemy(app)


# Modelos do banco de dados
# Tarefas Pendentes: Tabela que armazena as tarefas que ainda não foram concluídas
class TarefasPendentes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))  # Título da tarefa
    criadoEm = db.Column(db.DateTime, default=datetime.utcnow)  # Data de criação
    categoria = db.Column(db.String(50))  # Categoria da tarefa


# Tarefas Concluídas: Tabela que armazena as tarefas já concluídas
class TarefasConcluidas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))  # Título da tarefa
    criadoEm = db.Column(db.DateTime)  # Data de criação
    concluidoEm = db.Column(db.DateTime, default=datetime.utcnow)  # Data de conclusão
    categoria = db.Column(db.String(50))  # Categoria da tarefa



# Instância da fila para armazenar as tarefas pendentes
fila_tarefas = Fila()


# Função para carregar as tarefas pendentes do banco de dados para a fila
def carregar_tarefas_pendentes():
    fila_tarefas.primeiro = None  # Limpa a fila antes de recarregar
    tarefas_pendentes = TarefasPendentes.query.order_by(TarefasPendentes.criadoEm).all()
    for tarefa in tarefas_pendentes:
        fila_tarefas.enqueue(
            {"id": tarefa.id, "titulo": tarefa.titulo, "criadoEm": tarefa.criadoEm, "categoria": tarefa.categoria}
        )


# Rota principal - Exibe as tarefas pendentes
@app.route("/")
def index():
    lista_tarefas = fila_tarefas.get_all_tasks()
    return render_template("index.html", listaTarefas=lista_tarefas)


# Rota para adicionar uma nova tarefa
@app.route("/adicionar", methods=["POST"])
def adicionar():
    nome_tarefa = request.form.get("nomeTarefa")
    categoria = request.form.get("categoria")
    nova_tarefa = TarefasPendentes(
        titulo=nome_tarefa, criadoEm=datetime.utcnow(), categoria=categoria
    )
    db.session.add(nova_tarefa)
    db.session.commit()
    carregar_tarefas_pendentes()  # Atualiza a fila
    return redirect(url_for("index"))


# Rota de filtro para tarefas pendentes
@app.route("/filtro/<categoria>", methods=["GET"])
def filtro(categoria):
    if categoria == "Todas":
        listaTarefas = TarefasPendentes.query.all()  # Mostrar todas as tarefas
    else:
        listaTarefas = TarefasPendentes.query.filter_by(
            categoria=categoria
        ).all()  # Filtra pela categoria específica

    return render_template("index.html", listaTarefas=listaTarefas)


# Rota para concluir uma tarefa seguindo o conceito FIFO
@app.route("/concluir/<int:task_index>")
def concluir(task_index):
    lista_tarefas = fila_tarefas.get_all_tasks()
    if task_index == 0:  # Apenas permite concluir a primeira tarefa
        tarefa = fila_tarefas.dequeue()
        if tarefa:
            tarefa_concluida = TarefasConcluidas(
                titulo=tarefa["titulo"], criadoEm=tarefa["criadoEm"], categoria=tarefa["categoria"]
            )
            db.session.add(tarefa_concluida)
            tarefa_pendente = TarefasPendentes.query.filter_by(id=tarefa["id"]).first()
            if tarefa_pendente:
                db.session.delete(tarefa_pendente)
            db.session.commit()
        return redirect(url_for("index"))
    else:
        flash("Você deve seguir a ordem FIFO para concluir as tarefas.")
        return redirect(url_for("index"))


# Rota para deletar uma tarefa pendente
@app.route("/deletar_pendente/<int:id>")
def deletar_pendente(id):
    tarefa_pendente = TarefasPendentes.query.get(id)
    if tarefa_pendente:
        db.session.delete(tarefa_pendente)
        db.session.commit()
    carregar_tarefas_pendentes()
    return redirect(url_for("index"))


# Rota para deletar uma tarefa concluída
@app.route("/deletar_concluida/<int:id>")
def deletar_concluida(id):
    tarefa_concluida = TarefasConcluidas.query.get(id)
    if tarefa_concluida:
        db.session.delete(tarefa_concluida)
        db.session.commit()
    return redirect(url_for("tarefasConcluidas"))


# Rota para exibir as tarefas concluídas
@app.route("/tarefasConcluidas")
def tarefasConcluidas():
    tarefas_concluidas = TarefasConcluidas.query.order_by(
        TarefasConcluidas.concluidoEm
    ).all()
    return render_template("concluidas.html", tarefasConcluidas=tarefas_concluidas)


# Inicialização da aplicação
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados, caso não existam
        carregar_tarefas_pendentes()  # Carrega as tarefas na inicialização
    app.run(debug=True)
