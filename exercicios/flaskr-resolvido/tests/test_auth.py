import pytest
from flask import g
from flask import session

from flaskr.db import get_db


# Testa o fluxo de registro de usuário.
# O Flaskr usa formulários HTML, então as requisições usam data=, não json=.
def test_register(client, app):
    # Arrange/Act: GET na página de registro.
    # Isso verifica se o template renderiza sem erro interno.
    # Se houvesse erro no Jinja2 ou na view, o Flask provavelmente retornaria 500.
    assert client.get("/auth/register").status_code == 200

    # Act: envia o formulário de registro com dados válidos.
    response = client.post("/auth/register", data={"username": "a", "password": "a"})

    # Assert: após registrar, o comportamento esperado é redirecionar para login.
    # response.headers["Location"] guarda o destino do redirect.
    assert response.headers["Location"] == "/auth/login"

    # Assert de integração com o banco: a resposta HTTP sozinha não prova que
    # o usuário foi realmente persistido.
    # app.app_context() é necessário porque get_db() depende do contexto do app.
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )


# Parametrize, visto na Aula 1, executa o mesmo teste para vários cenários.
# Isso evita escrever uma função separada para cada erro de validação.
# Cada tupla fornece username, password e a mensagem esperada.
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        # O usuário "test" já existe por causa do data.sql.
        ("test", "test", b"already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    # Act: envia dados inválidos para o registro.
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )

    # Assert: o Flaskr não retorna JSON aqui; ele re-renderiza HTML com erro.
    # Por isso a comparação é feita em response.data, que contém bytes.
    # Mensagens esperadas também são bytes: b"...".
    assert message in response.data


# Testa o fluxo de login.
def test_login(client, auth):
    # Arrange/Act: GET apenas verifica se a página renderiza sem erro.
    assert client.get("/auth/login").status_code == 200

    # Act: usa a fixture auth para logar com o usuário criado no data.sql.
    response = auth.login()

    # Assert: login bem-sucedido redireciona para a página inicial.
    assert response.headers["Location"] == "/"

    # with client mantém o contexto de request ativo após a resposta.
    # Isso é importante porque session e g normalmente só existem durante
    # uma requisição. Sem esse with, não poderíamos inspecioná-los aqui.
    with client:
        # Esta nova GET dispara os hooks de requisição do Flaskr.
        # Em particular, o Flaskr carrega g.user a partir de session["user_id"].
        client.get("/")

        # session guarda dados entre requisições, normalmente via cookie assinado.
        # Depois do login, esperamos que o id do usuário esteja na sessão.
        assert session["user_id"] == 1

        # g é um objeto de armazenamento válido apenas para a request atual.
        # Aqui verificamos que o usuário foi carregado corretamente para uso
        # durante a requisição.
        assert g.user["username"] == "test"


# Testa mensagens de erro do login usando parametrize.
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"Incorrect username."),
        ("test", "a", b"Incorrect password."),
    ),
)
def test_login_validate_input(auth, username, password, message):
    # Act: tenta logar com credenciais inválidas.
    response = auth.login(username, password)

    # Assert: a mensagem de erro aparece no HTML renderizado.
    assert message in response.data


# Testa logout.
def test_logout(client, auth):
    # Arrange: para testar logout, o usuário precisa estar logado antes.
    auth.login()

    # with client permite inspecionar a sessão depois da resposta de logout.
    with client:
        # Act: realiza logout.
        auth.logout()

        # Assert: logout correto não apenas redireciona; ele deve remover o
        # usuário da sessão.
        assert "user_id" not in session