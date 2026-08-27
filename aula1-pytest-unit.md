# Aula 1 — Testes Unitários em Python e Qualidade de Código

**Pré-requisitos:** Aulas de OOP (classes, métodos, `to_dict()`), funções, listas, dicionários, ambientes virtuais (`venv`) e `pip`.

**Objetivo da aula:** entender a diferença entre teste manual e automatizado, escrever testes unitários com `pytest` para validar regras de negócio e usar o `ruff` para manter o código padronizado.

> **Nota de vocabulário:** **Teste automatizado** é um pedaço de código cujo único propósito é executar outro pedaço do seu código e verificar se ele se comportou como o esperado.

---

## 0. Introdução conceitual: por que testar

### 0.1 O problema do "teste manual"

Até agora, para verificar se uma função ou classe funciona, você provavelmente fez algo assim:

```python
t = Tarefa("Estudar Python")
t.concluir()
print(t.resumo())  # Olha no terminal se apareceu ✅
```

Ou então, no caso do Flask, você:

1. Rodou o servidor (`flask run`);
2. Abriu o Postman ou o navegador;
3. Enviou um JSON;
4. Olhou a resposta;
5. Abriu o DB Browser para ver se a linha foi gravada no SQLite.

Isso funciona para uma ou duas verificações. Mas o que acontece quando você adiciona uma nova regra de negócio (ex: "tarefa não pode ter mais de 100 caracteres") e precisa garantir que **nenhuma outra parte do sistema quebrou** por causa dessa mudança?

Fazer o teste manual de todas as rotas e regras toda vez que você salva um arquivo é inviável. O resultado é o medo de alterar código antigo (o famoso "se mexer aqui, quebra ali").

### 0.2 A solução: Testes Automatizados

Em vez de testar manualmente, você escreve **funções de teste**. Essas funções:

1. Criam o cenário (ex: instanciam uma `Tarefa`);
2. Executam a ação (ex: chamam `validar()`);
3. Afirmam o resultado esperado (ex: "o resultado deve ser `False`").

Você roda todas as suas funções de teste com um único comando no terminal. Se algo quebrar, o framework de testes aponta exatamente qual regra falhou.

---

## 1. Preparando o ambiente

Para esta aula, usaremos duas ferramentas que são o padrão do mercado Python moderno:

- **`pytest`**: o framework de testes mais usado no ecossistema Python.
- **`ruff`**: uma ferramenta que analisa seu código (linter), formata e organiza os imports automaticamente. Ela substitui ferramentas como `flake8`, `black` e `isort`.

### 1.1 Instalação

No seu ambiente virtual (`.venv`), instale ambas como dependências de desenvolvimento:

```bash
pip install pytest ruff
pip freeze > requirements.txt
```

### 1.2 Estrutura de pastas

Testes em Python geralmente ficam em uma pasta separada chamada `tests/` ou ao lado dos arquivos que eles testam, com o prefixo `test_`.

Para esta aula, vamos usar a seguinte estrutura:

```text
projeto/
├── .venv/
├── tarefa.py          # A classe de domínio que já conhecemos
├── test_tarefa.py     # Os testes da classe Tarefa
└── requirements.txt
```

O `pytest` descobre automaticamente qualquer arquivo que comece com `test_` e qualquer função dentro dele que comece com `test_`.

<details>
<summary> Por que pytest em vez de unittest?  </summary>

### 1.3 Por que `pytest` e não o `unittest` da biblioteca padrão?

O Python já vem com um módulo de testes embutido chamado `unittest`. Então, por que a indústria (e este curso) adota o `pytest`, que exige instalação via `pip`?

A resposta curta é: **o `unittest` foi inspirado em linguagens como Java e exige muito código repetitivo (boilerplate). O `pytest` foi desenhado para ser "Pythonico", usando funções simples e o `assert` nativo da linguagem.**

Vamos comparar os dois na prática.

#### Comparação 1: Estrutura e Boilerplate

**Com `unittest` (Biblioteca Padrão):**
Você é obrigado a criar uma classe, herdar de `unittest.TestCase` e usar métodos específicos de asserção.

```python
import unittest
from tarefa import Tarefa

class TestTarefa(unittest.TestCase):
    def test_tarefa_valida(self):
        t = Tarefa("Estudar Python")
        # Método específico da classe TestCase
        self.assertTrue(t.validar()) 

    def test_tarefa_invalida(self):
        t = Tarefa("")
        self.assertFalse(t.validar())

if __name__ == '__main__':
    unittest.main()
```

**Com `pytest` (Padrão de Mercado):**
Você usa funções puras e o `assert` nativo do Python. Sem classes obrigatórias, sem herança, sem `if __name__ == '__main__'`.

```python
from tarefa import Tarefa

def test_tarefa_valida():
    t = Tarefa("Estudar Python")
    assert t.validar() is True

def test_tarefa_invalida():
    t = Tarefa("")
    assert t.validar() is False
```
*Menos código, mesma cobertura, leitura muito mais limpa.*

#### Comparação 2: A mémoria das Asserções

No `unittest`, você precisa decorar dezenas de métodos diferentes para cada tipo de comparação:
- `self.assertEqual(a, b)`
- `self.assertNotEqual(a, b)`
- `self.assertIn(item, lista)`
- `self.assertRaises(ValueError)`

No `pytest`, você simplesmente usa a linguagem Python que você já conhece:
- `assert a == b`
- `assert a != b`
- `assert item in lista`
- `with pytest.raises(ValueError):`

#### Comparação 3: Relatórios de Erro (A "Mágica" do pytest)

Quando um teste falha, a clareza da mensagem de erro é fundamental para corrigir o bug.

Se o `unittest` falha em um `self.assertEqual(lista_esperada, lista_real)`, ele cospe um bloco de texto genérico e difícil de ler.

O `pytest` intercepta o `assert` nativo do Python e faz uma **introspecção** das variáveis. Se você escrever `assert resultado == esperado` e o teste falhar, o `pytest` mostrará exatamente o que havia dentro de `resultado` e o que havia dentro de `esperado`, destacando a diferença caractere por caractere ou item por item, sem que você precise escrever código extra para gerar logs de depuração.

#### Comparação 4: Preparando o terreno para o Backend (Fixtures)

Na próxima aula, precisaremos criar um banco de dados falso em memória para cada teste e destruí-lo logo em seguida. 
- No `unittest`, isso é feito com os métodos `setUp()` e `tearDown()`, que compartilham estado via `self` e podem se tornar confusos em testes complexos.
- No `pytest`, usamos **Fixtures** (`@pytest.fixture`), que injetam dependências nas funções de teste de forma modular e explícita. É o recurso mais poderoso do framework e o principal motivo pelo qual ele domina o ecossistema Flask/Django/FastAPI.

**Resumo:** O `unittest` é útil se você estiver preso em um ambiente corporativo restrito onde não pode instalar pacotes de terceiros via `pip`. Para qualquer outro cenário moderno em Python, o `pytest` é a ferramenta correta.

---

Com essa adição, a Aula 1 fica blindada contra a dúvida do "por que não usar o que já vem instalado?". 

Podemos seguir para a estrutura e material da **Aula 2 (Testes de Integração: Flask + SQLite + Fixtures)**?
</details>



---

## 2. O primeiro teste e o padrão AAA

### 2.1 A classe a ser testada

Considere a classe `Tarefa` que construímos na Aula 1 de OOP:

```python
# tarefa.py
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
```

### 2.2 Escrevendo o teste

Crie o arquivo `test_tarefa.py`:

```python
# test_tarefa.py
from tarefa import Tarefa

def test_tarefa_valida():
    # 1. Arrange (Preparar): criar o objeto e os dados necessários
    t = Tarefa("Estudar Python")
    
    # 2. Act (Agir): executar a ação que queremos testar
    resultado = t.validar()
    
    # 3. Assert (Assertar): verificar se o resultado é o esperado
    assert resultado is True
```

### 2.3 O padrão AAA

Todo teste unitário bem escrito segue o padrão **AAA**:

| Etapa | O que faz | Exemplo |
|---|---|---|
| **Arrange** (Preparar) | Configura o estado inicial, cria objetos e dados. | `t = Tarefa("Estudar")` |
| **Act** (Agir) | Chama o método ou função que está sob teste. | `resultado = t.validar()` |
| **Assert** (Assertar) | Verifica se o resultado bate com a expectativa. | `assert resultado is True` |

### 2.4 Executando o teste

No terminal, na raiz do projeto (onde está o `test_tarefa.py`), execute:

```bash
pytest
```

Saída esperada:

```text
============================= test session starts ==============================
collected 1 item

test_tarefa.py .                                                         [100%]

============================== 1 passed in 0.01s ===============================
```

O ponto (`.`) verde indica que o teste passou. Se o teste falhasse, apareceria um `F` vermelho e o `pytest` mostraria exatamente em qual linha a asserção quebrou.

---

## 3. Testando casos de borda

Testar apenas o "caminho feliz" (quando tudo dá certo) é insuficiente. A maior parte dos bugs de software ocorre nas bordas: dados vazios, nulos, negativos ou extremamente grandes.

### 3.1 Múltiplos testes para a mesma função

Vamos adicionar testes para as regras de validação da nossa classe:

```python
# test_tarefa.py (adicionando novos testes)
from tarefa import Tarefa

def test_tarefa_valida():
    t = Tarefa("Estudar Python")
    assert t.validar() is True

def test_tarefa_invalida_se_descricao_vazia():
    t = Tarefa("")
    assert t.validar() is False

def test_tarefa_invalida_se_descricao_apenas_espacos():
    t = Tarefa("   ")
    assert t.validar() is False

def test_tarefa_invalida_se_descricao_muito_longa():
    descricao_gigante = "A" * 101  # 101 caracteres
    t = Tarefa(descricao_gigante)
    assert t.validar() is False

def test_tarefa_invalida_se_descricao_nao_for_string():
    t = Tarefa(12345)
    assert t.validar() is False
```

Agora, ao rodar `pytest`, a saída será:

```text
collected 5 items

test_tarefa.py .....                                                     [100%]

============================== 5 passed in 0.02s ===============================
```

Cada função `test_*` é isolada. O estado de uma não contamina a outra. Se um teste falhar, os outros continuam rodando, permitindo que você veja o panorama completo dos erros de uma só vez.

---

## 4. Testando mudanças de estado e exceções

### 4.1 Testando métodos que alteram o objeto

O método `concluir()` não retorna nada (retorna `None`), ele apenas altera o estado interno do objeto. O teste deve verificar o **efeito colateral**:

```python
def test_concluir_altera_estado():
    t = Tarefa("Estudar Flask")
    
    # Estado inicial
    assert t.concluida is False
    
    # Ação
    t.concluir()
    
    # Estado final esperado
    assert t.concluida is True
```

### 4.2 Testando conversão para dicionário

```python
def test_to_dict_retorna_estrutura_correta():
    t = Tarefa("Estudar", id=42, concluida=True)
    
    dicionario = t.to_dict()
    
    assert isinstance(dicionario, dict)
    assert dicionario["id"] == 42
    assert dicionario["descricao"] == "Estudar"
    assert dicionario["concluida"] is True
```

### 4.3 Testando exceções com `pytest.raises`

Em alguns casos, em vez de retornar `False`, um método pode levantar uma exceção (como vimos no Flask com `ValueError`). O `pytest` fornece um gerenciador de contexto para capturar e afirmar que a exceção correta foi levantada:

```python
import pytest

def dividir(a, b):
    if b == 0:
        raise ValueError("Divisor não pode ser zero.")
    return a / b

def test_divisao_por_zero_levanta_excecao():
    with pytest.raises(ValueError, match="Divisor não pode ser zero"):
        dividir(10, 0)
```

O `match` aceita uma expressão regular ou substring para verificar se a mensagem de erro está correta. Se a exceção não for levantada, o teste falha.

---

## 5. Qualidade de código com Ruff

Escrever testes garante que a **lógica** está correta. Mas e a **formatação**? E os imports não utilizados? E as variáveis declaradas e nunca lidas?

No mercado de trabalho, equipes usam ferramentas de **Linting** (análise estática) para impor padrões de código automaticamente, evitando discussões subjetivas em *Code Reviews*.

### 5.1 O que é o Ruff

O `ruff` é uma ferramenta que analisa seu código Python em busca de:

- **Linting:** Detecta imports não utilizados, variáveis nunca lidas e outros problemas.
- **Formatação:** Aplica estilo consistente:  aspas simples vs duplas, espaçamento, quebras de linha, etc.
- **Organização de imports:** Ordena os imports existentes no topo do módulo em grupos (stdlib, terceiros, local). Não move imports que estão dentro de funções (intencionalmente importados sob demanda).

### 5.2 Verificando o código (Linting)

No terminal, rode:

```bash
ruff check .
```

Se o seu código estiver limpo, a saída será:

```text
All checks passed!
```

Se houver problemas (ex: um import não usado em `tarefa.py`), o `ruff` listará o arquivo, a linha e o código do erro:

```text
tarefa.py:1:1: F401 `os` imported but unused
Found 1 error.
```

### 5.3 Corrigindo automaticamente

Muitos erros de formatação e imports podem ser corrigidos automaticamente pelo `ruff`:

```bash
ruff check . --fix
```

### 5.4 Formatando o código

Para aplicar uma formatação padrão (semelhante ao que o `black` fazia), use o formatador embutido do `ruff`:

```bash
ruff format .
```

Isso reescreve seus arquivos `.py` garantindo que toda a equipe use o mesmo estilo visual, sem esforço manual.

### 5.5 O fluxo de trabalho sugerido

```bash
ruff check . --fix
ruff format .
pytest
```

---

## 6. Exemplo mais completo: Classe Produto

Vamos testar a classe `Produto` vista na Aula 1 de OOP.

```python
# produto.py
class Produto:
    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def validar(self):
        if not self.nome:
            return False
        if self.preco <= 0:
            return False
        if self.estoque < 0:
            return False
        return True
```

E os testes correspondentes:

```python
# test_produto.py
from produto import Produto

def test_produto_valido():
    p = Produto("Teclado", 150.0, 10)
    assert p.validar() is True

def test_produto_invalido_sem_nome():
    p = Produto("", 150.0, 10)
    assert p.validar() is False

def test_produto_invalido_preco_zero():
    p = Produto("Mouse", 0, 5)
    assert p.validar() is False

def test_produto_invalido_preco_negativo():
    p = Produto("Monitor", -100.0, 2)
    assert p.validar() is False

def test_produto_invalido_estoque_negativo():
    p = Produto("Cabo", 10.0, -1)
    assert p.validar() is False

def test_produto_valido_com_estoque_zero():
    # Estoque zero é permitido (produto esgotado, mas válido)
    p = Produto("Webcam", 200.0, 0)
    assert p.validar() is True
```

---

### Parametrização de testes

Quando você tem muitos testes que fazem exatamente a mesma coisa, mudando apenas os dados de entrada e o resultado esperado, o `pytest` permite **parametrizar** o teste. Isso evita a repetição de código (DRY - *Don't Repeat Yourself*).

```python
import pytest
from produto import Produto

@pytest.mark.parametrize("nome, preco, estoque, esperado", [
    ("Teclado", 150.0, 10, True),
    ("", 150.0, 10, False),
    ("Mouse", 0, 5, False),
    ("Monitor", -100.0, 2, False),
    ("Cabo", 10.0, -1, False),
    ("Webcam", 200.0, 0, True),
])
def test_validacao_de_produto(nome, preco, estoque, esperado):
    p = Produto(nome, preco, estoque)
    assert p.validar() is esperado
```

O `pytest` vai executar a função `test_validacao_de_produto` 6 vezes, injetando os valores de cada tupla como argumentos. Na saída do terminal, você verá algo como:

```text
test_produto.py::test_validacao_de_produto[Teclado-150.0-10-True] PASSED
test_produto.py::test_validacao_de_produto[-150.0-10-False] PASSED
...
```

## 7. Testes que encontram bugs reais

Até agora, nossos testes verificaram funções simples e óbvias. Mas o verdadeiro poder dos testes automatizados aparece quando testamos **lógica de negócio complexa** e **casos de borda** que facilmente passam despercebidos em inspeção visual.

Vamos analisar alguns exemplos realistas onde o código **parece correto**, mas contém bugs sutis que só testes automatizados conseguem capturar.

### 7.1 Exemplo 1: Desconto progressivo com limite errado

Considere esta função que aplica descontos progressivos em um carrinho de compras:

```python
# carrinho.py
def calcular_total_com_desconto(itens):
    """
    Calcula o total de um carrinho aplicando descontos progressivos:
    - Até R$ 100: sem desconto
    - De R$ 100,01 a R$ 500: 10% de desconto
    - Acima de R$ 500: 20% de desconto

    Args:
        itens: lista de dicionários com 'preco' e 'quantidade'

    Returns:
        dict com 'subtotal', 'desconto_aplicado' (em %), 'valor_desconto' e 'total_final'
    """
    subtotal = sum(item['preco'] * item['quantidade'] for item in itens)

    if subtotal >= 500:
        desconto_percentual = 20
    elif subtotal >= 100:
        desconto_percentual = 10
    else:
        desconto_percentual = 0

    valor_desconto = subtotal * (desconto_percentual / 100)
    total_final = subtotal - valor_desconto

    return {
        'subtotal': round(subtotal, 2),
        'desconto_aplicado': desconto_percentual,
        'valor_desconto': round(valor_desconto, 2),
        'total_final': round(total_final, 2)
    }
```
À primeira vista, o código parece correto. A documentação é clara, a lógica parece seguir as regras especificadas. Vamos escrever testes:

```python
# test_carrinho.py
from carrinho import calcular_total_com_desconto

def test_carrinho_sem_desconto():
    itens = [{'preco': 50.0, 'quantidade': 1}]
    resultado = calcular_total_com_desconto(itens)
    assert resultado['subtotal'] == 50.0
    assert resultado['desconto_aplicado'] == 0
    assert resultado['total_final'] == 50.0

def test_carrinho_com_10_porcento():
    itens = [{'preco': 100.0, 'quantidade': 2}]  # Total: R$ 200
    resultado = calcular_total_com_desconto(itens)
    assert resultado['subtotal'] == 200.0
    assert resultado['desconto_aplicado'] == 10
    assert resultado['total_final'] == 180.0

def test_carrinho_com_20_porcento():
    itens = [{'preco': 300.0, 'quantidade': 2}]  # Total: R$ 600
    resultado = calcular_total_com_desconto(itens)
    assert resultado['subtotal'] == 600.0
    assert resultado['desconto_aplicado'] == 20
    assert resultado['total_final'] == 480.0

def test_carrinho_exatamente_100_reais():
    """
    A documentação diz 'Até R$ 100: sem desconto'.
    R$ 100,00 exatos NÃO devem receber desconto.
    """
    itens = [{'preco': 50.0, 'quantidade': 2}]  # Total: R$ 100
    resultado = calcular_total_com_desconto(itens)

    assert resultado['subtotal'] == 100.0
    assert resultado['desconto_aplicado'] == 0   # FALHA: código retorna 10
    assert resultado['valor_desconto'] == 0.0
    assert resultado['total_final'] == 100.0

def test_carrinho_exatamente_500_reais():
    """
    BUG DETECTADO PELO TESTE:
    A documentação diz 'Acima de R$ 500: 20%'.
    R$ 500,00 exatos devem receber 10%, não 20%.
    """
    itens = [{'preco': 250.0, 'quantidade': 2}]  # Total: R$ 500
    resultado = calcular_total_com_desconto(itens)

    assert resultado['subtotal'] == 500.0
    assert resultado['desconto_aplicado'] == 10  # FALHA: código retorna 20
    assert resultado['total_final'] == 450.0
```

Saída do `pytest`:

```text
test_carrinho.py ...FF

FAILED test_carrinho.py::test_carrinho_exatamente_100_reais - assert 10 == 0
FAILED test_carrinho.py::test_carrinho_exatamente_500_reais - assert 20 == 10
```


**O bug:** O código usa `subtotal > 100`, mas a documentação diz "De R$ 100,01". Para um subtotal de exatamente R$ 100,00, o código aplica 10% de desconto quando não deveria. A correção seria usar `subtotal >= 100.01` ou, mais pragmaticamente, `subtotal > 100` está correto se a documentação for ajustada.

Esse é o tipo de bug que:
- Passa em inspeção visual (o código parece seguir a lógica)
- Só aparece em casos de borda específicos
- Pode causar problemas financeiros reais em produção
---

### 7.2 Exemplo 2: Validação de data com ano bissexto

Considere esta função que calcula a idade de uma pessoa. Para tornar a função testável sem depender da data atual, ela aceita um parâmetro opcional `data_referencia`.

```python
# idade.py
from datetime import date

def calcular_idade(data_nascimento_str, data_referencia=None):
    """
    Calcula a idade em anos completos a partir de uma data de nascimento.

    Args:
        data_nascimento_str: string no formato 'DD/MM/AAAA'
        data_referencia: date opcional para testes (padrão: hoje)

    Returns:
        int: idade em anos completos

    Raises:
        ValueError: se a data for inválida ou no futuro
    """
    dia, mes, ano = map(int, data_nascimento_str.split('/'))

    # BUG 1: não valida se a data existe.
    # "29/02/2001" é aceita sem erro, mas 2001 não é ano bissexto.
    # A validação correta seria: date(ano, mes, dia)

    hoje = data_referencia if data_referencia else date.today()

    if (ano, mes, dia) > (hoje.year, hoje.month, hoje.day):
        raise ValueError("Data de nascimento não pode ser no futuro")

    idade = hoje.year - ano

    # BUG 2: usa >= em vez de >.
    # No dia do aniversário, (mes, dia) == (hoje.month, hoje.day),
    # então >= é True e subtrai 1 ano indevidamente.
    if (mes, dia) >= (hoje.month, hoje.day):
        idade -= 1

    return idade
```

Os testes:

```python
# test_idade.py
from datetime import date
import pytest
from idade import calcular_idade

def test_idade_basica():
    """Aniversário já passou este ano."""
    ref = date(2026, 8, 26)
    assert calcular_idade("15/05/2000", ref) == 26

def test_idade_aniversario_hoje():
    """
    BUG DETECTADO PELO TESTE:
    No dia do aniversário, a pessoa JÁ fez anos.
    O código usa >= e subtrai 1 indevidamente.
    """
    ref = date(2026, 8, 26)
    assert calcular_idade("26/08/2000", ref) == 26  # FALHA: retorna 25

def test_idade_aniversario_amanha():
    """Se o aniversário é amanhã, ainda não fez anos."""
    ref = date(2026, 8, 26)
    assert calcular_idade("27/08/2000", ref) == 25

def test_idade_data_invalida_29_fev():
    """
    BUG DETECTADO PELO TESTE:
    29/02/2001 não existe (2001 não é bissexto).
    O código deveria levantar ValueError, mas aceita silenciosamente.
    """
    ref = date(2026, 8, 26)
    with pytest.raises(ValueError):
        calcular_idade("29/02/2001", ref)  # FALHA: não levanta exceção
```

Saída do `pytest`:

```text
test_idade.py .F.F

FAILED test_idade.py::test_idade_aniversario_hoje - assert 25 == 26
FAILED test_idade.py::test_idade_data_invalida_29_fev - DID NOT RAISE <class 'ValueError'>
```

**As correções** seriam:
1. Adicionar `date(ano, mes, dia)` logo após o `map(int, ...)` para validar a data.
2. Trocar `>=` por `>` na comparação do aniversário.

---

### 7.3 Exemplo 3: Classificação de produto com limite errado

A documentação diz `preço < 50` para promoção relâmpago, mas o código usa `<=`.

```python
# produto_classificar.py
def classificar_produto(preco, estoque, categoria):
    """
    Classifica um produto para fins de promoção.

    Regras:
    - Se preço <= 0 ou estoque < 0: 'inválido'
    - Se estoque == 0: 'esgotado'
    - Se preço < 50 e categoria == 'eletrônicos': 'promoção_relâmpago'
    - Se preço < 100 e estoque > 10: 'promoção'
    - Se preço >= 1000: 'premium'
    - Caso contrário: 'normal'
    """
    if preco <= 0 or estoque < 0:
        return 'inválido'

    if estoque == 0:
        return 'esgotado'

    # BUG: usa <= em vez de <.
    # A documentação diz "preço < 50", mas <= inclui R$ 50,00.
    if preco <= 50 and categoria == 'eletrônicos':
        return 'promoção_relâmpago'

    if preco < 100 and estoque > 10:
        return 'promoção'

    if preco >= 1000:
        return 'premium'

    return 'normal'
```

Os testes:

```python
# test_produto_classificar.py
from produto_classificar import classificar_produto

def test_produto_invalido_preco_negativo():
    assert classificar_produto(-10, 5, 'livros') == 'inválido'

def test_produto_invalido_estoque_negativo():
    assert classificar_produto(50, -1, 'livros') == 'inválido'

def test_produto_esgotado():
    assert classificar_produto(100, 0, 'livros') == 'esgotado'

def test_produto_promocao_relampago():
    assert classificar_produto(30, 5, 'eletrônicos') == 'promoção_relâmpago'

def test_produto_exatamente_50_reais():
    """
    BUG DETECTADO PELO TESTE:
    A documentação diz 'preço < 50'.
    R$ 50,00 exatos NÃO devem ser promoção_relâmpago.
    """
    assert classificar_produto(50, 5, 'eletrônicos') == 'normal'  # FALHA: retorna 'promoção_relâmpago'

def test_produto_exatamente_100_reais():
    """Preço exatamente R$ 100 não é < 100, portanto não é 'promoção'."""
    assert classificar_produto(100, 15, 'livros') == 'normal'

def test_produto_exatamente_1000_reais():
    """Preço exatamente R$ 1000 é >= 1000, portanto é 'premium'."""
    assert classificar_produto(1000, 5, 'livros') == 'premium'

def test_produto_promocao():
    assert classificar_produto(80, 15, 'livros') == 'promoção'

def test_produto_premium():
    assert classificar_produto(1500, 5, 'eletrônicos') == 'premium'

def test_produto_normal():
    assert classificar_produto(200, 5, 'livros') == 'normal'

def test_produto_esgotado_tem_prioridade():
    """Produto esgotado é 'esgotado' mesmo que o preço indicasse outra coisa."""
    assert classificar_produto(30, 0, 'eletrônicos') == 'esgotado'
```

Saída do `pytest`:

```text
test_produto_classificar.py ....F..........

FAILED test_produto_classificar.py::test_produto_exatamente_50_reais - assert 'promoção_relâmpago' == 'normal'
```

**A correção** seria trocar `<=` por `<` no `if` da promoção relâmpago.

---

### 7.4 O que esses exemplos demonstram

1. **`>` vs `>=` vs `<` vs `<=`** são a fonte mais comum de bugs de limite. Inspeção visual raramente os detecta.
2. **Falta de validação de entrada** permite dados impossíveis (datas inexistentes) sem erro.
3. **Testes de caso de borda** (valores exatamente nos limites) são os que mais revelam bugs.
4. **Testes que esperam exceções** (`pytest.raises`) capturam a ausência de validação.
5. **Parâmetros injetáveis** (como `data_referencia`) tornam o código testável sem depender do ambiente.

---

## 8. Exercícios

### Exercício 1 — Testando a classe Livro

Crie o arquivo `livro.py` com a classe abaixo:

```python
class Livro:
    def __init__(self, titulo, autor, ano_publicacao):
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao

    def validar(self):
        if not isinstance(self.titulo, str) or not self.titulo.strip():
            return False
        if not isinstance(self.autor, str) or not self.autor.strip():
            return False
        if not isinstance(self.ano_publicacao, int):
            return False
        if self.ano_publicacao < 0:
            return False
        return True
```

Escreva o arquivo `test_livro.py` contendo pelo menos 5 testes unitários cobrindo:
1. Um livro válido.
2. Um livro com título vazio.
3. Um livro com autor contendo apenas espaços.
4. Um livro com ano de publicação negativo.
5. Um livro com ano de publicação igual a zero (deve ser válido).

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
# test_livro.py
from livro import Livro

def test_livro_valido():
    l = Livro("1984", "George Orwell", 1949)
    assert l.validar() is True

def test_livro_invalido_titulo_vazio():
    l = Livro("", "George Orwell", 1949)
    assert l.validar() is False

def test_livro_invalido_autor_espacos():
    l = Livro("1984", "   ", 1949)
    assert l.validar() is False

def test_livro_invalido_ano_negativo():
    l = Livro("1984", "George Orwell", -500)
    assert l.validar() is False

def test_livro_valido_ano_zero():
    l = Livro("História Antiga", "Autor Desconhecido", 0)
    assert l.validar() is True
```
</details>

---

### Exercício 2 — Testando exceções

Crie a função `calcular_desconto(preco, percentual)` abaixo em um arquivo chamado `desconto.py`:

```python
def calcular_desconto(preco, percentual):
    if preco < 0:
        raise ValueError("Preço não pode ser negativo.")
    if percentual < 0 or percentual > 100:
        raise ValueError("Percentual deve estar entre 0 e 100.")
    return preco - (preco * percentual / 100)
```

Escreva o arquivo `test_desconto.py` com testes que afirmem:
1. O cálculo correto de um desconto de 20% em 100 reais (deve retornar 80.0).
2. Que passar um preço negativo levanta `ValueError`.
3. Que passar um percentual de 110 levanta `ValueError`.

<details>
<summary><strong>Ver solução resumida</strong></summary>

```python
# test_desconto.py
import pytest
from desconto import calcular_desconto

def test_calculo_correto():
    resultado = calcular_desconto(100.0, 20)
    assert resultado == 80.0

def test_preco_negativo_levanta_excecao():
    with pytest.raises(ValueError, match="Preço não pode ser negativo"):
        calcular_desconto(-50.0, 10)

def test_percentual_acima_de_100_levanta_excecao():
    with pytest.raises(ValueError, match="Percentual deve estar entre 0 e 100"):
        calcular_desconto(100.0, 110)
```
</details>

---

### Exercício 3 — Uso do Ruff

1. Crie um arquivo chamado `sujo.py` com o seguinte código intencionalmente ruim:

```python
import os
import sys
import json

def somar( a,b ):
    x = 10
    return a+b
```

2. Rode `ruff check sujo.py` e observe os erros (imports não usados, espaçamento).
3. Rode `ruff check sujo.py --fix` para ver o que ele consegue corrigir sozinho.
4. Rode `ruff format sujo.py` para ver a formatação final.

<details>
<summary><strong>Ver resultado esperado após ruff format</strong></summary>

```python
def somar(a, b):
    return a + b
```
Os imports `os`, `sys` e `json` foram removidos pelo `--fix` pois não eram utilizados. A variável `x` foi removida pelo mesmo motivo. O espaçamento da função foi corrigido pelo `format`.
</details>

---


### Exercício 4 — Encontre o bug: Validação de senha

A função abaixo deveria exigir os três tipos de caractere simultaneamente, mas usa `or` em vez de `and` no retorno.

```python
# senha.py
def validar_senha(senha):
    """
    Valida uma senha baseada em critérios de segurança.

    Regras:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número

    Retorna True se a senha for válida, False caso contrário.
    """
    if len(senha) < 8:
        return False

    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False

    for char in senha:
        if char.isupper():
            tem_maiuscula = True
        elif char.islower():
            tem_minuscula = True
        elif char.isdigit():
            tem_numero = True

    # BUG: usa 'or' em vez de 'and'.
    # Basta UM dos critérios para retornar True.
    return tem_maiuscula or tem_minuscula or tem_numero
```

**Sua tarefa:** escreva testes que detectem o bug.

<details>
<summary><strong>Ver testes que detectam o bug</strong></summary>

```python
# test_senha.py
from senha import validar_senha

def test_senha_valida_completa():
    """Senha com os três tipos deve ser válida."""
    assert validar_senha("Senha123") is True

def test_senha_muito_curta():
    assert validar_senha("Sen1") is False

def test_senha_sem_maiuscula():
    """
    BUG DETECTADO: senha sem maiúscula deveria ser inválida,
    mas o 'or' faz com que retorne True (tem minúscula E número).
    """
    assert validar_senha("senha123") is False  # FALHA: retorna True

def test_senha_sem_minuscula():
    """
    BUG DETECTADO: senha sem minúscula deveria ser inválida.
    """
    assert validar_senha("SENHA123") is False  # FALHA: retorna True

def test_senha_sem_numero():
    """
    BUG DETECTADO: senha sem número deveria ser inválida.
    """
    assert validar_senha("SenhaABC") is False  # FALHA: retorna True

def test_senha_apenas_numeros():
    """
    BUG DETECTADO: senha só com números deveria ser inválida.
    """
    assert validar_senha("12345678") is False  # FALHA: retorna True

def test_senha_apenas_letras():
    """
    BUG DETECTADO: senha só com letras deveria ser inválida.
    """
    assert validar_senha("abcdefgh") is False  # FALHA: retorna True
```

Saída esperada:

```text
test_senha.py ..FFFFF

5 failed, 2 passed
```

**A correção** é trocar `or` por `and`:

```python
return tem_maiuscula and tem_minuscula and tem_numero
```
</details>

---

### Exercício 5 — Encontre o bug: Média ponderada sem validação de pesos

A documentação diz que pesos devem ser positivos, mas o código não valida isso.

```python
# media.py
def calcular_media_ponderada(notas, pesos):
    """
    Calcula a média ponderada de uma lista de notas.

    Args:
        notas: lista de números (notas)
        pesos: lista de números positivos (pesos correspondentes)

    Returns:
        float: média ponderada

    Raises:
        ValueError: se as listas tiverem tamanhos diferentes,
                    se estiverem vazias, se algum peso for negativo,
                    ou se a soma dos pesos for zero
    """
    if len(notas) != len(pesos):
        raise ValueError("Listas de notas e pesos devem ter o mesmo tamanho")

    if len(notas) == 0:
        raise ValueError("Lista de notas não pode estar vazia")

    # BUG: não valida se os pesos são positivos.
    # A documentação diz "pesos positivos", mas o código aceita negativos.

    soma_ponderada = sum(nota * peso for nota, peso in zip(notas, pesos))
    soma_pesos = sum(pesos)

    if soma_pesos == 0:
        raise ValueError("Soma dos pesos não pode ser zero")

    return soma_ponderada / soma_pesos
```

**Sua tarefa:** escreva testes que detectem o bug.

<details>
<summary><strong>Ver testes que detectam o bug</strong></summary>

```python
# test_media.py
import pytest
from media import calcular_media_ponderada

def test_media_basica():
    """Média ponderada simples funciona corretamente."""
    resultado = calcular_media_ponderada([8.0, 9.0, 7.0], [1, 2, 3])
    assert abs(resultado - 7.833333) < 0.0001

def test_media_pesos_iguais():
    """Com pesos iguais, equivale à média simples."""
    resultado = calcular_media_ponderada([8.0, 9.0, 7.0], [1, 1, 1])
    assert resultado == 8.0

def test_media_listas_tamanhos_diferentes():
    with pytest.raises(ValueError, match="mesmo tamanho"):
        calcular_media_ponderada([8.0, 9.0], [1, 2, 3])

def test_media_lista_vazia():
    with pytest.raises(ValueError, match="vazia"):
        calcular_media_ponderada([], [])

def test_media_peso_negativo_deve_levantar_erro():
    """
    BUG DETECTADO:
    A documentação diz que pesos devem ser positivos.
    Peso negativo não faz sentido conceitual.
    O código deveria levantar ValueError, mas aceita e calcula.
    """
    with pytest.raises(ValueError, match="[Pp]eso"):
        calcular_media_ponderada([8.0, 9.0], [2, -1])
    # FALHA: DID NOT RAISE. O código retorna 7.0 sem erro.

def test_media_peso_zero_deve_levantar_erro():
    """
    BUG DETECTADO:
    Peso zero também não faz sentido (anula a nota).
    """
    with pytest.raises(ValueError, match="[Pp]eso"):
        calcular_media_ponderada([8.0, 9.0], [1, 0])
    # FALHA: DID NOT RAISE. O código retorna 8.0 sem erro.
```

Saída esperada:

```text
test_media.py .....FF

FAILED test_media.py::test_media_peso_negativo_deve_levantar_erro - DID NOT RAISE
FAILED test_media.py::test_media_peso_zero_deve_levantar_erro - DID NOT RAISE
```

**A correção** é adicionar a validação antes do cálculo:

```python
for peso in pesos:
    if peso <= 0:
        raise ValueError("Todos os pesos devem ser positivos.")
```
</details>

---

### Exercício 6 — Encontre o bug: Arredondamento bancário

A função abaixo calcula juros simples mas tem um erro de arredondamento que acumula ao longo de múltiplos períodos.

```python
# juros.py
def calcular_juros_simples(capital, taxa_percentual, periodos):
    """
    Calcula o montante final com juros simples.

    Regra: o valor é arredondado para 2 casas decimais
    apenas no resultado final, não a cada período.

    Args:
        capital: valor inicial (float)
        taxa_percentual: taxa por período em % (ex: 10 para 10%)
        periodos: número de períodos (int)

    Returns:
        float: montante final arredondado a 2 casas
    """
    taxa = taxa_percentual / 100

    # BUG: arredonda a cada iteração, acumulando erro.
    # A documentação diz arredondar apenas no final.
    montante = capital
    for _ in range(periodos):
        juros_periodo = montante * taxa
        montante = round(montante + juros_periodo, 2)

    return montante
```

**Sua tarefa:** escreva um teste que detecte a diferença entre arredondar a cada período vs. arredondar apenas no final.

<details>
<summary><strong>Ver teste que detecta o bug</strong></summary>

```python
# test_juros.py
from juros import calcular_juros_simples

def test_juros_simples_um_periodo():
    """Com um período, arredondar no meio ou no final dá o mesmo."""
    resultado = calcular_juros_simples(100.0, 10, 1)
    assert resultado == 110.0

def test_juros_simples_multiplos_periodos():
    """
    BUG DETECTADO:
    100 * (1 + 0.10 * 3) = 130.00  (cálculo direto, sem arredondamento intermediário)

    Com arredondamento a cada período:
      Período 1: 100 + 10.00 = 110.00
      Período 2: 110 + 11.00 = 121.00  (110 * 0.1 = 11)
      Período 3: 121 + 12.10 = 133.10  (121 * 0.1 = 12.1)

    Mas isso é JUROS COMPOSTOS disfarçado!
    Juros simples: 100 + (100 * 0.1 * 3) = 130.00

    O bug é duplo: arredondamento intermediário E cálculo sobre
    o montante acumulado em vez do capital original.
    """
    resultado = calcular_juros_simples(100.0, 10, 3)
    # Juros simples correto: 100 + 100*0.1*3 = 130.0
    assert resultado == 130.0  # FALHA: retorna 133.1
```

Saída esperada:

```text
test_juros.py .F

FAILED test_juros.py::test_juros_simples_multiplos_periodos - assert 133.1 == 130.0
```

**A correção** é calcular juros sempre sobre o capital original:

```python
def calcular_juros_simples(capital, taxa_percentual, periodos):
    taxa = taxa_percentual / 100
    montante = capital + capital * taxa * periodos
    return round(montante, 2)
```
</details>

---
<!-- 
## Verificação: saída esperada ao rodar todos os testes

```text
$ pytest -v

test_carrinho.py::test_carrinho_sem_desconto PASSED
test_carrinho.py::test_carrinho_com_10_porcento PASSED
test_carrinho.py::test_carrinho_com_20_porcento PASSED
test_carrinho.py::test_carrinho_exatamente_100_reais FAILED
test_carrinho.py::test_carrinho_exatamente_500_reais FAILED
test_idade.py::test_idade_basica PASSED
test_idade.py::test_idade_aniversario_hoje FAILED
test_idade.py::test_idade_aniversario_amanha PASSED
test_idade.py::test_idade_data_invalida_29_fev FAILED
test_produto_classificar.py::test_produto_invalido_preco_negativo PASSED
test_produto_classificar.py::test_produto_invalido_estoque_negativo PASSED
test_produto_classificar.py::test_produto_esgotado PASSED
test_produto_classificar.py::test_produto_promocao_relampago PASSED
test_produto_classificar.py::test_produto_exatamente_50_reais FAILED
test_produto_classificar.py::test_produto_exatamente_100_reais PASSED
test_produto_classificar.py::test_produto_exatamente_1000_reais PASSED
test_produto_classificar.py::test_produto_promocao PASSED
test_produto_classificar.py::test_produto_premium PASSED
test_produto_classificar.py::test_produto_normal PASSED
test_produto_classificar.py::test_produto_esgotado_tem_prioridade PASSED
test_senha.py::test_senha_valida_completa PASSED
test_senha.py::test_senha_muito_curta PASSED
test_senha.py::test_senha_sem_maiuscula FAILED
test_senha.py::test_senha_sem_minuscula FAILED
test_senha.py::test_senha_sem_numero FAILED
test_senha.py::test_senha_apenas_numeros FAILED
test_senha.py::test_senha_apenas_letras FAILED
test_media.py::test_media_basica PASSED
test_media.py::test_media_pesos_iguais PASSED
test_media.py::test_media_listas_tamanhos_diferentes PASSED
test_media.py::test_media_lista_vazia PASSED
test_media.py::test_media_peso_negativo_deve_levantar_erro FAILED
test_media.py::test_media_peso_zero_deve_levantar_erro FAILED
test_juros.py::test_juros_simples_um_periodo PASSED
test_juros.py::test_juros_simples_multiplos_periodos FAILED

========================= 12 failed, 23 passed in 0.05s =========================
```

Cada `FAILED` corresponde a um bug real no código testado, não a um teste mal escrito. -->

## 9. Checklist da aula

Ao final desta aula, você deve conseguir:

- explicar a diferença entre teste manual e automatizado;
- entender o padrão AAA (Arrange, Act, Assert);
- escrever testes unitários simples usando `pytest` e a palavra-chave `assert`;
- testar o "caminho feliz" e os "casos de borda" de uma função ou método;
- usar `pytest.raises` para testar se uma exceção foi levantada corretamente;
- usar `ruff check` para encontrar erros lógicos e imports inúteis;
- usar `ruff format` para padronizar a formatação do código automaticamente.

---

## 10. Recapitulação

| Conceito | Significado |
|---|---|
| Teste Unitário | Teste que verifica uma unidade isolada de código (uma função ou método de classe). |
| `pytest` | Framework que descobre e executa funções que começam com `test_`. |
| `assert` | Palavra-chave do Python que interrompe a execução se a condição for falsa. |
| AAA (Arrange, Act, Assert) | Padrão de estruturação de testes: Preparar, Agir, Assertar. |
| Casos de borda | Cenários extremos (vazio, nulo, negativo, máximo) onde bugs costumam se esconder. |
| `pytest.raises` | Gerenciador de contexto para afirmar que um bloco de código levanta uma exceção específica. |
| Linting | Análise estática do código em busca de erros lógicos e más práticas. |
| `ruff` | Ferramenta moderna que faz linting, formatação e organização de imports. |

---

## 11. O que não vimos no curso até aqui

Os tópicos abaixo são comuns em testes profissionais, mas ficaram de fora desta aula introdutória para manter o foco no que é essencial para o seu projeto atual.

| Tópico | Síntese |
|---|---|
| **TDD (Test-Driven Development)** | Metodologia onde o teste é escrito *antes* do código da funcionalidade. O ciclo é: Teste Falha (Vermelho) -> Código Passa (Verde) -> Refatora. |
| **Mocks e Patches** | Técnicas para isolar o código testado, "fingindo" que dependências externas (como o SQLite ou a API do ViaCEP) retornaram um valor específico, sem precisar de internet ou banco de dados real. |
| **Fixtures (`@pytest.fixture`)** | Funções que preparam um estado complexo (como popular um banco de dados de teste) e o injetam automaticamente em vários testes diferentes. |
| **Cobertura de Código (`coverage.py`)** | Ferramenta que mede a porcentagem exata de linhas do seu código que foram executadas pelos testes. |
| **Testes de Integração e E2E** | Testes que verificam múltiplas camadas juntas (Flask + SQLite) ou simulam um usuário real clicando no navegador (Playwright). Serão vistos nas próximas aulas. |