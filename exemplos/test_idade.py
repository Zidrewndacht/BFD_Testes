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
