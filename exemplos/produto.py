# produto.py
class Produto:
    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def validar(self):
        if not self.nome:
            return False
        if self.preco <= 0:
            return False
        if self.estoque < 0:
            return False
        return True
