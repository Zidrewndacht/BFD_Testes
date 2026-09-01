# test_produto.py
import pytest
from produto import Produto

# Versão não-parametrizada:
# def test_produto_valido():
#     p = Produto("Teclado", 150.0, 10)
#     assert p.validar() is True

# def test_produto_invalido_sem_nome():
#     p = Produto("", 150.0, 10)
#     assert p.validar() is False

# def test_produto_invalido_preco_zero():
#     p = Produto("Mouse", 0, 5)
#     assert p.validar() is False

# def test_produto_invalido_preco_negativo():
#     p = Produto("Monitor", -100.0, 2)
#     assert p.validar() is False

# def test_produto_invalido_estoque_negativo():
#     p = Produto("Cabo", 10.0, -1)
#     assert p.validar() is False

# def test_produto_valido_com_estoque_zero():
#     # Estoque zero é permitido (produto esgotado, mas válido)
#     p = Produto("Webcam", 200.0, 0)
#     assert p.validar() is True

# Versão parametrizada:
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
