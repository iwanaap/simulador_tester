

class Carta:
    def __init__(self, nombre, nomenclatura, nivel):
        self.nombre = nombre
        self.nomenclatura = nomenclatura
        self.nivel = nivel
        self.tipo = self.definir_tipo()

    def definir_tipo(self):
        uni = self.nombre.upper()
        if "AZAR" in uni:
            return "AZAR"
        elif "CERTERO" in uni:
            return "CERTERO"
        return "NORMAL"

    def accion_principal(self):
        return self.nomenclatura.split("+")[0].strip()

    def __repr__(self):
        return f"{self.nombre} (Nivel {self.nivel}, Tipo: {self.tipo})"


