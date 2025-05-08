from .carta import Carta
from .jugador import Jugador

class Logger:
    def __init__(
        self,
        partida: int,
        turno: int,
        jugador: str,
        fase: str,
        evento: str,
        j1: Jugador,
        j2: Jugador,
    ):
        self.partida = partida
        self.turno = turno
        self.jugador = jugador
        self.fase = fase
        self.evento = evento
        self.j1 = j1
        self.j2 = j2


    def actualizar_campos(self, campos: dict):
        for key, value in campos.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"El campo '{key}' no existe en la clase Logger.")

    def log_inicio_turno(self, detalle: list, saltar: bool):
        
        detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Fase": "InicioTurno",
                "Evento": "; ".join(self.evento) or "—",
                "SaltaTurno": saltar,
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )

    def log_reaccion(self, detalle: list, resultado: str, carta: Carta, evento: str):
        detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Carta": carta.nombre,
                "Fase": "Reaccion",
                "Resultado": resultado,
                "Evento": evento,
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )

    def log_fin_turno(self, detalle: list, carta: Carta, dado: int, resultado: str, evento: str):
        
        detalle.append(
            {
                "Partida": self.partida,
                "Turno": self.turno,
                "Jugador": self.jugador,
                "Carta": carta.nombre,
                "Nivel": carta.nivel,
                "Tipo": carta.tipo,
                "Dado": dado,
                "Resultado": resultado,
                "Evento": evento,
                "Vida J1": self.j1.vida,
                "Defensa J1": self.j1.estado["defensa"],
                "Vida J2": self.j2.vida,
                "Defensa J2": self.j2.estado["defensa"]
            }
        )
