import random

class Jugador:
    def __init__(self, nombre: str, mazo_cartas: list, origen_set: dict):
        self.nombre = nombre
        self.mazo = list(mazo_cartas)
        random.shuffle(self.mazo)
        self.origen_set = origen_set
        self.mano: list = []
        self.vida = 15
        self.suerte_turnos = 0
        self.descartadas: list = []
        self.estado = {
            "defensa": 0,
            "sangrado": 0,
            "fuego": 0,
            "congelado": 0,
            "paralizado": 0,
            "esquiva": False
        }

    def robar(self, cantidad=1):
        for _ in range(cantidad):
            if self.mazo:
                self.mano.append(self.mazo.pop(0))

    def activar_suerte(self):
        self.suerte_turnos = 4

    def tiene_suerte(self):
        return self.suerte_turnos > 0

    def esta_vivo(self):
        return self.vida > 0

    def sin_cartas(self):
        return not self.mazo and not self.mano
    
    def puede_continuar(self):
        return self.esta_vivo() and not self.sin_cartas()

    def actualizar_estados(self):
        if self.suerte_turnos > 0:
            self.suerte_turnos -= 1

    def __str__(self):
        return f"{self.nombre} (Vida: {self.vida}, Cartas en mazo: {len(self.mazo)})"