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

def test_concluir_altera_estado():
    t = Tarefa("Estudar Flask")
    
    # Estado inicial
    assert t.concluida is False
    
    # Ação
    t.concluir()
    
    # Estado final esperado
    assert t.concluida is True

def test_to_dict_retorna_estrutura_correta():
    t = Tarefa("Estudar", id=42, concluida=True)
    
    dicionario = t.to_dict()
    
    assert isinstance(dicionario, dict)
    assert dicionario["id"] == 42
    assert dicionario["descricao"] == "Estudar"
    assert dicionario["concluida"] is True

import pytest

def dividir(a, b):
    if b == 0:
        raise ValueError("Divisor não pode ser zero.")
    return a / b

def test_divisao_por_zero_levanta_excecao():
    with pytest.raises(ValueError, match="Divisor não pode ser zero"):
        dividir(10, 0)
