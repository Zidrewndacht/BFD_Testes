import pytest
from app import get_conexao


def test_lista_retorna_dados_iniciais(client):
    resposta = client.get("/api/tarefas")

    assert resposta.status_code == 200

    assert resposta.json == [
        {
            "id": 1,
            "descricao": "Estudar Flask",
            "concluida": False,
        }
    ]

def test_post_cria_tarefa(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": "Estudar pytest"},
    )

    assert resposta.status_code == 201

    dados = resposta.json

    assert dados["id"] == 2
    assert dados["descricao"] == "Estudar pytest"
    assert dados["concluida"] is False

    resposta_lista = client.get("/api/tarefas")
    assert len(resposta_lista.json) == 2

def test_post_descricao_vazia_retorna_400(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": ""},
    )

    assert resposta.status_code == 400
    assert "obrigatório" in resposta.json["erro"]

def test_post_descricao_muito_longa_retorna_400(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": "A" * 101},
    )

    assert resposta.status_code == 400
    assert "100 caracteres" in resposta.json["erro"]

@pytest.mark.parametrize(
    "descricao",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_post_descricao_invalida_retorna_400(client, descricao):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": descricao},
    )

    assert resposta.status_code == 400
    assert "obrigatório" in resposta.json["erro"]

def test_post_invalido_nao_persiste(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": ""},
    )

    assert resposta.status_code == 400

    resposta_lista = client.get("/api/tarefas")

    assert resposta_lista.status_code == 200
    assert len(resposta_lista.json) == 1 # Continua tendo apenas a tarefa do data.sql

def test_post_persiste_no_banco(app, client):
    client.post(
        "/api/tarefas",
        json={"descricao": "Nova tarefa"},
    )

    
    with app.app_context():
        conexao = get_conexao()
        linha = conexao.execute(
            "SELECT COUNT(*) AS total FROM tarefas"
        ).fetchone()
        conexao.close()
        
        assert linha["total"] == 2 # 1 do data.sql + 1 criada no teste

def test_delete_remove_tarefa(client):
    resposta = client.delete("/api/tarefas/1")

    assert resposta.status_code == 204

    resposta_lista = client.get("/api/tarefas")
    assert resposta_lista.json == []

def test_delete_inexistente_retorna_404(client):
    resposta = client.delete("/api/tarefas/999")

    assert resposta.status_code == 404
    assert resposta.json["erro"] == "Tarefa não encontrada."
