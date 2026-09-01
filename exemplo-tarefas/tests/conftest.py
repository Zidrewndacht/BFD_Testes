import os
import tempfile
import threading
import socket
import pytest
from app import criar_app

from app import criar_app, get_conexao

@pytest.fixture
def app():
    # 1. Cria um arquivo temporário para o banco de dados
    db_fd, db_path = tempfile.mkstemp()
    
    # 2. Cria a aplicação apontando para o banco temporário
    app = criar_app({
        "TESTING": True,
        "DATABASE": db_path,
    })
    
    # 3. Insere dados iniciais específicos do teste
    with app.app_context():
        conexao = get_conexao()
        with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
            conexao.executescript(f.read().decode("utf8"))
        conexao.close()
    
    # 4. Entrega o app para o teste
    yield app
    
    # 5. Limpeza: fecha o arquivo e remove o banco temporário
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(autouse=True)
def limpar_banco(app_e2e):
    """
    ISOLAMENTO DE ESTADO (Regra de Ouro):
    Roda automaticamente antes de cada teste.
    Garante que o banco de dados comece 100% vazio para cada cenário,
    evitando que testes 'vazem' dados uns para os outros.
    """
    with app_e2e.app_context():
        from app import get_conexao
        conexao = get_conexao()
        conexao.execute("DELETE FROM tarefas")
        conexao.commit()
        conexao.close()
        
    yield
    # Poderíamos limpar após o teste também, mas limpar antes já garante 
    # que o próximo teste encontre um ambiente virgem.

@pytest.fixture
def client(app):
    return app.test_client()

# Fixtures para aula 3:
@pytest.fixture(scope="session")
def app_e2e():
    """Cria um banco temporário e a aplicação Flask para a sessão de testes E2E."""
    db_fd, db_path = tempfile.mkstemp()
    app = criar_app({
        "TESTING": True,
        "DATABASE": db_path,
    })
    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="session")
def servidor(app_e2e):
    """Sobe o servidor Flask em uma porta livre em uma thread separada."""
    s = socket.socket()
    s.bind(('', 0)) # Pega uma porta livre do sistema
    port = s.getsockname()[1]
    s.close()
    
    url = f"http://localhost:{port}"
    
    def run():
        # use_reloader=False é crucial para não duplicar a thread
        app_e2e.run(host="localhost", port=port, use_reloader=False, threaded=True)
        
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    yield url