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
