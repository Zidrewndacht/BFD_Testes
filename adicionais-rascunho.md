## Tópicos deixados de fora em cada aula:

Rascunho, em ajustes, alguns podem ainda ser incluídos nas aulas e removidos daqui, ou o contrário:

## Aula 1 — Testes Unitários em Python

| Tópico | Por que estudar depois | Documentação |
|---|---|---|
| **TDD (Test-Driven Development)** | Metodologia onde o teste é escrito *antes* do código. Muda a forma de pensar o design da aplicação: o ciclo Vermelho → Verde → Refatorar produz código mais desacoplado e testável por construção. | [Wikipedia — Test-driven development](https://en.wikipedia.org/wiki/Test-driven_development) |
| **Cobertura de código (`coverage.py`)** | Mede quais linhas e ramificações (`if/else`) foram realmente executadas pelos testes. Útil para encontrar "pontos cegos" em funções com muitas condicionais. | [coverage.py docs](https://coverage.readthedocs.io/) |
| **`pytest.mark.parametrize` avançado** | Permite testar combinações de parâmetros (ex: todos os status codes × todos os tipos de entrada) com `itertools.product` e nomes customizados para cada caso. | [pytest — Parametrizing fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html) |
| **Testes de exceções personalizados** | Criar hierarquia própria de exceções (`class TarefaInvalidaError(ValueError)`) e testar atributos específicos da exceção com `pytest.raises` e `match`. | [pytest — Asserting about expected exceptions](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions) |
| **Hypothesis (testes baseados em propriedades)** | Em vez de exemplos fixos, gera automaticamente centenas de entradas aleatórias para encontrar casos de borda que um humano jamais pensaria em testar. | [Hypothesis docs](https://hypothesis.readthedocs.io/) |

---

## Aula 2 — Testes de Integração: Flask + SQLite

| Tópico | Por que estudar depois | Documentação |
|---|---|---|
| **Fixtures avançadas (`scope`, factories)** | Escopos (`session`, `module`, `class`) controlam o ciclo de vida da fixture. Factories permitem parametrizar fixtures e gerar dados variados, essencial para suítes grandes. | [pytest — Fixture scope](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes) |
| **Mocks com `unittest.mock` e `pytest-mock`** | Isolar o código testado substituindo dependências externas (APIs, serviços de email, gateways de pagamento) por objetos falsos que retornam valores controlados. | [pytest-mock docs](https://pytest-mock.readthedocs.io/) |
| **Cobertura de código com `pytest-cov`** | Plugin que integra `coverage.py` ao pytest e gera relatórios HTML mostrando exatamente quais linhas do seu Flask app foram (e não foram) cobertas pelos testes. | [pytest-cov docs](https://pytest-cov.readthedocs.io/) |
| **Testes com autenticação e sessão** | Simular login, cookies e flash messages usando `client.session_transaction()` para testar rotas protegidas e fluxos que dependem de usuário autenticado. | [Flask — Accessing and Modifying the Session](https://flask.palletsprojects.com/en/stable/testing/#accessing-and-modifying-the-session) |
| **Padrão `g` e `teardown_appcontext`** | Gerenciar conexões de banco por requisição usando o objeto `g` do Flask, como o tutorial oficial do Flaskr faz. É o padrão idiomático para aplicações Flask de produção. | [Flask — Storing Data](https://flask.palletsprojects.com/en/stable/tutorial/database/#store-data) |
| **Testes de comandos CLI (`test_cli_runner`)** | Testar comandos personalizados registrados com `@app.cli.command()` (ex: `flask init-db`, `flask seed-data`) sem executá-los de verdade no terminal. | [Flask — Running Commands with the CLI Runner](https://flask.palletsprojects.com/en/stable/testing/#running-commands-with-the-cli-runner) |

---

## Aula 3: E2E com Playwright

| Tópico | Por que estudar depois | Documentação |
|---|---|---|
| **Page Object Model (POM)** | Padrão de design que encapsula cada página da aplicação em uma classe, tornando testes E2E mais legíveis e menos frágeis a mudanças de layout. | [Playwright — Page object models](https://playwright.dev/python/docs/pom) |
| **Fixtures customizadas no Playwright** | Criar fixtures que já entregam um usuário autenticado, dados populados ou uma página específica, reduzindo boilerplate nos testes E2E. | [Playwright — Fixtures](https://playwright.dev/python/docs/test-fixtures) |
| **Visual regression testing** | Comparar screenshots atuais com screenshots de referência para detectar mudanças visuais não intencionais no CSS ou layout. | [Playwright — Test runner — Screenshots](https://playwright.dev/python/docs/test-snapshots) |
| **Emulação de dispositivos e rede** | Testar a aplicação em diferentes tamanhos de tela (mobile, tablet), geolocalizações e condições de rede lenta usando recursos nativos do Playwright. | [Playwright — Emulation](https://playwright.dev/python/docs/emulation) |
| **Testes em múltiplos navegadores** | Configurar o Playwright para rodar a mesma suíte em Chromium, Firefox e WebKit, garantindo compatibilidade cross-browser. | [Playwright — Browsers](https://playwright.dev/python/docs/browsers) |
| **Network interception** | Interceptar e modificar requisições HTTP feitas pela página durante o teste, útil para simular respostas lentas, erros de servidor ou APIs externas sem dependência de rede. | [Playwright — Network](https://playwright.dev/python/docs/network) |

---

**Resumo do ajuste:** a seção passou a ser uma **biblioteca de caminhos de estudo**, onde cada linha responde implicitamente à pergunta *"acabei esta aula, para onde vou agora se quiser me aprofundar?"*. Tópicos distantes do tema da aula (CI/CD, TDD estrito na Aula 2, etc.) foram removidos, pois pertenceriam a aulas específicas sobre esses assuntos.

Posso aplicar esse mesmo padrão editorial à Aula 3 quando formos montá-la.