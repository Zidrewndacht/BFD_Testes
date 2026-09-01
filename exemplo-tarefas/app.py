import sqlite3
from flask import Flask, current_app, request, render_template

# --- Classes da Aula 2 de OOP ---

class Tarefa:
    def __init__(self, descricao, id=None, concluida=False):
        self.id = id
        self.descricao = descricao
        self.concluida = concluida

    def validar(self):
        if not isinstance(self.descricao, str):
            return False
        if not self.descricao.strip():
            return False
        if len(self.descricao) > 100:
            return False
        return True

    def concluir(self):
        self.concluida = True

    def to_dict(self):
        return {
            "id": self.id,
            "descricao": self.descricao,
            "concluida": self.concluida,
        }

def tarefa_from_row(row):
    return Tarefa(
        id=row["id"],
        descricao=row["descricao"],
        concluida=bool(row["concluida"])
    )

class TarefaRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    def inicializar(self):
        with self.conexao:
            self.conexao.execute("""
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    concluida INTEGER DEFAULT 0
                )
            """)

    def inserir(self, tarefa):
        sql = "INSERT INTO tarefas (descricao, concluida) VALUES (?, ?)"
        with self.conexao:
            cursor = self.conexao.execute(sql, (tarefa.descricao, int(tarefa.concluida)))
        tarefa.id = cursor.lastrowid
        return tarefa

    def listar(self):
        rows = self.conexao.execute("SELECT * FROM tarefas ORDER BY id").fetchall()
        return [tarefa_from_row(row) for row in rows]

    def buscar_por_id(self, id_tarefa):
        row = self.conexao.execute("SELECT * FROM tarefas WHERE id = ?", (id_tarefa,)).fetchone()
        return tarefa_from_row(row) if row else None

    def deletar(self, id_tarefa):
        with self.conexao:
            self.conexao.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))

# --- Conexão com o BD (Adaptada para Testes) ---

def get_conexao():
    # Pega o caminho do banco da configuração do Flask
    db_path = current_app.config["DATABASE"]
    conexao = sqlite3.connect(db_path)
    conexao.row_factory = sqlite3.Row
    return conexao

# --- Application Factory ---

def criar_app(config_extra=None):
    app = Flask(__name__, template_folder="templates") #atualizado para aula3
    
    # Configuração padrão para desenvolvimento
    app.config["DATABASE"] = "tarefas.db"
    app.config["TESTING"] = False
    
    if config_extra:
        app.config.update(config_extra)

    # Inicializa o schema do banco na criação da app
    # Precisamos do app_context() para que current_app.config funcione aqui
    with app.app_context():
        conexao_init = get_conexao()
        TarefaRepository(conexao_init).inicializar()
        conexao_init.close()

    @app.get("/api/tarefas")
    def api_listar_tarefas():
        conexao = get_conexao()
        repository = TarefaRepository(conexao)
        try:
            tarefas = repository.listar()
            return [t.to_dict() for t in tarefas]
        finally:
            conexao.close()

    @app.post("/api/tarefas")
    def api_criar_tarefa():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return {"erro": "Envie um corpo JSON válido."}, 400

        tarefa = Tarefa(descricao=dados.get("descricao", ""))
        if not tarefa.validar():
            return {"erro": "O campo 'descricao' é obrigatório e deve ter no máximo 100 caracteres."}, 400

        conexao = get_conexao()
        repository = TarefaRepository(conexao)
        try:
            repository.inserir(tarefa)
            return tarefa.to_dict(), 201
        finally:
            conexao.close()

    @app.delete("/api/tarefas/<int:id_tarefa>")
    def api_deletar_tarefa(id_tarefa):
        conexao = get_conexao()
        repository = TarefaRepository(conexao)
        try:
            tarefa = repository.buscar_por_id(id_tarefa)
            if tarefa is None:
                return {"erro": "Tarefa não encontrada."}, 404
            repository.deletar(id_tarefa)
            return "", 204
        finally:
            conexao.close()

    # Rota raiz que serve a interface web.
    # O Playwright acessará esta URL para iniciar os testes E2E.
    @app.get("/")
    def index():
        return render_template("index.html")


    return app

if __name__ == "__main__":
    app = criar_app()
    app.run(debug=True)
