# Aula 3 — Testes End-to-End (E2E) e o Fluxo Full-Stack com Playwright

**Pré-requisitos:** Aulas de testes unitários e de integração, Flask, HTML/CSS e JavaScript Client-Side (fetch e manipulação do DOM).

**Objetivo da aula:** testar a aplicação completa do ponto de vista do usuário real. Você vai aprender a automatizar um navegador para abrir sua página, preencher formulários, clicar em botões e verificar se o JavaScript (e o backend Flask) responderam corretamente, sem precisar fazer isso manualmente.

> **Definição rápida:** **Teste unitário** é um pedaço de código cujo único propósito é executar outro pedaço do seu código e verificar se ele, sozinho, se comporta como o esperado.

> **Definição rápida:** **Teste de integração** verifica se duas ou mais partes do sistema funcionam juntas. Nesta aula, vamos testar a integração entre **rota Flask + validação HTTP + Repositório OOP + SQLite**.

> **Definição rápida:** **Teste End-to-End (E2E)** é um teste que simula um usuário real interagindo com a aplicação completa através de um navegador automatizado, validando a integração entre o frontend (HTML/JS) e o backend.

---

## 0. A Pirâmide de Testes e o problema do teste manual

Até agora, construímos uma base sólida de testes:
1. **Testes Unitários (Aula 1):** Rápidos e baratos. Testam a lógica pura (ex: a classe `Tarefa` valida corretamente o tamanho da string?).
2. **Testes de Integração (Aula 2):** Intermediários. Testam a "casca" da aplicação (ex: a rota `POST /api/tarefas` salva no SQLite e retorna `201 Created`?).

Mas o que acontece quando o usuário abre a página no navegador, digita "Estudar Playwright", clica em "Adicionar" e... nada acontece?

O backend pode estar perfeito (a API funciona no Postman ou no `test_client`), mas o **JavaScript** que faz o `fetch` e atualiza o DOM pode estar com um bug, ou o CSS pode estar escondendo o botão. Testar esse fluxo manualmente toda vez que você altera uma linha de CSS ou JS é exaustivo e propenso a esquecimentos.

Para resolver isso, usamos a ponta da **Pirâmide de Testes**: os testes E2E. Eles são mais lentos e "caros" de rodar (pois abrem um navegador real), mas são essenciais para garantir que os fluxos críticos do usuário (como criar uma tarefa) nunca quebrem.

---

## 1. O que é o Playwright (e por que ele substituiu o Selenium)

Historicamente, a ferramenta padrão para automatizar navegadores era o **Selenium**. No entanto, o Selenium é notório por ser lento e gerar testes "flaky" (intermitentes), que falham aleatoriamente porque o teste tenta clicar em um botão antes de o JavaScript terminar de renderizá-lo na tela.

O **Playwright**, criado pela Microsoft, é o padrão moderno da indústria. 

| Característica | Selenium (O jeito antigo) | Playwright (O jeito moderno) |
|---|---|---|
| **Velocidade** | Lento, comunicação via HTTP legada. | Extremamente rápido, comunicação via WebSocket nativo. |
| **Espera (Waits)** | Exige `time.sleep()` ou `WebDriverWait` manual e verboso. | **Auto-wait:** espera automaticamente o elemento ficar visível e interativo antes de agir. |
| **Configuração** | Exige baixar drivers de navegadores manualmente. | Um comando (`playwright install`) baixa e gerencia tudo. |
| **Múltiplos Navegadores** | Foco em Chrome/Gecko. | Suporte nativo e idêntico para Chromium (Chrome/Edge), Firefox e WebKit (Safari). |

Nesta aula, usaremos o **Playwright integrado ao pytest**, através do plugin oficial `pytest-playwright`.

---

## 2. Preparando o ambiente

No seu ambiente virtual, instale o plugin do Playwright para o pytest:

```bash
pip install pytest-playwright
```

Em seguida, você precisa baixar os binários dos navegadores que o Playwright usará para rodar os testes. Execute no terminal:

```bash
playwright install
```

*Nota: Isso baixará versões otimizadas do Chromium, Firefox e WebKit. É um download de algumas centenas de megabytes feito apenas uma vez.*

---

## 3. A aplicação Full-Stack de teste

Para testar de ponta a ponta, precisamos de uma interface. Vamos criar um arquivo HTML simples que consome nossa API Flask.

### 3.1 O Frontend (`templates/index.html`)

Crie a pasta `templates/` na raiz do projeto e adicione o arquivo `index.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Minhas Tarefas</title>
</head>
<body>
    <h1>Minhas Tarefas</h1>
    
    <form id="form-tarefa">
        <input type="text" id="descricao" placeholder="Descrição da tarefa" required>
        <button type="submit">Adicionar</button>
    </form>

    <ul id="lista-tarefas"></ul>

    <script>
        const form = document.getElementById('form-tarefa');
        const lista = document.getElementById('lista-tarefas');
        const inputDescricao = document.getElementById('descricao');

        async function carregarTarefas() {
            const resposta = await fetch('/api/tarefas');
            const tarefas = await resposta.json();
            lista.innerHTML = '';
            tarefas.forEach(tarefa => {
                const li = document.createElement('li');
                li.textContent = tarefa.descricao;
                lista.appendChild(li);
            });
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const descricao = inputDescricao.value;
            
            const resposta = await fetch('/api/tarefas', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({descricao: descricao})
            });
            
            if (resposta.ok) {
                inputDescricao.value = ''; // Limpa o input
                carregarTarefas();         // Atualiza a lista
            }
        });

        carregarTarefas();
    </script>
</body>
</html>
```

### 3.2 Ajustando o Backend (`app.py`)

No seu `app.py` (da Aula 2), garanta que o Flask sabe onde estão os templates e adicione a rota raiz:

```python
# app.py
from flask import Flask, render_template, request
# ... (resto das importações e classes da Aula 2) ...

def criar_app(config_extra=None):
    # Adicione template_folder="templates"
    app = Flask(__name__, template_folder="templates")
    
    # ... (configurações de BD e inicialização) ...

    @app.get("/")
    def index():
        return render_template("index.html")

    # ... (rotas /api/tarefas que já existiam) ...

    return app
```

#### 3.3 O servidor de testes (`tests/conftest.py`) e o Princípio do Isolamento

O Playwright precisa de um servidor web rodando para acessar a página. Vamos criar uma fixture que sobe o Flask em uma *thread* secundária automaticamente.

Nota: Um teste nunca pode depender da ordem em que é executado, nem do estado deixado por um teste anterior. Se o Teste A cria uma tarefa, o Teste B não pode começar a rodar vendo essa tarefa na tela. Para garantir performance (não reiniciar o servidor Flask do zero a cada teste), vamos manter o servidor no ar, mas **limpar o banco de dados antes de cada teste individual** através de uma fixture com `autouse=True`:

```python
import os
import tempfile
import threading
import socket
import pytest
from app import criar_app

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

@pytest.fixture(scope="session")
def servidor(app_e2e):
    """Sobe o servidor Flask em uma porta livre em uma thread separada."""
    s = socket.socket()
    s.bind(('', 0)) # Pega uma porta livre do sistema
    port = s.getsockname()[1]
    s.close()
    
    url = f"http://localhost:{port}"
    
    def run():
        # use_reloader=False é crucial para não duplicar a thread do Flask
        app_e2e.run(host="localhost", port=port, use_reloader=False, threaded=True)
        
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    yield url
```

**O que mudou?**
Adicionamos a fixture `limpar_banco` com o decorador `autouse=True`. Isso instrui o `pytest` a executar essa função **antes e depois de cada teste E2E**, mesmo que o teste não a declare explicitamente em seus parâmetros. É o padrão *Database Cleaner* utilizado em frameworks profissionais de mercado.


## 4. O primeiro teste E2E

Crie o arquivo `tests/test_e2e_tarefas.py`. O plugin `pytest-playwright` injeta automaticamente uma fixture chamada `page` em qualquer teste que a solicite. Essa `page` representa a aba do navegador.

```python
from playwright.sync_api import expect

def test_adicionar_tarefa_fluxo_completo(page, servidor):
    # 1. Navega até a URL do nosso servidor Flask
    page.goto(servidor)

    # 2. Localiza o input pelo placeholder e preenche
    page.get_by_placeholder("Descrição da tarefa").fill("Estudar Playwright")

    # 3. Localiza o botão pelo seu texto (role) e clica
    page.get_by_role("button", name="Adicionar").click()

    # 4. Verifica se a tarefa apareceu na lista
    # O Playwright espera automaticamente o JS processar o fetch e atualizar o DOM!
    expect(page.get_by_text("Estudar Playwright")).to_be_visible()
```

Rode o teste:

```bash
pytest tests/test_e2e_tarefas.py
```

Saída esperada:

```text
collected 1 item

tests/test_e2e_tarefas.py .                                                [100%]

============================== 1 passed in 2.34s ===============================
```

🎯 **Impacto visual:** Por padrão, o Playwright roda em modo **headless** (sem abrir a janela do navegador, para ser rápido). Mas ele executou todo o fluxo real: abriu o Chromium, digitou, clicou, esperou o `fetch` bater no Flask, o Flask salvar no SQLite e o JS desenhar o `<li>` na tela.

---

## 5. Localizadores (Locators): Como o Playwright "enxerga" a página

No Selenium antigo, você usava seletores CSS complexos e frágeis (ex: `page.querySelector('#container > div.btn-primary')`). Se o designer mudasse a classe CSS, o teste quebrava.

O Playwright prioriza **Localizadores baseados na experiência do usuário e acessibilidade**. Os métodos `get_by_*` são os mais recomendados:

| Método | O que busca | Exemplo |
|---|---|---|
| `get_by_role()` | Elementos pelo papel semântico (ARIA) e nome acessível. | `page.get_by_role("button", name="Salvar")` |
| `get_by_text()` | Elementos que contêm um texto específico. | `page.get_by_text("Bem-vindo")` |
| `get_by_placeholder()` | Inputs pelo texto do placeholder. | `page.get_by_placeholder("Digite seu e-mail")` |
| `get_by_label()` | Inputs associados a uma `<label>`. | `page.get_by_label("Senha")` |
| `locator()` | Seletor CSS ou XPath (use apenas como último recurso). | `page.locator(".classe-especifica")` |

> **Dica de ouro:** `get_by_role` é o mais resiliente. Um botão `<button>Adicionar</button>` sempre será encontrado por `get_by_role("button", name="Adicionar")`, não importa se você mudar a cor, a classe CSS ou o ID dele no futuro.

---

## 6. Asserções e a Mágica do "Auto-wait"

A maior dor de cabeça em testes de frontend é o **assincronismo**. O clique no botão dispara um `fetch`, que leva alguns milissegundos para voltar do servidor e atualizar o DOM.

Se você usasse um `assert "Estudar Playwright" in page.content()` logo após o clique, o teste falharia, pois o Python executaria a verificação antes do JavaScript terminar de renderizar o `<li>`.

O Playwright resolve isso com a função `expect`:

```python
from playwright.sync_api import expect

# O expect POLL (verifica repetidamente) a página por até 5 segundos
# até que a condição seja verdadeira.
expect(page.get_by_text("Estudar Playwright")).to_be_visible()
```

**Asserções comuns do Playwright:**
- `expect(locator).to_be_visible()`
- `expect(locator).to_have_text("texto esperado")`
- `expect(locator).to_be_empty()` (ótimo para verificar se um input foi limpo)
- `expect(locator).to_be_enabled()` / `to_be_disabled()`

#### 6.5 Boas Práticas: Testes Determinísticos

Na engenharia de testes, um teste é considerado **flaky (intermitente)** quando ele passa e falha aleatoriamente sem que nenhuma linha de código da aplicação tenha mudado. **Testes flaky são piores que a ausência de testes**, pois destroem a confiança da equipe na suíte de automação.

As duas causas mais comuns de testes E2E flaky e suas soluções são:

1. **Vazamento de Estado:** Um teste depende de dados criados por outro teste. 
   * **Solução:** Nunca confie em dados residuais. Use `autouse=True` para limpar o ambiente antes de cada teste ou crie os dados explicitamente dentro do próprio teste.
2. **Asserções Prematuras (Race Conditions):** O teste verifica algo na tela antes de o JavaScript terminar de processar uma requisição de rede.
   * **Solução:** Nunca use `assert` puro do Python para verificar elementos DOM que dependem de rede. Sempre use o `expect()` do Playwright, que possui *auto-wait* (espera ativa) embutido.

> **Regra de Sanidade:** Um teste E2E correto deve passar consistentemente tanto em modo `headless` (CI/CD, velocidade máxima) quanto em modo `--headed --slowmo 1000` (depuração visual). Se o teste falha ao ser desacelerado, ele não estava validando a integração real, estava apenas "vencendo uma corrida" contra o navegador.

---

## 7. Executando em modo visível e em outros navegadores

Ver o teste acontecendo "ao vivo" é uma das experiências mais motivadoras do desenvolvimento web. O `pytest-playwright` aceita argumentos de linha de comando poderosos:

### 7.1 Modo Headed (Ver o navegador abrir)
```bash
pytest --headed
```
O navegador abrirá na sua tela, executará os passos em velocidade real e fechará ao final.

### 7.2 Modo Lento (Para acompanhar passo a passo)
```bash
pytest --headed --slowmo 500
```
Adiciona um atraso de 500ms entre cada ação (fill, click), ideal para entender o que o teste está fazendo.

### 7.3 Testando em outros navegadores
```bash
pytest --browser firefox
pytest --browser webkit # (Motor do Safari)
```
Com uma única linha, você garante que seu JS e CSS funcionam no Firefox e no Safari, não apenas no Chrome.

---

## 8. Exercícios

### Exercício 1 — Verificando o estado do input
Após adicionar uma tarefa com sucesso, o JavaScript que fornecemos limpa o campo de input (`inputDescricao.value = ''`). Escreva um teste que verifique se o input está vazio após a adição.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
def test_input_eh_limpo_apos_adicionar(page, servidor):
    # ARRANGE
    page.goto(servidor)
    input_tarefa = page.get_by_placeholder("Descrição da tarefa")
    
    # ACT
    input_tarefa.fill("Tarefa temporária")
    page.get_by_role("button", name="Adicionar").click()
    
    # ASSERT 1: Espera a tarefa aparecer para garantir que o fetch terminou
    # e o DOM foi atualizado. Isso sincroniza o teste com o estado final da UI.
    expect(page.get_by_text("Tarefa temporária")).to_be_visible()
    
    # ASSERT 2: Verifica se o input foi limpo pelo JS (inputDescricao.value = '').
    # O matcher 'to_be_empty()' é específico para campos de formulário.
    expect(input_tarefa).to_be_empty()
```
</details>

---

#### Exercício 2 — A Validação Nativa do HTML5

O nosso input possui o atributo `required` (`<input ... required>`). Isso significa que o próprio navegador **bloqueia o envio do formulário** e exibe um tooltip de erro nativo antes mesmo de o JavaScript ser executado. Consequentemente, o `fetch` nunca é disparado.

Escreva um teste que tente adicionar uma tarefa com o campo vazio. Como garantimos no `conftest.py` que o banco começa limpo a cada teste, você pode asserir com segurança que a lista de tarefas na tela deve permanecer estritamente vazia (`to_have_count(0)`), provando que o backend nunca recebeu a requisição inválida.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
def test_formulario_nao_envia_vazio(page, servidor):
    # ARRANGE
    page.goto(servidor)
    
    # BOA PRÁTICA: Aguarda todas as requisições de rede iniciais terminarem.
    # O JS da página faz um fetch('/api/tarefas') ao carregar.
    # 'networkidle' garante que o estado inicial da tela está estável
    # antes de começarmos a interagir e fazer asserções.
    page.wait_for_load_state('networkidle')
    
    # ASSERT 1: Como o conftest.py limpa o banco antes de cada teste (autouse=True),
    # temos certeza absoluta de que a lista começa vazia.
    lista = page.locator("#lista-tarefas li")
    expect(lista).to_have_count(0)
    
    # ACT: Clica direto sem preencher.
    # O atributo HTML5 'required' no input bloqueia o submit nativamente.
    # O evento 'submit' do JS nunca dispara, logo, nenhum fetch é enviado.
    page.get_by_role("button", name="Adicionar").click()
    
    # ASSERT 2: A lista deve continuar rigorosamente vazia.
    # Isso prova que o backend Flask nunca recebeu a requisição inválida,
    # validando a integração entre a validação HTML5 e o comportamento da UI.
    expect(lista).to_have_count(0)
```
</details>

---

### Exercício 3 — Adicionando múltiplas tarefas
Escreva um teste que adicione três tarefas diferentes em sequência e verifique se todas as três estão visíveis na tela ao final.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
def test_adicionar_multiplas_tarefas(page, servidor):
    # ARRANGE
    page.goto(servidor)
    input_tarefa = page.get_by_placeholder("Descrição da tarefa")
    botao = page.get_by_role("button", name="Adicionar")
    
    tarefas = ["Comprar pão", "Estudar Python", "Pagar contas"]
    
    # ACT: Loop para adicionar múltiplas tarefas em sequência.
    for nome in tarefas:
        input_tarefa.fill(nome)
        botao.click()
        
        # ASSERT (dentro do loop): Espera cada uma aparecer antes de adicionar a próxima.
        # Isso evita que o Playwright digite a próxima tarefa enquanto o fetch
        # da anterior ainda está atualizando o DOM, prevenindo race conditions.
        expect(page.get_by_text(nome)).to_be_visible()
        
    # ASSERT FINAL: Verificação cruzada de que todas coexistem na tela.
    expect(page.get_by_text("Comprar pão")).to_be_visible()
    expect(page.get_by_text("Estudar Python")).to_be_visible()
    expect(page.get_by_text("Pagar contas")).to_be_visible()
```
</details>

---

## 9. Erros comuns

### Erro 1: Usar `assert` do Python em vez de `expect` do Playwright
**Errado:**
```python
texto = page.locator("#lista-tarefas").inner_text()
assert "Estudar" in texto # Falha se o JS ainda não terminou de renderizar
```
**Certo:**
```python
expect(page.get_by_text("Estudar")).to_be_visible() # Espera até 5s
```

### Erro 2: Esquecer de subir o servidor
Se você não usar a fixture `servidor` (ou não tiver o `flask run` rodando), o `page.goto()` falhará com `net::ERR_CONNECTION_REFUSED`. A fixture que criamos no `conftest.py` resolve isso automaticamente.

### Erro 3: Tentar testar o JS unitariamente no Playwright
O Playwright serve para testar o **fluxo completo no navegador**. Se você quer testar uma função JavaScript isolada (ex: `calcularTotal()`), o Playwright não é a ferramenta ideal. Para isso, usam-se ferramentas como Jest ou Vitest.

---

## 10. Quando usar / Quando não usar

### Use testes E2E (Playwright) para:
- ✅ Validar fluxos críticos do usuário (Login, Checkout, Criar Tarefa).
- ✅ Garantir que o Frontend e o Backend estão "conversando" corretamente.
- ✅ Testar a responsividade e a renderização visual (usando screenshots).
- ✅ Validar integrações complexas de JavaScript (fetch, DOM, eventos).

### Não use testes E2E para:
- ❌ Testar todas as regras de negócio e validações de string (use testes unitários em Python, Aula 1).
- ❌ Testar todas as variações de status code HTTP (use testes de integração com `test_client`, Aula 2).
- ❌ Rodar a cada segundo (E2E é lento. Rode antes de um deploy ou em pull requests importantes).

---

## 11. Checklist da aula

Ao final desta aula, você deve conseguir:
- explicar o conceito da Pirâmide de Testes e o papel do E2E;
- instalar e configurar o `pytest-playwright` e seus navegadores;
- criar uma fixture para subir um servidor Flask temporário para os testes;
- usar locators modernos (`get_by_role`, `get_by_placeholder`) para encontrar elementos;
- interagir com a página (`fill`, `click`);
- usar `expect` para fazer asserções que esperam o JavaScript assíncrono (auto-wait);
- executar testes em modo visível (`--headed`) e em diferentes navegadores.

---

## 12. Recapitulação

| Conceito | Significado |
|---|---|
| E2E (End-to-End) | Teste que simula um usuário real no navegador, validando o sistema completo. |
| Playwright | Framework moderno da Microsoft para automação de navegadores, sucessor do Selenium. |
| `page` | Fixture do pytest que representa a aba do navegador onde o teste ocorre. |
| Locators (`get_by_*`) | Métodos resilientes para encontrar elementos baseados em texto, papel (role) ou atributos. |
| `expect` | Função de asserção do Playwright que implementa auto-wait (espera o elemento ficar pronto). |
| `--headed` | Flag do pytest para rodar os testes abrindo a janela do navegador visualmente. |

---

## 13. O que não vimos no curso

| Tópico | Síntese |
|---|---|
| **Playwright Codegen** | O Playwright possui uma ferramenta (`playwright codegen url`) que grava suas ações manuais no navegador e gera o código Python do teste automaticamente. Excelente para criar rascunhos de testes rápidos. |
| **Testes Unitários de Frontend (Jest/Vitest)** | Ferramentas para testar funções JS isoladas, mockando o DOM e o `fetch`. Fora do escopo deste curso introdutório. |
| **Network Mocking** | O Playwright pode interceptar chamadas de rede (`page.route()`) para simular lentidão, erros 500 do backend ou testar o frontend offline. |
| **Visual Regression Testing** | Comparar screenshots automáticos da página com uma imagem base para detectar mudanças não intencionais no CSS. |
| **Emulação Mobile** | Configurar o Playwright para rodar testes simulando a tela e o user-agent de um iPhone ou dispositivo Android. |

---

## 14. Referências

- [Playwright Python - Getting Started](https://playwright.dev/python/docs/intro)
- [Playwright Python - Locators](https://playwright.dev/python/docs/locators)
- [Playwright Python - Assertions](https://playwright.dev/python/docs/test-assertions)
- [Playwright Pytest Plugin Reference](https://playwright.dev/python/docs/test-runners)