# Aula 2 — Testes de Integração: Flask + SQLite + Fixtures

**Pré-requisitos:** Aula 1 de testes (`pytest`, `assert`, AAA), Aula 2 de OOP (classes de domínio, repositórios, rotas Flask), SQLite básico.

**Objetivo da aula:** testar rotas Flask que acessam um banco SQLite sem precisar rodar o servidor manualmente, sem sujar o banco de desenvolvimento e sem depender de navegador, Postman ou Insomnia. Você vai usar o `test_client` do Flask e **fixtures** do `pytest`.

> **Definição rápida:** **Teste de integração** verifica se duas ou mais partes do sistema funcionam juntas. Nesta aula, vamos testar a integração entre **rota Flask + validação HTTP + Repositório OOP + SQLite**.

Esta aula segue o padrão geral de testes do tutorial oficial do Flask:
- [Testing Flask Applications](https://flask.palletsprojects.com/en/stable/testing/)
- [Test Coverage — Flask Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/tests/)

---

## 0. Introdução: por que automatizar testes do backend

### 0.1 O problema do teste manual

Até agora, para testar uma rota Flask, você provavelmente fazia algo assim:

1. Rodava o servidor (`flask run` ou `python app.py`);
2. Abria o navegador ou o DevTools;
3. Fazia uma requisição manualmente via `fetch` no console;
4. Conferia a resposta;
5. Conferia o banco no DB Browser.

Isso funciona para uma verificação pontual, mas não escala. Toda vez que você muda o código, precisa repetir vários cenários (criar tarefa válida, inválida, listar, apagar). Além disso, testar manualmente costuma mexer no seu banco de desenvolvimento, gerando dados sujos.

### 0.2 A solução: `test_client` + banco de testes

O Flask fornece um cliente de testes (`test_client`) que simula requisições à aplicação sem precisar subir um servidor real. Com isso, podemos escrever testes que:

1. Criam uma aplicação Flask configurada para testes;
2. Criam um banco SQLite temporário;
3. Enviam requisições simuladas;
4. Verificam status codes e respostas JSON;
5. Verificam efeitos no banco;
6. Descartam o banco temporário ao final.

---

## 1. O que muda em relação ao teste manual

| Situação | Teste manual | Teste automatizado |
|---|---|---|
| Subir servidor | Precisa rodar `flask run` | Não precisa |
| Enviar requisição | Navegador, console ou ferramenta manual | `client.get()`, `client.post()`, `client.delete()` |
| Verificar status code | Olhar DevTools | `assert resposta.status_code == 201` |
| Verificar JSON | Ler resposta manualmente | `assert resposta.json["descricao"] == "Estudar Flask"` |
| Banco de dados | Usa banco de desenvolvimento | Usa banco temporário |
| Repetição | Lenta e propensa a erro | Rápida e repetível |

---

## 2. Adaptando a aplicação OOP para testes (Application Factory)

Na Aula 2 de OOP, nosso `app` era global e o banco era fixo (`tarefas.db`). Para testar, precisamos criar múltiplas instâncias da aplicação, cada uma apontando para um banco diferente (o banco de testes). 

Para isso, transformamos nosso script em uma **Application Factory** (uma função `criar_app` que devolve o objeto Flask configurado). Isso mantém 100% da lógica OOP que já construímos, apenas a empacotando para permitir a injeção de configurações de teste.

### 2.1 O código da aplicação (`app.py`)

```python
import sqlite3
from flask import Flask, current_app, request

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
    app = Flask(__name__)
    
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

    return app

if __name__ == "__main__":
    app = criar_app()
    app.run(debug=True)
```

---

## 3. Estrutura do projeto e Instalação

Vamos usar a seguinte estrutura:

```text
projeto/
├── .venv/
├── app.py
├── requirements.txt
├── conftest.py
├── data.sql
└── test_tarefas.py
```

Com o ambiente virtual ativado:

```bash
pip install flask pytest
pip freeze > requirements.txt
```

---

## 4. Criando dados de teste

Para que os testes comecem com um estado conhecido, vamos criar um arquivo com dados iniciais.

Crie o arquivo `tests/data.sql`:

```sql
INSERT INTO tarefas (descricao, concluida)
VALUES
  ('Estudar Flask', 0);
```

Isso significa que todo teste começará com um banco contendo uma tarefa. Cada teste ainda será isolado, porque o banco será criado temporariamente para cada teste.

---

## 5. Criando `tests/conftest.py`

O arquivo `conftest.py` é especial para o pytest: ele é lido automaticamente e disponibiliza as fixtures para todos os testes no mesmo diretório.

```python
import os
import tempfile
import pytest

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
```

### Entendendo a fixture `app`
A fixture cria um arquivo vazio com `tempfile.mkstemp()`, passa esse caminho como `DATABASE` para o Flask, ativa `TESTING: True`, insere os dados do `data.sql` e, após o teste terminar (`yield`), remove o arquivo do sistema.

### Entendendo a fixture `client`
Apenas retorna o cliente de testes da aplicação (`app.test_client()`). Qualquer teste que receber `client` poderá fazer requisições simuladas.

---

## 6. Primeiro teste: listar tarefas

Crie o arquivo `tests/test_tarefas.py`. Como nosso banco já começa com uma tarefa, o primeiro teste verifica esse estado inicial.

```python
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
```

Quando a resposta da rota é JSON, podemos acessar diretamente `resposta.json`. Ele já contém os dados convertidos para dicionários e listas Python.

---

## 7. Testando criação de tarefa

Agora vamos testar o `POST /api/tarefas`. Como já existe uma tarefa no banco, a nova tarefa deve receber `id` 2.

```python
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
```

Observe o uso de `json={"descricao": "..."}`. O próprio cliente de testes cuida de converter o dicionário para JSON e definir o header `Content-Type: application/json`.

---

## 8. Testando validações

Agora vamos testar entradas inválidas.

### 8.1 Descrição vazia
```python
def test_post_descricao_vazia_retorna_400(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": ""},
    )

    assert resposta.status_code == 400
    assert "obrigatório" in resposta.json["erro"]
```

### 8.2 Descrição muito longa
```python
def test_post_descricao_muito_longa_retorna_400(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": "A" * 101},
    )

    assert resposta.status_code == 400
    assert "100 caracteres" in resposta.json["erro"]
```

---

## 9. Usando `pytest.mark.parametrize`

Podemos usar esse recurso para testar várias entradas inválidas com o mesmo código, evitando repetição.

```python
import pytest

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
```

Esse teste será executado quatro vezes, injetando cada valor da lista no parâmetro `descricao`.

---

## 10. Testando que uma requisição inválida não salva no banco

Um bom teste de integração não verifica apenas a resposta HTTP. Ele também pode verificar o efeito colateral (ou a falta dele).

```python
def test_post_invalido_nao_persiste(client):
    resposta = client.post(
        "/api/tarefas",
        json={"descricao": ""},
    )

    assert resposta.status_code == 400

    resposta_lista = client.get("/api/tarefas")

    assert resposta_lista.status_code == 200
    assert len(resposta_lista.json) == 1 # Continua tendo apenas a tarefa do data.sql
```

---

## 11. Verificando o banco diretamente

Também podemos acessar o banco diretamente dentro de um contexto de aplicação para fazer asserções sobre o SQLite.

```python
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
```

---

## 12. Testando remoção

Agora vamos testar o `DELETE`.

```python
def test_delete_remove_tarefa(client):
    resposta = client.delete("/api/tarefas/1")

    assert resposta.status_code == 204

    resposta_lista = client.get("/api/tarefas")
    assert resposta_lista.json == []

def test_delete_inexistente_retorna_404(client):
    resposta = client.delete("/api/tarefas/999")

    assert resposta.status_code == 404
    assert resposta.json["erro"] == "Tarefa não encontrada."
```

---

## 13. Arquivo completo de testes

O arquivo `tests/test_tarefas.py` consolidado fica assim:

```python
import pytest
from app import get_conexao

def test_lista_retorna_dados_iniciais(client):
    resposta = client.get("/api/tarefas")
    assert resposta.status_code == 200
    assert resposta.json == [{"id": 1, "descricao": "Estudar Flask", "concluida": False}]

def test_post_cria_tarefa(client):
    resposta = client.post("/api/tarefas", json={"descricao": "Estudar pytest"})
    assert resposta.status_code == 201
    assert resposta.json["id"] == 2
    assert len(client.get("/api/tarefas").json) == 2

@pytest.mark.parametrize("descricao", ["", "   ", None, 123])
def test_post_descricao_invalida_retorna_400(client, descricao):
    resposta = client.post("/api/tarefas", json={"descricao": descricao})
    assert resposta.status_code == 400

def test_post_descricao_muito_longa_retorna_400(client):
    resposta = client.post("/api/tarefas", json={"descricao": "A" * 101})
    assert resposta.status_code == 400

def test_post_invalido_nao_persiste(client):
    client.post("/api/tarefas", json={"descricao": ""})
    assert len(client.get("/api/tarefas").json) == 1

def test_post_persiste_no_banco(app, client):
    client.post("/api/tarefas", json={"descricao": "Nova tarefa"})
    with app.app_context():
        conexao = get_conexao()
        linha = conexao.execute("SELECT COUNT(*) AS total FROM tarefas").fetchone()
        conexao.close()
        assert linha["total"] == 2

def test_delete_remove_tarefa(client):
    assert client.delete("/api/tarefas/1").status_code == 204
    assert client.get("/api/tarefas").json == []

def test_delete_inexistente_retorna_404(client):
    resposta = client.delete("/api/tarefas/999")
    assert resposta.status_code == 404
```

---

## 14. Executando os testes

Na raiz do projeto, rode:

```bash
python -m pytest -v
```

Usamos `python -m pytest` para garantir que a raiz do projeto esteja no caminho de imports do Python, evitando o erro `ModuleNotFoundError: No module named 'app'`.

---

## 15. Dados de requisição: JSON e formulário

Nesta aula, testamos uma API JSON. Por isso usamos `json=`. Mas, se você estiver testando uma rota que recebe dados de formulário HTML (`request.form`), o envio deve ser feito com `data=`.

| Tipo de corpo da requisição | Como enviar no teste |
|---|---|
| JSON (`request.get_json()`) | `json={...}` |
| Formulário (`request.form`) | `data={...}` |
| Texto puro | `data="texto"` |

---

## 16. Respostas JSON e respostas HTML

Para respostas JSON, usamos `resposta.json`.

Para respostas HTML (como templates Jinja2), você pode verificar o conteúdo como texto:

```python
assert "Estudar Flask" in resposta.text
```

Também é possível verificar bytes diretamente em `resposta.data`. Mas, se fizer isso, lembre-se de comparar bytes com bytes:

```python
assert b"Estudar Flask" in resposta.data
```

---

## 17. Erros comuns

### Erro 1: usar o banco de desenvolvimento nos testes

**Errado:**
```python
app = criar_app()
client = app.test_client()
```
*O teste usará o banco padrão (`tarefas.db`) e pode apagar seus dados reais.*

**Certo:**
```python
db_fd, db_path = tempfile.mkstemp()
app = criar_app({"TESTING": True, "DATABASE": db_path})
```

### Erro 2: esquecer de inicializar o banco de testes

Se você não rodar o `inicializar()` do repositório (ou `init_db()`), as tabelas não existirão e o primeiro teste falhará com erro de SQL. Nossa `criar_app()` já cuida disso, mas é um ponto de atenção ao criar factories do zero.

### Erro 3: usar `json=` para testar formulário

**Errado:**
```python
client.post("/login", json={"username": "test"})
```

**Certo:**
```python
client.post("/login", data={"username": "test"})
```

### Erro 4: usar `data=` para testar JSON

**Errado:**
```python
client.post("/api/tarefas", data={"descricao": "Estudar"})
```
*O Flask não vai conseguir parsear isso como JSON no `request.get_json()`.*

**Certo:**
```python
client.post("/api/tarefas", json={"descricao": "Estudar"})
```

### Erro 5: achar que `test_client` executa JavaScript

O `test_client` não abre navegador real. Ele não executa JavaScript. Portanto, ele não é a ferramenta correta para testar cliques em botões, atualização de DOM ou chamadas `fetch` escritas no frontend. Isso será visto na Aula 3, com testes E2E usando Playwright.

---

## 18. Quando usar / Quando não usar

### Use testes de integração para verificar
- se uma rota responde com o status code correto;
- se uma rota retorna o JSON correto;
- se validações de entrada estão funcionando;
- se dados estão sendo gravados no SQLite;
- se operações de criação, leitura e remoção funcionam juntas.

### Não use testes de integração para tudo
- **Regras de negócio puras** (ex: cálculo de desconto, validação de string) devem ser testadas como **testes unitários** (Aula 1).
- **JavaScript de frontend** não deve ser testado com `test_client`.
- **Fluxos completos de usuário no navegador** devem ser testados com **E2E** (Aula 3).

---

## 19. Exercícios

### Exercício 1 — Popular o banco com duas tarefas
Altere `tests/data.sql` para inserir duas tarefas. Depois ajuste o teste `test_lista_retorna_dados_iniciais` para esperar duas tarefas.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```sql
-- tests/data.sql
INSERT INTO tarefas (descricao, concluida) VALUES ('Estudar Flask', 0), ('Estudar pytest', 0);
```

```python
# tests/test_tarefas.py
def test_lista_retorna_dados_iniciais(client):
    resposta = client.get("/api/tarefas")
    assert resposta.status_code == 200
    assert len(resposta.json) == 2
```
*Nota: Se você fizer essa alteração, testes que esperam `id == 2` para a primeira tarefa criada no teste precisarão ser ajustados para `id == 3`.*
</details>

### Exercício 2 — Parametrizar mais casos inválidos
Adicione novos casos ao teste parametrizado de descrição inválida: uma lista vazia `[]`, um dicionário vazio `{}` e um booleano `True`. Todos devem resultar em `400`.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
@pytest.mark.parametrize("descricao", ["", "   ", None, 123, [], {}, True])
def test_post_descricao_invalida_retorna_400(client, descricao):
    resposta = client.post("/api/tarefas", json={"descricao": descricao})
    assert resposta.status_code == 400
```
</details>

### Exercício 3 — Implementar `GET /api/tarefas/<id>`
Adicione em `app.py` uma rota `GET /api/tarefas/<int:tarefa_id>`. Ela deve retornar `200` com os dados da tarefa se ela existir, ou `404` se não existir. Escreva dois testes para ela.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
# Rota em app.py
@app.get("/api/tarefas/<int:id_tarefa>")
def api_buscar_tarefa(id_tarefa):
    conexao = get_conexao()
    repository = TarefaRepository(conexao)
    try:
        tarefa = repository.buscar_por_id(id_tarefa)
        if tarefa is None:
            return {"erro": "Tarefa não encontrada."}, 404
        return tarefa.to_dict()
    finally:
        conexao.close()
```

```python
# Testes
def test_get_por_id_retorna_tarefa_existente(client):
    resposta = client.get("/api/tarefas/1")
    assert resposta.status_code == 200
    assert resposta.json["descricao"] == "Estudar Flask"

def test_get_por_id_retorna_404_para_inexistente(client):
    resposta = client.get("/api/tarefas/999")
    assert resposta.status_code == 404
```
</details>

### Exercício 4 — Implementar conclusão de tarefa
Adicione em `app.py` uma rota `POST /api/tarefas/<int:tarefa_id>/concluir`. Ela deve marcar a tarefa como concluída (usando o método `tarefa.concluir()` e `repository.atualizar()`) e retornar `200`. Escreva testes para o sucesso, para o erro `404` e um teste que verifique diretamente no banco que `concluida` foi atualizada para `1`.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
# Rota em app.py (certifique-se de que o método atualizar existe no Repository)
@app.post("/api/tarefas/<int:id_tarefa>/concluir")
def api_concluir_tarefa(id_tarefa):
    conexao = get_conexao()
    repository = TarefaRepository(conexao)
    try:
        tarefa = repository.buscar_por_id(id_tarefa)
        if tarefa is None:
            return {"erro": "Tarefa não encontrada."}, 404
        tarefa.concluir()
        repository.atualizar(tarefa)
        return tarefa.to_dict()
    finally:
        conexao.close()
```

```python
# Testes
def test_concluir_tarefa_existente(client):
    resposta = client.post("/api/tarefas/1/concluir")
    assert resposta.status_code == 200
    assert resposta.json["concluida"] is True

def test_concluir_persiste_no_banco(app, client):
    client.post("/api/tarefas/1/concluir")
    with app.app_context():
        conexao = get_conexao()
        linha = conexao.execute("SELECT concluida FROM tarefas WHERE id = 1").fetchone()
        conexao.close()
        assert linha["concluida"] == 1
```
</details>

### Exercício 5 — Testes no Flaskr
Como exercício adicional, aplique os conceitos desta aula (fixtures, `test_client`, banco temporário com `tempfile.mkstemp()`) para testar as rotas de autenticação e posts do projeto **Flaskr** do tutorial oficial.
Guia de referência: [Test Coverage — Flask Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/tests/)

---

## 20. Checklist da aula

Ao final desta aula, você deve conseguir:
- explicar a diferença entre teste unitário e teste de integração;
- transformar um script Flask em uma Application Factory para permitir testes;
- usar o `test_client` do Flask para simular requisições HTTP;
- criar fixtures `app` e `client` com `pytest`;
- usar `tempfile.mkstemp()` para criar um banco SQLite temporário;
- testar rotas `GET`, `POST` e `DELETE`;
- verificar respostas JSON com `response.json`;
- entender quando usar `data=` e quando usar `json=`;
- saber que o `test_client` não executa JavaScript.

---

## 21. Recapitulação

| Conceito | Significado |
|---|---|
| Teste de integração | Testa partes do sistema funcionando juntas (Flask + SQLite). |
| Application Factory | Função que cria e configura o objeto Flask, essencial para isolar testes. |
| `test_client` | Cliente HTTP do Flask que simula requisições sem subir servidor. |
| Fixture | Função que prepara objetos para os testes (`@pytest.fixture`). |
| `tempfile.mkstemp()` | Cria um arquivo temporário seguro para o banco de testes. |
| `response.json` | Corpo JSON da resposta já convertido para Python. |
| `data=` | Usado para enviar dados de formulário. |
| `json=` | Usado para enviar dados JSON. |

---

## 22. O que não vimos no curso

| Tópico | Síntese |
|---|---|
| Cobertura de código (`coverage.py`) | Mede quais linhas foram executadas. Útil, mas o foco aqui é escrever testes úteis, não atingir 100%. |
| Mocks de serviços externos | Simular respostas de APIs externas (ex: ViaCEP) sem fazer requisição real. |
| Testes de templates HTML | Verificar detalhes de HTML renderizado por Jinja2 (usando `response.data`). |
| Testes com sessões e autenticação | Simular login, cookies e flash messages via `client.session_transaction()`. |
| CI/CD | Rodar testes automaticamente no GitHub Actions ou similar. |

---

## 23. Referências

- [Flask — Testing Flask Applications](https://flask.palletsprojects.com/en/stable/testing/)
- [Flask Tutorial — Test Coverage](https://flask.palletsprojects.com/en/stable/tutorial/tests/)
- [pytest — Fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Python — tempfile](https://docs.python.org/3/library/tempfile.html)
- [Python — sqlite3](https://docs.python.org/3/library/sqlite3.html)