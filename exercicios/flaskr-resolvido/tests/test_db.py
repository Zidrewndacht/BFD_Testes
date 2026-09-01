import sqlite3

import pytest

from flaskr.db import get_db


# Este teste verifica o ciclo de vida da conexão com o banco no Flaskr.
# O objetivo não é testar SQL em si, mas garantir que get_db() se comporta
# corretamente dentro e fora do application context.
def test_get_close_db(app):
    # Arrange/Act: entra em um application context porque get_db() depende
    # do contexto atual da aplicação.
    with app.app_context():
        db = get_db()

        # Dentro do mesmo contexto, get_db() deve reaproveitar a mesma conexão.
        # O operador "is" verifica identidade: não é apenas uma conexão igual,
        # é exatamente o mesmo objeto em memória.
        # Isso evita abrir conexões desnecessárias durante a mesma requisição.
        assert db is get_db()

    # Ao sair do with, o contexto termina.
    # O Flaskr usa esse momento para fechar a conexão associada ao contexto.

    # Assert: tentar usar a conexão depois do contexto deve falhar.
    # pytest.raises, visto na Aula 1, captura a exceção esperada.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    # A mensagem exata pode variar conforme o SQLite, então verificamos apenas
    # o trecho relevante que indica que a conexão está fechada.
    assert "closed" in str(e.value)


# Este teste verifica o comando CLI init-db.
# Esse tipo de teste não foi usado nas aulas anteriores, pois o curso focou
# em rotas HTTP e não em comandos de terminal registrados no Flask.
def test_init_db_command(runner, monkeypatch):
    # Arrange: init_db() não retorna um valor fácil de asserting.
    # Por isso criamos um objeto simples cujo único papel é registrar se a
    # função foi chamada.
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    # monkeypatch não foi visto no curso.
    # Ele substitui temporariamente um atributo/função durante o teste.
    # Aqui, flaskr.db.init_db é trocado por fake_init_db apenas neste teste.
    # O pytest desfaz a substituição automaticamente depois.
    # Isso permite testar o comando CLI sem executar novamente a inicialização
    # real do banco.
    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)

    # Act: runner.invoke executa o comando Click dentro do próprio processo.
    # Não é um subprocess nem depende de chamar "flask init-db" no terminal.
    # args=["init-db"] representa o comando que está sendo invocado.
    result = runner.invoke(args=["init-db"])

    # Assert: o comando deve produzir feedback textual para o usuário.
    assert "Initialized" in result.output

    # Assert: o comando deve realmente chamar a função de inicialização do banco.
    # Como init_db foi substituída por fake_init_db, Recorder.called prova a chamada.
    assert Recorder.called