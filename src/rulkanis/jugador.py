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
        self.salta_turno: bool = False
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
    
    def lanzar_dado(self):
        return random.randint(1, 10)

    def terminar_turno(self):
        self.robar(1)
        self.actualizar_estados()

    def tiene_carta_de_esquive(self):
        

    def descartar(self, carta):
        if carta in self.mano:
            self.mano.remove(carta)
            self.descartadas.append(carta)
        else:
            raise ValueError("Carta no está en la mano")

    def actualizar_estados(self):
        if self.suerte_turnos > 0:
            self.suerte_turnos -= 1

    def aplicar_efectos_de_estado(self):
        eventos = []
        self.salta_turno = False
        # Sangrado
        if self.estado.get("sangrado",0) > 0:
            self.vida -= 1
            self.estado["sangrado"] -= 1
            eventos.append("Sangrado: -1 vida")

        # Fuego
        if self.estado.get("fuego",0) > 0:
            if self.estado["defensa"] > 0:
                self.estado["defensa"] -= 1
                eventos.append("Fuego: -1 defensa")
            else:
                self.vida -= 1
                eventos.append("Fuego: -1 vida")
            self.estado["fuego"] -= 1

        # Congelar
        if self.estado.get("congelado",0) > 0:
            self.estado["congelado"] -= 1
            eventos.append("Congelado: pierde turno")
            self.salta_turno = True

        # Paralizar (siempre chequeamos, no es elif de congelado)
        if self.estado.get("paralizado", 0) > 0:
            # umbral cambia si tiene suerte activada
            limite = 4 if self.tiene_suerte() else 6
            d = self.lanzar_dado()
            if d < limite:
                eventos.append(f"Paralizado: dado {d} (<{limite}), pierde turno")
                self.salta_turno = True
            else:
                eventos.append(f"Paralizado: dado {d} (≥{limite}), puede jugar")
            self.estado["paralizado"] -= 1

        return eventos


    def __str__(self):
        return f"{self.nombre} (Vida: {self.vida}, Cartas en mazo: {len(self.mazo)})"