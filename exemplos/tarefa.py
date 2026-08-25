# tarefa.py
class Tarefa:
    def __init__(self, descricao, id=None, concluida=False):
        self.id = id
        self.descricao = descricao
        self.concluida = concluida

    def validar(self):
        if not isinstance(self.descricao, str):
            return False
        if not self.descricao.strip():
            return False
        if len(self.descricao) > 100:
            return False
        return True

    def concluir(self):
        self.concluida = True

    def to_dict(self):
        return {
            "id": self.id,
            "descricao": self.descricao,
            "concluida": self.concluida,
        }
