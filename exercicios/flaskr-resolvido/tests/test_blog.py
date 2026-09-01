import pytest

from flaskr.db import get_db


# Testa a página inicial do blog em dois estados:
# 1. usuário anônimo;
# 2. usuário autenticado.
def test_index(client, auth):
    # Arrange/Act: request sem login.
    response = client.get("/")

    # Assert: como a resposta é HTML, response.data retorna bytes.
    # Nas aulas anteriores trabalhamos principalmente com response.json,
    # mas aqui precisamos verificar conteúdo HTML.
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Arrange: autentica o usuário "test", criado em data.sql.
    auth.login()

    # Act: acessa a mesma página agora autenticado.
    response = client.get("/")

    # Assert: o post criado em data.sql deve aparecer na página.
    assert b"test title" in response.data

    # Verifica a renderização dos metadados do post.
    assert b"by test on 2018-01-01" in response.data

    # O data.sql usa x'0a' para inserir quebra de linha no body.
    # Aqui verificamos se essa quebra de linha aparece corretamente no HTML.
    assert b"test\nbody" in response.data

    # Como o usuário logado é o autor do post, a interface deve mostrar o link
    # para edição do post 1.
    assert b'href="/1/update"' in response.data


# Testa rotas protegidas: sem login, todas devem redirecionar para /auth/login.
# parametrize evita repetir o mesmo teste para cada rota.
@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    # Act: tenta executar a ação sem estar logado.
    # O Flaskr usa POST para essas ações porque elas vêm de formulários HTML,
    # não porque segue uma API REST JSON.
    response = client.post(path)

    # Assert: a aplicação não deve executar a ação.
    # Ela deve redirecionar o usuário para a página de login.
    # Checar o header Location valida o destino do redirect, não apenas o status.
    assert response.headers["Location"] == "/auth/login"


# Testa autorização: não basta estar logado; é preciso ser dono do post.
def test_author_required(app, client, auth):
    # Arrange: altera o dono do post 1 diretamente no banco.
    # Isso cria um cenário específico que seria difícil de produzir apenas
    # usando as rotas normais da aplicação.
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    # Arrange: loga com o usuário "test", que possui id 1.
    # Após o UPDATE acima, ele não é mais o autor do post 1.
    auth.login()

    # Assert: tentar modificar post de outro usuário deve retornar 403 Forbidden.
    # 403 é diferente de 404: o recurso existe, mas o usuário não tem permissão.
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403

    # A interface também não deve oferecer uma ação que o usuário não pode executar.
    assert b'href="/1/update"' not in client.get("/").data


# Testa acesso a recursos inexistentes.
# Mesmo autenticado, operar sobre post inexistente deve retornar 404.
@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    # Arrange: autenticação é necessária para chegar até a verificação de
    # existência do post. Sem login, o teste verificaria outro comportamento.
    auth.login()

    # Act/Assert: o post 2 não existe no data.sql.
    assert client.post(path).status_code == 404


# Testa criação de post.
def test_create(client, auth, app):
    # Arrange: criar post exige usuário logado.
    auth.login()

    # Assert inicial: GET apenas verifica se o formulário de criação renderiza.
    assert client.get("/create").status_code == 200

    # Act: cria o post enviando dados de formulário.
    client.post("/create", data={"title": "created", "body": ""})

    # Assert de efeito colateral no banco.
    # A resposta HTTP sozinha não prova que o post foi gravado.
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]

        # O data.sql começa com 1 post.
        # Depois da criação, o total deve ser 2.
        assert count == 2


# Testa atualização de post existente.
def test_update(client, auth, app):
    # Arrange: o usuário precisa estar logado e ser dono do post.
    auth.login()

    # Assert inicial: GET verifica se o formulário de edição renderiza.
    assert client.get("/1/update").status_code == 200

    # Act: envia o formulário de atualização.
    client.post("/1/update", data={"title": "updated", "body": ""})

    # Assert: consulta o banco diretamente para garantir que o UPDATE persistiu.
    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()

        # A coluna title deve ter sido atualizada no banco.
        assert post["title"] == "updated"


# Testa a mesma regra de validação em duas rotas diferentes: create e update.
# parametrize permite reaproveitar o teste para os dois caminhos.
@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    # Arrange: ambas as rotas exigem autenticação.
    auth.login()

    # Act: envia título vazio, o que deve ser rejeitado.
    response = client.post(path, data={"title": "", "body": ""})

    # Assert: como a resposta é HTML, a mensagem de erro é verificada em bytes.
    assert b"Title is required." in response.data


# Testa remoção de post.
def test_delete(client, auth, app):
    # Arrange: somente usuário autenticado e autor pode deletar.
    auth.login()

    # Act: deleta o post 1.
    # O Flaskr usa POST para ações de formulário HTML, incluindo delete.
    response = client.post("/1/delete")

    # Assert: após deletar, o usuário deve voltar para a página inicial.
    assert response.headers["Location"] == "/"

    # Assert de integração com o banco: a resposta redirect não prova remoção.
    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()

        # fetchone() retorna None quando não há linha correspondente.
        # Portanto, isso confirma que o post foi apagado do banco.
        assert post is None