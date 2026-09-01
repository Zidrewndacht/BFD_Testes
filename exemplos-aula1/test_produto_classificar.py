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
