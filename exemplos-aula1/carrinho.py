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
