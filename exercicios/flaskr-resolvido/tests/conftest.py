import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import get_db
from flaskr.db import init_db


# conftest.py é descoberto automaticamente pelo pytest quando os testes estão
# nesta mesma pasta. As fixtures definidas aqui ficam disponíveis para os
# arquivos test_*.py sem precisar importá-las manualmente.

# Lê os dados de teste uma única vez, na importação do módulo.
# Isso evita reler o arquivo a cada teste.
# __file__ representa o caminho deste conftest.py; dirname(__file__) retorna
# a pasta tests/, então o caminho do data.sql funciona independentemente do
# diretório a partir do qual o pytest foi executado.
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


# Fixture de aplicação, mesma ideia usada na Aula 2.
# Cada teste que declarar um parâmetro chamado "app" receberá uma aplicação
# nova, isolada das demais. O pytest resolve isso pelo nome do parâmetro.
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""

    # Cria um banco temporário por teste.
    # Isso garante isolamento: dados criados, alterados ou apagados por um
    # teste não afetam outro teste.
    # mkstemp() retorna um file descriptor e um caminho. O descriptor fica
    # aberto até o teardown para garantir que o arquivo seja liberado corretamente.
    db_fd, db_path = tempfile.mkstemp()

    # A application factory recebe configurações específicas de teste.
    # TESTING=True informa ao Flask que o app está em modo de teste.
    # DATABASE aponta para o arquivo temporário, evitando mexer no banco real.
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # Entramos em um application context porque init_db() e get_db() dependem
    # de mecanismos internos do Flask, como current_app e g.
    # Esse padrão também apareceu na Aula 2 ao inspecionar o banco diretamente.
    with app.app_context():
        # init_db() cria as tabelas a partir do schema do Flaskr.
        init_db()

        # executescript() executa múltiplos comandos SQL de uma vez.
        # Aqui populamos o banco com dados fixos usados pelos testes.
        get_db().executescript(_data_sql)

    # yield entrega o app para o teste.
    # Tudo depois do yield é o teardown: roda após o teste, mesmo se ele falhar.
    yield app

    # Encerra o file descriptor aberto pelo mkstemp() e remove o arquivo temporário.
    os.close(db_fd)
    os.unlink(db_path)


# Fixture de cliente HTTP, vista na Aula 2.
# Ela depende da fixture app: o pytest cria app primeiro e injeta o resultado aqui.
# test_client simula requisições HTTP sem subir servidor e sem abrir navegador.
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


# Fixture para testar comandos CLI.
# Este recurso não foi usado nas aulas anteriores, mas é necessário aqui porque
# o Flaskr possui um comando init-db registrado via Click.
# O runner executa o comando no mesmo processo e captura a saída.
@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


# Classe auxiliar de autenticação.
# Ela não é uma fixture por si só, mas encapsula ações repetidas de login/logout.
# O objetivo é evitar que vários testes repitam manualmente o mesmo POST de login.
class AuthActions:
    def __init__(self, client):
        self._client = client

    # Usa data= porque as rotas de autenticação do Flaskr lêem formulário HTML.
    # Se fossem APIs JSON, usaríamos json=, como na Aula 2.
    # Os valores padrão usam o usuário "test", criado em data.sql.
    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


# Fixture que entrega o objeto de autenticação pronto para uso.
# Testes podem apenas chamar auth.login() sem repetir a montagem da requisição.
@pytest.fixture
def auth(client):
    return AuthActions(client)