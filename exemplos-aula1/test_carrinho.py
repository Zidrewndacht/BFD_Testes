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
