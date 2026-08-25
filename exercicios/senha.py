# senha.py
def validar_senha(senha):
    """
    Valida uma senha baseada em critérios de segurança.

    Regras:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número

    Retorna True se a senha for válida, False caso contrário.
    """
    if len(senha) < 8:
        return False

    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False

    for char in senha:
        if char.isupper():
            tem_maiuscula = True
        elif char.islower():
            tem_minuscula = True
        elif char.isdigit():
            tem_numero = True

    # BUG: usa 'or' em vez de 'and'.
    # Basta UM dos critérios para retornar True.
    return tem_maiuscula or tem_minuscula or tem_numero
