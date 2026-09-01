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

@pytest.fixture
def client(app):
    return app.test_client()

# Fixtures para aula 3:

# FIXTURE: app_e2e
# Diferente da Aula 2, onde o escopo padrão (function) criava um app por teste,
# aqui usamos scope="session". O servidor Flask será criado apenas UMA VEZ
# para toda a suíte de testes E2E.
# Motivo: Iniciar o Flask e criar as tabelas a cada teste E2E seria muito lento.
# O isolamento de dados será garantido pela fixture 'limpar_banco' abaixo.
@pytest.fixture(scope="session")
def app_e2e():
    """Cria um banco temporário e a aplicação Flask para a sessão de testes E2E."""
    db_fd, db_path = tempfile.mkstemp()
    app = criar_app({
        "TESTING": True,
        "DATABASE": db_path,
    })
    
    yield app
    
    # Teardown da sessão: remove o banco temporário após todos os testes E2E terminarem.
    os.close(db_fd)
    os.unlink(db_path)


# FIXTURE: limpar_banco
# O decorator autouse=True faz com que esta fixture seja executada automaticamente
# ANTES de cada teste, mesmo que o teste não a declare nos parâmetros.
# Isso implementa o padrão "Database Cleaner": garantimos que cada teste E2E
# comece com o banco 100% vazio, evitando que dados de um teste vazem para o outro.
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
        # Trunca a tabela de tarefas. Não precisamos recriar o schema,
        # pois o app_e2e já foi inicializado no escopo da sessão.
        conexao.execute("DELETE FROM tarefas")
        conexao.commit()
        conexao.close()
        
    yield
    # O teardown após o yield está vazio. Limpar antes do teste é suficiente
    # para garantir que o próximo teste encontre um ambiente virgem.


# FIXTURE: servidor
# Sobe o Flask em uma thread secundária para que o pytest (na thread principal)
# possa continuar rodando e executar o Playwright em paralelo.
# Escopo "session" para não subir/derrubar o servidor a cada teste.
@pytest.fixture(scope="session")
def servidor(app_e2e):
    """Sobe o servidor Flask em uma porta livre em uma thread separada."""
    # Cria um socket temporário apenas para descobrir uma porta livre no sistema.
    # Isso evita o erro "Address already in use" se a porta 5000 estiver ocupada.
    s = socket.socket()
    s.bind(('', 0)) # Pega uma porta livre do sistema
    port = s.getsockname()[1]
    s.close()
    
    url = f"http://localhost:{port}"
    
    def run():
        # use_reloader=False é crucial. O reloader do Flask cria processos filhos
        # que quebrariam o controle da nossa thread de teste.
        # threaded=True permite que o Flask atenda múltiplas requisições do Playwright.
        app_e2e.run(host="localhost", port=port, use_reloader=False, threaded=True)
        
    # daemon=True garante que a thread do servidor seja encerrada abruptamente
    # quando o processo principal do pytest terminar, evitando travamentos no terminal.
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    # Entrega a URL base para os testes usarem no page.goto()
    yield url