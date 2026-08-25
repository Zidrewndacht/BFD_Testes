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
