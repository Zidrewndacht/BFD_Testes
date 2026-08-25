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
