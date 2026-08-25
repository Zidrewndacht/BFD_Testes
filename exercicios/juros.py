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
